from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from modules.load_vectorstore import load_and_embed_documents
from fastapi.responses import JSONResponse
from logger import logger



router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(files: List[UploadFile] = File(...)
):
    try:
        logger.info("Received request to upload PDF files.")
        load_and_embed_documents(files)
        logger.info("PDF files processed and embedded successfully.")
        return JSONResponse(content={"message": "Files uploaded and processed successfully."})
    except Exception as e:
        logger.exception(f"Error in upload_pdf: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error", "error": str(e)})         
        