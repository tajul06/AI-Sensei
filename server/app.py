import asyncio
import httpx
import time

async def send_request(client, query):
    start = time.perf_counter()
    resp = await client.post(
        "http://localhost:8000/ask/",
        data={"user_query": query, "subject": "Biology"},
    )
    elapsed = time.perf_counter() - start
    print(f"Query '{query}' took {elapsed:.2f}s, status {resp.status_code}")

async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        start = time.perf_counter()
        await asyncio.gather(
            send_request(client, "what is diabetes"),
            send_request(client, "what is a virus"),
        )
        total = time.perf_counter() - start
        print(f"Total wall time for both: {total:.2f}s")

asyncio.run(main())