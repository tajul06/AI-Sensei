# test_jina_rerank.py
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import httpx

# Adjust this path if your .env lives somewhere else relative to this script
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

JINA_API_KEY = os.environ.get("JINA_API_KEY")
JINA_RERANK_URL = "https://api.jina.ai/v1/rerank"
JINA_RERANK_MODEL = "jina-reranker-v3.5"

QUERY = "what is diabetes"
DOCUMENTS = [
    "Diabetes is a chronic condition that affects how your body turns food into energy.",
    "The French Revolution began in 1789 and reshaped European politics.",
    "Symptoms of diabetes include increased thirst, frequent urination, and fatigue.",
]


async def test_jina_rerank():
    if not JINA_API_KEY:
        raise RuntimeError("JINA_API_KEY not found — check your .env path and key name")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            JINA_RERANK_URL,
            headers={
                "Authorization": f"Bearer {JINA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": JINA_RERANK_MODEL,
                "query": QUERY,
                "documents": DOCUMENTS,
                "top_n": len(DOCUMENTS),
            },
        )

    print("Status:", response.status_code)
    print("Raw body:", response.text)

    if response.status_code == 200:
        result = response.json()
        print("\nParsed results:")
        for item in result.get("results", []):
            idx = item.get("index")
            score = item.get("relevance_score")
            doc_text = DOCUMENTS[idx] if idx is not None else "?"
            print(f"  score={score}  ->  {doc_text}")


if __name__ == "__main__":
    asyncio.run(test_jina_rerank())