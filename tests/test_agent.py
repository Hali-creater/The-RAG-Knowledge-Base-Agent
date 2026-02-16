import pytest
from src.rag_agent import RAGAgent
import os

def test_agent_initialization():
    # Mocking environment variables
    os.environ["OPENAI_API_KEY"] = "sk-dummy"
    agent = RAGAgent()
    assert agent is not None
    # Just check if it has the components
    assert hasattr(agent, 'vector_store')
    assert hasattr(agent, 'memory_manager')

def test_text_processing():
    from src.text_splitter import TextSplitter
    from langchain_core.documents import Document

    splitter = TextSplitter()
    docs = [Document(page_content="This is a test document. It has some text.", metadata={"source": "test.txt"})]
    chunks = splitter.split_documents(docs)
    assert len(chunks) > 0
    assert "test document" in chunks[0].page_content
