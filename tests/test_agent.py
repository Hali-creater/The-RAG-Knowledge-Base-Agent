import pytest
from src.rag_agent import RAGAgent
import os
from unittest.mock import MagicMock
import sys

# Ensure onprem is mocked
if 'onprem' not in sys.modules:
    sys.modules['onprem'] = MagicMock()

def test_agent_initialization():
    agent = RAGAgent()
    assert agent is not None
    assert hasattr(agent, 'memory_manager')
    assert agent.model_name == "ollama/llama3.2"

def test_agent_answer_format():
    agent = RAGAgent()
    # Mock the LLM property
    agent._llm = MagicMock()
    agent._llm.ask.return_value = "Test Answer"

    response = agent.answer_question("Test Question")
    assert "answer" in response
    assert response["answer"] == "Test Answer"
    assert "sources" in response
