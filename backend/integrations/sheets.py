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


def _clean_private_key(key: str) -> str:
    """Aggressively clean and re-format a PEM private key."""
    if not key:
        return ""
    import re
    
    # 1. Remove obvious headers and footers first
    clean_data = key.replace("-----BEGIN PRIVATE KEY-----", "")
    clean_data = clean_data.replace("-----END PRIVATE KEY-----", "")
    clean_data = clean_data.replace("BEGIN PRIVATE KEY", "")
    clean_data = clean_data.replace("END PRIVATE KEY", "")
    clean_data = clean_data.replace("PRIVATE KEY", "")
    
    # 2. Keep ONLY valid base64 characters (A-Z, a-z, 0-9, +, /, =)
    # This strips dashes, newlines, and the remaining 'BEGIN'/'END' if they were missed
    clean_data = re.sub(r"[^A-Za-z0-9+/=]", "", clean_data)
    
    # 3. Reconstruct standard PEM format (64 chars per line)
    formatted_key = "-----BEGIN PRIVATE KEY-----\n"
    for i in range(0, len(clean_data), 64):
        formatted_key += clean_data[i:i+64] + "\n"
    formatted_key += "-----END PRIVATE KEY-----\n"
    return formatted_key


def _get_client():
    if not GSPREAD_AVAILABLE:
        raise ImportError("gspread not installed. Run: pip install gspread google-auth")
    
    base64_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64", "")
    creds_dict = None
    
    # 1. Try file
    if os.path.exists("google-service-account.json"):
        try:
            with open("google-service-account.json", "r") as f:
                creds_dict = json.load(f)
                print("DEBUG: Using google-service-account.json file")
        except Exception as e:
            print(f"DEBUG: File load failed: {e}")
            
    # 2. Try Base64 Env
    if not creds_dict and base64_str:
        try:
            import base64
            json_str = base64.b64decode(base64_str).decode("utf-8")
            creds_dict = json.loads(json_str)
            print("DEBUG: Using Base64 environment credentials")
        except Exception as e:
            print(f"DEBUG: Base64 decode failed: {e}")
            
    # 3. Try Regular Env
    if not creds_dict and SHEETS_SERVICE_ACCOUNT_JSON:
        try:
            json_str = SHEETS_SERVICE_ACCOUNT_JSON.strip()
            if (json_str.startswith("'") and json_str.endswith("'")) or (json_str.startswith('"') and json_str.endswith('"')):
                json_str = json_str[1:-1]
            creds_dict = json.loads(json_str)
            print("DEBUG: Using regular JSON environment credentials")
        except Exception as e:
            print(f"DEBUG: Regular JSON parse failed: {e}")

    if not creds_dict:
        raise ValueError("No valid Google Service Account credentials found (file or environment)")

    # Aggressively clean the private key regardless of source
    if "private_key" in creds_dict:
        creds_dict["private_key"] = _clean_private_key(creds_dict["private_key"])
    
    try:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
        )
        client = gspread.authorize(creds)
        print("DEBUG: Successfully authorized with Google Sheets API")
        return client
    except Exception as e:
        print(f"DEBUG: Final authorization failed: {str(e)}")
        raise RuntimeError(f"Google Sheets Authentication Failed: {str(e)}")


def _get_worksheet(sheet_url: Optional[str] = None):
    """Helper to get authorized worksheet with robust URL/Key handling."""
    client = _get_client()
    url = sheet_url or SHEET_URL
    if not url:
        raise ValueError("No sheet URL provided")
    
    # Try opening by URL, fallback to ID extraction
    try:
        sheet = client.open_by_url(url)
    except Exception:
        # Extract ID from URL: .../d/ID/...
        import re
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if match:
            sheet_id = match.group(1)
            sheet = client.open_by_key(sheet_id)
        else:
            raise
            
    return sheet.sheet1


def read_leads_from_sheet(sheet_url: Optional[str] = None) -> list[dict]:
    """Read leads from the configured Google Sheet. Returns list of lead dicts."""
    worksheet = _get_worksheet(sheet_url)
    rows = worksheet.get_all_records(expected_headers=HEADERS)
    
    leads = []
    for row in rows:
        lead = {k: row.get(k, "") for k in REQUIRED_INPUT_COLS}
        if lead.get("name") or lead.get("company"):
            leads.append(lead)
    
    return leads


def read_unprocessed_leads(sheet_url: Optional[str] = None) -> list[dict]:
    """Read only leads that haven't been processed (tier column empty)."""
    worksheet = _get_worksheet(sheet_url)
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
    worksheet = _get_worksheet(sheet_url)
    
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
    worksheet = _get_worksheet(sheet_url)
    worksheet.update("A1:P1", [HEADERS])
    
    for col in ["A", "B", "C", "D", "E", "F"]:
        worksheet.format(f"{col}1", {"textFormat": {"bold": True}})
    
    worksheet.set_basic_filter(1, 1, 1, len(HEADERS))
    
    return f"Formatted sheet at {url}"


if __name__ == "__main__":
    print("Sheets integration module loaded.")
    print(f"Gspread available: {GSPREAD_AVAILABLE}")
    print(f"Sheet URL configured: {bool(SHEET_URL)}")