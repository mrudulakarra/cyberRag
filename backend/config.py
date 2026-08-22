import os
import site
import sys
from pathlib import Path

# Ensure user site-packages are in sys.path
user_site = getattr(site, 'USER_SITE', None) or site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.append(user_site)

from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Server Settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# Path Settings
CHROMA_DB_DIR = BASE_DIR / os.getenv("CHROMA_DB_DIR", "chroma_storage")
KNOWLEDGE_BASE_DIR = BASE_DIR / os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")

# RAG Hyperparameters
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "4"))
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# LLM Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# Ensure required directories exist
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

def is_gemini_configured() -> bool:
    """Check if a non-placeholder Gemini API key is configured."""
    return bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here")
