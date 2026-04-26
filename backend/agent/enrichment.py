"""
agent/enrichment.py — Adaptive Enrichment Executor

Runs API calls based on strategy (A/B/C) with parallel execution.
Strategy A: Census + FRED + News + WalkScore + DDG (parallel)
Strategy B: Census + News + WalkScore (parallel)
Strategy C: Census + WalkScore (parallel)
"""

import concurrent.futures
from typing import Optional, Callable

from tools.census_api import get_census_data
from tools.fred_api import get_fred_rent_growth
from tools.news_api import get_company_news
from tools.walkscore_api import get_walkscore_data
from tools.ddg_search import search_comprehensive


def _call_census(lead: dict) -> dict:
    return get_census_data(
        city=lead.get("city", ""),
        state=lead.get("state", ""),
        address=lead.get("property_address"),
    )


def _call_fred(lead: dict) -> dict:
    return get_fred_rent_growth(state=lead.get("state", ""))


def _call_news(lead: dict) -> dict:
    return get_company_news(
        company=lead.get("company", ""),
        city=lead.get("city", ""),
    )


def _call_walkscore(lead: dict) -> dict:
    return get_walkscore_data(
        address=lead.get("property_address", ""),
        city=lead.get("city", ""),
        state=lead.get("state", ""),
    )


def _call_ddg(lead: dict) -> dict:
    return search_comprehensive(
        company=lead.get("company", ""),
        city=lead.get("city", ""),
        state=lead.get("state", ""),
    )


def execute_enrichment(
    lead: dict,
    apis_to_call: list[str],
    progress_callback: Optional[Callable] = None
) -> dict:
    """
    Execute enrichment based on the APIs needed.
    Uses ThreadPoolExecutor for parallel execution.
    
    Args:
        lead: dict with keys: company, city, state, property_address
        apis_to_call: list of APIs to invoke
        progress_callback: optional function to report progress
    
    Returns:
        dict with keys: census, fred, news, walkscore, ddg, quality_meta
    """
    results = {}
    quality_meta = {
        "apis_called": len(apis_to_call),
        "apis_succeeded": 0,
        "apis_failed": 0,
    }
    
    # Map API names to functions
    api_functions = {
        "census": _call_census,
        "fred": _call_fred,
        "news": _call_news,
        "walkscore": _call_walkscore,
        "ddg": _call_ddg,
    }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(apis_to_call)) as executor:
        futures = {}
        
        for api_name in apis_to_call:
            if api_name in api_functions:
                if progress_callback:
                    progress_callback(f"Fetching {api_name} data...")
                futures[api_name] = executor.submit(api_functions[api_name], lead)
        
        for api_name, future in futures.items():
            try:
                results[api_name] = future.result(timeout=30)
                quality_meta["apis_succeeded"] += 1
            except Exception as e:
                results[api_name] = {"error": str(e)}
                quality_meta["apis_failed"] += 1
    
    results["quality_meta"] = quality_meta
    return results


def get_enrichment_quality(enriched: dict) -> str:
    """
    Assess the quality of enrichment data.
    Returns: "high", "medium", "low", or "insufficient"
    """
    census = enriched.get("census", {})
    fred = enriched.get("fred", {})
    news = enriched.get("news", {})
    walkscore = enriched.get("walkscore", {})
    ddg = enriched.get("ddg", {})
    
    score = 0
    
    # Core Census data (most important)
    if census.get("renter_pct") is not None:
        score += 2
    if census.get("vacancy_rate") is not None:
        score += 1
    if census.get("median_income") is not None:
        score += 1
    
    # FRED
    if fred.get("rent_growth_pct") is not None:
        score += 1
    
    # News/Wikipedia
    if news.get("company_summary") is not None:
        score += 1
    if news.get("company_headlines"):
        score += 1
    
    # WalkScore
    if walkscore.get("walkscore") is not None:
        score += 1
    
    # DuckDuckGo
    ddg_results = ddg.get("company_results", []) or ddg.get("market_results", [])
    if ddg_results:
        score += 1
    
    if score >= 6:
        return "high"
    elif score >= 4:
        return "medium"
    elif score >= 2:
        return "low"
    return "insufficient"


if __name__ == "__main__":
    test_lead = {
        "name": "Sarah Chen",
        "email": "s.chen@greystar.com",
        "company": "Greystar",
        "property_address": "450 W 33rd St",
        "city": "Austin",
        "state": "TX",
    }
    
    print("=== Enrichment Executor Test ===\n")
    
    for strategy in ["A", "B", "C"]:
        apis = {
            "A": ["census", "fred", "news", "walkscore", "ddg"],
            "B": ["census", "news", "walkscore"],
            "C": ["census", "walkscore"],
        }[strategy]
        
        print(f"Strategy {strategy} ({', '.join(apis)})...")
        result = execute_enrichment(test_lead, apis)
        quality = get_enrichment_quality(result)
        print(f"  Quality: {quality}")
        print(f"  Census: renter_pct={result['census'].get('renter_pct')}")
        if "fred" in result:
            print(f"  FRED: rent_growth={result['fred'].get('rent_growth_pct')}")
        if "news" in result:
            print(f"  News: {result['news'].get('company_summary', 'None')[:50]}...")
        if "walkscore" in result:
            print(f"  WalkScore: {result['walkscore'].get('walkscore')}")
        if "ddg" in result:
            print(f"  DDG: {len(result['ddg'].get('company_results', []))} company results")
        print()