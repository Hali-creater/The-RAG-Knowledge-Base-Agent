import os
import shutil
from typing import List, Optional
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
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), knowledge_area: str = "General"):
    count = 0
    errors = []
    results = []
    for file in files:
        if allowed_file(file.filename):
            safe_filename = os.path.basename(file.filename)
            file_path = os.path.join("uploads", safe_filename)
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                # Ingest to RAG Agent
                ingest_res = agent.ingest_document(file_path, knowledge_area=knowledge_area)
                # Move to data/documents for persistence
                shutil.move(file_path, os.path.join("data/documents", safe_filename))
                count += 1
                results.append({"filename": file.filename, "summary": ingest_res["summary"]})
            except Exception as e:
                errors.append(f"Error processing {file.filename}: {str(e)}")
        else:
            errors.append(f"File type not allowed: {file.filename}")

    if not errors:
        return {"count": count}
    else:
        return JSONResponse(status_code=207, content={"count": count, "errors": errors})

@app.post("/ask")
async def ask_question(request: QuestionRequest, groq_api_key: Optional[str] = None, knowledge_area: str = "General", assistant_type: str = "General"):
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key

    try:
        response = agent.answer_question(request.question, knowledge_area=knowledge_area, assistant_type=assistant_type)
        return response
    except Exception as e:
        error_msg = str(e)
        if "GROQ_API_KEY" in error_msg:
            raise HTTPException(status_code=401, detail="Groq API Key required.")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/documents")
async def get_documents():
    if os.path.exists("data/documents"):
        return os.listdir("data/documents")
    return []

@app.post("/clear")
async def clear_history():
    agent.memory_manager.clear_memory()
    return {"status": "cleared"}

@app.post("/reset")
async def reset_database():
    if agent.clear_database():
        return {"status": "reset"}
    else:
        raise HTTPException(status_code=500, detail="Failed to reset database")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
