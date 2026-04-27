"""
agent/pipeline.py — Unified GTM Engine Pipeline

Sequential pipeline:
1. ENRICHMENT: Fetch Census/FRED/News data (Python API calls, no LLM)
2. SCORING: Assign Tier A/B/C using LLM (temp: 0.0, model: 8b-instant)
3. OUTREACH: Generate email/talking points using LLM (temp: 0.5, model: 70b-versatile)
4. SYNC: Push to Slack + Sheets

All LLM interactions centralized via LLMRouter.
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Callable
from threading import Semaphore

from dotenv import load_dotenv

load_dotenv()

MAX_CONCURRENT_LEADS = int(os.getenv("MAX_CONCURRENT_LEADS", "3"))

# Import LLM tasks
from agent.tasks import execute_scoring_task, execute_outreach_task
from agent.tasks.scoring import _infer_tier, _infer_score, _build_decision_maker_context, _build_industry_benchmark
from agent.tasks.outreach import _build_objections, _build_roi, _build_case_study, _build_talking_points, _build_email_draft
from agent.llm_router import LLMRouter

# Import existing modules
from agent.router import route_lead_fast
from agent.enrichment import execute_enrichment
from schemas.validator import apply_validation_to_result
from integrations import trigger_integrations


def _extract_signals_from_ddg(ddg_data: dict) -> dict:
    """Extract buying signals from DDG search results."""
    signals = {
        "expansion_detected": False,
        "expansion_detail": None,
        "funding_detected": False,
        "funding_detail": None,
        "leadership_change": False,
        "leadership_detail": None,
        "portfolio_growth": False,
        "portfolio_detail": None,
    }
    
    if not ddg_data:
        return signals
    
    company_results = ddg_data.get("company_results", [])
    market_results = ddg_data.get("market_results", [])
    
    # Combine all text for analysis
    all_company_text = " ".join([
        f"{r.get('title', '')} {r.get('body', '')}"
        for r in company_results
    ]).lower()
    
    all_market_text = " ".join([
        f"{r.get('title', '')} {r.get('body', '')}"
        for r in market_results
    ]).lower()
    
    # Funding keywords
    funding_keywords = ["funding round", "series a", "series b", "series c", "raised $", "secured $", 
                         "venture capital", "private equity", "ipo", "investment", "capital raise"]
    for keyword in funding_keywords:
        if keyword in all_company_text:
            signals["funding_detected"] = True
            # Find the actual headline/title
            for r in company_results:
                text = f"{r.get('title', '')} {r.get('body', '')}".lower()
                if keyword in text:
                    signals["funding_detail"] = r.get('title', keyword)
                    break
            else:
                signals["funding_detail"] = f"Funding news: {keyword}"
            break
    
    # Expansion/Acquisition keywords
    expansion_keywords = ["acquired", "acquisition", "merger", "acquires", "merged with", "expansion",
                          "expanded", "new property", "new development", "buying"]
    for keyword in expansion_keywords:
        if keyword in all_company_text:
            signals["expansion_detected"] = True
            for r in company_results:
                text = f"{r.get('title', '')} {r.get('body', '')}".lower()
                if keyword in text:
                    signals["expansion_detail"] = r.get('title', keyword)
                    break
            else:
                signals["expansion_detail"] = f"Expansion news: {keyword}"
            break
    
    # Leadership keywords
    leadership_keywords = ["new ceo", "appointed ceo", "hired chief", "executive hire", 
                           "promoted to", "leadership", "executive team"]
    for keyword in leadership_keywords:
        if keyword in all_company_text:
            signals["leadership_change"] = True
            for r in company_results:
                text = f"{r.get('title', '')} {r.get('body', '')}".lower()
                if keyword in text:
                    signals["leadership_detail"] = r.get('title', keyword)
                    break
            else:
                signals["leadership_detail"] = f"Leadership change: {keyword}"
            break
    
    # Portfolio/Size keywords
    portfolio_keywords = ["million units", "thousand units", "largest operator", "#1 ranked",
                          "bedrooms under management", "units under management", "portfolio of",
                          "managed by", "operates", "properties"]
    for keyword in portfolio_keywords:
        if keyword in all_company_text:
            signals["portfolio_growth"] = True
            for r in company_results:
                text = f"{r.get('title', '')} {r.get('body', '')}".lower()
                if keyword in text:
                    signals["portfolio_detail"] = r.get('title', keyword)
                    break
            else:
                signals["portfolio_detail"] = f"Portfolio confirmed: {keyword}"
            break
    
    # Check for large operator mentions
    if "1.1 million" in all_company_text or "largest" in all_company_text:
        signals["portfolio_growth"] = True
        signals["portfolio_detail"] = "Major portfolio operator confirmed"
    
    return signals


def _build_market_signals(census: dict, fred: dict, city: str, state: str) -> list:
    """Build market signals from verified data."""
    signals = []
    
    renter_pct = census.get("renter_pct", 0)
    vacancy = census.get("vacancy_rate", 0)
    rent_growth = fred.get("rent_growth_pct", 0)
    
    if renter_pct and renter_pct > 40:
        signals.append(f"High renter demand: {renter_pct}% renters - high inquiry volume")
    elif renter_pct and renter_pct > 30:
        signals.append(f"Growing renter market: {renter_pct}% renters in {city}")
    
    if vacancy and vacancy < 3:
        signals.append(f"Tight inventory: Only {vacancy}% vacancy - every lead counts")
    elif vacancy and vacancy < 5:
        signals.append(f"Low vacancy: {vacancy}% in {city} market")
    elif vacancy and vacancy > 10:
        signals.append(f"High vacancy: {vacancy}% - fill units faster")
    
    if rent_growth and rent_growth > 2:
        signals.append(f"Active market: {rent_growth}% rent growth YoY in {state}")
    elif rent_growth and rent_growth > 0:
        signals.append(f"Rent growth: {rent_growth}% YoY in {state}")
    elif rent_growth == 0:
        signals.append(f"Flat rents: 0% growth in {state} - compete on service")
    
    return signals


def _get_sales_signal(renter_pct: float, vacancy: float, income: int, rent_growth: float, portfolio_growth: bool) -> str:
    """Build sales signal from verified data."""
    signal = f"{renter_pct}% renters, {vacancy}% vacancy, ${income:,} income"
    
    if rent_growth > 0:
        signal += f", +{rent_growth}% rent growth"
    elif rent_growth == 0:
        signal += ", flat rents"
    else:
        signal += f", {rent_growth}% rent decline"
    
    if portfolio_growth:
        signal += " | Major operator (1M+ units)"
    
    return signal


def _build_key_data_points(census: dict, fred: dict, news: dict, walkscore: dict) -> dict:
    """Build key data points from enrichment data."""
    kdp = {}
    
    kdp["renter_pct"] = census.get("renter_pct")
    kdp["vacancy_rate"] = census.get("vacancy_rate")
    kdp["rent_growth_pct"] = fred.get("rent_growth_pct")
    kdp["median_income"] = census.get("median_income")
    kdp["total_renter_units"] = census.get("total_renter_units")
    
    if walkscore:
        kdp["walkscore"] = walkscore.get("walkscore")
        kdp["transitscore"] = walkscore.get("transitscore")
        kdp["bikescore"] = walkscore.get("bikescore")
    
    if news:
        headlines = news.get("company_headlines", [])
        if headlines:
            kdp["top_news_headline"] = headlines[0].get("title")
        if news.get("company_summary"):
            kdp["company_summary"] = news["company_summary"]
    
    return kdp


def _process_single_lead(lead: dict, progress_callback: Optional[Callable] = None) -> dict:
    """Process a single lead through the unified pipeline."""
    api_errors = []
    llm_available = bool(os.getenv("GROQ_API_KEY", "").strip())
    
    try:
        # === STAGE 1: ENRICHMENT (Python API calls, no LLM) ===
        if progress_callback:
            progress_callback("Routing lead...")
        
        routing = route_lead_fast(
            company=lead.get("company", ""),
            city=lead.get("city", ""),
            state=lead.get("state", ""),
        )
        apis = routing["apis_to_call"]
        
        if progress_callback:
            progress_callback("Fetching data...")
        
        enriched = execute_enrichment(lead, apis, progress_callback)
        
        # Extract data
        census = enriched.get("census", {})
        fred = enriched.get("fred", {})
        walkscore = enriched.get("walkscore", {})
        ddg = enriched.get("ddg", {})
        news = enriched.get("news", {})
        
        # Extract buying signals
        buying_signals = _extract_signals_from_ddg(ddg)
        
        # Check for portfolio growth
        portfolio_growth = buying_signals.get("portfolio_growth", False)
        if not portfolio_growth:
            for result in ddg.get("company_results", []):
                text = f"{result.get('title', '')} {result.get('body', '')}".lower()
                if "1.1 million" in text or "largest" in text:
                    buying_signals["portfolio_growth"] = True
                    buying_signals["portfolio_detail"] = "Major portfolio confirmed"
                    portfolio_growth = True
                    break
        
        # === STAGE 2: SCORING (LLM temp: 0.0) ===
        scoring_result = {}
        if llm_available:
            if progress_callback:
                progress_callback("Calculating priority tier...")
            try:
                scoring_result = execute_scoring_task(
                    lead=lead,
                    census=census,
                    fred=fred,
                    news=news,
                    buying_signals=buying_signals,
                    progress_callback=progress_callback,
                )
                if "error" in scoring_result:
                    api_errors.append(f"Scoring LLM: {scoring_result['error']}")
                    scoring_result = {}
            except Exception as e:
                api_errors.append(f"Scoring: {str(e)}")
                scoring_result = {}
        
        # Fallback scoring if LLM failed
        if not scoring_result or "tier" not in scoring_result:
            tier = _infer_tier(census, fred, buying_signals)
            score = _infer_score(tier, census)
            scoring_result = {
                "tier": tier,
                "priority_score": score,
                "score_rationale": _build_score_rationale(lead, census, fred, portfolio_growth),
                "decision_maker_context": _build_decision_maker_context(lead, census, news),
                "industry_benchmark": _build_industry_benchmark(census, fred),
            }
        else:
            scoring_result.setdefault("score_rationale", _build_score_rationale(lead, census, fred, portfolio_growth))
        
        # === STAGE 3: OUTREACH (LLM temp: 0.5) ===
        outreach_result = {}
        if llm_available:
            if progress_callback:
                progress_callback("Generating outreach...")
            try:
                enrichment_data = {"census": census, "fred": fred, "news": news, "walkscore": walkscore}
                outreach_result = execute_outreach_task(
                    lead=lead,
                    enrichment=enrichment_data,
                    scoring=scoring_result,
                    progress_callback=progress_callback,
                )
                if "error" in outreach_result:
                    api_errors.append(f"Outreach LLM: {outreach_result['error']}")
                    outreach_result = {}
            except Exception as e:
                api_errors.append(f"Outreach: {str(e)}")
                outreach_result = {}
        
        # Build market signals
        market_signals = _build_market_signals(census, fred, lead.get("city", ""), lead.get("state", ""))
        
        # Build sales signal
        sales_signal = _get_sales_signal(
            census.get("renter_pct", 0),
            census.get("vacancy_rate", 0),
            census.get("median_income", 0),
            fred.get("rent_growth_pct", 0),
            portfolio_growth,
        )
        
        # Fallback for outreach if LLM failed - build from real data
        if not outreach_result:
            enrichment_data = {"census": census, "fred": fred, "news": news, "walkscore": walkscore}
            outreach_result = {
                "talking_points": _build_talking_points(lead, enrichment_data),
                "email_draft": _build_email_draft(lead, enrichment_data),
                "objection_handling": _build_objections(lead, enrichment_data),
                "roi_estimate": _build_roi(lead, enrichment_data),
                "peer_case_study": _build_case_study(lead, enrichment_data),
            }
        
        # Merge all results
        # Ensure roi_estimate always has market context from Census
        roi_estimate = outreach_result.get("roi_estimate", {})
        if "market_renter_pct" not in roi_estimate:
            roi_estimate["market_renter_pct"] = census.get("renter_pct")
        if "market_vacancy" not in roi_estimate:
            roi_estimate["market_vacancy"] = census.get("vacancy_rate")
        
        result = {
            "tier": scoring_result.get("tier", "C"),
            "priority_score": scoring_result.get("priority_score", 50),
            "score_rationale": scoring_result.get("score_rationale", ""),
            "key_data_points": _build_key_data_points(census, fred, news, walkscore),
            "buying_signals": buying_signals,
            "market_signals": market_signals,
            "sales_signal": sales_signal,
            # From outreach
            "talking_points": outreach_result.get("talking_points", []),
            "email_draft": outreach_result.get("email_draft", {}),
            "objection_handling": outreach_result.get("objection_handling", {}),
            "roi_estimate": roi_estimate,
            "peer_case_study": outreach_result.get("peer_case_study", {}),
            # From scoring
            "decision_maker_context": scoring_result.get("decision_maker_context", {}),
            "industry_benchmark": scoring_result.get("industry_benchmark", {}),
            "estimated_time_saved_minutes": 45,
        }
        
        # Add metadata - ensure _lead always preserves all original fields including name
        result["_lead"] = {
            "name": lead.get("name") or lead.get("Name") or "",
            "email": lead.get("email") or lead.get("Email") or "",
            "company": lead.get("company") or lead.get("Company") or "",
            "property_address": lead.get("property_address") or lead.get("Property Address") or "",
            "city": lead.get("city") or lead.get("City") or "",
            "state": lead.get("state") or lead.get("State") or "",
        }
        result["_raw_data"] = enriched
        result["_api_errors"] = api_errors
        result["_strategy"] = routing.get("strategy", "unknown")
        result["_needs_manual_review"] = len(api_errors) > 0 or not llm_available
        
    except Exception as e:
        result = {
            "tier": "C",
            "priority_score": 30,
            "score_rationale": f"Pipeline error: {str(e)[:100]}",
            "key_data_points": {},
            "buying_signals": {},
            "market_signals": [],
            "talking_points": [],
            "email_draft": {},
            "_needs_manual_review": True,
            "_api_errors": [str(e)],
            "_lead": {
                "name": lead.get("name") or lead.get("Name") or "",
                "email": lead.get("email") or lead.get("Email") or "",
                "company": lead.get("company") or lead.get("Company") or "",
                "property_address": lead.get("property_address") or lead.get("Property Address") or "",
                "city": lead.get("city") or lead.get("City") or "",
                "state": lead.get("state") or lead.get("State") or "",
            },
        }
    
    # Apply schema validation
    result = apply_validation_to_result(result, lead)
    
    return result


def _build_score_rationale(lead: dict, census: dict, fred: dict, portfolio_growth: bool) -> str:
    """Build score rationale from verified data."""
    city = lead.get("city", "Unknown")
    state = lead.get("state", "Unknown")
    renter_pct = census.get("renter_pct", 0)
    vacancy = census.get("vacancy_rate", 0)
    rent_growth = fred.get("rent_growth_pct", 0)
    
    if renter_pct > 40 and vacancy < 3:
        rationale = f"{city}, {state}: {renter_pct}% renter population, {vacancy}% vacancy - tight market"
    elif renter_pct > 30:
        rationale = f"{city}, {state}: {renter_pct}% renters, {vacancy}% vacancy - solid renter demand"
    else:
        rationale = f"{city}, {state}: {renter_pct}% renter population"
    
    if rent_growth > 2:
        rationale += f", +{rent_growth}% rent growth"
    elif rent_growth == 0:
        rationale += ", flat rents"
    
    if portfolio_growth:
        rationale += ". Large portfolio operator."
    
    return rationale


def run_pipeline(
    lead: dict,
    progress_callback: Optional[Callable] = None,
    validate: bool = True,
) -> dict:
    """Run the unified GTM pipeline."""
    result = _process_single_lead(lead, progress_callback)
    
    # Trigger integrations (SYNC stage)
    try:
        result = trigger_integrations(result, lead)
    except Exception:
        pass
    
    return result


def run_batch(
    leads: list[dict],
    progress_callback: Optional[Callable] = None,
    on_lead_complete: Optional[Callable] = None,
) -> list[dict]:
    """Run pipeline on batch of leads concurrently."""
    results = []
    total = len(leads)
    
    semaphore = Semaphore(MAX_CONCURRENT_LEADS)
    
    def process_with_semaphore(lead):
        with semaphore:
            return _process_single_lead(lead)
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_LEADS) as executor:
        future_to_lead = {
            executor.submit(process_with_semaphore, lead): lead 
            for lead in leads
        }
        
        completed = 0
        for future in as_completed(future_to_lead):
            lead = future_to_lead[future]
            completed += 1
            
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "tier": "C",
                    "priority_score": 30,
                    "score_rationale": f"Processing error: {str(e)[:100]}",
                    "_lead": lead,
                    "_needs_manual_review": True,
                })
            
            if progress_callback:
                progress_callback(f"Processed {completed}/{total}: {lead.get('company', 'Unknown')}")
            
            if on_lead_complete:
                on_lead_complete(completed, total, result)
    
    # Batch sync (Sheets write)
    _trigger_batch_integrations(results, leads)
    
    return results


def _trigger_batch_integrations(results: list[dict], leads: list[dict]):
    """Trigger integrations after batch processing."""
    try:
        from integrations.sheets import write_result_to_sheet
        for result, lead in zip(results, leads):
            try:
                write_result_to_sheet(result, lead)
            except Exception:
                pass
    except Exception:
        pass
    
    try:
        from integrations.slack import send_lead_alert
        from integrations.webhook import send_to_webhook
        
        for result, lead in zip(results, leads):
            tier = result.get("tier", "")
            
            if tier == "A" or result.get("_needs_manual_review"):
                try:
                    send_lead_alert(result, lead)
                except Exception:
                    pass
            
            if tier == "A":
                try:
                    send_to_webhook(result, lead)
                except Exception:
                    pass
    except Exception:
        pass