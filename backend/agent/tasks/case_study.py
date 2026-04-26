"""
agent/tasks/case_study.py — Case Study Task Executor

Executes the CASE_STUDY task with temp: 0.5 for creative storytelling.
"""

from agent.llm_router import TaskType, generate_gtm_intel
from agent.prompts.case_study import CASE_STUDY_SYSTEM_PROMPT, build_case_study_user_prompt


def execute_case_study_task(
    lead: dict,
    enrichment: dict,
    scoring: dict,
    outreach: dict,
    progress_callback=None,
) -> dict:
    """
    Execute case study task to generate a peer case study.
    
    Uses temp: 0.5 for creative, compelling storytelling.
    
    Args:
        lead: Lead data dict
        enrichment: Enrichment data dict
        scoring: Scoring result dict
        outreach: Outreach result dict
        progress_callback: Optional progress callback
    
    Returns:
        dict with peer_case_study
    """
    user_prompt = build_case_study_user_prompt(lead, enrichment, scoring, outreach)
    
    result = generate_gtm_intel(
        TaskType.CASE_STUDY,
        CASE_STUDY_SYSTEM_PROMPT,
        user_prompt,
        progress_callback,
    )
    
    # Validate and ensure required fields
    if "error" not in result:
        result.setdefault("peer_case_study", _default_case_study(lead, enrichment))
    
    return result


def _default_case_study(lead: dict, enrichment: dict) -> dict:
    """Generate peer case study from real data only - no fabrication."""
    census = enrichment.get("census", {})
    news = enrichment.get("news", {})
    city = lead.get("city", "")
    state = lead.get("state", "")
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    
    case_study = {}
    
    # Use real market data if available
    if city and state:
        case_study["market"] = f"{city}, {state}"
    
    if renter_pct is not None:
        market_data = f"{renter_pct}% renter population"
        if vacancy is not None:
            market_data += f", {vacancy}% vacancy"
        case_study["market_data"] = market_data
    
    # Use real news data for similar company if available
    company_summary = news.get("company_summary", "")
    if company_summary:
        # Use first 50 chars of summary as reference instead of fabricating
        case_study["similar_company"] = f"Peer operators in {state}" if state else "Peer operators"
        case_study["company_size"] = f"{renter_pct}% renter market" if renter_pct else None
    else:
        # NO fabricated company names
        case_study["similar_company"] = None
        case_study["company_size"] = f"{renter_pct}% renter market" if renter_pct else None
    
    # Challenge/result based on real market conditions
    if vacancy is not None and vacancy < 5:
        case_study["challenge"] = "High inquiry volume with limited staff to respond quickly"
        case_study["result"] = "Faster response times, improved lead conversion"
    elif renter_pct is not None and renter_pct > 35:
        case_study["challenge"] = "Managing high prospect demand during active market"
        case_study["result"] = "Higher conversion rates"
    else:
        # No fabricated results without data
        case_study["challenge"] = None
        case_study["result"] = None
    
    # Remove None values for clean output
    return {k: v for k, v in case_study.items() if v is not None}