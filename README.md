# CyberRAG — Cybersecurity Assistance Chatbot

> A modern, responsive, and grounded full-stack web application designed for cybersecurity students. Powered by Retrieval-Augmented Generation (RAG), FastAPI, ChromaDB, and Google Gemini API.

---

## 1. Project Overview
**CyberRAG** is a specialized cybersecurity assistance chatbot designed specifically to help students ask complex security questions and receive grounded, accurate, and understandable answers. Rather than acting as a generic conversational AI, CyberRAG retrieves domain-specific knowledge from a managed cybersecurity document store before generating an answer.

---

## 2. Problem Statement
Cybersecurity students face unique challenges when learning complex concepts:
- **Scattered Information**: Security documentation (OWASP guides, MITRE ATT&CK frameworks, NIST standards, RFCs) is spread across thousands of pages of heavy technical specs.
- **Generic AI Hallucinations**: Standard off-the-shelf LLMs often invent non-existent command flags, misstate vulnerability mechanics, or hallucinate security guidance.
- **Lack of Source Transparency**: Traditional chatbots answer questions without showing where their knowledge originated or which document sections informed the response.

---

## 3. What is CyberRAG?
CyberRAG addresses these challenges by implementing a strict **Retrieval-Augmented Generation (RAG)** pipeline:
$$\text{Cybersecurity Documents} \longrightarrow \text{Vector Retrieval} \longrightarrow \text{Grounded Context} \longrightarrow \text{Gemini AI} \longrightarrow \text{Student Answer}$$

By enforcing this flow, CyberRAG ensures that generated responses directly reference curated cybersecurity learning resources.

---

## 4. Why CyberRAG?
- ⚡ **Faster Learning**: Students get direct answers with code examples instead of spending hours searching PDFs manually.
- 🎯 **Focused Knowledge**: Restricts context to trusted cybersecurity documents (OWASP Top 10, MITRE ATT&CK, Networking, Linux Security).
- 🛡️ **Grounded Responses**: Prevents generic AI hallucinations by feeding retrieved context directly to Google Gemini.
- 📚 **Expandable Knowledge Base**: Teachers and students can easily add new PDFs or notes via the document upload feature.
- 🧠 **Student-Friendly Explanations**: Concepts are explained with structured headings, code blocks, and key takeaways.
- 🔍 **RAG Transparency**: Displays live execution steps and expandable source document citations.

---

## 5. How CyberRAG Works

```text
Cybersecurity Documents (PDF, MD, TXT)
        │
        ▼
Text Processing & Extraction (pypdf)
        │
        ▼
Chunking & Metadata Tagging (800 char chunks with overlap)
        │
        ▼
Vector Embedding Generation
        │
        ▼
ChromaDB Persistent Storage (chroma_storage/)
        │
        ▼
Student Question (via Web UI)
        │
        ▼
Vector Similarity Search (ChromaDB)
        │
        ▼
Retrieve Top Relevant Context Chunks
        │
        ▼
Construct Prompt with Retrieved Context
        │
        ▼
Google Gemini API Generation (gemini-1.5-flash)
        │
        ▼
Display Grounded Answer + Transparency Steps + Source Cards in Chat UI
```

---

## 6. System Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                   Frontend Presentation Layer                   │
│          HTML5 + CSS3 + Vanilla JavaScript (Glassmorphic UI)    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP REST API
┌────────────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend Application                   │
│      main.py  •  rag_pipeline.py  •  document_processor.py      │
└────────────────┬────────────────────────────────┬───────────────┘
                 │                                │
                 ▼                                ▼
