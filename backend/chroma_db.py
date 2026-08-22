import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from backend.config import CHROMA_DB_DIR

class ChromaDBManager:
    """Manages ChromaDB vector store for cybersecurity document indexing and similarity retrieval."""

    COLLECTION_NAME = "cybersecurity_knowledge"

    def __init__(self, storage_dir: Path = CHROMA_DB_DIR):
        self.storage_dir = storage_dir
        self.client = chromadb.PersistentClient(path=str(self.storage_dir))
        # Get or create collection using ChromaDB's default ONNX / MiniLM embedding function
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "Cybersecurity Knowledge Base Chunks"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Indexes document chunks into ChromaDB. Replaces existing IDs if present."""
        if not chunks:
            return 0

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Ingest in batches to avoid payload memory spikes
        batch_size = 50
        total_added = 0

        for i in range(0, len(chunks), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]

            self.collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta
            )
            total_added += len(batch_ids)

        return total_added

    def query(self, query_text: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Performs vector similarity search for a given question."""
        if self.collection.count() == 0:
            return []

        # Adjust top_k if collection has fewer items
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
                # Calculate similarity score percentage (ChromaDB L2 / Cosine distance conversion)
                similarity_score = max(0.0, min(1.0, 1.0 - (dist / 2.0 if dist > 0 else 0.0)))
                formatted_results.append({
                    "id": doc_id,
                    "text": doc,
                    "metadata": meta,
                    "distance": round(dist, 4),
                    "score_pct": round(similarity_score * 100, 1)
                })

        return formatted_results

    def get_stats(self) -> Dict[str, Any]:
        """Returns collection stats, total chunk count, and unique sources."""
        total_chunks = self.collection.count()
        sources = set()

        if total_chunks > 0:
            data = self.collection.get(include=["metadatas"])
            if data and data.get("metadatas"):
                for m in data["metadatas"]:
                    if m and "source" in m:
                        sources.add(m["source"])

        return {
            "total_chunks": total_chunks,
            "unique_documents": len(sources),
            "sources": sorted(list(sources)),
            "collection_name": self.COLLECTION_NAME
        }

    def clear_collection(self):
        """Clears all data from the collection."""
        self.client.delete_collection(name=self.COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "Cybersecurity Knowledge Base Chunks"}
        )
