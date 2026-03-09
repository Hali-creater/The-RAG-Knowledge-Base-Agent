import inspect
from src.rag_agent import RAGAgent

agent = RAGAgent()
sig = inspect.signature(agent.answer_question)
print(f"Signature: {sig}")
for param in sig.parameters.values():
    print(f"Param: {param.name}")
