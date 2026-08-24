import httpx
from langchain_core.documents import Document
from config.settings import JINA_API_KEY

JINA_API_URL = "https://api.jina.ai/v1/rerank"
JINA_MODEL = "jina-reranker-v3.5"

async def rerank_documents(query: str, docs: list[Document] ,top_n:int) -> list[Document]:
    """
    Rerank documents using Jina's reranking API.

    """
    if not docs:
        return docs

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                JINA_API_URL,
                headers={
                    "Authorization": f"Bearer {JINA_API_KEY}",
                    "Content-Type": "application/json",
                    },
                json={
                    "model": JINA_MODEL,
                    "query": query,
                    "documents": [doc.page_content for doc in docs],
                    "top_n": top_n
                },
            )
            response.raise_for_status()
            results = response.json()
    except (httpx.HTTPError ,ValueError) as e:
        print(f"Error occurred while reranking documents: {e}"  )
        return docs[:top_n]  # Return the original documents if there's an error

    ranked_indices = [item["index"] for item in results.get("results", [])]
    return [docs[i] for i in ranked_indices ]
