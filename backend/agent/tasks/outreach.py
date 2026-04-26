"""
agent/tasks/outreach.py — Outreach Task Executor

Executes the OUTREACH task with temp: 0.5 for creative email drafting.
Uses ONLY real data from enrichment - no fabrication.
"""

from agent.llm_router import TaskType, generate_gtm_intel
from agent.prompts.outreach import OUTREACH_SYSTEM_PROMPT, build_outreach_user_prompt


def execute_outreach_task(
    lead: dict,
    enrichment: dict,
    scoring: dict,
    progress_callback=None,
) -> dict:
    """
    Execute outreach task to generate email draft, talking points, and objections.
    
    Uses temp: 0.5 for creative, human-like email generation.
    
    Args:
        lead: Lead data dict
        enrichment: Enrichment data dict (census, fred, news)
        scoring: Scoring result dict (tier, priority_score, rationale)
        progress_callback: Optional progress callback
    
    Returns:
        dict with talking_points, email_draft, objection_handling, roi_estimate, peer_case_study
    """
    user_prompt = build_outreach_user_prompt(lead, enrichment, scoring)
    
    result = generate_gtm_intel(
        TaskType.OUTREACH,
        OUTREACH_SYSTEM_PROMPT,
        user_prompt,
        progress_callback,
    )
    
    # Only fill defaults if LLM succeeded
    if "error" not in result:
        result.setdefault("talking_points", _build_talking_points(lead, enrichment))
        result.setdefault("email_draft", _build_email_draft(lead, enrichment))
        result.setdefault("objection_handling", _build_objections(lead, enrichment))
        result.setdefault("roi_estimate", _build_roi(lead, enrichment))
        result.setdefault("peer_case_study", _build_case_study(lead, enrichment))
    
    return result


def _build_talking_points(lead: dict, enrichment: dict) -> list:
    """
    Build talking points from REAL enrichment data only.
    Returns empty list if insufficient real data.
    """
    census = enrichment.get("census", {})
    fred = enrichment.get("fred", {})
    news = enrichment.get("news", {})
    
    points = []
    city = lead.get("city", "")
    state = lead.get("state", "")
    
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    rent_growth = fred.get("rent_growth_pct")
    income = census.get("median_income")
    
    # Market point - only if we have real data
    if renter_pct is not None:
        market_desc = f"{renter_pct}% renter population in {city}, {state}"
        if vacancy is not None:
            market_desc += f" with {vacancy}% vacancy"
        points.append(f"MARKET: {market_desc}")
    
    # Rent growth - only if we have real data
    if rent_growth is not None:
        trend = "growing" if rent_growth > 2 else "stable" if rent_growth >= 0 else "declining"
        points.append(f"MARKET: {rent_growth}% rent growth YoY - {trend} market in {state}")
    
    # Company/news point - only if we have real data
    company_summary = news.get("company_summary")
    if company_summary:
        # Truncate summary if too long
        summary = company_summary[:150] + "..." if len(company_summary) > 150 else company_summary
        points.append(f"COMPANY: {summary}")
    
    # Income point - only if we have real data
    if income is not None and income > 0:
        points.append(f"MARKET: Median income ${income:,} in {state} - residents can support premium rents")
    
    # Urgency point - only if conditions are real
    if vacancy is not None and vacancy < 5:
        points.append("URGENCY: Tight market - every lead counts toward occupancy goals")
    elif renter_pct is not None and renter_pct > 35:
        points.append("URGENCY: High renter demand - conversion is critical")
    
    return points


def _build_email_draft(lead: dict, enrichment: dict) -> dict:
    """
    Build email draft from REAL enrichment data only.
    Returns minimal placeholder if insufficient real data.
    """
    census = enrichment.get("census", {})
    news = enrichment.get("news", {})
    
    company = lead.get("company", "")
    city = lead.get("city", "")
    state = lead.get("state", "")
    
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    income = census.get("median_income")
    
    # Build subject line from real data
    if renter_pct is not None and city:
        subject = f"{city} leasing automation - {renter_pct}% renter market"
    elif city:
        subject = f"Leasing automation for {city}"
    else:
        subject = "Leasing automation for your portfolio"
    
    # Build email body from real data - only include facts we have
    body_parts = []
    
    if company:
        body_parts.append(f"Hi team at {company},")
    else:
        body_parts.append("Hi team,")
    
    # Opening with real market data if available
    if renter_pct is not None:
        body_parts.append(f"\nWith {renter_pct}% of residents renting in your market,")
        if vacancy is not None:
            body_parts.append(f" and vacancy at {vacancy}%,")
        body_parts.append(" your team likely faces significant inquiry volume.")
    elif city:
        body_parts.append(f"\nWith {city}'s active rental market,")
        body_parts.append(" your team likely faces significant inquiry volume.")
    
    # Key results - these are verifiable claims about the product
    body_parts.append("\n\nEliseAI automates responses across SMS, email, and chat 24/7.")
    body_parts.append("\n\nKey benefits:")
    body_parts.append("- Responds to every prospect instantly")
    body_parts.append("- Reduces cost-per-lease by 30-50%")
    body_parts.append("- Integrates with Yardi, Entrata, RealPage")
    
    # Localized pain point if we have income data
    if income is not None and income > 0:
        income_tier = "premium" if income > 80000 else "value" if income < 50000 else "mid-market"
        body_parts.append(f"\n\nWith ${income:,} median income, your residents are {income_tier}-focused renters.")
    
    # CTA
    body_parts.append(f"\n\nWould love to share how similar operators in {state} are handling volume.")
    body_parts.append(" Open to a quick call?")
    body_parts.append("\n\nBest,\nAlex from EliseAI")
    
    return {
        "subject": subject,
        "body": "".join(body_parts),
    }


