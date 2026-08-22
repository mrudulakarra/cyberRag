import time
from typing import List, Dict, Any
from backend.config import GEMINI_API_KEY, GEMINI_MODEL, RETRIEVAL_TOP_K, is_gemini_configured
from backend.chroma_db import ChromaDBManager

class RAGPipeline:
    """Orchestrates document retrieval, context synthesis, Gemini LLM generation, and transparency logging."""

    SYSTEM_PROMPT = """You are CyberRAG — a specialized Cybersecurity Learning Assistant designed for cybersecurity students.

YOUR MANDATE:
1. Answer the student's question primarily using the RETRIEVED KNOWLEDGE BASE CONTEXT provided below.
2. Explain concepts clearly, educationally, and structurally (use markdown headings, bullet points, and code snippets where helpful).
3. Ground your answers firmly in cybersecurity best practices and the provided documents.
4. If the retrieved context DOES NOT contain sufficient information to answer the question accurately, clearly inform the student:
   "I couldn't find enough relevant information in the current cybersecurity knowledge base to provide a complete answer."
5. Never invent or hallucinate citations or facts not backed by cybersecurity principles or the context.
6. Keep answers encouraging, professional, and accessible for students learning cybersecurity.

--- RETRIEVED KNOWLEDGE CONTEXT ---
{context}
--- END RETRIEVED CONTEXT ---

STUDENT QUESTION: {question}

Provide your grounded cybersecurity explanation below:"""

    def __init__(self, db_manager: ChromaDBManager):
        self.db = db_manager
        self.genai_client = None
        self.legacy_model = None
        self._init_gemini()

    def _init_gemini(self):
        """Initializes Gemini SDK if configured."""
        if is_gemini_configured():
            try:
                from google import genai
                self.genai_client = genai.Client(api_key=GEMINI_API_KEY)
                print("[RAGPipeline] Successfully initialized official google.genai Client.")
            except Exception as e:
                try:
                    import google.generativeai as legacy_genai
                    legacy_genai.configure(api_key=GEMINI_API_KEY)
                    self.legacy_model = legacy_genai.GenerativeModel(GEMINI_MODEL)
                    print("[RAGPipeline] Initialized legacy google.generativeai Model.")
                except Exception as ex:
                    print(f"[RAGPipeline] Could not initialize Gemini SDK: {ex}")

    def query(self, question: str, top_k: int = RETRIEVAL_TOP_K) -> Dict[str, Any]:
        """Runs the end-to-end RAG query flow."""
        start_time = time.time()
        steps = []

        # Step 1: Question received
        steps.append({
            "step": 1,
            "title": "Question Received",
            "detail": f"Processing query: '{question}'",
            "status": "completed"
        })

        # Step 2: Knowledge base search
        steps.append({
            "step": 2,
            "title": "Searching Vector Database",
            "detail": "Executing similarity search in ChromaDB vector store...",
            "status": "completed"
        })

        # Retrieve relevant chunks from ChromaDB
        retrieved_chunks = self.db.query(question, top_k=top_k)

        # Step 3: Retrieval results
        if retrieved_chunks:
            top_source = retrieved_chunks[0]["metadata"].get("source", "Document")
            top_score = retrieved_chunks[0]["score_pct"]
            steps.append({
                "step": 3,
                "title": "Document Retrieval Complete",
                "detail": f"Retrieved {len(retrieved_chunks)} relevant chunk(s). Highest match: {top_source} ({top_score}% similarity).",
                "status": "completed"
            })
        else:
            steps.append({
                "step": 3,
                "title": "Document Retrieval Notice",
                "detail": "No documents currently match the query in ChromaDB vector store.",
                "status": "warning"
            })

        # Step 4: Context preparation
        steps.append({
            "step": 4,
            "title": "Prompt & Context Synthesis",
            "detail": f"Assembled context from {len(retrieved_chunks)} chunk(s) into Cybersecurity Assistant prompt template.",
            "status": "completed"
        })

        # Step 5: Gemini LLM response generation
        steps.append({
            "step": 5,
            "title": "Gemini AI Generation",
            "detail": "Sending grounded context and student query to Google Gemini API...",
            "status": "completed"
        })

        # Generate answer using Gemini or Grounded Fallback
        answer, used_llm = self._generate_response(question, retrieved_chunks)

        elapsed_sec = round(time.time() - start_time, 2)

        # Build clean source items for UI transparency
        formatted_sources = []
        for chunk in retrieved_chunks:
            formatted_sources.append({
                "source": chunk["metadata"].get("source", "Unknown Document"),
                "title": chunk["metadata"].get("title", "Cybersecurity Document"),
                "page": chunk["metadata"].get("page", "N/A"),
                "score_pct": chunk.get("score_pct", 0),
                "text_snippet": chunk["text"][:280] + ("..." if len(chunk["text"]) > 280 else "")
            })

        return {
            "question": question,
            "answer": answer,
            "sources": formatted_sources,
            "transparency_steps": steps,
            "used_llm": used_llm,
            "elapsed_seconds": elapsed_sec
        }

    def _generate_response(self, question: str, retrieved_chunks: List[Dict[str, Any]]) -> tuple[str, bool]:
        """Calls Gemini API with retrieved context, or generates a grounded fallback if API key is missing."""
        if not retrieved_chunks:
            return (
                "I couldn't find enough relevant information in the current cybersecurity knowledge base to provide a reliable answer. "
                "Please make sure cybersecurity documents (such as OWASP guides, MITRE ATT&CK materials, networking docs, or security notes) "
                "are added to the `knowledge_base/` folder.",
                False
            )

        # Build formatted context block
        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            source_name = chunk["metadata"].get("source", "Doc")
            page_info = f" (Section/Page: {chunk['metadata'].get('page')})" if chunk['metadata'].get('page') else ""
            context_blocks.append(f"[Source #{idx}: {source_name}{page_info}]\n{chunk['text']}")

        formatted_context = "\n\n".join(context_blocks)
        full_prompt = self.SYSTEM_PROMPT.format(context=formatted_context, question=question)

        # Try live Gemini API call
        if is_gemini_configured():
            if not self.genai_client and not self.legacy_model:
                self._init_gemini()

            try:
                if self.genai_client:
                    # New google-genai SDK
                    response = self.genai_client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=full_prompt
                    )
                    if response and hasattr(response, "text") and response.text:
                        return response.text.strip(), True
                elif self.legacy_model:
                    # Legacy google.generativeai SDK
                    response = self.legacy_model.generate_content(full_prompt)
                    if response and response.text:
                        return response.text.strip(), True
            except Exception as e:
                print(f"[RAGPipeline] Gemini API Error: {type(e).__name__}: {e}")
                pass

        # Grounded Fallback Response (when GEMINI_API_KEY is not set yet or offline)
        fallback_header = (
            "> [!NOTE]\n"
            "> **Grounded Knowledge Base Context** *(To enable live Google Gemini LLM synthesis, set your `GEMINI_API_KEY` in `.env`)*\n\n"
        )
        
        paragraphs = []
        for idx, chunk in enumerate(retrieved_chunks[:3], start=1):
            title = chunk["metadata"].get("title", "Cybersecurity Document")
            page = chunk["metadata"].get("page", "N/A")
            paragraphs.append(f"### Grounded Knowledge Point #{idx} ({title} - {page})\n{chunk['text']}")

        fallback_answer = fallback_header + "\n\n".join(paragraphs)
        return fallback_answer, False
