import requests
from config import API_URL

def upload_pdf_api(files):
    files_payload = [("files", (files.name, files, 'application/pdf')) for files in files]
    return requests.post(f"{API_URL}/upload_pdf", files=files_payload)

def ask_question_api(question):
    return requests.post(f"{API_URL}/ask/", data={"user_query": question})