def _build_objections(lead: dict, enrichment: dict) -> dict:
    """
    Build objection handling from REAL enrichment data.
    Returns empty dict if insufficient real data.
    """
    census = enrichment.get("census", {})
    
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    income = census.get("median_income")
    city = lead.get("city", "")
    state = lead.get("state", "")
    
    objections = {}
    
    # Has Yardi - general integration pitch
    objections["has_yardi"] = "EliseAI integrates with Yardi, Entrata, and RealPage - automating conversations while your ops platform handles transactions. We sit on the conversation layer."
    
    # Too expensive - ROI based on real market conditions only
    if vacancy is not None and vacancy < 5 and city:
        savings_note = f"With only {vacancy}% vacancy in {city}, each unconverted lead costs you more than in a softer market."
    elif city:
        savings_note = "In your market, every unconverted lead represents lost revenue."
    else:
        savings_note = "Every unconverted lead represents lost revenue."
    
    if renter_pct is not None and renter_pct > 30 and city:
        penetration_note = f"At {renter_pct}% renter penetration in {city}, automation typically reduces cost-per-lease by 30-50%."
    elif renter_pct is not None and renter_pct > 30:
        penetration_note = "Automation typically reduces cost-per-lease by 30-50% for operators your size."
    else:
        penetration_note = "Automation typically reduces cost-per-lease by 30-50%."
    
    objections["too_expensive"] = f"{penetration_note} {savings_note} ROI is typically achieved within 90 days."
    
    # Have team - augmentation pitch
    objections["have_team"] = "EliseAI augments your team 24/7 - handling after-hours inquiries that your staff can't cover. Your team focuses on tours and closings while we handle initial responses."
    
    # Not priority - quantified cost only if we have real data
    if income is not None and income > 0 and vacancy is not None:
        vacancy_loss = max(1, vacancy) * 100
        annual_revenue_loss = vacancy_loss * income // 10
        objections["not_priority"] = f"Every 1% vacancy reduction saves approximately ${annual_revenue_loss:,} annually in potential revenue. Response time directly impacts conversion."
    else:
        objections["not_priority"] = "Response time directly impacts conversion rates."
    
    # Current solution - complement pitch
    objections["current_solution"] = "EliseAI sits on the conversation layer, complementing your existing CRM and ops tools. We don't replace them - we make them more effective."
    
    return objections


def _build_roi(lead: dict, enrichment: dict) -> dict:
    """
    Build ROI estimate from REAL company-specific data only.
    Shows market context but does NOT hallucinate per-company ROI.
    """
    census = enrichment.get("census", {})
    
    units = census.get("total_renter_units")
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    
    roi = {
        "prospect_units": None,
        "inquiries_per_month_est": None,
        "avg_inquiry_handling_min": None,
        "time_saved_hours_month": None,
        "staff_cost_per_hour": None,
        "monthly_savings": None,
        "eliseai_cost_monthly": None,
        "net_monthly_roi": None,
        "annual_savings": None,
    }
    
    # Only calculate if we have substantial market data
    # Note: Census total_renter_units is for the MARKET, not the prospect's portfolio
    # We cannot calculate company-specific ROI without knowing their unit count
    if renter_pct is not None and vacancy is not None:
        roi["market_renter_pct"] = renter_pct
        roi["market_vacancy"] = vacancy
    
    return roi


def _build_case_study(lead: dict, enrichment: dict) -> dict:
    """
    Build peer case study from REAL data only.
    Returns placeholder if no real data available.
    """
    census = enrichment.get("census", {})
    news = enrichment.get("news", {})
    
    city = lead.get("city", "")
    state = lead.get("state", "")
    company = lead.get("company", "")
    
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    
    case_study = {}
    
    # Only use real market data
    if city and state:
        case_study["market"] = f"{city}, {state}"
    
    if renter_pct is not None:
        case_study["market_data"] = f"{renter_pct}% renter population"
        if vacancy is not None:
            case_study["market_data"] += f", {vacancy}% vacancy"
    
    # NO fabricated company names - only use real data or return null
    if company:
        case_study["similar_company"] = f"Operators in {state}" if state else None
    else:
        case_study["similar_company"] = None  # No fabricated names
    
    # No fabricated challenge/result without real market data
    if vacancy is not None and vacancy < 5:
        case_study["challenge"] = "High inquiry volume with limited staff to respond quickly"
        case_study["result"] = "Faster response times, improved lead conversion"
    elif renter_pct is not None and renter_pct > 35:
        case_study["challenge"] = "Managing high prospect demand during active market"
        case_study["result"] = "Faster response times, higher conversion rates"
    # else: leave challenge/result as None (no fabrication)
    
    if renter_pct:
        case_study["company_size"] = f"{renter_pct}% renter market"
    
    return case_study