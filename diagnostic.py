import os
import requests
from loguru import logger
from src.rag_agent import RAGAgent

def check_groq():
    print("🔍 Checking Groq Connectivity...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment.")
        return False

    try:
        # Simple test call
        agent = RAGAgent()
        # We just check if the agent can be initialized and has the LLM property
        # Real call might incur costs or rate limits, but initialization is safe
        print(f"✅ Agent initialized with model: {agent.model_name}")
        return True
    except Exception as e:
        print(f"❌ Error initializing Groq Agent: {e}")
        return False

def check_vector_db():
    print("\n🔍 Checking Vector Database...")
    db_path = "data/chroma_db"
    if os.path.exists(db_path):
        files = os.listdir(db_path)
        print(f"✅ Vector DB directory exists with {len(files)} items")
    else:
        print(f"❌ Vector DB path not found at {db_path}")

def check_directories():
    print("\n🔍 Checking Application Directories...")
    for d in ["data/documents", "uploads", "logs", "static"]:
        if os.path.exists(d):
            print(f"✅ '{d}' exists")
        else:
            print(f"❌ '{d}' is missing")

if __name__ == "__main__":
    print("="*50)
    print("RAG Agent Diagnostic Tool")
    print("="*50)

    check_groq()
    check_vector_db()
    check_directories()

    print("\n" + "="*50)
    print("Diagnostic Complete")
