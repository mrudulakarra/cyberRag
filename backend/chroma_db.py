import os
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.config import CHROMA_DB_DIR, IS_VERCEL

class ChromaDBManager:
    """Manages ChromaDB vector store with pure-Python fallback for serverless environments."""

    COLLECTION_NAME = "cybersecurity_knowledge"

    def __init__(self, storage_dir: Path = CHROMA_DB_DIR):
        self.storage_dir = storage_dir
        self.client = None
        self.collection = None
        self.fallback_chunks: List[Dict[str, Any]] = []
        self._init_client()

    def _init_client(self):
        try:
            import chromadb
            if IS_VERCEL:
                self.client = chromadb.Client()
            else:
                self.client = chromadb.PersistentClient(path=str(self.storage_dir))
            
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"description": "Cybersecurity Knowledge Base Chunks"}
            )
            print("[ChromaDBManager] Initialized ChromaDB client successfully.")
        except Exception as e:
            print(f"[ChromaDBManager Notice] Using In-Memory Serverless Retriever: {e}")
            self.client = None
            self.collection = None

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Indexes document chunks into ChromaDB or fallback store."""
        if not chunks:
            return 0

        # Store in fallback store
        existing_ids = {c["id"] for c in self.fallback_chunks}
        for chunk in chunks:
            if chunk["id"] not in existing_ids:
                self.fallback_chunks.append(chunk)
                existing_ids.add(chunk["id"])

        if not self.collection:
            return len(chunks)

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        batch_size = 50
        total_added = 0

        for i in range(0, len(chunks), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]

            try:
                self.collection.upsert(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_meta
                )
                total_added += len(batch_ids)
            except Exception as e:
                print(f"[ChromaDB add_chunks Warning] {e}")

        return total_added if total_added > 0 else len(chunks)

    def query(self, query_text: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Performs vector similarity search for a given question."""
        if self.collection:
            try:
                if self.collection.count() > 0:
                    effective_k = min(top_k, self.collection.count())
                    results = self.collection.query(
                        query_texts=[query_text],
                        n_results=effective_k,
                        include=["documents", "metadatas", "distances"]
                    )
                    formatted_results = []
                    if results and results.get("documents") and results["documents"][0]:
                        docs = results["documents"][0]
                        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                        ids = results["ids"][0] if results.get("ids") else [""] * len(docs)
                        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

                        for doc, meta, doc_id, dist in zip(docs, metas, ids, distances):
                            similarity_score = max(0.0, min(1.0, 1.0 - (dist / 2.0 if dist > 0 else 0.0)))
                            formatted_results.append({
                                "id": doc_id,
                                "text": doc,
                                "metadata": meta,
                                "distance": round(dist, 4),
                                "score_pct": round(similarity_score * 100, 1)
                            })
                    return formatted_results
            except Exception as e:
                print(f"[ChromaDB query Error] {e}")

        # Pure Python Fallback Similarity Search
        if not self.fallback_chunks:
            return []

        q_words = set(re.findall(r'\w+', query_text.lower()))
        if not q_words:
            return []

        scored = []
        for chunk in self.fallback_chunks:
            t_words = set(re.findall(r'\w+', chunk["text"].lower()))
            if not t_words:
                continue
            common = q_words.intersection(t_words)
            score = len(common) / math.sqrt(len(q_words) * len(t_words)) if len(t_words) > 0 else 0.0
            score_pct = round(min(100.0, score * 150), 1)  # Scale normalized score
            if score > 0.05:
                scored.append((score_pct, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored[:top_k]

        res = []
        for score_pct, chunk in top_matches:
            res.append({
                "id": chunk["id"],
                "text": chunk["text"],
                "metadata": chunk.get("metadata", {}),
                "distance": round(1.0 - (score_pct / 100.0), 4),
                "score_pct": score_pct
            })
        return res

    def get_stats(self) -> Dict[str, Any]:
        """Returns collection stats, total chunk count, and unique sources."""
        total_chunks = 0
        sources = set()

        if self.collection:
            try:
                total_chunks = self.collection.count()
                if total_chunks > 0:
                    data = self.collection.get(include=["metadatas"])
                    if data and data.get("metadatas"):
                        for m in data["metadatas"]:
                            if m and "source" in m:
                                sources.add(m["source"])
            except Exception:
                pass

        if total_chunks == 0 and self.fallback_chunks:
            total_chunks = len(self.fallback_chunks)
            for c in self.fallback_chunks:
                src = c.get("metadata", {}).get("source")
                if src:
                    sources.add(src)

        return {
            "total_chunks": total_chunks,
            "unique_documents": len(sources),
            "sources": sorted(list(sources)),
            "collection_name": self.COLLECTION_NAME
        }

    def clear_collection(self):
        """Clears all data from the collection."""
        self.fallback_chunks = []
        if self.client:
            try:
                self.client.delete_collection(name=self.COLLECTION_NAME)
                self.collection = self.client.create_collection(
                    name=self.COLLECTION_NAME,
                    metadata={"description": "Cybersecurity Knowledge Base Chunks"}
                )
            except Exception:
                pass
