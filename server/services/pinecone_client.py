from pinecone import Pinecone ,PineconeAsyncio
from config.settings import PINECONE_API_KEY, PINECONE_INDEX_NAME

_index_host = None
_async_pc = None
_async_index = None

def get_pinecone_index() ->str:
    """
    fetches and caches the Pinecone index host URL for the specified index name. If the index does not exist, it will be created.
    """

    global _index_host
    if _index_host is not None:
        return _index_host

    pc = Pinecone(api_key=PINECONE_API_KEY)
    description = pc.describe_index(PINECONE_INDEX_NAME)
    _index_host = description.host
    return _index_host

async def get_async_pinecone_index() :
    """
    Returns a cached PineconeAsyncio index connection, creating it once on
    first call and reusing it for every subsequent query — avoids paying
    connection setup cost on every request.
    """

    global _async_pc, _async_index
    if _async_index is not None:
        return _async_index

    host = get_pinecone_index()
    _async_pc = PineconeAsyncio(api_key=PINECONE_API_KEY)
    await _async_pc.__aenter__()
    _async_index = await _async_pc.IndexAsyncio(host=host).__aenter__()
    return _async_index

async def query_pinecone_async(vector:list, top_k:int, filter:dict):
    """
    Queries the Pinecone index asynchronously with the provided vector, top_k, and filter.
    Returns the query results.
    """

    index = await get_async_pinecone_index()
    results = await index.query(
          vector=vector,
          top_k=top_k, 
          include_metadata=True, 
          filter=filter,
          )
    return results