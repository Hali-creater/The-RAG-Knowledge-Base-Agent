from fastapi import FastAPI, Request, Query, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os
from database import get_all_leads, update_lead, delete_lead, get_daily_summary, export_to_csv

app = FastAPI(title="Real Estate Lead Intelligence Dashboard")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

class LeadUpdate(BaseModel):
    status: str = None
    notes: str = None

@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    source: str = Query(None),
    status: str = Query(None),
    lead_type: str = Query(None),
    intent_level: str = Query(None),
    location: str = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("DESC")
):
    filters = {
        "source": source,
        "status": status,
        "lead_type": lead_type,
        "intent_level": intent_level,
        "location": location
    }
    active_filters = {k: v for k, v in filters.items() if v}
    leads = get_all_leads(active_filters, sort_by, sort_order)
    summary = get_daily_summary()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "leads": leads,
        "summary": summary,
        "filters": filters,
        "sort": {"by": sort_by, "order": sort_order}
    })

@app.post("/update_lead/{lead_id}")
async def modify_lead(lead_id: int, update: LeadUpdate):
    update_lead(lead_id, update.dict(exclude_none=True))
    return {"status": "success"}

@app.delete("/delete_lead/{lead_id}")
async def remove_lead(lead_id: int):
    delete_lead(lead_id)
    return {"status": "success"}

@app.get("/export_csv")
async def export_csv(
    source: str = Query(None),
    status: str = Query(None),
    lead_type: str = Query(None),
    intent_level: str = Query(None)
):
    filters = {
        "source": source,
        "status": status,
        "lead_type": lead_type,
        "intent_level": intent_level
    }
    active_filters = {k: v for k, v in filters.items() if v}
    leads = get_all_leads(active_filters)
    csv_data = export_to_csv(leads)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )

def run_dashboard():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_dashboard()
