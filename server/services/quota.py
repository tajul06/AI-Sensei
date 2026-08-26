from datetime import date
from services.chat_history import supabase

DAILY_LIMIT = 30

def check_and_increment_quota(user_id: str) -> bool:
    today = date.today().isoformat()
    result = supabase.table("usage_quota").select("*").eq("user_id", user_id).execute()

    if not result.data:
        supabase.table("usage_quota").insert({"user_id": user_id, "request_count": 1, "quota_date": today}).execute()
        return True

    row = result.data[0]
    if row["quota_date"] != today:
        supabase.table("usage_quota").update({"request_count": 1, "quota_date": today}).eq("user_id", user_id).execute()
        return True

    if row["request_count"] >= DAILY_LIMIT:
        return False

    supabase.table("usage_quota").update({"request_count": row["request_count"] + 1}).eq("user_id", user_id).execute()
    return True