import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.rag_agent import RAGAgent
from src.utils import ensure_dirs, allowed_file

app = FastAPI(title="RAG Intelligence Agent")

# Setup directories
ensure_dirs()

# Templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Agent
agent = RAGAgent()

class QuestionRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    count = 0
    for file in files:
        if allowed_file(file.filename):
            safe_filename = os.path.basename(file.filename)
            file_path = os.path.join("uploads", safe_filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Ingest to RAG Agent
            agent.ingest_document(file_path)
            # Move to data/documents for persistence
            shutil.move(file_path, os.path.join("data/documents", safe_filename))
            count += 1

    return {"count": count}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        response = agent.answer_question(request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def get_documents():
    return agent.vector_store.get_all_sources()

@app.post("/clear")
async def clear_history():
    agent.memory_manager.clear_memory()
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
