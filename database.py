"""
ChromaDB integration for storing political documents and querying themes.
"""
import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self, db_dir: str = "data/chroma_db", collection_name: str = "politieke_standpunten"):
        self.db_dir = db_dir
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Add chunks to ChromaDB collection."""
        if not chunks:
            return

        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [c["id"] for c in chunks]

        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_theme(self, query: str, n_results: int = 5, party_filter: str = None) -> List[Dict[str, Any]]:
        """Query relevant document chunks for a specific theme or question."""
        where_clause = None
        if party_filter:
            where_clause = {"party": party_filter}

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                formatted_results.append({
                    "text": doc,
                    "metadata": meta,
                    "relevance_score": float(dist)
                })

        return formatted_results

    def get_all_parties(self) -> List[str]:
        """Get list of all indexed parties."""
        data = self.collection.get()
        if not data or "metadatas" not in data or not data["metadatas"]:
            return []
        
        parties = set()
        for meta in data["metadatas"]:
            if meta and "party" in meta:
                parties.add(meta["party"])
        return sorted(list(parties))

    def reset_database(self):
        """Reset the ChromaDB collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
