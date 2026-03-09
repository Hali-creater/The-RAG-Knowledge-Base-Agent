from src.rag_agent import RAGAgent
import os

os.environ["GROQ_API_KEY"] = "dummy"
agent = RAGAgent()
try:
    agent.answer_question("test", knowledge_area="General")
    print("Success")
except TypeError as e:
    print(f"Caught expected error: {e}")
except Exception as e:
    print(f"Caught other error: {e}")