┌────────────────────────────────┐ ┌──────────────────────────────┐
│  ChromaDB Vector Store         │ │  Google Gemini API           │
│  (Persistent Storage)          │ │  (gemini-1.5-flash LLM)      │
└────────────────────────────────┘ └──────────────────────────────┘
```

---

## 7. Technology Stack
- **Frontend**: HTML5, CSS3 (Custom Cyber Theme, Glassmorphism, CSS Grid), Vanilla JavaScript (No heavy frameworks required).
- **Backend**: Python 3.12, FastAPI, Uvicorn ASGI Server.
- **RAG Architecture**: Vector similarity search + Grounded LLM Prompting.
- **Vector Database**: ChromaDB (Persistent storage engine).
- **AI / LLM**: Google Gemini API (`google-generativeai` SDK).
- **Document Processing**: `pypdf`, Regex, Markdown text parsers.

---

## 8. Project Structure

```text
XFactor/
│
├── frontend/
│   ├── index.html        # Main SPA HTML (Landing Page & Live Chat)
│   ├── style.css         # Cybersecurity dark theme & glassmorphism CSS
│   └── script.js         # Single page app router & chat controller
│
├── backend/
│   ├── __init__.py
│   ├── main.py               # FastAPI routes (/api/chat, /api/upload, /api/health)
│   ├── config.py             # Environment config & constants
│   ├── document_processor.py # PDF/MD text parser & semantic chunker
│   ├── chroma_db.py          # ChromaDB vector store manager
│   └── rag_pipeline.py       # End-to-end RAG retriever & Gemini API caller
│
├── knowledge_base/           # Seed cybersecurity documents directory
│   ├── owasp_top_10_guide.md
│   ├── mitre_attack_framework.md
│   ├── networking_security_fundamentals.md
│   ├── web_security_and_cryptography.md
│   └── linux_security_and_incident_response.md
│
├── chroma_storage/           # Auto-generated persistent ChromaDB data
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Local environment configuration
└── README.md                 # Project documentation
```

---

## 9. Installation Instructions

1. **Clone or Open the Repository**:
   ```bash
   cd XFactor
   ```

2. **Create and Activate a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Required Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 10. Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your **Google Gemini API Key**:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   HOST=127.0.0.1
   PORT=8000
   CHROMA_DB_DIR=chroma_storage
   KNOWLEDGE_BASE_DIR=knowledge_base
   RETRIEVAL_TOP_K=4
   GEMINI_MODEL=gemini-1.5-flash
   ```
   > *Note: If no API key is set, CyberRAG automatically operates in **Offline Demonstration Mode**, providing grounded context summaries directly from ChromaDB.*

---

## 11. How to Run the FastAPI Backend

Run the FastAPI application using Python or Uvicorn:

```bash
python backend/main.py
```
*or*
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The server will automatically:
1. Scan `knowledge_base/` on startup.
2. Ingest and chunk all seed cybersecurity documents into ChromaDB.
3. Serve the API at `http://127.0.0.1:8000`.

---

## 12. How to Access the Frontend

Once the FastAPI backend is running:
- Open your browser and navigate to: **`http://127.0.0.1:8000`**
- Click **Start Learning** or **Launch Chatbot** to interact with CyberRAG.

---

## 13. How to Add Cybersecurity Documents

### Method 1: Via the Web UI
1. Scroll to the **Knowledge Base** section on the Landing Page.
2. Drag and drop any `.pdf`, `.md`, or `.txt` file into the upload dropzone.
3. CyberRAG will automatically process, chunk, and index the file into ChromaDB immediately.

### Method 2: Manual Directory Placement
1. Drop your cybersecurity PDFs or markdown files directly into the `knowledge_base/` folder.
2. Restart the backend or call `POST /api/reindex`.

---

## 14. Example Cybersecurity Questions to Try

- **Web Security**: *"What is SQL Injection and how can developers prevent it using prepared statements?"*
- **OWASP Top 10**: *"Explain Cross-Site Scripting (XSS) and the difference between Stored and Reflected XSS."*
- **Networking**: *"Explain the TCP 3-way handshake sequence (SYN, SYN-ACK, ACK)."*
- **Networking**: *"What is ARP spoofing and how does it work on local networks?"*
- **Threat Intel**: *"What is OS Credential Dumping (T1003.001) in the MITRE ATT&CK framework?"*
- **OS & Incident Response**: *"What are the four phases of the NIST Incident Response lifecycle?"*
- **Cryptography**: *"What is the difference between symmetric and asymmetric encryption?"*

---

## 15. Security Considerations
- **API Key Protection**: All Gemini API calls are strictly handled on the FastAPI backend. No secret keys are exposed to HTML, CSS, or JS.
- **Input Validation**: Student queries are sanitized and length-checked before entering the pipeline.
- **Prompt Injection Awareness**: System instructions explicitly bound Gemini to answer strictly within cybersecurity learning contexts.
- **Trusted Knowledge Base**: Only validated cybersecurity materials in `knowledge_base/` are indexed into ChromaDB.

---

## 16. Limitations
- **Grounding Scope**: Answers depend directly on the depth and coverage of documents present in `knowledge_base/`.
- **OCR Constraints**: Non-searchable scanned image PDFs require an external OCR pre-processor.

---

## 17. Future Enhancements
- 🔍 **Interactive Code Sandbox**: Live execution testing for web vulnerability fixes.
- 🌐 **Web Scraper Pipeline**: Automated ingestion of latest CVE advisories and Security Week updates.
- 📊 **Multi-User Study Analytics**: Tracking student progress and quiz generation from document chunks.
