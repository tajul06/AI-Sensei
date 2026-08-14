from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from modules.llm import get_llm_chain
from modules.query_handlers import query_chain
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from pinecone import Pinecone
from pydantic import Field
from typing import List, Optional
from logger import logger
import os

router = APIRouter()


@router.post("/ask/")
async def ask_question(user_query: str = Form(...)):
    try:
        logger.info(f"Received user query: {user_query}")
        # embeddding and pinecone setup

        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
        index = pc.Index(os.environ.get("PINECONE_INDEX_NAME"))
        hf_token = os.environ.get("HF_TOKEN")
        embeddings =HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",

        huggingfacehub_api_token=os.environ.get("HF_TOKEN")
    )

        embedded_query = embeddings.embed_query(user_query)
        results = index.query(vector=embedded_query, top_k=5, include_metadata=True)

        docs = [
            Document(
                page_content=match['metadata'].get("text", ""),
                metadata=match['metadata'],
            )
            for match in results['matches']
        ]

        class SimpleRetriever(BaseRetriever):
            tags: Optional[List[str]] = Field(default_factory=list)
            metadata: Optional[dict] = Field(default_factory=dict)

            def _init__(self, documents: List[Document]):
                super().__init__()
                self.documents = documents

            def get_relevant_documents(self, query: str) -> List[Document]:
                return self.documents

        retriever = SimpleRetriever(documents=docs)
        llm_chain = get_llm_chain(retriever)
        response = query_chain(llm_chain, user_query)

        logger.info("Successfully processed user query.")
        return JSONResponse(content=response)

    except Exception as e:
        logger.exception(f"Error in ask_question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "error": str(e)},
        )