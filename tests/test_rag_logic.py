import pytest
from unittest.mock import MagicMock, patch
from src.rag_agent import RAGAgent
from langchain_core.messages import AIMessage

@patch('src.rag_agent.ChatGroq')
@patch('src.rag_agent.VectorStore')
def test_answer_question_standalone_query(mock_vector_store, mock_chat_groq):
    # Setup mocks
    mock_llm_instance = MagicMock()
    mock_chat_groq.return_value = mock_llm_instance

    # 1. Answer 1st question
    # 2. Reformulate 2nd question
    # 3. Answer 2nd question
    mock_res1 = MagicMock()
    mock_res1.content = "The capital of France is Paris. [Source: geography.txt]"
    mock_res_eval = MagicMock()
    mock_res_eval.content = "95"
    mock_res2 = MagicMock()
    mock_res2.content = "What is the population of Paris?"
    mock_res3 = MagicMock()
    mock_res3.content = "The population of Paris is about 2.1 million. [Source: geography.txt]"
    mock_llm_instance.invoke.side_effect = [mock_res1, mock_res_eval, mock_res2, mock_res3, mock_res_eval]

    mock_vs_instance = MagicMock()
    mock_vector_store.return_value = mock_vs_instance
    mock_vs_instance.similarity_search.return_value = [
        (MagicMock(page_content="Paris is the capital of France.", metadata={"source": "geography.txt"}), 0.9)
    ]

    import os
    os.environ["GROQ_API_KEY"] = "gsk-dummy"

    agent = RAGAgent()

    # First question
    agent.answer_question("What is the capital of France?")

    # Second question (follow-up)
    response = agent.answer_question("And what about its population?")

    # Check if reformulation was called
    # Calls: 1. First Answer, 2. First Eval, 3. Second Rewrite, 4. Second Answer, 5. Second Eval
    assert mock_llm_instance.invoke.call_count == 5
    assert "The population of Paris" in response["answer"]
    assert any("geography.txt" in s for s in response["sources"])

def test_memory_manager_history():
    from src.memory_manager import MemoryManager
    mm = MemoryManager(max_history=2)
    mm.add_exchange("Q1", "A1")
    mm.add_exchange("Q2", "A2")
    mm.add_exchange("Q3", "A3")

    history = mm.get_history()
    assert len(history) == 2
    assert history[0]["question"] == "Q2"
    assert history[1]["question"] == "Q3"
