import os
import sys
import shutil
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.config import KNOWLEDGE_BASE_DIR, HOST, PORT, is_gemini_configured, GEMINI_MODEL
from backend.document_processor import DocumentProcessor
from backend.chroma_db import ChromaDBManager
from backend.rag_pipeline import RAGPipeline
from backend.chat_history import history_db

# Initialize FastAPI App
app = FastAPI(
    title="CyberRAG — Cybersecurity Assistance Chatbot API",
    description="RAG-powered backend for cybersecurity learning and document grounding",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core RAG Components
doc_processor = DocumentProcessor()
db_manager = ChromaDBManager()
rag_pipeline = RAGPipeline(db_manager)

# Request Models
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, description="Student's cybersecurity question")
    session_id: Optional[str] = Field(None, description="Optional chat session ID for persistent history")

# Startup Event: Automatically ingest seed documents if ChromaDB is empty
@app.on_event("startup")
def auto_ingest_knowledge_base():
    """Runs on backend startup to ensure seed documents are indexed."""
    stats = db_manager.get_stats()
    if stats["total_chunks"] == 0:
        print("[Startup] ChromaDB is empty. Ingesting seed documents from knowledge_base/...")
        chunks_indexed = ingest_all_documents()
        print(f"[Startup] Ingestion complete. Indexed {chunks_indexed} chunks.")

def ingest_all_documents() -> int:
    """Helper function to process and index all files in knowledge_base/."""
    all_chunks = []
    if not KNOWLEDGE_BASE_DIR.exists():
        KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
        return 0

    for file_path in KNOWLEDGE_BASE_DIR.glob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".pdf", ".md", ".txt", ".docx", ".doc"]:
            chunks = doc_processor.process_file(file_path)
            all_chunks.extend(chunks)

    if all_chunks:
        return db_manager.add_chunks(all_chunks)
    return 0

# --- API ENDPOINTS ---

@app.get("/api/health")
def health_check():
    """Returns backend system status and vector database statistics."""
    db_stats = db_manager.get_stats()
    return {
        "status": "online",
        "service": "CyberRAG API",
        "version": "1.0.0",
        "gemini_configured": is_gemini_configured(),
        "model_name": GEMINI_MODEL,
        "vector_db": {
            "status": "connected",
            "total_chunks": db_stats["total_chunks"],
            "unique_documents": db_stats["unique_documents"],
            "sources": db_stats["sources"]
        }
    }

@app.post("/api/chat")
def handle_chat_query(request: ChatRequest):
    """Processes a student's cybersecurity question through the RAG pipeline with persistent session history."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    session_id = request.session_id or history_db.create_session(initial_title=question)

    try:
        # Record user message in persistent SQLite history
        history_db.add_message(session_id, "user", {"question": question}, auto_update_title=True)

        # Execute RAG query
        response = rag_pipeline.query(question)
        response["session_id"] = session_id

        # Record bot response in persistent SQLite history
        history_db.add_message(session_id, "bot", response)

        return response
    except Exception as e:
        print(f"[ChatAPI Error] {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request through the CyberRAG pipeline."
        )

# --- CHAT HISTORY REST ENDPOINTS ---
@app.get("/api/history")
def get_chat_history_sessions():
    """Returns list of past chat sessions."""
    return {"sessions": history_db.get_sessions()}

@app.get("/api/history/{session_id}")
def get_chat_session_messages(session_id: str):
    """Returns all stored messages for a specific session."""
    messages = history_db.get_session_messages(session_id)
    return {"session_id": session_id, "messages": messages}

@app.delete("/api/history/{session_id}")
def delete_chat_session(session_id: str):
    """Deletes a specific chat session."""
    history_db.delete_session(session_id)
    return {"message": "Session deleted successfully", "session_id": session_id}

@app.delete("/api/history")
def clear_all_chat_history():
    """Clears all chat history."""
    history_db.clear_all_history()
    return {"message": "All chat history cleared successfully."}

@app.get("/api/documents")
def list_documents():
    """Returns list of documents in knowledge_base/ and ChromaDB statistics."""
    kb_files = []
    if KNOWLEDGE_BASE_DIR.exists():
        for f in KNOWLEDGE_BASE_DIR.glob("*"):
            if f.is_file() and f.suffix.lower() in [".pdf", ".md", ".txt", ".docx", ".doc"]:
                kb_files.append({
                    "name": f.name,
                    "size_bytes": f.stat().st_size,
                    "extension": f.suffix[1:].upper()
                })

    db_stats = db_manager.get_stats()
    return {
        "files": kb_files,
        "total_files": len(kb_files),
        "db_stats": db_stats
    }

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a cybersecurity document (PDF/MD/TXT) and indexes it into ChromaDB."""
    filename = file.filename
    ext = Path(filename).suffix.lower()
    
    if ext not in [".pdf", ".md", ".txt", ".docx", ".doc"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload PDF, Markdown (.md), or Plain Text (.txt) files."
        )

    target_path = KNOWLEDGE_BASE_DIR / filename
    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process and index newly uploaded file
        chunks = doc_processor.process_file(target_path)
        chunks_added = db_manager.add_chunks(chunks)

        return {
            "message": f"Successfully uploaded and indexed '{filename}'.",
            "filename": filename,
            "chunks_added": chunks_added,
            "total_chunks_in_db": db_manager.get_stats()["total_chunks"]
        }
    except Exception as e:
        print(f"[Upload Error] {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

@app.post("/api/reindex")
def trigger_reindex():
    """Re-indexes all documents in knowledge_base/."""
    try:
        db_manager.clear_collection()
        chunks_indexed = ingest_all_documents()
        return {
            "message": "Knowledge base re-indexed successfully.",
            "total_chunks_indexed": chunks_indexed,
            "stats": db_manager.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")

# Mount Frontend Static Assets
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(frontend_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
