"""
schemas/validator.py — Post-pipeline validation logic

Validates lead input and SDR output after pipeline runs.
"""

import re
from typing import Dict, List, Optional, Any
from schemas.lead import ValidationResult


EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
}


def validate_lead_input(lead: dict) -> ValidationResult:
    """
    Validate lead input fields (before pipeline runs).
    
    Args:
        lead: Raw lead dict
    
    Returns:
        ValidationResult with any errors/warnings
    """
    result = ValidationResult()
    
    # Check required fields
    if not lead.get("company"):
        result.add_error("company", "Company is required")
    if not lead.get("city"):
        result.add_error("city", "City is required")
    if not lead.get("state"):
        result.add_error("state", "State is required")
    
    # Validate state format
    state = lead.get("state", "").strip().upper()
    if state and state not in US_STATES:
        result.add_error("state", f"Invalid state code: {state}. Must be 2-letter US code.")
    
    # Validate email format
    email = lead.get("email", "").strip() if lead.get("email") else ""
    if email and not re.match(EMAIL_REGEX, email):
        result.add_error("email", f"Invalid email format: {email}")
    
    # Warnings for missing optional fields
    if not lead.get("name"):
        result.add_warning("No contact name provided")
    if not lead.get("property_address"):
        result.add_warning("No property address provided")
    
    return result


def validate_pipeline_output(result: dict, lead: dict) -> ValidationResult:
    """
    Validate SDR output after pipeline runs.
    
    Args:
        result: Pipeline result dict
        lead: Original lead dict
    
    Returns:
        ValidationResult with any errors/warnings
    """
    result_validation = ValidationResult()
    
    # Validate lead input first
    input_validation = validate_lead_input(lead)
    if not input_validation.is_valid:
        for field in input_validation.failed_fields:
            error_msg = next((e for e in input_validation.errors if field in e), "")
            result_validation.add_error(field, error_msg or "Invalid")
        for warning in input_validation.warnings:
            result_validation.add_warning(warning)
    
    # Check SDR output critical fields
    if not result.get("tier"):
        result_validation.add_error("tier", "Pipeline did not return a tier")
    elif result.get("tier") in ["C", "NEEDS_REVIEW"]:
        result_validation.add_warning(f"Tier {result.get('tier')} may indicate data quality issues")
    
    if not result.get("priority_score"):
        result_validation.add_error("priority_score", "No priority score returned")
    
    if not result.get("score_rationale"):
        result_validation.add_warning("No score rationale provided")
    
    # Check buying signals (optional but recommended)
    buying_signals = result.get("buying_signals", {})
    if not buying_signals:
        result_validation.add_warning("No buying signals detected")
    
    # Check talking points
    talking_points = result.get("talking_points", [])
    if not talking_points or len(talking_points) < 3:
        result_validation.add_warning("Less than 3 talking points generated")
    
    # Check email draft
    email_draft = result.get("email_draft")
    if not email_draft:
        result_validation.add_warning("No email draft generated")
    
    # Check for API errors
    api_errors = result.get("_api_errors", [])
    if api_errors:
        result_validation.add_warning(f"API errors: {', '.join(api_errors[:2])}")
    
    return result_validation


def apply_validation_to_result(result: dict, lead: dict) -> dict:
    """
    Apply validation to pipeline result and mark invalid leads.
    
    Args:
        result: Pipeline result
        lead: Original lead
    
    Returns:
        Modified result with _validation attached
    """
    validation = validate_pipeline_output(result, lead)
    
    # Attach validation to result
    result["_validation"] = {
        "is_valid": validation.is_valid,
        "errors": validation.errors,
        "warnings": validation.warnings,
        "failed_fields": validation.failed_fields,
        "quality_score": validation.quality_score,
    }
    
    # Mark for manual review if invalid
    if not validation.is_valid:
        result["_needs_manual_review"] = True
        
        # Override tier to NEEDS_REVIEW if lead validation failed
        if "company" in validation.failed_fields or "city" in validation.failed_fields or "state" in validation.failed_fields:
            result["tier"] = "NEEDS_REVIEW"
            result["priority_score"] = 0
    
    # Add quality grade
    if validation.quality_score >= 90:
        result["_validation"]["quality_grade"] = "A"
    elif validation.quality_score >= 70:
        result["_validation"]["quality_grade"] = "B"
    elif validation.quality_score >= 50:
        result["_validation"]["quality_grade"] = "C"
    else:
        result["_validation"]["quality_grade"] = "D"
    
    return result


def get_validation_summary(results: List[dict]) -> dict:
    """
    Get summary statistics for a batch of results.
    
    Args:
        results: List of pipeline results
    
    Returns:
        Summary dict with counts
    """
    total = len(results)
    valid = sum(1 for r in results if r.get("_validation", {}).get("is_valid", True))
    invalid = total - valid
    needs_review = sum(1 for r in results if r.get("_needs_manual_review", False))
    
    return {
        "total": total,
        "valid": valid,
        "invalid": invalid,
        "needs_review": needs_review,
        "validation_rate": round(valid / total * 100, 1) if total > 0 else 0,
    }