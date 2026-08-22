from fastapi import APIRouter, UploadFile, File, Form , Depends
from fastapi.concurrency import run_in_threadpool
from typing import List
from services.load_vectorstore import load_and_embed_documents
from fastapi.responses import JSONResponse
from config.subjects import group_for_subject
from services.auth import get_current_user
from logger import logger



router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(
    files: List[UploadFile] = File(...),
    subject: str = Form(...),
    user_id: str = Depends(get_current_user),
):
    try:
        group_for_subject(subject)  # Validate subject
        logger.info(f"Received request to upload PDF files for subject: {subject}, user_id: {user_id} .")
        await run_in_threadpool(load_and_embed_documents, files, subject, user_id)
        logger.info("PDF files processed and embedded successfully.")
        return JSONResponse(content={"message": "Files uploaded and processed successfully."})
    except ValueError as ve:
        logger.warning(f"Invalid subject provided: {subject}. Error: {str(ve)}")
        return JSONResponse(status_code=400, content={"message": str(ve)})
    except Exception as e:
        logger.exception(f"Error in upload_pdf: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error", "error": str(e)})         
        