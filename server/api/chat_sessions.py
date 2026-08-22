from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from services.auth import get_current_user
from services.chat_history import create_session, get_full_history, list_user_sessions

router = APIRouter()


@router.post("/chat_sessions/")
async def start_session(subject: str = Form(...), user_id: str = Depends(get_current_user)):
    session_id = create_session(user_id, subject)
    return {"session_id": session_id}


@router.get("/chat_sessions/")
async def list_sessions(user_id: str = Depends(get_current_user)):
    return {"sessions": list_user_sessions(user_id)}


@router.get("/chat_sessions/{session_id}/history")
async def fetch_history(session_id: str, user_id: str = Depends(get_current_user)):
    try:
        return {"messages": get_full_history(session_id, user_id)}
    except PermissionError:
        return JSONResponse(status_code=403, content={"message": "Forbidden"})