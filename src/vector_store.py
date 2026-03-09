import os
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.embeddings_manager import EmbeddingsManager

class VectorStore:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings_manager = EmbeddingsManager()
        self._vector_store = None

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings_manager.get_embeddings()
            )
        return self._vector_store

    def add_documents(self, documents: List[Document]):
        self.vector_store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 5, score_threshold: float = 0.4, knowledge_area: Optional[str] = None):
        filter_dict = {}
        if knowledge_area and knowledge_area != "General":
            filter_dict["knowledge_area"] = knowledge_area

        results = self.vector_store.similarity_search_with_relevance_scores(
            query, k=k, filter=filter_dict if filter_dict else None
        )

        # Manually normalize and threshold scores to handle potential negative relevance from Chroma
        filtered_results = []
        for doc, score in results:
            normalized_score = max(0, score)
            if normalized_score >= score_threshold:
                filtered_results.append((doc, normalized_score))

        # Sort by score descending and take top K
        filtered_results.sort(key=lambda x: x[1], reverse=True)
        return filtered_results[:k]

    def delete_document_chunks(self, source_name: str):
        try:
            self.vector_store.delete(where={"source": source_name})
        except Exception:
            pass

    def clear_database(self):
        """Step 10: Clear and rebuild the vector database."""
        try:
            self.vector_store.delete_collection()
            self._vector_store = None
            return True
        except Exception:
            return False

    def get_all_sources(self, knowledge_area: Optional[str] = None):
        try:
            data = self.vector_store.get()
        except Exception:
            return []
        if data and 'metadatas' in data:
            sources = []
            for m in data['metadatas']:
                if 'source' in m:
                    if not knowledge_area or m.get('knowledge_area') == knowledge_area:
                        sources.append(m['source'])
            return list(set(sources))
        return []

    def get_all_sources_with_metadata(self):
        try:
            data = self.vector_store.get()
            if data and 'metadatas' in data:
                # Return unique sources with their associated metadata (latest one found)
                unique_sources = {}
                for m in data['metadatas']:
                    if 'source' in m:
                        unique_sources[m['source']] = m
                return list(unique_sources.values())
        except Exception:
            pass
        return []
