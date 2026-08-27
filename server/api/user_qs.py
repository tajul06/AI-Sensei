import time
import asyncio
from fastapi import APIRouter, Form ,Depends
from fastapi import Request,HTTPException
from fastapi.responses import JSONResponse ,StreamingResponse
from fastapi.concurrency import run_in_threadpool
from slowapi.util import get_remote_address
from services.llm import get_llm_chain
from services.query_handlers import query_chain
from services.pinecone_client import query_pinecone_async
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
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
from services.quota import check_and_increment_quota
from services.limiter import limiter



router = APIRouter()


@router.post("/ask/")
@limiter.limit("10/minute")
async def ask_question(
    request: Request,
    user_query: str = Form(...),
    subject: str = Form(...),
    session_id: str = Form(...),
    user_id: str = Depends(get_current_user)
):
    if not check_and_increment_quota(user_id):
        raise HTTPException(status_code=429, detail="Quota exceeded. Please try again later.")
    start = time.perf_counter()
    try:
        logger.info(f"[{start:.2f}] Received request to process user query for subject: {subject} : {user_query}")
        group=group_for_subject(subject)  # Validate subject
        logger.info(f"Query for subject={subject}, user={user_id}, session={session_id}: {user_query}")

        history=get_recent_messages(session_id)

        condenser_llm = ChatGoogleGenerativeAI(model =GEMINI_MODEL, api_key=GOOGLE_API_KEY)
        standalone_query = await condense_query(user_query, history, condenser_llm)
        logger.info(f"[Diagnostic] Original query: '{user_query}' -> Standalone query: '{standalone_query}' ")
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

        raw_matches = results.get("matches", [])
        logger.info(f"[Diagnostic] Pinecone returned {len(raw_matches)} matches for filter subject={subject}, user_id={user_id}")
        docs = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {}) or {}
            page_content = metadata.get("text") or ""
            if not page_content:
                continue
            docs.append(Document(page_content=page_content, metadata=metadata))

        logger.info(f"[Diagnostic] Constructed {len(docs)} Document objects from Pinecone matches for subject={subject}, user_id={user_id}")

        if RERANK_ENABLED:
            docs = await rerank_documents(standalone_query, docs, top_n=RERANK_TOP_N)
            logger.info(f"[Diagnostic] Reranked documents, reduced to {len(docs)} docs remained")
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

        collected: list[str] = []

        async def generate():
            try:
                async for chunk in llm_chain.astream(standalone_query):
                    collected.append(chunk)
                    # Gemini chunks can be large; break them into smaller pieces for a smoother, ChatGPT-like visual stream
                    chunk_size = 3
                    for i in range(0, len(chunk), chunk_size):
                        yield chunk[i:i+chunk_size]
                        await asyncio.sleep(0.01)
                # Save after stream is fully consumed
                full_response = "".join(collected)
                save_message(session_id, "user", user_query)
                save_message(session_id, "assistant", full_response)
                elapsed = time.perf_counter() - start
                logger.info(f"[{elapsed:.2f}s] Stream complete for subject={subject}, user={user_id}: {user_query!r}")
            except Exception as e:
                logger.error(f"Error during stream generation: {e}")
                yield f"\n\nAn error occurred while generating the response: {e}"

        return StreamingResponse(generate(), media_type="text/plain")

    
        
    except ChatGoogleGenerativeAIError as ce:
        if "RESOURCE_EXHAUSTED" in str(ce):
            return JSONResponse(status_code=503, content={"message": "High demand right now. Please try again shortly."})
        logger.exception(f"Google Generative AI Error: {str(ce)}")
        return JSONResponse(status_code=500, content={"message": "AI Model Error", "error": str(ce)})
    except ValueError as ve:
        logger.warning(f"Invalid subject provided: {subject}. Error: {str(ve)}")
        return JSONResponse(status_code=400, content={"message": str(ve)})
    except Exception as e:
        logger.exception(f"Error in ask_question: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error", "error": str(e)},
        )