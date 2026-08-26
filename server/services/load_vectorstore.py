
import time
from pathlib import Path


from tqdm.auto import tqdm 
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME, HF_TOKEN
from config.models import HF_EMBEDDING_MODEL, EMBEDDING_DIMENSION
from config.subjects import group_for_subject
from config.chunking import get_splitter
from config.perser import load_with_pymupdf4llm
from services.uploaded_files import record_uploaded_file


PINECONE_ENV = "us-east-1"  


UPLOAD_DIR = "./uploaded_docs"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)



#initialize pinecone instance
_pc = None
_index = None

def get_pinecone_index():
    global _pc, _index
    if _index is not None:
        return _index

    _pc = Pinecone(api_key=PINECONE_API_KEY)
    spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    existing_indexes = [i["name"] for i in _pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        _pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=spec
        )
        while not _pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
            time.sleep(5)

    _index = _pc.Index(PINECONE_INDEX_NAME)
    return _index

#load ,split and embed documents
def load_and_embed_documents(uploaded_files ,subject:str ,user_id:str):
    group = group_for_subject(subject)
    index = get_pinecone_index()

    embed_model = HuggingFaceEndpointEmbeddings(
    model=HF_EMBEDDING_MODEL,
    task="feature-extraction",
    huggingfacehub_api_token=HF_TOKEN,
)
    text_splitter = get_splitter(group)
    # List of (save_path, original_filename) so inner loop can record each file correctly
    file_entries: list[tuple[str, str]] = []

    #1. Save uploaded files to the UPLOAD_DIR
    for file in uploaded_files:
        print("DEBUG filename:", repr(file.filename), "content_type:", file.content_type)
        if not file.filename:
            raise ValueError(
                f"Received a file with no filename. content_type={file.content_type}. "
                "Check that Postman's form-data key is set to type 'File', not 'Text'."
            )
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_entries.append((str(save_path), file.filename))

    #2. Load, split, embed, and record each document
    for file_path, filename in file_entries:
        try:
            if group in ("math", "stem"):
                documents = load_with_pymupdf4llm(file_path)
            else:
                loader = PyPDFLoader(file_path)
                documents = loader.load()

            chunks = text_splitter.split_documents(documents)

            texts = [chunk.page_content for chunk in chunks]
            metadata = []
            for chunk in chunks:
                chunk_metadata = dict(chunk.metadata)
                chunk_metadata["text"] = chunk.page_content
                chunk_metadata["subject"] = subject
                chunk_metadata["group"] = group
                chunk_metadata["user_id"] = user_id
                metadata.append(chunk_metadata)
            ids = [f"{user_id}_{Path(file_path).stem}_{i}" for i in range(len(chunks))]

            print(f"Embedding and uploading {len(texts)} chunks from {file_path} to Pinecone...")
            embeddings = embed_model.embed_documents(texts)

            # Upsert embeddings to Pinecone in batches of 100
            print("Uploading embeddings to Pinecone...")
            with tqdm(total=len(embeddings), desc="Uploading embeddings") as progress_bar:
                for i in range(0, len(embeddings), 100):
                    batch_embeddings = embeddings[i:i + 100]
                    batch_ids = ids[i:i + 100]
                    batch_metadata = metadata[i:i + 100]

                    index.upsert(vectors=list(zip(batch_ids, batch_embeddings, batch_metadata)))
                    progress_bar.update(len(batch_embeddings))

            print(f"Finished uploading embeddings for {file_path} to Pinecone.")
            # Record this specific file — not the last loop variable
            record_uploaded_file(user_id, subject, filename)
        finally:
            # Clean up the uploaded file after processing
            Path(file_path).unlink(missing_ok=True)