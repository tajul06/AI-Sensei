from pinecone import Pinecone
from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# dummy query vector just to test the filter — doesn't need to be semantically meaningful for this check
stats = index.describe_index_stats()
print(stats)