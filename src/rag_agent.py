import os
from typing import Optional, List, Dict
from onprem import LLM
from src.memory_manager import MemoryManager
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Setup logging
logger.add("logs/agent.log", rotation="10 MB", level="INFO")

class RAGAgent:
    def __init__(self,
                 model_name: str = "ollama/llama3.2",
                 chunk_size: int = 500,
                 chunk_overlap: int = 100):
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.memory_manager = MemoryManager()
        self._llm = None
        # onprem library handles vector store and embeddings internally
        # but we can specify the persistence directory
        self.db_path = "data/chroma_db"

    @property
    def llm(self):
        if self._llm is None:
            # Check for remote Ollama base URL
            ollama_base_url = os.getenv("OLLAMA_BASE_URL")
            llm_kwargs = {
                "verbose": False,
                "db_path": self.db_path,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }

            # If OLLAMA_BASE_URL is set, we use it to connect to remote Ollama
            model_url = self.model_name
            if ollama_base_url and "ollama" in self.model_name:
                model_url = ollama_base_url
                llm_kwargs["model"] = self.model_name.replace("ollama/", "")
                logger.info(f"Connecting to remote Ollama at {ollama_base_url}")

            # Using onprem LLM with the specified model
            self._llm = LLM(model_url, **llm_kwargs)
        return self._llm

    def ingest_document(self, file_path: str):
        logger.info(f"Ingesting document: {file_path}")
        # In onprem, we can ingest a single file or a directory
        # We'll use the parent directory of the file since onprem.ingest takes a path
        directory = os.path.dirname(file_path)
        try:
            self.llm.ingest(directory)
            logger.success(f"Successfully ingested: {file_path}")
            return 1
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")
            raise

    def rewrite_query(self, question: str) -> str:
        """Step 4: Query Rewriting - Refines vague questions."""
        history_text = self.memory_manager.get_formatted_history()
        if not history_text:
            return question

        rewrite_prompt = (
            f"Given the following conversation history, rewrite the user's latest question "
            f"to be a standalone question that captures the full context for document retrieval.\n\n"
            f"History:\n{history_text}\n"
            f"Latest Question: {question}\n\n"
            f"Rewritten Question (Return ONLY the question):"
        )
        try:
            # Using prompt() for a direct LLM call without RAG for rewriting
            rewritten = self.llm.prompt(rewrite_prompt).strip()
            return rewritten if rewritten else question
        except Exception:
            return question

    def answer_question(self, question: str) -> Dict:
        logger.info(f"Answering question: {question}")
        # Step 1: Query Rewriting (Advanced Feature)
        search_query = self.rewrite_query(question)
        logger.info(f"Rewritten query: {search_query}")

        # Step 2: Build a context-aware final prompt
        history_text = self.memory_manager.get_formatted_history()
        final_prompt = search_query
        if history_text:
            final_prompt = (
                f"Conversation Context:\n{history_text}\n"
                f"Question: {search_query}\n\n"
                f"Instructions: Answer accurately using the context documents. "
                f"Include inline citations like [Source: filename.pdf] if possible."
            )

        # Step 3: Ask the local LLM (Performs RAG internally)
        # onprem's ask() method performs RAG and returns a dictionary or string
        logger.info("Performing Vector Search and LLM Generation...")
        try:
            result = self.llm.ask(final_prompt)
        except Exception as e:
            error_str = str(e)
            if "Cannot assign requested address" in error_str or "ConnectionError" in error_str:
                logger.error(f"Connection error to Ollama: {error_str}")
                raise RuntimeError("Failed to connect to local AI engine (Ollama). Please ensure Ollama is running and accessible. If you are running in a container, you may need to set OLLAMA_BASE_URL.")
            raise
        logger.success("Generated response successfully")

        # Depending on onprem version/config, result might be a dict or string
        if isinstance(result, dict):
            answer = result.get('answer', str(result))
            source_docs = result.get('source_documents', [])
            sources = []
            for doc in source_docs:
                src = os.path.basename(doc.metadata.get('source', 'Unknown'))
                if src not in sources:
                    sources.append(src)
        else:
            answer = result
            sources = []

        # Confidence Scoring
        confidence = "medium"
        if len(sources) >= 2:
            confidence = "high"
        elif not sources:
            confidence = "low"

        # Step 4 - Maintain Conversation
        self.memory_manager.add_exchange(question, answer)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "search_query": search_query
        }
