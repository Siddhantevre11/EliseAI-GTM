"""
tools/census_api.py — US Census ACS 5-Year Estimates

Pulls renter occupancy %, median household income, total renter-occupied units,
and rental vacancy rate for a given city + state.

Uses Geopy + AddFIPS to resolve city/state -> County FIPS, with a fallback
to the Census Geocoder API.
"""

import os
import requests
from typing import Optional, Tuple, Dict, List
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from addfips import AddFIPS

load_dotenv()

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")
BASE_URL = "https://api.census.gov/data/2022/acs/acs5"
GEO_URL = "https://geocoding.geo.census.gov/geocoder/geographies/address"

# Initialize Geopy and AddFIPS
geolocator = Nominatim(user_agent="elise_ai_enrichment_agent")
af = AddFIPS()


def _get_state_fips(state: str) -> Optional[str]:
    """Get state FIPS code from state abbreviation."""
    STATE_FIPS = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
        "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
        "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
        "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
        "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
        "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
        "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
        "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
        "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
        "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
        "DC": "11", "PR": "72",
    }
    return STATE_FIPS.get(state.strip().upper(), None)


def _query_acs_state(variables: List[str], state_fips: str) -> Optional[Dict]:
    """Query ACS 5-year estimates for entire state."""
    params = {
        "get": ",".join(["NAME"] + variables),
        "for": f"state:{state_fips}",
        "key": CENSUS_API_KEY,
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        rows = r.json()
        if len(rows) < 2:
            return None
        headers = rows[0]
        values = rows[1]
        return dict(zip(headers, values))
    except Exception:
        return None


def _get_state_county_fips(city: str, state: str, address: Optional[str] = None) -> Optional[Tuple[str, str]]:
    """
    Resolve city/state (and optional address) to (state_fips, county_fips).
    Tries Geopy + AddFIPS first for robustness, falls back to Census Geocoder.
    """
    
    # 1. Try Geopy + AddFIPS (Robust for City/State)
    try:
        query = f"{city}, {state}, USA"
        location = geolocator.geocode(query, addressdetails=True, timeout=10)
        
        if location and 'address' in location.raw:
            addr = location.raw['address']
            county_name = addr.get('county')
            if county_name:
                # addfips handles the conversion
                fips = af.get_county_fips(county_name, state=state)
                if fips:
                    return fips[:2], fips[2:] # state_fips, county_fips
    except Exception:
        pass

    # 2. Fallback to Census Geocoder API (Good for specific street addresses)
    street = address if address else "1 Main St"
    params = {
        "street": street,
        "city": city,
        "state": state,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "layers": "Counties",
        "format": "json",
    }
    try:
        r = requests.get(GEO_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        matches = data.get("result", {}).get("addressMatches", [])
        
        if not matches and address:
            params["street"] = "1 Main St"
            r = requests.get(GEO_URL, params=params, timeout=10)
            data = r.json()
            matches = data.get("result", {}).get("addressMatches", [])

        if matches:
            geo = matches[0].get("geographies", {})
            counties = geo.get("Counties", [])
            if counties:
                county = counties[0]
                return county["STATE"], county["COUNTY"]
    except Exception:
        pass

    return None


def _query_acs(variables: List[str], state_fips: str, county_fips: str) -> Optional[Dict]:
    """Query ACS 5-year estimates for a set of variable codes."""
    params = {
        "get": ",".join(["NAME"] + variables),
        "for": f"county:{county_fips}",
        "in": f"state:{state_fips}",
        "key": CENSUS_API_KEY,
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        rows = r.json()
        if len(rows) < 2:
            return None
        headers = rows[0]
        values = rows[1]
        return dict(zip(headers, values))
    except Exception:
        return None


def get_census_data(city: str, state: str, address: Optional[str] = None) -> dict:
    """
    Main entry point. Returns dict with:
      renter_pct, owner_pct, median_income, total_renter_units,
      vacancy_rate, county_name, or error key on failure.
    
    FALLBACK STRATEGY:
      1. Try city+state -> county FIPS
      2. If city fails, try state-level data
      3. State-level also fails -> return error with no N/A in UI
    """
    result = {
        "city": city,
        "state": state,
        "renter_pct": None,
        "owner_pct": None,
        "median_income": None,
        "total_renter_units": None,
        "vacancy_rate": None,
        "county_name": None,
        "data_level": "county",
        "is_fallback": False,
        "error": None,
    }

    # Step 1: Try county-level first
    state_fips, county_fips = None, None
    fips = _get_state_county_fips(city, state, address)
    if fips:
        state_fips, county_fips = fips

    # ACS variable codes
    variables = [
        "B25003_001E",  # total occupied housing units
        "B25003_002E",  # owner-occupied
        "B25003_003E",  # renter-occupied
        "B19013_001E",  # median household income
        "B25004_006E",  # for-rent vacant units
        "B25004_001E",  # total vacant units
        "B25002_001E",  # total housing units
    ]

    # Step 2: Try state-level fallback if county failed
    if not state_fips:
        state_fips = _get_state_fips(state)
        if state_fips:
            data = _query_acs_state(variables, state_fips)
            if data:
                result["data_level"] = "state"
                result["county_name"] = f"{state.upper()} (State Average)"
                result["is_fallback"] = True
                result["error"] = None
                return _parse_acs_data(data, result)
        result["error"] = f"Could not geocode {city}, {state} and no state-level data available"
        result["renter_pct"] = 35.0
        result["vacancy_rate"] = 6.0
        result["is_fallback"] = True
        return result

    # Fetch county-level data
    data = _query_acs(variables, state_fips, county_fips)
    if not data:
        # Step 3: Fallback to state level
        if not state_fips:
            state_fips = _get_state_fips(state)
        if state_fips:
            data = _query_acs_state(variables, state_fips)
            if data:
                result["data_level"] = "state"
                result["county_name"] = f"{state.upper()} (State Average)"
                result["is_fallback"] = True
                result["error"] = None
                return _parse_acs_data(data, result)
        # Last resort: return default values
        result["error"] = f"No Census data available for {city}, {state}"
        result["renter_pct"] = 35.0
        result["vacancy_rate"] = 6.0
        result["is_fallback"] = True
        return result

    result["county_name"] = data.get("NAME", "")
    return _parse_acs_data(data, result)


def _parse_acs_data(data: Dict, result: dict) -> dict:
    """Parse ACS data into result dict. Shared by county and state queries."""
    try:
        total_occupied = int(data.get("B25003_001E") or 0)
        owner_occ = int(data.get("B25003_002E") or 0)
        renter_occ = int(data.get("B25003_003E") or 0)
        median_income = int(data.get("B19013_001E") or 0)
        for_rent_vacant = int(data.get("B25004_006E") or 0)

        result["total_renter_units"] = renter_occ
        result["median_income"] = median_income if median_income > 0 else None

        if total_occupied > 0:
            result["renter_pct"] = round(renter_occ / total_occupied * 100, 1)
            result["owner_pct"] = round(owner_occ / total_occupied * 100, 1)

        renal_universe = renter_occ + for_rent_vacant
        if renal_universe > 0:
            result["vacancy_rate"] = round(for_rent_vacant / renal_universe * 100, 1)

    except (ValueError, ZeroDivisionError) as e:
        result["error"] = f"Data parsing error: {e}"

    return result
