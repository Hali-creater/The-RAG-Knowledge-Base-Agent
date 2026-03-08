import sys
from unittest.mock import MagicMock

# Mock onprem module
mock_onprem = MagicMock()
sys.modules['onprem'] = mock_onprem

import pytest
from src.rag_agent import RAGAgent

def test_answer_question_local():
    # Setup mock
    mock_llm_instance = MagicMock()
    mock_onprem.LLM.return_value = mock_llm_instance

    mock_llm_instance.ask.return_value = {
        "answer": "This is a local answer.",
        "source_documents": [
            MagicMock(metadata={"source": "local_doc.pdf"}),
            MagicMock(metadata={"source": "local_doc_2.pdf"})
        ]
    }

    agent = RAGAgent()
    response = agent.answer_question("What is the local answer?")

    assert response["answer"] == "This is a local answer."
    assert "local_doc.pdf" in response["sources"]
    assert response["confidence"] == "high"

def test_ingest_document_local():
    mock_llm_instance = MagicMock()
    mock_onprem.LLM.return_value = mock_llm_instance

    agent = RAGAgent()
    agent.ingest_document("data/test.txt")

    mock_llm_instance.ingest.assert_called_once()
