import asyncio
from dotenv import load_dotenv
load_dotenv("d:/Ai Sensei/server/.env")

import os
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=os.environ.get("GOOGLE_API_KEY"),
    max_output_tokens=1024,
)

prompt = PromptTemplate.from_template("Question: {question}\nAnswer:")
chain = {"question": RunnablePassthrough()} | prompt | llm | StrOutputParser()

async def test():
    print("Testing astream...")
    try:
        async for chunk in chain.astream("What is 2+2?"):
            print(f"CHUNK: {repr(chunk)}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())
