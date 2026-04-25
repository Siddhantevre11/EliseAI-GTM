"""
tools/walkscore_api.py — WalkScore API Integration

Fetches Walk Score, Transit Score, and Bike Score for property addresses.
Uses geopy to get lat/lon, then calls WalkScore API.
"""

import os
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

WALK_SCORE_API_KEY = os.getenv("WALK_SCORE_API_KEY", "")
WALK_SCORE_API_KEY = os.getenv("WALK_SCORE_API", WALK_SCORE_API_KEY)
BASE_URL = "https://api.walkscore.com/score"

# Transit description mapping
TRANSIT_TYPES = {
    1: "None",
    2: "Minimal",
    3: "Some",
    4: "Good",
    5: "Excellent",
}

BIKE_TYPES = {
    1: "Minimal",
    2: "Some",
    3: "Very Bikeable",
}


def _geocode_address(address: str, city: str, state: str) -> Optional[tuple]:
    """Get lat/lon from address using geopy."""
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    
    geolocator = Nominatim(user_agent="EliseAI-Enrichment")
    full_address = f"{address}, {city}, {state}, USA"
    
    try:
        location = geolocator.geocode(full_address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
    except (GeocoderTimedOut, GeocoderUnavailable):
        pass
    
    # Fallback: try just city, state
    try:
        location = geolocator.geocode(f"{city}, {state}, USA", timeout=10)
        if location:
            return (location.latitude, location.longitude)
    except (GeocoderTimedOut, GeocoderUnavailable):
        pass
    
    return None


def get_walkscore_data(address: str, city: str, state: str) -> dict:
    """
    Get walk, transit, and bike scores for a property address.
    
    Returns:
        {
            "walkscore": int,
            "transitscore": int, 
            "bikescore": int,
            "walk_description": str,
            "transit_description": str,
            "bike_description": str,
            "error": None or str
        }
    """
    result = {
        "address": address,
        "city": city,
        "state": state,
        "walkscore": None,
        "transitscore": None,
        "bikescore": None,
        "walk_description": None,
        "transit_description": None,
        "bike_description": None,
        "error": None,
    }

    if not WALK_SCORE_API_KEY:
        result["error"] = "WalkScore API key not set"
        return result

    # Step 1: Get lat/lon from address
    coords = _geocode_address(address, city, state)
    if not coords:
        result["error"] = "Could not geocode address to lat/lon"
        return result
    
    lat, lon = coords

    # Step 2: Call WalkScore API
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "address": f"{address}, {city}, {state}",
        "transit": 1,
        "bike": 1,
        "wsapikey": WALK_SCORE_API_KEY,
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()

        # Check for API error codes
        status_code = data.get("status")
        if status_code == 30:
            result["error"] = "Invalid lat/lon - location not found"
            return result
        elif status_code == 40:
            result["error"] = "Invalid API key"
            return result
        elif status_code == 41:
            result["error"] = "WalkScore daily quota exceeded"
            return result
        elif status_code not in (1, 2):
            result["error"] = f"WalkScore API error: {status_code}"
            return result

        # Walk Score
        ws = data.get("walkscore")
        if ws is not None:
            result["walkscore"] = int(ws)
            result["walk_description"] = data.get("description", "")

        # Transit Score
        transit = data.get("transit")
        if transit and transit.get("score") is not None:
            result["transitscore"] = int(transit["score"])
            trans_type = transit.get("transit_type", 1)
            result["transit_description"] = TRANSIT_TYPES.get(trans_type, "Unknown")

        # Bike Score  
        bike = data.get("bike")
        if bike and bike.get("score") is not None:
            result["bikescore"] = int(bike["score"])
            result["bike_description"] = bike.get("description", "")

    except requests.exceptions.Timeout:
        result["error"] = "WalkScore API timeout"
    except requests.exceptions.RequestException as e:
        result["error"] = f"WalkScore API error: {str(e)}"
    except Exception as e:
        result["error"] = f"WalkScore error: {str(e)}"

    return result


def get_walkscore_synced(address: str, city: str, state: str) -> dict:
    """Synchronous wrapper for get_walkscore_data."""
    return get_walkscore_data(address, city, state)


if __name__ == "__main__":
    test = get_walkscore_data("450 W 33rd St", "Austin", "TX")
    print(test)