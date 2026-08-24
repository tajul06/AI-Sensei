import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

def _require_env(name:str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable '{name}' is required but not set.")
    
    return value

PINECONE_API_KEY = _require_env("PINECONE_API_KEY")
PINECONE_INDEX_NAME = _require_env("PINECONE_INDEX_NAME")
GOOGLE_API_KEY = _require_env("GOOGLE_API_KEY")
HF_TOKEN = _require_env("HF_TOKEN")
SUPABASE_URL = _require_env("SUPABASE_URL")
SUPABASE_SECRET_KEY = _require_env("SUPABASE_SECRET_KEY")
JINA_API_KEY = _require_env("JINA_API_KEY")
