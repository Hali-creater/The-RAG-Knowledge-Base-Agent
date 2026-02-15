from fastapi import FastAPI, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from database import get_all_leads, update_lead_status, delete_lead, get_daily_summary

app = FastAPI(title="Real Estate Lead Intelligence Dashboard")

# Get the absolute path to the templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    intent_type: str = Query(None),
    status: str = Query(None),
    location: str = Query(None)
):
    filters = {
        "intent_type": intent_type,
        "status": status,
        "location": location
    }
    # Clean filters (remove None or empty strings)
    active_filters = {k: v for k, v in filters.items() if v}

    leads = get_all_leads(active_filters)
    summary = get_daily_summary()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "leads": leads,
        "summary": summary,
        "filters": filters
    })

@app.post("/update_status/{lead_id}")
async def update_status(lead_id: int, status: str):
    update_lead_status(lead_id, status)
    return {"status": "success"}

@app.delete("/delete_lead/{lead_id}")
async def remove_lead(lead_id: int):
    delete_lead(lead_id)
    return {"status": "success"}

def run_dashboard():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_dashboard()
