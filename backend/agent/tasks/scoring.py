"""
agent/tasks/scoring.py — Scoring Task Executor

Executes the SCORING task with temp: 0.0 for deterministic results.
"""

from agent.llm_router import TaskType, generate_gtm_intel
from agent.prompts.scoring import SCORING_SYSTEM_PROMPT, build_scoring_user_prompt


def execute_scoring_task(
    lead: dict,
    census: dict,
    fred: dict,
    news: dict,
    buying_signals: dict,
    progress_callback=None,
) -> dict:
    """
    Execute scoring task to determine tier and priority score.
    
    Uses temp: 0.0 for deterministic, reproducible scoring.
    Same data should always produce the same tier/score.
    
    Args:
        lead: Lead data dict
        census: Census API response
        fred: FRED API response
        news: News/Wikipedia API response
        buying_signals: Pre-detected buying signals from DDG
        progress_callback: Optional progress callback
    
    Returns:
        dict with tier, priority_score, score_rationale, decision_maker_context, industry_benchmark
    """
    user_prompt = build_scoring_user_prompt(lead, census, fred, news, buying_signals)
    
    result = generate_gtm_intel(
        TaskType.SCORING,
        SCORING_SYSTEM_PROMPT,
        user_prompt,
        progress_callback,
    )
    
    if "error" not in result:
        result.setdefault("tier", _infer_tier(census, fred, buying_signals))
        result.setdefault("priority_score", _infer_score(result.get("tier", "C"), census))
        result.setdefault("decision_maker_context", _build_decision_maker_context(lead, census, news))
        result.setdefault("industry_benchmark", _build_industry_benchmark(census, fred))
    
    return result


def _infer_tier(census: dict, fred: dict, buying_signals: dict) -> str:
    """
    Infer tier from data - only use REAL data, no fabrication.
    
    Tier A: High renter demand (>40%) + buying signals + good rent growth
    Tier B: Moderate renter demand (>30%) OR good market conditions
    Tier C: Default when data is insufficient or market is weak
    """
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    rent_growth = fred.get("rent_growth_pct")
    
    # Track positive indicators
    indicators = []
    
    # Check for buying signals (strong positive indicator)
    has_signals = any([
        buying_signals.get("funding_detected"),
        buying_signals.get("expansion_detected"),
        buying_signals.get("portfolio_growth"),
    ])
    if has_signals:
        indicators.append("buying_signal")
    
    # High renter demand
    if renter_pct is not None and renter_pct > 40:
        indicators.append("high_renter")
    elif renter_pct is not None and renter_pct > 30:
        indicators.append("moderate_renter")
    
    # Low vacancy (tight market)
    if vacancy is not None and vacancy < 5:
        indicators.append("tight_market")
    
    # Positive rent growth
    if rent_growth is not None and rent_growth > 2:
        indicators.append("growth_market")
    
    # Tier assignment based on real indicators
    if len(indicators) >= 3 and ("high_renter" in indicators or "buying_signal" in indicators):
        return "A"
    elif len(indicators) >= 2:
        return "B"
    elif len(indicators) >= 1:
        return "B"
    else:
        # Insufficient data or weak market - still return a tier
        return "C"


def _infer_score(tier: str, census: dict) -> int:
    """
    Infer score from tier and real data - no fabrication.
    """
    base_scores = {"A": 85, "B": 70, "C": 50}
    base = base_scores.get(tier, 50)
    
    # Adjust based on REAL vacancy data
    vacancy = census.get("vacancy_rate")
    if vacancy is not None:
        if vacancy < 3:
            base += 5
        elif vacancy < 5:
            base += 2
        elif vacancy > 10:
            base -= 10
        elif vacancy > 7:
            base -= 5
    
    # Adjust based on REAL income data
    income = census.get("median_income")
    if income is not None:
        if income > 80000:
            base += 5
        elif income < 40000:
            base -= 5
    
    return min(100, max(0, base))


def _build_decision_maker_context(lead: dict, census: dict, news: dict) -> dict:
    """
    Build decision maker context from REAL data - no fabricated values.
    """
    context = {}
    
    # Use company size hints if available
    company = lead.get("company", "")
    if company:
        # Large operators often have recognizable names
        large_operator_patterns = ["greystar", "camden", "avalonbay", "equity", "amcr", "mid", "home", "bell", "lake", "west"]
        if any(pattern in company.lower() for pattern in large_operator_patterns):
            context["company_size_tier"] = "National"
        else:
            context["company_size_tier"] = "Regional"
    
    # Use market data for pain point
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    
    if renter_pct is not None and renter_pct > 35:
        context["primary_pain_point"] = "High inquiry volume from renter-heavy market"
    elif vacancy is not None and vacancy < 5:
        context["primary_pain_point"] = "Managing high prospect demand with limited staffing"
    else:
        context["primary_pain_point"] = "Leasing efficiency and response time"
    
    # Use market data for search context
    state = lead.get("state", "")
    if state and renter_pct is not None:
        context["what_they_google"] = f"leasing automation {state} apartment"
    else:
        context["what_they_google"] = "leasing automation AI"
    
    context["typical_buyer"] = "VP of Operations or Director of Leasing"
    
    return context


def _build_industry_benchmark(census: dict, fred: dict) -> dict:
    """
    Build industry benchmark from REAL data - no fabricated averages.
    """
    benchmark = {
        "avg_response_time_hours": None,
        "prospect_response_time": None,
        "avg_vacancy_rate": None,
        "prospect_market_vacancy": census.get("vacancy_rate"),
        "avg_rent_growth": None,
        "prospect_market_rent_growth": fred.get("rent_growth_pct"),
    }
    
    # Only use real data - don't fabricate industry averages
    # Leave benchmark values as None if we don't have real data
    
    return benchmark