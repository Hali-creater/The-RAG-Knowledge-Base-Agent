import sys
from unittest.mock import MagicMock

# Mock necessary modules
sys.modules['langchain_groq'] = MagicMock()
sys.modules['langchain_huggingface'] = MagicMock()
sys.modules['langchain_chroma'] = MagicMock()
sys.modules['langchain_community'] = MagicMock()
sys.modules['langchain_community.document_loaders'] = MagicMock()
sys.modules['langchain_community.embeddings'] = MagicMock()

# Handle nested mocks for langchain_core
langchain_core_mock = MagicMock()
sys.modules['langchain_core'] = langchain_core_mock
sys.modules['langchain_core.messages'] = MagicMock()
sys.modules['langchain_core.documents'] = MagicMock()

sys.modules['langchain_text_splitters'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['onprem'] = MagicMock()

import pytest
from src.rag_agent import RAGAgent

def test_signature_robustness():
    agent = RAGAgent()
    # Mocking retrieval to avoid real calls
    agent.rewrite_query = MagicMock(return_value="standalone")
    agent.vector_store.similarity_search = MagicMock(return_value=[])

    # This should NOT raise TypeError now
    res = agent.answer_question("test", knowledge_area="HR", extra_bogus_arg=True)
    assert res is not None
