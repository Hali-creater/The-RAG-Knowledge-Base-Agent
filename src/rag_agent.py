import os
from typing import Optional, List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.vector_store import VectorStore
from src.memory_manager import MemoryManager
from src.document_loader import DocumentLoader
from src.text_splitter import TextSplitter
from dotenv import load_dotenv

load_dotenv()

class RAGAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        self.vector_store = VectorStore()
        self.memory_manager = MemoryManager()
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.text_splitter = TextSplitter()

    def ingest_document(self, file_path: str):
        # UPDATING DOCUMENTS PROTOCOL:
        # 1. Find all existing chunks from this document
        # 2. Delete them from vector database
        source_name = file_path # In main.py we pass the path
        # But VectorStore uses the 'source' metadata which is usually the file path
        # We should use the base filename as source identifier for consistency
        base_name = os.path.basename(file_path)

        # Note: LangChain loaders often set 'source' to the full path.
        # We'll handle both or ensure consistent metadata.

        docs = DocumentLoader.load_document(file_path)
        for doc in docs:
            doc.metadata["source"] = base_name # Ensure consistent source name

        chunks = self.text_splitter.split_documents(docs)

        # 2. Delete existing
        self.vector_store.delete_document_chunks(base_name)

        # 3. Process as new
        self.vector_store.add_documents(chunks)
        return len(chunks)

    def answer_question(self, question: str) -> Dict:
        # STEP 1 - Analyze Question (is it a follow-up?)
        is_follow_up = self.memory_manager.is_follow_up(question)

        # STEP 2 - Retrieve Context
        # If follow-up, we might want to augment the query with history
        search_query = question
        if is_follow_up and self.memory_manager.history:
            last_exchange = self.memory_manager.history[-1]
            search_query = f"{last_exchange['question']} {last_exchange['answer']} {question}"

        results = self.vector_store.similarity_search(search_query, k=5, score_threshold=0.7)

        if not results:
            return {
                "answer": "I don't have information about that in my knowledge base",
                "sources": [],
                "confidence": "low"
            }

        context_text = ""
        sources = []
        for doc, score in results:
            source = doc.metadata.get("source", "Unknown")
            context_text += f"--- Source: {source} ---\n{doc.page_content}\n\n"
            if source not in sources:
                sources.append(source)

        # STEP 3 & 4 - Build Enhanced Prompt & Generate Response
        history_text = self.memory_manager.get_formatted_history()

        system_prompt = (
            "You are a RAG Knowledge Base Agent. "
            "Your purpose is to answer questions using ONLY the provided context documents.\n\n"
            "CORE RULES:\n"
            "1. If the answer is in the context, provide it clearly and concisely\n"
            "2. If the answer is NOT in the context, say: 'I cannot find this information in the available documents.'\n"
            "3. NEVER make up or hallucinate information\n"
            "4. NEVER use your training data—only the retrieved context\n"
            "5. Every factual statement should cite its source document. Format: [Source: filename.pdf]\n\n"
            f"Conversation History:\n{history_text}\n"
            f"Context:\n{context_text}"
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {question}\nAnswer using ONLY the above context:")
        ]

        response = self.llm.invoke(messages)
        answer = response.content

        # CHECK 3 - Confidence Scoring
        confidence = "high" if len(results) >= 3 else "medium"
        # If confidence is low, add disclaimer
        if len(results) < 2:
            confidence = "low"
            answer += "\n\n(Disclaimer: This information may be incomplete)"

        # STEP 5 - Maintain Conversation
        self.memory_manager.add_exchange(question, answer)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence
        }
