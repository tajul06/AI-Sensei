from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from services.llm import get_llm_chain
from services.query_handlers import query_chain
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from pinecone import Pinecone
from pydantic import Field
from typing import List, Optional
from logger import logger
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME, HF_TOKEN
from config.models import HF_EMBEDDING_MODEL
from config.subjects import group_for_subject
from config.retrieval import get_top_k_for_group


router = APIRouter()


@router.post("/ask/")
async def ask_question(
    user_query: str = Form(...),
    subject: str = Form(...),
):
    try:
        group=group_for_subject(subject)  # Validate subject
        logger.info(f"Received request to process user query for subject: {subject} : {user_query}")
    
        # embeddding and pinecone setup

        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        embeddings = HuggingFaceEndpointEmbeddings(
            model=HF_EMBEDDING_MODEL,
            huggingfacehub_api_token=HF_TOKEN,
        )

        embedded_query = embeddings.embed_query(user_query)
        results = index.query(
            vector=embedded_query, 
            top_k=get_top_k_for_group(group), 
            include_metadata=True ,
            filter={"subject": subject}
            )

        docs = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {}) or {}
            page_content = metadata.get("text") or ""
            if not page_content:
                continue
            docs.append(Document(page_content=page_content, metadata=metadata))

        class SimpleRetriever(BaseRetriever):
            

            documents: List[Document] = Field(default_factory=list)

            def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
                return self.documents

        retriever = SimpleRetriever(documents=docs)
        llm_chain = get_llm_chain(subject, retriever)
        response = query_chain(llm_chain, user_query)

        logger.info("Successfully processed user query.")
        serializable_response = {
    "result": response.get("result"),
    "source_documents": [
        {
            "page_content": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in response.get("source_documents", [])
    ],
}
        return JSONResponse(content=serializable_response)
    except ValueError as ve:
        logger.warning(f"Invalid subject provided: {subject}. Error: {str(ve)}")
        return JSONResponse(status_code=400, content={"message": str(ve)})
    except Exception as e:
        logger.exception(f"Error in ask_question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "error": str(e)},
        )