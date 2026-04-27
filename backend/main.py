"""
main.py — FastAPI backend for EliseAI GTM

Bridges the Next.js frontend with the Python enrichment pipeline.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
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
    allow_origins=["*"],
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


class SlackRequest(BaseModel):
    lead: dict
    result: dict


class SheetsRequest(BaseModel):
    lead: dict
    result: dict


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


@app.post("/slack")
async def send_slack_alert(request: SlackRequest):
    """Send Slack alert on button click."""
    from integrations.slack import send_lead_alert
    try:
        print(f"DEBUG: Sending Slack alert for {request.lead.get('company')}")
        result = send_lead_alert(request.result, request.lead)
        
        if result and isinstance(result, dict) and "error" in result:
             return {"success": False, "error": result["error"]}
        if not result:
             return {"success": False, "error": "Slack integration is not configured or client failed to initialize."}
             
        print(f"DEBUG: Slack response: {result}")
        return {"success": True, "response": "Message sent to Slack"}
    except Exception as e:
        print(f"DEBUG: Slack error: {str(e)}")
        return {"success": False, "error": str(e)}


@app.post("/sheets")
async def export_to_sheets(request: SheetsRequest):
    """Write single result to Google Sheets via service account."""
    from integrations.sheets import write_result_to_sheet
    try:
        print(f"DEBUG: Exporting to Sheets for {request.lead.get('company')}")
        result = write_result_to_sheet(request.result, request.lead)
        
        if not result:
             return {"success": False, "error": "Google Sheets integration failed to return a response."}
             
        print(f"DEBUG: Sheets response: {result}")
        return {"success": True, "response": result}
    except Exception as e:
        print(f"DEBUG: Sheets error: {str(e)}")
        return {"success": False, "error": str(e)}


@app.post("/export/csv")
async def export_csv(request: dict):
    """Return CSV data for download."""
    import csv
    import io
    from typing import List
    
    results = request.get("results", [])
    
    headers = [
        "name", "email", "company", "city", "state", "tier", "priority_score",
        "renter_pct", "vacancy_rate", "rent_growth_pct", "median_income",
        "sales_signal", "score_rationale"
    ]
    
    rows = []
    for r in results:
        lead = r.get("_lead", {})
        kdp = r.get("key_data_points", {})
        email = r.get("email_draft", {})
        if isinstance(email, dict):
            email_body = email.get("body", "")
        else:
            email_body = str(email)
        
        rows.append([
            lead.get("name", ""),
            lead.get("email", ""),
            lead.get("company", ""),
            lead.get("city", ""),
            lead.get("state", ""),
            r.get("tier", ""),
            r.get("priority_score", ""),
            kdp.get("renter_pct", ""),
            kdp.get("vacancy_rate", ""),
            kdp.get("rent_growth_pct", ""),
            kdp.get("median_income", ""),
            r.get("sales_signal", ""),
            r.get("score_rationale", ""),
        ])
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    
    return {"csv": output.getvalue()}


@app.post("/webhook")
async def send_webhook(request: dict):
    """Send to webhook endpoint."""
    from integrations.webhook import send_to_webhook
    try:
        result = send_to_webhook(request.get("result", {}), request.get("lead", {}))
        return {"success": True, "response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/upload-leads")
async def upload_leads(file: UploadFile = File(...)):
    """
    Accept CSV or XLSX file, validate, map columns, return un-enriched lead objects.
    - Max file size: 20MB
    - Max rows: 100
    - Required: 'company' column
    - Missing city/state: '[MISSING]' + requires_review=True
    - Missing email: None (no review flag)
    """
    import pandas as pd
    import io
    
    MAX_FILE_SIZE = 20_000_000  # 20MB
    MAX_ROWS = 100
    
    # 1. Validate file type
    filename = file.filename or ""
    if not any(filename.endswith(ext) for ext in [".csv", ".xlsx", ".xls"]):
        raise HTTPException(400, "Unsupported file format. Please upload CSV or XLSX.")
    
    # 2. Read file content
    contents = await file.read()
    
    # 3. Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File size exceeds 20MB limit.")
    
    # 4. Parse with pandas
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(400, f"Failed to parse file: {str(e)}")
    
    # 5. Check row limit
    if len(df) > MAX_ROWS:
        raise HTTPException(400, f"Batch limit exceeded. Please upload up to 100 leads for real-time enrichment.")
    
    # 6. Map columns using existing mapper
    from ingestion.mapper import detect_source, map_columns
    headers = df.columns.tolist()
    source = detect_source(headers)
    mapping, unmapped = map_columns(headers)
    
    # 7. Validate company column exists
    if "company" not in mapping.values():
        raise HTTPException(400, "Upload failed: Could not detect a 'Company' column. Please check your headers.")
    
    # 8. Transform rows to lead objects
    from parsers.unified_parser import transform_row
    
    leads = []
    for idx, row in df.iterrows():
        try:
            row_dict = row.to_dict()
            transformed = transform_row(row_dict, mapping, source)
            
            # Build lead object
            lead = {
                "name": transformed.get("name") or "",
                "email": transformed.get("email") or None,
                "company": (transformed.get("company") or "").strip(),
                "property_address": transformed.get("property_address") or "",
                "city": transformed.get("city") or "[MISSING]",
                "state": transformed.get("state") or "[MISSING]",
                "requires_review": False,
            }
            
            # Flag for review if city or state missing
            if lead["city"] == "[MISSING]" or lead["state"] == "[MISSING]":
                lead["requires_review"] = True
            
            leads.append(lead)
        except Exception:
            continue
    
    return {"leads": leads, "count": len(leads)}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)