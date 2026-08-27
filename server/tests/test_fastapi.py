import asyncio
import httpx

async def test_api():
    print("Sending request...")
    async with httpx.AsyncClient() as client:
        # We need an auth token, maybe it's not needed if we mock it?
        pass

if __name__ == "__main__":
    asyncio.run(test_api())
