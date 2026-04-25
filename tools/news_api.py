"""
tools/news_api.py — NewsAPI + Wikipedia API Integration

Fetches company news (NewsAPI), Wikipedia company data (summary, logo, website, category),
and uses DuckDuckGo as additional search fallback.
"""

import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWSAPI_URL = "https://newsapi.org/v2/everything"
WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


def _fetch_newsapi(query: str, max_results: int = 3) -> List[Dict]:
    if not NEWS_API_KEY:
        return []
    params = {"q": query, "language": "en", "sortBy": "relevancy", "pageSize": max_results, "apiKey": NEWS_API_KEY}
    try:
        r = requests.get(NEWSAPI_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", [])
        return [{"title": a.get("title", ""), "source": a.get("source", {}).get("name", ""), "url": a.get("url", ""), "date": a.get("publishedAt", "")[:10]} for a in articles if a.get("title")]
    except Exception:
        return []


def _fetch_wikipedia_summary(company: str) -> Optional[Dict]:
    """
    Fetch enhanced Wikipedia data for a company.
    Returns: {summary, description, thumbnail_url, external_url, categories}
    """
    result = {
        "summary": None,
        "description": None,
        "thumbnail_url": None,
        "external_url": None,
        "industry_category": None,
    }
    
    title = company.strip().replace(" ", "_")
    
    # 1. Try REST API for summary
    try:
        r = requests.get(f"{WIKIPEDIA_SUMMARY_URL}/{title}", headers={"User-Agent": "EliseAI-Agent/1.0"}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            result["summary"] = ". ".join(data.get("extract", "").split(". ")[:2]) + "."
            result["description"] = data.get("description", "")
            # Thumbnail/logo
            thumb = data.get("thumbnail")
            if thumb:
                result["thumbnail_url"] = thumb.get("source")
    except Exception:
        pass
    
    # 2. Try Action API for external links and categories
    try:
        params = {
            "action": "query",
            "titles": title,
            "prop": "extlinks|categories",
            "format": "json",
            "exlimit": 5,
            "cllimit": 10,
        }
        r = requests.get(WIKIPEDIA_API_URL, params=params, timeout=8)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    continue
                # External links (website)
                extlinks = page_data.get("extlinks", {})
                for el in list(extlinks)[:1]:
                    result["external_url"] = el.get("*", "")
                # Categories (industry)
                categories = page_data.get("categories", {})
                cat_names = [c.get("title", "").replace("Category:", "") for c in categories if c.get("title")]
                if cat_names:
                    result["industry_category"] = ", ".join(cat_names[:2])
    except Exception:
        pass
    
    return result if any(result.values()) else None


def get_company_news(company: str, city: str) -> dict:
    """
    Get company news with enhanced Wikipedia data + DuckDuckGo fallback.
    
    FALLBACK STRATEGY:
      1. Try NewsAPI.org (requires API key)
      2. Always try Wikipedia for company summary, logo, website, industry
      3. Try DuckDuckGo if no results (will be added in enrichment)
    """
    result = {
        "company": company,
        "city": city,
        "company_headlines": [],
        "company_summary": None,
        "company_logo": None,
        "company_website": None,
        "industry_category": None,
        "error": None,
    }
    
    # Get enhanced Wikipedia data
    wiki_data = _fetch_wikipedia_summary(company)
    if wiki_data:
        result["company_summary"] = wiki_data.get("summary")
        result["company_logo"] = wiki_data.get("thumbnail_url")
        result["company_website"] = wiki_data.get("external_url")
        result["industry_category"] = wiki_data.get("industry_category")
    
    # Try NewsAPI if key exists
    if NEWS_API_KEY:
        headlines = _fetch_newsapi(f'"{company}" multifamily OR apartments')
        if headlines:
            result["company_headlines"] = headlines
        else:
            result["error"] = "NewsAPI returned no results"
    else:
        result["error"] = "NEWS_API_KEY not set"
    
    # Final fallback for summary if Wikipedia failed
    if not result["company_summary"]:
        result["company_summary"] = None  # Don't fabricate - return None
    
    return result
