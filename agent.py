"""
agent.py — Lead enrichment pipeline using Groq (Llama 3.3).

Architecture:
  1. Python fetches all 3 APIs directly (Census, FRED, News) — no LLM involved.
  2. Real API data is injected into the prompt as a verified data block.
  3. Groq/Llama reasons ONLY on the real data — no hallucination possible.
  4. Returns structured JSON + the raw tool results for UI transparency.

Model: llama-3.3-70b-versatile (free tier)
"""

import json
import os
import re
from groq import Groq
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT
from tools.census_api import get_census_data
from tools.fred_api import get_fred_rent_growth
from tools.news_api import get_company_news

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY", "").strip())
MODEL = "llama-3.1-8b-instant"


def _fetch_all_data(lead: dict, progress_callback=None) -> dict:
    """Run all 3 API calls in Python. Returns raw results dict."""
    raw = {}

    if progress_callback:
        progress_callback("Fetching Census data (renter %, vacancy)...")
    raw["census"] = get_census_data(
        city=lead.get("city", ""),
        state=lead.get("state", ""),
        address=lead.get("property_address"),
    )

    if progress_callback:
        progress_callback("Fetching FRED rent growth data...")
    raw["fred"] = get_fred_rent_growth(state=lead.get("state", ""))

    if progress_callback:
        progress_callback("Fetching company news & Wikipedia summary...")
    raw["news"] = get_company_news(
        company=lead.get("company", ""),
        city=lead.get("city", ""),
    )

    return raw


def _generate_sales_signal(raw: dict) -> str:
    """Extracts 'Sales Signals' from raw JSON into a dense, single-paragraph string."""
    census = raw.get("census", {})
    fred = raw.get("fred", {})
    news = raw.get("news", {})

    parts = []
    
    # 1. Market Data
    market_parts = []
    renter = census.get("renter_pct")
    if renter: market_parts.append(f"{renter}% renters")
    vacancy = census.get("vacancy_rate")
    if vacancy is not None: market_parts.append(f"{vacancy}% vacancy")
    income = census.get("median_income")
    if income: market_parts.append(f"${income/1000:.1f}k income")
    
    if market_parts:
        parts.append("Market: " + ", ".join(market_parts))

    # 2. Trend Data
    growth = fred.get("rent_growth_pct")
    if growth:
        parts.append(f"Trend: {growth}% rent growth")

    # 3. News Data
    headlines = news.get("company_headlines", [])
    if headlines:
        news_str = ", ".join(f"{h.get('title')} ({h.get('date')})" if h.get('date') else h.get('title') for h in headlines[:2])
        parts.append(f"News: {news_str}")
        
    signal = "; ".join(parts)
    return signal if signal else "Signal: Insufficient data."

def _build_data_block(lead: dict, raw: dict, signal: str) -> str:
    """
    Format the real API results as a ground-truth block to inject into the prompt.
    Passes the dense sales signal string for cleaner LLM processing.
    """
    return f"""You are analyzing a lead for EliseAI. Use ONLY the data below. Produce the JSON output.

LEAD:
  Name: {lead.get('name', 'Unknown')}
  Email: {lead.get('email', 'Unknown')}
  Company: {lead.get('company', 'Unknown')}
  Property Address: {lead.get('property_address', 'Unknown')}, {lead.get('city', 'Unknown')}, {lead.get('state', 'Unknown')}

SALES SIGNAL:
  {signal}

RULES:
- Do NOT invent numbers, unit counts, or funding details not listed above.
- Use null for any missing value — never guess.
- The email must ONLY reference facts from above.
- Copy key_data_points values EXACTLY from this data.
"""


def enrich_lead(lead: dict, progress_callback=None) -> dict:
    """
    Run the full enrichment pipeline for one lead.

    Returns:
        dict with keys: tier, score_rationale, email_draft, talking_points,
        key_data_points, estimated_time_saved_minutes, _raw_data (for UI display).
    """
    # Step 1: Fetch all real data in Python
    raw = _fetch_all_data(lead, progress_callback)

    # Step 2: Build the sales signal and verified data block
    signal = _generate_sales_signal(raw)
    data_block = _build_data_block(lead, raw, signal)

    if progress_callback:
        progress_callback("Reasoning about ICP fit and drafting email...")

    # Step 3: Ask Groq to reason on the real data only (no tools)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": data_block},
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=1024,
            temperature=0.1,  # low temp for consistency
        )
        text = (response.choices[0].message.content or "").strip()
    except Exception as e:
        return {"error": f"Groq API call failed: {e}", "_raw_data": raw}

    # Step 4: Parse JSON from response
    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]).strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # Try to extract the outermost JSON object
        # Use a breadth-first approach: find the first '{' and the matching '}'
        start = text.find('{')
        if start != -1:
            depth = 0
            end = -1
            for i, ch in enumerate(text[start:], start):
                if ch == '{': depth += 1
                elif ch == '}': 
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            if end != -1:
                try:
                    result = json.loads(text[start:end+1])
                except json.JSONDecodeError:
                    result = {"error": "Agent returned malformed JSON", "raw": text[:500]}
            else:
                result = {"error": "No closing brace found in response", "raw": text[:500]}
        else:
            result = {"error": "No JSON found in response", "raw": text[:500]}

    # Step 5: Attach raw data for UI transparency
    result["_raw_data"] = raw
    result["sales_signal"] = signal

    # Ensure key_data_points is populated from real data if LLM left nulls
    kdp = result.get("key_data_points", {})
    census = raw.get("census", {})
    fred = raw.get("fred", {})
    kdp.setdefault("renter_pct", census.get("renter_pct"))
    kdp.setdefault("vacancy_rate", census.get("vacancy_rate"))
    kdp.setdefault("rent_growth_pct", fred.get("rent_growth_pct"))
    kdp.setdefault("median_income", census.get("median_income"))
    kdp.setdefault("total_renter_units", census.get("total_renter_units"))
    news = raw.get("news", {})
    headlines = news.get("company_headlines", [])
    if headlines and not kdp.get("top_news_headline"):
        kdp["top_news_headline"] = headlines[0].get("title")
    result["key_data_points"] = kdp

    return result


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = {
        "name": "Sarah Chen",
        "email": "s.chen@greystar.com",
        "company": "Greystar",
        "property_address": "450 W 33rd St",
        "city": "Austin",
        "state": "TX",
    }

    print(f"Enriching lead: {sample['name']} at {sample['company']} (via Groq)...")
    result = enrich_lead(sample, progress_callback=lambda s: print(f"  -> {s}"))
    # Don't print _raw_data in CLI (verbose)
    display = {k: v for k, v in result.items() if k != "_raw_data"}
    print(json.dumps(display, indent=2))
    print("\n--- Raw API Data ---")
    print(json.dumps(result.get("_raw_data", {}), indent=2))
