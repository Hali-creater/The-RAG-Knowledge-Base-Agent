import os
from typing import Optional, List, Dict
from onprem import LLM
from src.memory_manager import MemoryManager
from dotenv import load_dotenv

load_dotenv()

class RAGAgent:
    def __init__(self, model_name: str = "ollama/llama3.2"):
        self.model_name = model_name
        self.memory_manager = MemoryManager()
        self._llm = None
        # onprem library handles vector store and embeddings internally
        # but we can specify the persistence directory
        self.db_path = "data/chroma_db"

    @property
    def llm(self):
        if self._llm is None:
            # Using onprem LLM with the specified model
            self._llm = LLM(self.model_name, verbose=False, db_path=self.db_path)
        return self._llm

    def ingest_document(self, file_path: str):
        # In onprem, we can ingest a single file or a directory
        # We'll use the parent directory of the file since onprem.ingest takes a path
        directory = os.path.dirname(file_path)
        self.llm.ingest(directory)
        return 1 # return 1 as we ingested one file

    def answer_question(self, question: str) -> Dict:
        # Step 1: Format history
        history_text = self.memory_manager.get_formatted_history()

        # Step 2: Build a combined prompt if there is history
        prompt = question
        if history_text:
            prompt = f"Previous conversation:\n{history_text}\n\nCurrent Question: {question}\n\nPlease answer the current question based on the provided context from your documents."

        # Step 3: Ask the local LLM
        # onprem's ask() method performs RAG and returns a dictionary or string
        result = self.llm.ask(prompt)

        # Depending on onprem version/config, result might be a dict or string
        if isinstance(result, dict):
            answer = result.get('answer', str(result))
            source_docs = result.get('source_documents', [])
            sources = list(set([doc.metadata.get('source', 'Unknown') for doc in source_docs]))
        else:
            answer = result
            sources = []

        # Confidence Scoring (Simplified for local LLM)
        confidence = "medium"
        if sources:
            confidence = "high"
        elif "I don't know" in answer or "I cannot find" in answer:
            confidence = "low"

        # Step 4 - Maintain Conversation
        self.memory_manager.add_exchange(question, answer)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }
