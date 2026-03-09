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

    def ingest_document(self, file_path: str, knowledge_area: str = "General", **kwargs):
        logger.info(f"Ingesting document: {file_path} into {knowledge_area}")
        base_name = os.path.basename(file_path)

        try:
            docs = DocumentLoader.load_document(file_path)
            full_text = "\n".join([doc.page_content for doc in docs[:3]]) # Use first 3 pages for summary
            summary = self.summarize_document(full_text, base_name)

            for doc in docs:
                doc.metadata["source"] = base_name
                doc.metadata["knowledge_area"] = knowledge_area
                doc.metadata["summary"] = summary

            chunks = self.text_splitter.split_documents(docs)

            # Delete existing chunks for this document to avoid duplicates
            self.vector_store.delete_document_chunks(base_name)

            # Add new chunks
            self.vector_store.add_documents(chunks)

            logger.success(f"Successfully ingested {len(chunks)} chunks from {base_name}")
            return {"chunks": len(chunks), "summary": summary}
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {e}")
            raise

    def summarize_document(self, text: str, filename: str) -> str:
        """Step 11: Automated Document Summarization."""
        logger.info(f"Generating summary for {filename}")
        summary_prompt = (
            f"Provide a one-sentence summary of the following document content "
            f"from the file '{filename}':\n\n{text[:2000]}"
        )
        try:
            messages = [
                SystemMessage(content="You are a helpful assistant that summarizes documents concisely."),
                HumanMessage(content=summary_prompt)
            ]
            summary = self.llm.invoke(messages).content.strip()
            return summary
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Summary unavailable."

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

    def answer_question(self, question: str, knowledge_area: str = "General", assistant_type: str = "General", **kwargs) -> Dict:
        logger.info(f"Answering question: {question} in area: {knowledge_area} as {assistant_type}")

        # Step 1: Query Rewriting
        search_query = self.rewrite_query(question)
        logger.info(f"Rewritten query: {search_query}")

        # Step 2: Retrieve Context
        results = self.vector_store.similarity_search(search_query, k=5, score_threshold=0.4, knowledge_area=knowledge_area)

        # Fallback if no results
        if not results:
            results = self.vector_store.similarity_search(search_query, k=3, score_threshold=0.2, knowledge_area=knowledge_area)

        if not results:
            return {
                "answer": "No document in my knowledge base contains information relevant to this question.",
                "sources": [],
                "confidence": "none",
                "search_query": search_query
            }

        context_text = ""
        sources = []
        for doc, score in results:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "N/A")
            context_text += f"--- Source: {source} (Page {page}) ---\n{doc.page_content}\n\n"
            source_citation = f"{source} (Page {page})"
            if source_citation not in sources:
                sources.append(source_citation)

        # Step 3: Build Prompt & Generate
        history_text = self.memory_manager.get_formatted_history()

        persona_map = {
            "HR": "You are a specialized HR Assistant. Be professional, empathetic, and clear about company policies.",
            "Legal": "You are a Legal Compliance Assistant. Be precise, formal, and emphasize accuracy in legal citations.",
            "Finance": "You are a Financial Data Analyst. Be quantitative, analytical, and precise with numbers.",
            "General": "You are a professional RAG Intelligence Agent."
        }

        persona_intro = persona_map.get(assistant_type, persona_map["General"])

        system_prompt = (
            f"{persona_intro} "
            "Your purpose is to answer questions using ONLY the provided context documents.\n\n"
            "CORE RULES:\n"
            "1. If the answer is in the context, provide it clearly and concisely\n"
            "2. If the answer is NOT in the context, say: 'No document in my knowledge base contains information relevant to this question.'\n"
            "3. NEVER make up information or use external knowledge\n"
            "4. Every factual statement MUST cite its source. Format: [Source: filename.pdf (Page X)]\n\n"
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
