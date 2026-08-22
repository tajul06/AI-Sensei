# scripts/clear_index.py
from pinecone import Pinecone
from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
index.delete(delete_all=True)
print(f"Cleared all vectors from '{PINECONE_INDEX_NAME}'.")