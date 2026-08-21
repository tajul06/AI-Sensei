from langchain_core.vectorstores import VectorStore,VectorStoreRetriever
#Default number of chunks to retrieve per query
DEFAULT_TOP_K = 5

#per-group retrieval settings

GROUP_TOP_K: dict[str,int] = {
    "stem": 5,  
    "math": 4,
    "pros": 6,
}


SIMILARITY_THRESHOLD = 0.75

RERANK_ENABLED = False
RERANK_TOP_N = 3

def get_top_k_for_group(group:str) -> int:
    """
    Returns the top_k value for a given group. If the group is not recognized, it defaults to DEFAULT_TOP_K.
    """
    return GROUP_TOP_K.get(group, DEFAULT_TOP_K)


def build_retriever( group:str , vectorstore:VectorStore) -> VectorStoreRetriever:
    """
    Builds a retriever from the given vectorstore with settings based on the group.
    """
    return vectorstore.as_retriever(
        search_type="similarity_score_threshold",  
        search_kwargs={
            "k": get_top_k_for_group(group),
            "score_threshold": SIMILARITY_THRESHOLD,
        },
   )