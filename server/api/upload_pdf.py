from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from services.load_vectorstore import load_and_embed_documents
from fastapi.responses import JSONResponse
from config.subjects import group_for_subject
from logger import logger



router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(
    files: List[UploadFile] = File(...),
    subject: str = Form(...),
):
    try:
        group_for_subject(subject)  # Validate subject
        logger.info(f"Received request to upload PDF files for subject: {subject} .")
        
        load_and_embed_documents(files, subject)
        logger.info("PDF files processed and embedded successfully.")
        return JSONResponse(content={"message": "Files uploaded and processed successfully."})
    except ValueError as ve:
        logger.warning(f"Invalid subject provided: {subject}. Error: {str(ve)}")
        return JSONResponse(status_code=400, content={"message": str(ve)})
    except Exception as e:
        logger.exception(f"Error in upload_pdf: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error", "error": str(e)})         
        