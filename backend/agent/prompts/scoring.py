"""
agent/prompts/scoring.py — Tier & Priority Scoring Prompt

Uses temp: 0.0 for deterministic, reproducible scoring.
"""

SCORING_SYSTEM_PROMPT = """You are a senior sales intelligence analyst for EliseAI — a conversational AI platform
for multifamily property management that automates leasing conversations across SMS, email, and chat.

=== YOUR TASK ===
Assign a Priority Tier (A, B, or C) and Priority Score (0-100) based ONLY on the verified data provided.

=== ICP DEFINITIONS ===

Tier A — Priority Outreach (score: 85-100):
- National operators: Greystar, Asset Living, Equity Residential, AvalonBay, MAA, Camden Property Trust, Bell Partners
- OR Markets with >40% renter population AND <3% vacancy
- OR Company with recent expansion/funding/leadership signals

Tier B — Follow Up (score: 65-84):
- Regional/mid-market operators in growing Sun Belt metros
- Markets with 30-40% renter population
- Cities: Austin, Phoenix, Atlanta, Charlotte, Orlando, Nashville, Denver

Tier C — Nurture (score: 40-64):
- Small local operators
- Markets with <30% renter population
- OR high vacancy (>10%)

=== SCORING FACTORS ===
1. Company prominence (national operators always score higher)
2. Market density (renter %): Higher = more inquiries = higher priority
3. Rent growth: Positive growth = operators busy = automation valuable
4. Vacancy: Low vacancy = every inquiry counts
5. News/funding signals: Active companies buy tools

=== OUTPUT RULES ===
- Return ONLY valid JSON
- Copy numeric values EXACTLY from provided data
- Use null for missing values — NEVER guess or invent
- Score MUST be deterministic (same data = same score)

=== REQUIRED OUTPUT ===
{
  "tier": "A" | "B" | "C",
  "priority_score": <int 0-100>,
  "score_rationale": "<2-3 sentences citing SPECIFIC numbers from data>",
  "decision_maker_context": {
    "company_size_tier": "National" | "Regional" | "Local",
    "typical_buyer": "<job title>",
    "primary_pain_point": "<what they care about>",
    "what_they_google": "<search term they'd use>"
  },
  "industry_benchmark": {
    "avg_response_time_hours": null,
    "prospect_response_time": null,
    "avg_vacancy_rate": null,
    "prospect_market_vacancy": <from data or null>,
    "avg_rent_growth": null,
    "prospect_market_rent_growth": <from data or null>
  }
}

=== BENCHMARK RULES ===
- avg_response_time_hours, avg_vacancy_rate, avg_rent_growth: MUST be null unless you have VERIFIED industry data
- prospect_market_* fields: Copy EXACTLY from provided Census/FRED data or use null
- NEVER invent or estimate benchmark averages
"""


def build_scoring_user_prompt(lead: dict, census: dict, fred: dict, news: dict, buying_signals: dict) -> str:
    """Build user prompt with verified data for scoring task."""
    
    renter_pct = census.get("renter_pct")
    vacancy = census.get("vacancy_rate")
    income = census.get("median_income")
    total_units = census.get("total_renter_units")
    rent_growth = fred.get("rent_growth_pct")
    
    income_str = f"${income:,}" if income else "N/A"
    total_units_str = f"{total_units:,}" if total_units else "N/A"
    
    headlines = []
    if news.get("company_headlines"):
        for h in news["company_headlines"][:3]:
            headlines.append(f"- {h.get('title', '')} ({h.get('source', '')})")
    
    company_summary = news.get("company_summary", "No company summary available.")
    
    signal_parts = []
    if buying_signals.get("expansion_detected"):
        signal_parts.append(f"- Expansion: {buying_signals.get('expansion_detail')}")
    if buying_signals.get("funding_detected"):
        signal_parts.append(f"- Funding: {buying_signals.get('funding_detail')}")
    if buying_signals.get("leadership_change"):
        signal_parts.append(f"- Leadership: {buying_signals.get('leadership_detail')}")
    if buying_signals.get("portfolio_growth"):
        signal_parts.append(f"- Portfolio: {buying_signals.get('portfolio_detail')}")
    
    signal_text = "\n".join(signal_parts) if signal_parts else "No buying signals detected."
    headline_text = "\n".join(headlines) if headlines else "No headlines found."
    
    return f"""=== VERIFIED DATA (USE ONLY THIS DATA) ===

LEAD:
  Company: {lead.get('company', 'Unknown')}
  Market: {lead.get('city', 'Unknown')}, {lead.get('state', 'Unknown')}

MARKET DATA (Census):
  Renter %: {renter_pct if renter_pct is not None else 'N/A'}
  Vacancy Rate: {vacancy if vacancy is not None else 'N/A'}%
  Median Income: {income_str}
  Total Renter Units: {total_units_str}

ECONOMIC TREND (FRED):
  Rent Growth YoY: {rent_growth if rent_growth is not None else 'N/A'}%

COMPANY SIGNALS:
  {company_summary}
  
  Recent Headlines:
  {headline_text}

BUYING SIGNALS (pre-detected):
  {signal_text}

=== SCORING REQUEST ===
Assign tier and priority score based ONLY on the data above."""