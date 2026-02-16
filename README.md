# RAG Intelligence Agent

A Retrieval-Augmented Generation (RAG) agent that answers questions based on your documents.

## Features
- **Document Support**: PDF, DOCX, TXT, and Markdown.
- **Stylish UI**: Modern interface using FastAPI, Tailwind CSS, and Bootstrap.
- **Smart Retrieval**: Intelligent chunking and similarity search with ChromaDB.
- **Conversation Memory**: Remembers context and handles follow-up questions.
- **Security**: XSS protection and environment safety.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key in a `.env` file (see `.env.example`).
3. Run the application:
   ```bash
   python main.py
   ```
4. Open your browser at `http://localhost:8000`.

## Testing
Run unit tests:
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 tests/test_agent.py
```

## Demo
You can also run a quick CLI demo:
```bash
python demo.py
```
