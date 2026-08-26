from services.chat_history import supabase

def record_uploaded_file(user_id: str, subject: str, filename: str):
    supabase.table("uploaded_files").insert({
        "user_id": user_id, "subject": subject, "filename": filename
    }).execute()

def get_uploaded_files(user_id: str, subject: str) -> list[dict]:
    result = (
        supabase.table("uploaded_files")
        .select("id, filename, uploaded_at")
        .eq("user_id", user_id)
        .eq("subject", subject)
        .order("uploaded_at", desc=True)
        .execute()
    )
    return result.data