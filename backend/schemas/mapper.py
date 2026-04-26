"""
schemas/mapper.py — Column name mappings for different input sources

Normalizes lead data from CSV, Google Sheets, Salesforce, API to standard format.
"""

from typing import Dict, Optional
from schemas.lead import LeadInput


COLUMN_MAPPINGS: Dict[str, Dict[str, str]] = {
    "csv_standard": {
        "First Name": "name",
        "Last Name": "last_name",
        "Email": "email",
        "Company": "company",
        "Property Address": "property_address",
        "City": "city",
        "State": "state",
        "Zip": "zip",
    },
    "sheet_v1": {
        "company_name": "company",
        "city_location": "city",
        "st": "state",
        "address": "property_address",
        "zip_code": "zip",
        "contact_name": "name",
        "contact_email": "email",
    },
    "sheet_v2": {
        "Company": "company",
        "City": "city",
        "State": "state",
        "Address": "property_address",
        "Zip": "zip",
        "Name": "name",
        "Email": "email",
    },
    "salesforce": {
        "Company": "company",
        "BillingCity": "city",
        "BillingState": "state",
        "BillingAddress": "property_address",
        "BillingPostalCode": "zip",
        "FirstName": "name",
        "LastName": "last_name",
        "Email": "email",
        "Phone": "phone",
    },
    "hubspot": {
        "company": "company",
        "city": "city",
        "state": "state",
        "address": "property_address",
        "zip": "zip",
        "firstname": "name",
        "email": "email",
        "phone": "phone",
    },
    "api": {},  # Direct pass-through
}


def normalize_lead(data: dict, source: str = "api") -> dict:
    """
    Normalize lead data from any source to standard format.
    
    Args:
        data: Raw lead data dict
        source: Source type (csv/sheet/salesforce/hubspot/api)
    
    Returns:
        Normalized dict ready for LeadInput
    """
    mapping = COLUMN_MAPPINGS.get(source, COLUMN_MAPPINGS["api"])
    
    normalized = {}
    for input_key, output_key in mapping.items():
        if input_key in data and data[input_key]:
            value = data[input_key]
            if isinstance(value, str):
                value = value.strip()
            if output_key == "name" and input_key in ["First Name", "Last Name", "firstname", "LastName"]:
                first = data.get("First Name") or data.get("firstname") or ""
                last = data.get("Last Name") or data.get("lastname") or ""
                normalized["name"] = f"{first} {last}".strip()
            else:
                normalized[output_key] = value
    
    # Pass through any unmapped fields that are already correct
    for key in ["company", "city", "state", "name", "email", "property_address", "phone", "zip"]:
        if key in data and key not in normalized:
            value = data.get(key)
            if isinstance(value, str):
                value = value.strip()
            if value:
                normalized[key] = value
    
    normalized["source"] = source
    normalized["original_data"] = data
    
    return normalized


def detect_source_from_columns(columns: list[str]) -> str:
    """
    Auto-detect source type from column headers.
    
    Args:
        columns: List of column names from input
    
    Returns:
        Source type string
    """
    col_lower = [c.lower() for c in columns]
    
    if "first name" in col_lower and "last name" in col_lower:
        return "csv_standard"
    if "company" in col_lower and "billingcity" in col_lower:
        return "salesforce"
    if "firstname" in col_lower:
        return "hubspot"
    if "company_name" in col_lower or "city_location" in col_lower:
        return "sheet_v1"
    
    return "api"


def get_required_columns(source: str = "api") -> list[str]:
    """Get required columns for a source type."""
    if source == "api":
        return ["company", "city", "state"]
    return ["company", "city", "state"]