async def condense_query(user_query: str, history: list[dict], llm) -> str:
    if not history:
        return user_query

    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    prompt = (
        f"Given this conversation history:\n{history_text}\n\n"
        f"Rewrite this follow-up question as a standalone question. "
        f"If it's already standalone, return it unchanged.\n\n"
        f"Follow-up question: {user_query}\n\n"
        f"Standalone question:"
    )
    response = await llm.ainvoke(prompt)
    return response.content.strip()