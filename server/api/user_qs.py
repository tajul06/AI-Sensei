import time
from fastapi import APIRouter, Form ,Depends
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from services.llm import get_llm_chain
from services.query_handlers import query_chain
from services.pinecone_client import query_pinecone_async
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pinecone import Pinecone
from pydantic import Field
from typing import List, Optional
from logger import logger
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME, HF_TOKEN ,GOOGLE_API_KEY
from config.models import HF_EMBEDDING_MODEL ,GEMINI_MODEL
from config.subjects import group_for_subject
from config.retrieval import get_top_k_for_group , RERANK_ENABLED , RERANK_TOP_N ,BROAD_TOP_K
from services.auth import get_current_user
from services.query_handlers import query_chain
from services.pinecone_client import query_pinecone_async
from services.chat_history import get_recent_messages , save_message 
from services.query_condense import condense_query
from services.reranker import rerank_documents




router = APIRouter()


@router.post("/ask/")
async def ask_question(
    start =time.perf_counter(),
    user_query: str = Form(...),
    subject: str = Form(...),
    session_id: str = Form(...),
    user_id: str = Depends(get_current_user)
):
    try:
        logger.info(f"[{start:.2f}] Received request to process user query for subject: {subject} : {user_query}")
        group=group_for_subject(subject)  # Validate subject
        logger.info(f"Query for subject={subject}, user={user_id}, session={session_id}: {user_query}")

        history=get_recent_messages(session_id)

        condenser_llm = ChatGoogleGenerativeAI(model =GEMINI_MODEL, api_key=GOOGLE_API_KEY)
        standalone_query = await condense_query(user_query, history, condenser_llm)
        # embeddding and pinecone setup

        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        embeddings = HuggingFaceEndpointEmbeddings(
            model=HF_EMBEDDING_MODEL,
            huggingfacehub_api_token=HF_TOKEN,
        )

        embedded_query = await embeddings.aembed_query(standalone_query)
        results = await query_pinecone_async(
            vector=embedded_query,
            top_k=BROAD_TOP_K,
            filter={"subject": subject, "user_id": user_id},
        )
        docs = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {}) or {}
            page_content = metadata.get("text") or ""
            if not page_content:
                continue
            docs.append(Document(page_content=page_content, metadata=metadata))

        if RERANK_ENABLED:
            docs = await rerank_documents(standalone_query, docs, top_n=RERANK_TOP_N)
        else:
            docs = docs[:get_top_k_for_group(group)]

        class SimpleRetriever(BaseRetriever):
            

            documents: List[Document] = Field(default_factory=list)

            def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
                return self.documents

        retriever = SimpleRetriever(documents=docs)
        llm_chain = get_llm_chain(subject, retriever)
        response = await query_chain(llm_chain, standalone_query)

        save_message(session_id, "user", user_query)
        save_message(session_id, "assistant", response.get("result"))
        logger.info(f"[{time.perf_counter():.2f}] Query processed successfully for subject: {subject} : {user_query} (took {time.perf_counter()-start:.2f}seconds)")
        return JSONResponse(content={
            "result": response.get("result"),
            "source_documents": [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in response.get("source_documents", [])
            ],  
        })

    
        

    except ValueError as ve:
        logger.warning(f"Invalid subject provided: {subject}. Error: {str(ve)}")
        return JSONResponse(status_code=400, content={"message": str(ve)})
    except Exception as e:
        logger.exception(f"Error in ask_question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "error": str(e)},
        )