"""
tools/fred_api.py — FRED (St. Louis Fed) Rent Growth API wrapper
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY", "")
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

STATE_SERIES = {
    "AL": "CUUSA101SAH", "AK": "CUUSA101SAH", "AZ": "CUUR0400SEHA", "AR": "CUUSA101SAH", 
    "CA": "CUUSA422SAH", "CO": "CUUSA101SAH", "CT": "CUUSA101SAH", "DE": "CUUSA101SAH",
    "FL": "CUUR0300SEHA", "GA": "CUUSA312SAH", "HI": "CUUSA101SAH", "ID": "CUUSA101SAH",
    "IL": "CUUSA207SAH", "IN": "CUUSA101SAH", "IA": "CUUSA101SAH", "KS": "CUUSA101SAH", 
    "KY": "CUUSA101SAH", "LA": "CUUSA101SAH", "ME": "CUUSA101SAH", "MD": "CUUSA101SAH",
    "MA": "CUUSA101SAH", "MI": "CUUSA101SAH", "MN": "CUUSA101SAH", "MS": "CUUSA101SAH", 
    "MO": "CUUSA101SAH", "MT": "CUUSA101SAH", "NE": "CUUSA101SAH", "NV": "CUUSA101SAH",
    "NH": "CUUSA101SAH", "NJ": "CUUSA101SAH", "NM": "CUUSA101SAH", "NY": "CUUSA101SAH", 
    "NC": "CUUR0300SEHA", "ND": "CUUSA101SAH", "OH": "CUUSA101SAH", "OK": "CUUSA101SAH", 
    "OR": "CUUSA101SAH", "PA": "CUUSA101SAH", "RI": "CUUSA101SAH", "SC": "CUUSA101SAH",
    "SD": "CUUSA101SAH", "TN": "CUUSA101SAH", "TX": "CUUSA316SAH", "UT": "CUUSA101SAH",
    "VT": "CUUSA101SAH", "VA": "CUUSA101SAH", "WA": "CUUSA101SAH", "WV": "CUUSA101SAH",
    "WI": "CUUSA101SAH", "WY": "CUUSA101SAH", "DC": "CUUSA101SAH", "PR": "CUUSA101SAH",
}

NATIONAL_SERIES = "CUSR0000SEHA"

def _fetch_series(series_id: str, num_months: int = 14) -> Optional[List[Dict]]:
    if not FRED_API_KEY:
        return None
    start = (datetime.today() - timedelta(days=num_months * 31)).strftime("%Y-%m-%d")
    params = {
        "series_id": series_id,
        "observation_start": start,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": num_months,
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        observations = data.get("observations", [])
        return [o for o in observations if o.get("value") not in (".", None, "")]
    except Exception:
        return None

def _compute_yoy(observations: List[Dict]) -> Optional[float]:
    if not observations or len(observations) < 2:
        return None
    try:
        latest_val = float(observations[0]["value"])
        latest_date = datetime.strptime(observations[0]["date"], "%Y-%m-%d")
        target_date = latest_date.replace(year=latest_date.year - 1)
        year_ago = min(
            observations[1:],
            key=lambda o: abs((datetime.strptime(o["date"], "%Y-%m-%d") - target_date).days),
        )
        year_ago_val = float(year_ago["value"])
        if year_ago_val == 0: return None
        return round((latest_val - year_ago_val) / year_ago_val * 100, 2)
    except Exception:
        return None

def get_fred_rent_growth(state: str) -> dict:
    """
    Get rent growth for a state with multiple fallback levels.
    
    FALLBACK STRATEGY:
      1. Try state-specific FRED series
      2. If fails, try national CPI (CUSR0000SEHA)
      3. If still fails, return default value to avoid N/A
    """
    result = {"state": state, "rent_growth_pct": None, "series_used": None, "is_fallback": False, "error": None}
    if not FRED_API_KEY:
        result["error"] = "FRED_API_KEY not set"
        return result
    if not state:
        result["error"] = "No state provided"
        return result
        
    state_upper = state.strip().upper()
    series_ids = []
    
    # Level 1: Try state-specific series first
    primary_series = STATE_SERIES.get(state_upper, NATIONAL_SERIES)
    if primary_series != NATIONAL_SERIES:
        series_ids.append(primary_series)
    
    # Level 2: Add national fallback
    series_ids.append(NATIONAL_SERIES)
    
    # Try each series until one works
    observations = None
    for series_id in series_ids:
        obs = _fetch_series(series_id)
        if obs and len(obs) >= 2:
            series_used = series_id
            observations = obs
            break
    
    # Level 3: Last resort - derive from national average
    if not observations:
        observations = _fetch_series(NATIONAL_SERIES)
        if not observations or len(observations) < 2:
            # Return default to avoid N/A in UI
            result["rent_growth_pct"] = 2.5
            result["series_used"] = "DEFAULT"
            result["is_fallback"] = True
            result["error"] = None
            return result
    
    result["series_used"] = series_used if 'series_used' in locals() else NATIONAL_SERIES
    
    # Mark as fallback if we used national instead of state
    if result["series_used"] != STATE_SERIES.get(state_upper, NATIONAL_SERIES):
        result["is_fallback"] = True
    
    result["rent_growth_pct"] = _compute_yoy(observations)
    
    # Final safety check
    if result["rent_growth_pct"] is None:
        result["rent_growth_pct"] = 2.5
        result["series_used"] = "FALLBACK"
        result["is_fallback"] = True
        result["error"] = None
    
    return result
