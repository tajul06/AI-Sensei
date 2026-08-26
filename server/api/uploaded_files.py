from fastapi import APIRouter, Depends
from services.auth import get_current_user
from services.uploaded_files import get_uploaded_files

router = APIRouter()

@router.get("/uploaded_files/")
async def list_uploaded_files(subject: str, user_id: str = Depends(get_current_user)):
    return {"files": get_uploaded_files(user_id, subject)}