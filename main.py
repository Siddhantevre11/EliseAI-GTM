"""
main.py — FastAPI backend for EliseAI GTM

Bridges the Next.js frontend with the Python enrichment pipeline.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="EliseAI GTM Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from agent.pipeline import run_pipeline, run_batch
from integrations.sheets import read_unprocessed_leads, write_result_to_sheet


class LeadInput(BaseModel):
    name: str = ""
    email: str = ""
    company: str
    property_address: str = ""
    city: str
    state: str


class EnrichRequest(BaseModel):
    name: str = ""
    email: str = ""
    company: str
    property_address: str = ""
    city: str
    state: str
    check_validation: bool = True


class BatchRequest(BaseModel):
    leads: List[LeadInput]
    check_validation: bool = True


@app.get("/")
async def root():
    return {"status": "ok", "service": "EliseAI GTM Backend"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/enrich")
async def enrich_lead(request: EnrichRequest):
    try:
        lead_dict = request.model_dump()
        lead_dict.pop("check_validation", None)
        result = run_pipeline(
            lead=lead_dict,
            validate=request.check_validation,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch")
async def enrich_batch(request: BatchRequest):
    try:
        leads = [lead.model_dump() for lead in request.leads]
        results = run_batch(leads)
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-sheets")
async def sync_sheets():
    try:
        from automation import _run_daily_enrichment
        result = _run_daily_enrichment()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trigger")
async def trigger_manual():
    """Manually trigger lead enrichment."""
    from automation import trigger_manual_run
    try:
        result = trigger_manual_run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)