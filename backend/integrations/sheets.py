"""
integrations/sheets.py — Google Sheets Integration

Read leads from / write results to Google Sheets.
Requires: gspread, google-auth
Setup: Create service account in GCP Console, share sheet with service email.
"""

import os
import json
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import gspread
    from google.auth import exceptions
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False


SHEETS_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
SHEET_URL = os.getenv("GOOGLE_SHEET_URL", "")

HEADERS = [
    "name", "email", "company", "property_address", "city", "state",
    "tier", "score_rationale", "email_draft", "talking_points",
    "renter_pct", "vacancy_rate", "rent_growth_pct", "median_income",
    "quality_grade", "processed_at",
]

REQUIRED_INPUT_COLS = ["name", "email", "company", "city", "state"]


def _get_client():
    if not GSPREAD_AVAILABLE:
        raise ImportError("gspread not installed. Run: pip install gspread google-auth")
    
    base64_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64", "")
    if not SHEETS_SERVICE_ACCOUNT_JSON and not base64_str:
        if not os.path.exists("google-service-account.json"):
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 not set in .env")
    
    # Try service account file first
    creds = None
    if os.path.exists("google-service-account.json"):
        try:
            from google.oauth2 import service_account
            with open("google-service-account.json", "r") as f:
                creds_dict = json.load(f)
                # Fix any newlines
                if "private_key" in creds_dict:
                    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
                creds = service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=["https://www.googleapis.com/auth/spreadsheets"],
                )
            return gspread.authorize(creds)
        except Exception as e:
            print(f"Service account file failed: {e}")
    
    # Try reading from env directly
    try:
        import base64
        base64_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64", "")
        
        if base64_str:
            json_str = base64.b64decode(base64_str).decode("utf-8")
        else:
            json_str = SHEETS_SERVICE_ACCOUNT_JSON.strip()
            if (json_str.startswith("'") and json_str.endswith("'")) or (json_str.startswith('"') and json_str.endswith('"')):
                json_str = json_str[1:-1]
            
        creds_dict = json.loads(json_str)
        
        # Clean the private key
        key = creds_dict.get("private_key", "")
        if key:
            # Handle literal \n if they survived JSON loading
            key = key.replace("\\n", "\n")
            # Ensure it starts and ends correctly
            if not key.startswith("-----BEGIN"):
                key = "-----BEGIN PRIVATE KEY-----\n" + key
            if not key.endswith("-----END PRIVATE KEY-----\n") and not key.endswith("-----END PRIVATE KEY-----"):
                key = key + "\n-----END PRIVATE KEY-----\n"
            creds_dict["private_key"] = key
        
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
        )
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Environment credentials failed: {e}")
    
    raise RuntimeError("Could not authenticate with Google Sheets. Please check service account credentials.")


def read_leads_from_sheet(sheet_url: Optional[str] = None) -> list[dict]:
    """Read leads from the configured Google Sheet. Returns list of lead dicts."""
    client = _get_client()
    url = sheet_url or SHEET_URL
    if not url:
        raise ValueError("No sheet URL provided")
    
    sheet = client.open_by_url(url)
    worksheet = sheet.sheet1
    rows = worksheet.get_all_records(expected_headers=HEADERS)
    
    leads = []
    for row in rows:
        lead = {k: row.get(k, "") for k in REQUIRED_INPUT_COLS}
        if lead.get("name") or lead.get("company"):
            leads.append(lead)
    
    return leads


def read_unprocessed_leads(sheet_url: Optional[str] = None) -> list[dict]:
    """Read only leads that haven't been processed (tier column empty)."""
    client = _get_client()
    url = sheet_url or SHEET_URL
    if not url:
        raise ValueError("No sheet URL provided")
    
    sheet = client.open_by_url(url)
    worksheet = sheet.sheet1
    rows = worksheet.get_all_records(expected_headers=HEADERS)
    
    leads = []
    for i, row in enumerate(rows):
        if not row.get("tier") and (row.get("name") or row.get("company")):
            lead = {k: row.get(k, "") for k in REQUIRED_INPUT_COLS}
            lead["_row_index"] = i + 2
            leads.append(lead)
    
    return leads


def write_result_to_sheet(result: dict, lead: dict, row_index: Optional[int] = None, sheet_url: Optional[str] = None):
    """Write enrichment result back to the sheet."""
    client = _get_client()
    url = sheet_url or SHEET_URL
    if not url:
        raise ValueError("No sheet URL provided")
    
    sheet = client.open_by_url(url)
    worksheet = sheet.sheet1
    
    # Get next available row if not specified
    if row_index is None:
        row_num = len(worksheet.get_all_values()) + 1
    else:
        row_num = row_index
    
    kdp = result.get("key_data_points", {})
    validation = result.get("_validation", {})
    
    row_data = [
        lead.get("name", ""),
        lead.get("email", ""),
        lead.get("company", ""),
        lead.get("property_address", ""),
        lead.get("city", ""),
        lead.get("state", ""),
        result.get("tier", ""),
        result.get("score_rationale", ""),
        json.dumps(result.get("email_draft", {})),
        json.dumps(result.get("talking_points", [])),
        kdp.get("renter_pct", ""),
        kdp.get("vacancy_rate", ""),
        kdp.get("rent_growth_pct", ""),
        kdp.get("median_income", ""),
        validation.get("quality_grade", ""),
        datetime.now().isoformat(),
    ]
    
    col_range = f"A{row_num}:P{row_num}"
    worksheet.update(col_range, [row_data])
    
    return f"Successfully written to row {row_num}"


def create_sheet_template(sheet_url: Optional[str] = None) -> str:
    """Create/format the sheet with proper headers."""
    client = _get_client()
    url = sheet_url or SHEET_URL
    if not url:
        raise ValueError("No sheet URL provided")
    
    sheet = client.open_by_url(url)
    worksheet = sheet.sheet1
    worksheet.update("A1:P1", [HEADERS])
    
    for col in ["A", "B", "C", "D", "E", "F"]:
        worksheet.format(f"{col}1", {"textFormat": {"bold": True}})
    
    worksheet.set_basic_filter(1, 1, 1, len(HEADERS))
    
    return f"Formatted sheet at {url}"


if __name__ == "__main__":
    print("Sheets integration module loaded.")
    print(f"Gspread available: {GSPREAD_AVAILABLE}")
    print(f"Sheet URL configured: {bool(SHEET_URL)}")