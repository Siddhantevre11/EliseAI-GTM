"""
tools/ddg_search.py — DuckDuckGo Web Search Integration

Uses the duckduckgo Python package for free web search.
Provides company news, market information, and related articles.
"""

import os
from typing import Optional, List, Dict
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()


def search_company(company: str, max_results: int = 5) -> dict:
    """
    Search for company-related news and information.
    
    Returns:
        {
            "company": company name,
            "search_results": [
                {"title": str, "href": str, "body": str}
            ],
            "error": None or str
        }
    """
    result = {
        "company": company,
        "search_results": [],
        "error": None,
    }

    try:
        with DDGS() as ddgs:
            # Search for company + multifamily/news
            query = f"{company} multifamily apartments property management"
            results = list(ddgs.text(query, max_results=max_results))
            
            search_results = []
            for r in results:
                search_results.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")[:200] if r.get("body") else "",
                })
            
            result["search_results"] = search_results

    except Exception as e:
        result["error"] = f"DuckDuckGo search error: {str(e)}"

    return result


def search_market(city: str, state: str, max_results: int = 3) -> dict:
    """
    Search for market/rental market information.
    
    Returns:
        {
            "city": city,
            "state": state,
            "market_results": [...],
            "error": None or str
        }
    """
    result = {
        "city": city,
        "state": state,
        "market_results": [],
        "error": None,
    }

    try:
        with DDGS() as ddgs:
            query = f"{city} {state} rental market 2024 apartments vacancy"
            results = list(ddgs.text(query, max_results=max_results))
            
            market_results = []
            for r in results:
                market_results.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")[:200] if r.get("body") else "",
                })
            
            result["market_results"] = market_results

    except Exception as e:
        result["error"] = f"DuckDuckGo search error: {str(e)}"

    return result


def search_comprehensive(company: str, city: str, state: str) -> dict:
    """
    Run both company and market searches, combine results.
    
    Returns:
        {
            "company_results": [...],
            "market_results": [...],
            "error": None or str
        }
    """
    result = {
        "company_results": [],
        "market_results": [],
        "error": None,
    }

    # Company search
    company_results = search_company(company, max_results=5)
    result["company_results"] = company_results.get("search_results", [])
    
    # Market search
    market_results = search_market(city, state, max_results=3)
    result["market_results"] = market_results.get("market_results", [])

    # Track errors
    errors = []
    if company_results.get("error"):
        errors.append(company_results["error"])
    if market_results.get("error"):
        errors.append(market_results["error"])
    
    if errors:
        result["error"] = "; ".join(errors)

    return result


if __name__ == "__main__":
    # Test
    print("=== DuckDuckGo Search Test ===\n")
    
    r1 = search_company("Greystar", max_results=3)
    print(f"Company: {r1['company']}")
    print(f"Results: {len(r1['search_results'])} found")
    for res in r1["search_results"][:2]:
        print(f"  - {res['title'][:60]}")
    
    print()
    
    r2 = search_market("Austin", "TX", max_results=2)
    print(f"Market: {r2['city']}, {r2['state']}")
    print(f"Results: {len(r2['market_results'])} found")
    for res in r2["market_results"][:2]:
        print(f"  - {res['title'][:60]}")