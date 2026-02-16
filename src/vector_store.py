import os
from typing import List
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.embeddings_manager import EmbeddingsManager

class VectorStore:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings_manager = EmbeddingsManager()
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings_manager.get_embeddings()
        )

    def add_documents(self, documents: List[Document]):
        self.vector_store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 5, score_threshold: float = 0.7):
        # LangChain's Chroma similarity_search_with_relevance_scores returns (doc, score)
        # Note: Relevance score interpretation depends on the distance metric.
        # Chroma uses L2 by default, so we might need to adjust.
        results = self.vector_store.similarity_search_with_relevance_scores(
            query, k=k, score_threshold=score_threshold
        )
        return results

    def delete_document_chunks(self, source_name: str):
        # This is a bit tricky with LangChain's Chroma wrapper
        # but we can filter by metadata
        self.vector_store.delete(where={"source": source_name})

    def get_all_sources(self):
        # Get unique source names from metadata
        data = self.vector_store.get()
        if data and 'metadatas' in data:
            return list(set([m['source'] for m in data['metadatas'] if 'source' in m]))
        return []
