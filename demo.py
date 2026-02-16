import os
from src.rag_agent import RAGAgent
from src.utils import ensure_dirs

def run_demo():
    print("Initializing RAG Agent...")
    ensure_dirs()
    agent = RAGAgent()

    # Check if we have documents
    docs = agent.vector_store.get_all_sources()
    if not docs:
        print("No documents found in knowledge base. Please upload some via the Web UI or add them to data/documents.")
        # Create a dummy doc for demo if none exist
        dummy_path = "data/documents/sample.txt"
        with open(dummy_path, "w") as f:
            f.write("The RAG Knowledge Base Agent is a powerful tool for document-based Q&A. "
                    "It uses LangChain, ChromaDB, and OpenAI to provide accurate answers. "
                    "It supports PDF, DOCX, TXT, and MD files.")
        print(f"Created sample document: {dummy_path}")
        agent.ingest_document(dummy_path)

    print("\nKnowledge Base contains:")
    for doc in agent.vector_store.get_all_sources():
        print(f" - {doc}")

    question = "What files does the RAG agent support?"
    print(f"\nQuestion: {question}")

    try:
        response = agent.answer_question(question)
        print(f"Answer: {response['answer']}")
        print(f"Sources: {', '.join(response['sources'])}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure OPENAI_API_KEY is set in your .env file.")

if __name__ == "__main__":
    run_demo()
