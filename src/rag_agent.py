import os
from typing import Optional, List, Dict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.vector_store import VectorStore
from src.memory_manager import MemoryManager
from src.document_loader import DocumentLoader
from src.text_splitter import TextSplitter
from src.audit_logger import log_query
from src.gold_standard import get_gold_standard, save_gold_standard
from src.utils import get_file_hash, ROLE_PERMISSIONS
from src.connectors import ConnectorManager
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
        file_hash = get_file_hash(file_path)

        try:
            # Step 12: Content-based Deduplication
            existing_sources = self.vector_store.get_all_sources_with_metadata()
            for source in existing_sources:
                if source.get("file_hash") == file_hash and source.get("knowledge_area") == knowledge_area:
                    logger.info(f"Document {base_name} already ingested in {knowledge_area}. Skipping.")
                    return {"chunks": 0, "summary": source.get("summary", "Already exists.")}

            docs = DocumentLoader.load_document(file_path)
            full_text = "\n".join([doc.page_content for doc in docs[:3]]) # Use first 3 pages for summary
            summary = self.summarize_document(full_text, base_name)

            for doc in docs:
                doc.metadata["source"] = base_name
                doc.metadata["knowledge_area"] = knowledge_area
                doc.metadata["summary"] = summary
                doc.metadata["file_hash"] = file_hash

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
        # Step 14: Contextual Query Rewriting
        history_text = self.memory_manager.get_formatted_history()
        if not history_text:
            return question

        # If it's a short question and we have history, rewrite it.
        # But if it's already a complex question, keep it as is unless it's a clear follow-up.
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

    def evaluate_faithfulness(self, answer: str, context: str) -> str:
        """Simple LLM-based faithfulness evaluation."""
        eval_prompt = (
            f"Given the following context and an answer, rate the faithfulness of the answer to the context "
            f"on a scale of 0 to 100. Provide ONLY the number.\n\n"
            f"Context: {context[:2000]}\n\n"
            f"Answer: {answer[:1000]}\n\n"
            f"Faithfulness Score:"
        )
        try:
            messages = [
                SystemMessage(content="You are an expert evaluator for RAG systems."),
                HumanMessage(content=eval_prompt)
            ]
            score = self.llm.invoke(messages).content.strip()
            return f"{score}%"
        except Exception:
            return "N/A"

    def verify_answer(self, question: str, answer: str):
        """Step 15: Human-in-the-loop verification."""
        logger.info(f"Verifying answer for: {question}")
        save_gold_standard(question, answer)
        return True

    def clear_database(self):
        logger.warning("Clearing entire vector database...")
        return self.vector_store.clear_database()

    def ingest_from_connector(self, connector_type: str, params: Dict, knowledge_area: str = "General"):
        """Ingest documents from external connectors."""
        logger.info(f"Ingesting from {connector_type} into {knowledge_area}")
        try:
            if connector_type == "GDrive":
                docs = ConnectorManager.load_from_gdrive(params.get("folder_id"), params.get("service_account_path"))
            elif connector_type == "OneDrive":
                docs = ConnectorManager.load_from_onedrive(params.get("drive_id"), params.get("folder_path"))
            elif connector_type == "SharePoint":
                docs = ConnectorManager.load_from_sharepoint(params.get("site_id"), params.get("document_library_id"))
            else:
                raise ValueError(f"Unknown connector type: {connector_type}")

            if not docs:
                return {"chunks": 0, "message": "No documents found."}

            chunks = self.text_splitter.split_documents(docs)
            self.vector_store.add_documents(chunks)

            logger.success(f"Successfully ingested {len(chunks)} chunks from {connector_type}")
            return {"chunks": len(chunks)}
        except Exception as e:
            logger.error(f"Failed to ingest from {connector_type}: {e}")
            raise

    def answer_question(self, question: str, knowledge_area: str = "General", assistant_type: str = "General", language: str = "🇺🇸 English", **kwargs) -> Dict:
        logger.info(f"Answering question: {question} in area: {knowledge_area} as {assistant_type} in {language}")

        # Step -1: Check Gold Standard
        gold_answer = get_gold_standard(question)
        if gold_answer:
            logger.info(f"Found Gold Standard answer for: {question}")
            return {
                "answer": gold_answer + "\n\n*(Verified Gold Standard Response)*",
                "sources": ["Verified Internal Knowledge"],
                "confidence": "100%",
                "faithfulness": "100%",
                "search_query": question
            }

        # Step 0: Permission Check
        user_role = kwargs.get("user_role", "Employee")
        allowed_areas = ROLE_PERMISSIONS.get(user_role, ["General"])
        if knowledge_area not in allowed_areas:
             return {
                "answer": f"Access Denied: Your role ({user_role}) does not have permission to access the '{knowledge_area}' knowledge area.",
                "sources": [],
                "confidence": "0%",
                "faithfulness": "0%",
                "search_query": question
            }

        # Step 1: Query Rewriting
        if self.memory_manager.history:
            search_query = self.rewrite_query(question)
        else:
            search_query = question
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
            "Comparative": "You are a Comparative Analysis Expert. Your goal is to find discrepancies, similarities, and differences between multiple documents or versions of policies.",
            "General": "You are a professional RAG Intelligence Agent."
        }

        persona_intro = persona_map.get(assistant_type, persona_map["General"])

        structure_map = {
            "🇺🇸 English": {
                "summary": "Summary",
                "points": "Key Points",
                "insights": "Insights",
                "sources": "Sources"
            },
            "🇩🇪 German": {
                "summary": "Zusammenfassung",
                "points": "Wichtige Punkte",
                "insights": "Erkenntnisse",
                "sources": "Quellen"
            },
            "🇫🇷 French": {
                "summary": "Résumé",
                "points": "Points clés",
                "insights": "Aperçus",
                "sources": "Sources"
            }
        }
        struct = structure_map.get(language, structure_map["🇺🇸 English"])

        system_prompt = (
            f"{persona_intro} "
            f"Respond strictly in {language}. "
            "Your purpose is to answer questions using ONLY the provided context documents. Provide comprehensive, detailed, and well-structured answers.\n\n"
            "RESPONSE STRUCTURE (Use these headers translated to the output language):\n"
            f"1. **{struct['summary']}**: A brief overview of the answer.\n"
            f"2. **{struct['points']}**: Use bullet points for detailed findings.\n"
            f"3. **{struct['insights']}**: Strategic or analytical observations based on the context.\n"
            f"4. **{struct['sources']}**: List the specific documents and pages used.\n\n"
            "CORE RULES:\n"
            f"1. Respond strictly in {language}. "
            "2. If the answer is in the context, provide it in great detail, covering all relevant points mentioned. Use the RESPONSE STRUCTURE above.\n"
            "3. If the answer is NOT in the context, say: 'No document in my knowledge base contains information relevant to this question.' (translated to the output language)\n"
            "4. NEVER make up information or use external knowledge. Only use the provided context.\n"
            "5. Every factual statement MUST cite its source inline. Format: [Source: filename.pdf (Page X)]\n"
            "6. If the context contains multiple pieces of information related to the question, synthesize them into a cohesive and thorough response.\n"
            "7. If the source documents are in a different language than the output, provide an accurate technical translation of the key terms.\n\n"
            f"Conversation History:\n{history_text}\n"
            f"Context:\n{context_text}"
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {question}\nOutput Language: {language}\nAnswer using ONLY the above context:")
        ]

        logger.info("Invoking Groq LLM...")
        response = self.llm.invoke(messages)
        answer = response.content
        logger.success("Generated response successfully")

        # Confidence Scoring
        avg_score = sum(score for _, score in results) / len(results) if results else 0
        if avg_score > 0.8:
            confidence_val = 90 + (avg_score - 0.8) * 50
        elif avg_score > 0.6:
            confidence_val = 70 + (avg_score - 0.6) * 100
        else:
            confidence_val = avg_score * 110

        confidence_val = min(99, max(10, confidence_val))
        confidence = f"{confidence_val:.0f}%"

        # Step 4: Evaluation Metrics (Faithfulness)
        faithfulness_score = self.evaluate_faithfulness(answer, context_text)

        # Step 5: Maintain Conversation
        self.memory_manager.add_exchange(question, answer)

        # Step 6: Audit Logging
        user_role = kwargs.get("user_role", "Unknown")
        log_query(
            user_role=user_role,
            question=question,
            answer=answer,
            sources=sources,
            knowledge_area=knowledge_area,
            confidence=confidence,
            assistant_type=assistant_type
        )

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "faithfulness": faithfulness_score,
            "search_query": search_query
        }
