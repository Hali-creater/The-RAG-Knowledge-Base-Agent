import sys
from unittest.mock import MagicMock

# Mock necessary modules
sys.modules['langchain_groq'] = MagicMock()
sys.modules['langchain_huggingface'] = MagicMock()
sys.modules['langchain_chroma'] = MagicMock()
sys.modules['langchain_community'] = MagicMock()
sys.modules['langchain_community.document_loaders'] = MagicMock()

# Handle nested mocks for langchain_core
langchain_core_mock = MagicMock()
sys.modules['langchain_core'] = langchain_core_mock
sys.modules['langchain_core.messages'] = MagicMock()
sys.modules['langchain_core.documents'] = MagicMock()

sys.modules['langchain_text_splitters'] = MagicMock()
sys.modules['chromadb'] = MagicMock()

import pytest
from src.rag_agent import RAGAgent

def test_agent_initialization():
    import os
    os.environ["GROQ_API_KEY"] = "gsk-dummy"
    agent = RAGAgent()
    assert agent is not None
    assert agent.model_name == "llama-3.3-70b-versatile"

def test_rewrite_query_call():
    import os
    os.environ["GROQ_API_KEY"] = "gsk-dummy"
    agent = RAGAgent()
    agent._llm = MagicMock()

    # Mock LLM response for query rewriting
    mock_response = MagicMock()
    mock_response.content = "Standalone question?"
    agent._llm.invoke.return_value = mock_response

    agent.memory_manager.add_exchange("Previous Q", "Previous A")
    rewritten = agent.rewrite_query("Follow up Q")

    assert rewritten == "Standalone question?"
    agent._llm.invoke.assert_called_once()
