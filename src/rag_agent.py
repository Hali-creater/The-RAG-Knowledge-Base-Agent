import os
from typing import Optional, List, Dict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.vector_store import VectorStore
from src.memory_manager import MemoryManager
from src.document_loader import DocumentLoader
from src.text_splitter import TextSplitter
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Setup logging
logger.add("logs/agent.log", rotation="10 MB", level="INFO")

class RAGAgent:
    def __init__(self,
                 model_name: str = "llama-3.3-70b-versatile",
                 chunk_size: int = 500,
                 chunk_overlap: int = 100):
        self.model_name = model_name
        self.memory_manager = MemoryManager()
        self.text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self._llm = None
        self._vector_store = None

    @property
    def llm(self):
        if self._llm is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found. Please provide it in the UI or environment.")
            self._llm = ChatGroq(
                model_name=self.model_name,
                groq_api_key=api_key,
                temperature=0.1
            )
        return self._llm

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = VectorStore()
        return self._vector_store

    def ingest_document(self, file_path: str):
        logger.info(f"Ingesting document: {file_path}")
        base_name = os.path.basename(file_path)

        try:
            docs = DocumentLoader.load_document(file_path)
            for doc in docs:
                doc.metadata["source"] = base_name

            chunks = self.text_splitter.split_documents(docs)

            # Delete existing chunks for this document to avoid duplicates
            self.vector_store.delete_document_chunks(base_name)

            # Add new chunks
            self.vector_store.add_documents(chunks)

            logger.success(f"Successfully ingested {len(chunks)} chunks from {base_name}")
            return len(chunks)
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")
            raise

    def rewrite_query(self, question: str) -> str:
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
            messages = [
                SystemMessage(content="You are a helpful assistant that reformulates user questions."),
                HumanMessage(content=rewrite_prompt)
            ]
            rewritten = self.llm.invoke(messages).content.strip()
            return rewritten if rewritten else question
        except Exception:
            return question

    def answer_question(self, question: str) -> Dict:
        logger.info(f"Answering question: {question}")

        # Step 1: Query Rewriting
        search_query = self.rewrite_query(question)
        logger.info(f"Rewritten query: {search_query}")

        # Step 2: Retrieve Context
        results = self.vector_store.similarity_search(search_query, k=5, score_threshold=0.4)

        # Fallback if no results
        if not results:
            results = self.vector_store.similarity_search(search_query, k=3, score_threshold=0.2)

        if not results:
            return {
                "answer": "I cannot find specific information about that in my knowledge base. Please upload more documents.",
                "sources": [],
                "confidence": "none",
                "search_query": search_query
            }

        context_text = ""
        sources = []
        for doc, score in results:
            source = doc.metadata.get("source", "Unknown")
            context_text += f"--- Source: {source} ---\n{doc.page_content}\n\n"
            if source not in sources:
                sources.append(source)

        # Step 3: Build Prompt & Generate
        history_text = self.memory_manager.get_formatted_history()

        system_prompt = (
            "You are a professional RAG Intelligence Agent. "
            "Your purpose is to answer questions using ONLY the provided context documents.\n\n"
            "CORE RULES:\n"
            "1. If the answer is in the context, provide it clearly and concisely\n"
            "2. If the answer is NOT in the context, say: 'I cannot find this information in the available documents.'\n"
            "3. NEVER make up information\n"
            "4. Every factual statement should cite its source. Format: [Source: filename.pdf]\n\n"
            f"Conversation History:\n{history_text}\n"
            f"Context:\n{context_text}"
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {question}\nAnswer using ONLY the above context:")
        ]

        logger.info("Invoking Groq LLM...")
        response = self.llm.invoke(messages)
        answer = response.content
        logger.success("Generated response successfully")

        # Confidence Scoring
        confidence = "high" if len(results) >= 3 else "medium"
        if len(results) < 2:
            confidence = "low"
            answer += "\n\n(Disclaimer: This information may be incomplete)"

        # Step 4: Maintain Conversation
        self.memory_manager.add_exchange(question, answer)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "search_query": search_query
        }
