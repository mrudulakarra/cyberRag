import time
from typing import List, Dict, Any
from backend.config import GEMINI_API_KEY, GEMINI_MODEL, RETRIEVAL_TOP_K, is_gemini_configured
from backend.chroma_db import ChromaDBManager

class RAGPipeline:
    """Orchestrates document retrieval, context synthesis, Gemini LLM generation, and transparency logging."""

    SYSTEM_PROMPT = """You are CyberRAG — a friendly and educational Cybersecurity Assistance Chatbot.

YOUR MANDATE:
1. GREETINGS & BASIC CONVERSATION: If the student greets you (e.g., "hello", "hi", "hey", "good morning", "how are you") or asks basic conversational questions (e.g., "who are you", "what can you do"), respond warmly and introduce yourself as CyberRAG, your cybersecurity learning assistant.
2. TECHNICAL QUESTIONS: For cybersecurity and technical questions, use the RETRIEVED KNOWLEDGE BASE CONTEXT provided below to answer clearly, accurately, and educationally using markdown headings, bullet points, and code snippets where applicable.
3. STRICT GROUNDING: If a specific technical or security question is NOT answered in or supported by the provided context below, respond EXACTLY with:
   "I am sorry, but the answer to your question is not present in the provided knowledge base documents."
4. Do NOT hallucinate facts, citations, or non-existent document contents outside the provided context.

--- RETRIEVED KNOWLEDGE BASE CONTEXT ---
{context}
--- END RETRIEVED CONTEXT ---

STUDENT QUESTION: {question}

Provide your grounded answer below:"""

    NOT_FOUND_RESPONSE = "I am sorry, but the answer to your question is not present in the provided knowledge base documents."

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
            top_score = retrieved_chunks[0].get("score_pct", 0)
            steps.append({
                "step": 3,
                "title": "Document Retrieval Complete",
                "detail": f"Retrieved {len(retrieved_chunks)} relevant chunk(s). Top match: {top_source} ({top_score}% similarity).",
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
            "detail": f"Assembled context from {len(retrieved_chunks)} chunk(s) into RAG prompt template.",
            "status": "completed"
        })

        # Step 5: Gemini LLM response generation
        steps.append({
            "step": 5,
            "title": "Gemini AI Generation",
            "detail": "Generating grounded answer via Google Gemini API...",
            "status": "completed"
        })

        # Generate answer using Gemini or fallback
        answer, used_llm = self._generate_response(question, retrieved_chunks)

        elapsed_sec = round(time.time() - start_time, 2)

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
        """Calls Gemini API with retrieved context, or generates a grounded response."""
        q_clean = question.lower().strip()
        is_greeting = q_clean in ["hi", "hello", "hey", "good morning", "good evening", "greetings", "how are you", "who are you", "what is cyberrag"]

        if not retrieved_chunks and not is_greeting:
            return self.NOT_FOUND_RESPONSE, False

        # Build formatted context block
        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            source_name = chunk["metadata"].get("source", "Doc")
            page_info = f" (Section: {chunk['metadata'].get('page')})" if chunk['metadata'].get('page') else ""
            context_blocks.append(f"[Source #{idx}: {source_name}{page_info}]\n{chunk['text']}")

        formatted_context = "\n\n".join(context_blocks)
        full_prompt = self.SYSTEM_PROMPT.format(context=formatted_context, question=question)

        # Try live Gemini API call
        if is_gemini_configured():
            if not self.genai_client and not self.legacy_model:
                self._init_gemini()

            try:
                if self.genai_client:
                    response = self.genai_client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=full_prompt
                    )
                    if response and hasattr(response, "text") and response.text:
                        return response.text.strip(), True
                elif self.legacy_model:
                    response = self.legacy_model.generate_content(full_prompt)
                    if response and response.text:
                        return response.text.strip(), True
            except Exception as e:
                print(f"[RAGPipeline] Gemini API Error: {type(e).__name__}: {e}")
                pass

        # Offline / Fallback mode:
        if is_greeting:
            return "Hello! Welcome to CyberRAG. How can I assist you with your cybersecurity studies today?", False

        if retrieved_chunks:
            return retrieved_chunks[0]['text'].strip(), False

        return self.NOT_FOUND_RESPONSE, False
