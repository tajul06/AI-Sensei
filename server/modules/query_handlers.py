from logger import logger

def query_chain(chain,user_query:str):
    try:
        logger.debug(f"running query_chain with user_query: {user_query}")
        result = chain({"query": user_query})
        response = {
            "response": result['result'],
            "source_documents": [doc.metadata for doc in result['source_documents']]
        }
        logger.debug(f"query_chain result: {response}")
        return response
    except Exception as e:
        logger.exception(f"Error in query_chain: {str(e)}")
        raise