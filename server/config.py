import os
from dotenv import load_dotenv

load_dotenv()

#API KEYS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

#Upload settings
MAX_PAGES = 20
MAX_FILE_SIZE_MB = 25
ALLOWED_FILE_TYPES = [".pdf"]

#Retrieval settings
TOP_K = 5

#Subjects
SUBJECTS = [
    "Bangla",
    "English",
    "Math",
    "Physics",
    "Chemistry",
    "Biology",
    "History",
    "Geography",
    "Philosophy",
    "Literature",
    "Social Science",
    "ICT",
    "Religion",
    "Physical Education",
]

