import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm 
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings


load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = "us-east1"
PINECONE_INDEX_NAME = "ai-sensei"

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)



#initialize pinecone instance
pc = Pinecone(api_key=PINECONE_API_KEY)
spec = ServerlessSpec(cloud="aws", region = PINECONE_ENV)
existing_indexes = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=spec
    )       
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
       
        time.sleep(5)

index = pc.Index(PINECONE_INDEX_NAME)

#load ,split and embed documents
def load_and_embed_documents(uploaded_files):

    embed_model = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",

        
    )

    file_paths = []

    #1. Save uploaded files to the UPLOAD_DIR
    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))

#2. Load and split documents
    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks =text_splitter.split_documents(documents)

        texts =[chunk.page_content for chunk in chunks]
        metadata =[chunk.metadata for chunk in chunks]
        ids=[f"{Path(file_path).stem}_{i}" for i in range(len(chunks))]

        print(f"Embedding and uploading {len(texts)} chunks from {file_path} to Pinecone...")
        embeddings =embed_model.embed_documents(texts)
#upsert embeddings to pinecone in batches of 100
        print("Uploading embeddings to Pinecone..."
              )
        with tqdm(total=len(embeddings), desc="Uploading embeddings") as progress_bar:
            for i in range(0, len(embeddings), 100):
                batch_embeddings = embeddings[i:i + 100]
                batch_ids = ids[i:i + 100]
                batch_metadata = metadata[i:i + 100]
                index.upsert(vectors=zip(batch_ids, batch_embeddings, batch_metadata))
                progress_bar.update(len(batch_embeddings))

        print(f"Finished uploading embeddings for {file_path} to Pinecone.")