from supabase import create_client
from config.settings import SUPABASE_URL, SUPABASE_SECRET_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def create_session(user_id: str, subject: str) -> str:
    result = supabase.table("chat_sessions").insert({
        "user_id": user_id,
        "subject": subject,
    }).execute()
    return result.data[0]["id"]


def save_message(session_id: str, role: str, content: str):
    supabase.table("chat_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content,
    }).execute()


def get_recent_messages(session_id: str, limit: int = 6) -> list[dict]:
    result = (
        supabase.table("chat_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(result.data))


def get_full_history(session_id: str, user_id: str) -> list[dict]:
    session = (
        supabase.table("chat_sessions")
        .select("user_id")
        .eq("id", session_id)
        .single()
        .execute()
    )
    if session.data["user_id"] != user_id:
        raise PermissionError("Not your session")

    result = (
        supabase.table("chat_messages")
        .select("role, content, created_at")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return result.data


def list_user_sessions(user_id: str) -> list[dict]:
    result = (
        supabase.table("chat_sessions")
        .select("id, subject, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data