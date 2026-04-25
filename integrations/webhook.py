"""
integrations/webhook.py — Webhook Integration for EliseAI GTM

Sends lead data to external webhook endpoints.
Requires: WEBHOOK_URL in .env
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY", "")
WEBHOOK_ENABLED = bool(WEBHOOK_URL)


def send_to_webhook(result: dict, lead: dict) -> Optional[dict]:
    """
    Send lead data to webhook endpoint.
    
    Args:
        result: Pipeline result
        lead: Original lead dict
    
    Returns:
        API response or None
    """
    if not WEBHOOK_ENABLED:
        return None
    
    # Build payload
    payload = {
        "lead": {
            "name": lead.get("name"),
            "email": lead.get("email"),
            "company": lead.get("company"),
            "property_address": lead.get("property_address"),
            "city": lead.get("city"),
            "state": lead.get("state"),
        },
        "enrichment": {
            "tier": result.get("tier"),
            "priority_score": result.get("priority_score"),
            "score_rationale": result.get("score_rationale"),
            "buying_signals": result.get("buying_signals"),
            "talking_points": result.get("talking_points"),
            "email_draft": result.get("email_draft"),
            "roi_estimate": result.get("roi_estimate"),
        },
        "market_data": result.get("key_data_points", {}),
        "_validation": result.get("_validation"),
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    if WEBHOOK_API_KEY:
        headers["Authorization"] = f"Bearer {WEBHOOK_API_KEY}"
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )
        return {
            "status_code": response.status_code,
            "success": response.ok,
            "text": response.text[:200] if response.text else None,
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "success": False}


def send_batch_to_webhook(results: list[dict]) -> Optional[dict]:
    """
    Send batch results to webhook.
    
    Args:
        results: List of pipeline results
    
    Returns:
        API response or None
    """
    if not WEBHOOK_ENABLED:
        return None
    
    # Build payload
    payload = {
        "batch": {
            "total": len(results),
            "tier_a": sum(1 for r in results if r.get("tier") == "A"),
            "tier_b": sum(1 for r in results if r.get("tier") == "B"),
            "tier_c": sum(1 for r in results if r.get("tier") == "C"),
            "needs_review": sum(1 for r in results if r.get("_needs_manual_review")),
        },
        "results": [
            {
                "lead": {
                    "company": r.get("_lead", {}).get("company"),
                    "city": r.get("_lead", {}).get("city"),
                    "state": r.get("_lead", {}).get("state"),
                },
                "tier": r.get("tier"),
                "priority_score": r.get("priority_score"),
                "buying_signals": r.get("buying_signals"),
            }
            for r in results
        ],
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    if WEBHOOK_API_KEY:
        headers["Authorization"] = f"Bearer {WEBHOOK_API_KEY}"
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )
        return {
            "status_code": response.status_code,
            "success": response.ok,
            "text": response.text[:200] if response.text else None,
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "success": False}


def test_webhook() -> Optional[dict]:
    """Test webhook connectivity."""
    if not WEBHOOK_ENABLED:
        return {"error": "WEBHOOK_URL not set"}
    
    payload = {"test": True, "message": "EliseAI GTM test"}
    
    headers = {"Content-Type": "application/json"}
    if WEBHOOK_API_KEY:
        headers["Authorization"] = f"Bearer {WEBHOOK_API_KEY}"
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )
        return {
            "status_code": response.status_code,
            "success": response.ok,
        }
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "success": False}


if __name__ == "__main__":
    print("Webhook integration loaded.")
    print(f"Enabled: {WEBHOOK_ENABLED}")
    print(f"URL: {WEBHOOK_URL[:50]}..." if WEBHOOK_URL else "URL: Not set")