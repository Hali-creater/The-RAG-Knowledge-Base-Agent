import pytest
from src.rag_agent import RAGAgent
import os
from unittest.mock import MagicMock
import sys

def test_agent_initialization():
    os.environ["GROQ_API_KEY"] = "gsk-dummy"
    agent = RAGAgent()
    assert agent is not None
    assert hasattr(agent, 'memory_manager')
    assert agent.model_name == "llama-3.3-70b-versatile"

def test_persona_switching():
    os.environ["GROQ_API_KEY"] = "gsk-dummy"
    agent = RAGAgent()
    agent._llm = MagicMock()
    agent.vector_store.similarity_search = MagicMock(return_value=[])

    # Just verify it returns the fallback message for any persona
    response = agent.answer_question("test", assistant_type="HR")
    assert "No document in my knowledge base" in response["answer"]
