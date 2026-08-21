from logger import logger

def query_chain(chain, user_query):
    try:
        result = chain({"query": user_query})
        return result
    except Exception as e:
        # TEMP DEBUG — show the real error body from OpenRouter
        print("=== FULL ERROR DEBUG ===")
        print("Type:", type(e))
        print("Args:", e.args)
        if hasattr(e, "response_data"):
            print("Response data:", e.response_data)
        if hasattr(e, "http_res_text"):
            print("Raw response text:", e.http_res_text)
        print("=========================")
        raise