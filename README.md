# Private RAG Knowledge Base Agent 🤖

A 100% local, privacy-first Retrieval-Augmented Generation (RAG) agent. No data leaves your machine, and no API keys are required.

## 🚀 Key Features

- **Groq AI Integration**: Ultra-fast inference using Groq's API (defaulting to `llama-3.3-70b-versatile`).
- **Hybrid RAG Pipeline**:
  - **Vector Database**: Semantic search using local ChromaDB.
  - **Query Rewriting**: Automatically refines vague follow-up questions for better retrieval.
  - **Chunking Control**: Configurable chunk size and overlap for precision.
  - **Inline Citations**: Transparently shows which documents were used for the answer.
- **Dual Interface**:
  - **FastAPI Backend**: Professional API for integration.
  - **Streamlit Frontend**: Intuitive, stylish chat interface.
- **Support for Multiple Formats**: PDF, DOCX, TXT, MD, and more.

## 🏗 Architecture

```mermaid
graph TD
    User((User)) -->|Question| UI[Streamlit / FastAPI]
    UI -->|Ingest| Agent[RAG Agent]
    Agent -->|1. Rewrite| Rewriter[Query Rewriter]
    Rewriter -->|Standalone Query| Search[Vector Search]
    Search -->|Context Chunks| VDB[(ChromaDB)]
    VDB -->|Retrieve| Agent
    Agent -->|2. Generate| LLM[Groq Llama 3.3]
    LLM -->|Answer + Sources| UI
    UI -->|Display| User
```

## 🛠 Installation

1. **Get a Groq API Key**:
   Create a free account and get your key at [console.groq.com](https://console.groq.com).

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   - **Streamlit (Recommended)**:
     ```bash
     streamlit run streamlit_app.py
     ```
   - **FastAPI**:
     ```bash
     python main.py
     ```

## 📁 Repository Structure

- `src/`: Core logic (Agent, Memory Manager, Utils).
- `templates/`: HTML templates for FastAPI.
- `data/`: Persistent storage for documents and vector database.
- `logs/`: Application logs (powered by Loguru).
- `tests/`: Automated test suite.

## 🔒 Privacy & Security

- **Local Embeddings**: Document embeddings are generated locally for privacy.
- **Secure API**: Only text context and queries are sent to Groq for ultra-fast inference.
- **Data Persistence**: Your documents are stored in `data/documents/` and indexed in `data/chroma_db/`.

---
*Built with Python, onprem, ChromaDB, and FastAPI.*
