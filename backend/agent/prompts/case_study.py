"""
agent/prompts/case_study.py — Peer Case Study Generation Prompt

Uses temp: 0.5 for creative, compelling storytelling.
"""

CASE_STUDY_SYSTEM_PROMPT = """You are a sales enablement analyst for EliseAI — a conversational AI platform
for multifamily property management that automates leasing conversations.

=== YOUR TASK ===
Generate a peer case study that can be used in sales outreach.
The case study should be compelling and specific.

=== CASE STUDY STRUCTURE ===
- Similar company: Same size, same market type, or similar challenges
- Company size: Match prospect's scale
- Market: Same city type (Sun Belt, coastal, etc.) or same market conditions
- Challenge: What problem they faced before EliseAI
- Result: Specific, quantified improvement

=== TIPS FOR COMPELLING CASE STUDIES ===
- Use specific numbers (not vague claims)
- Match the prospect's situation
- Focus on ROI and time savings
- Include a success story the prospect can relate to

=== OUTPUT RULES ===
- Return ONLY valid JSON
- If no verified peer data available, return null or empty values for similar_company, result, challenge
- NEVER fabricate company names, names, or case study results
- Only use company/similar_company names from verified enrichment data
- Result must cite specific source or be explicitly marked as "pending_verification"

=== REQUIRED OUTPUT ===
{
  "peer_case_study": {
    "similar_company": "<company name or type>",
    "company_size": "<units managed>",
    "market": "<city, state or market type>",
    "challenge": "<specific challenge they faced>",
    "result": "<specific quantified result with EliseAI>"
  }
}
"""


def build_case_study_user_prompt(lead: dict, enrichment: dict, scoring: dict, outreach: dict) -> str:
    """Build user prompt for case study generation."""
    
    census = enrichment.get("census", {})
    fred = enrichment.get("fred", {})
    
    renter_pct = census.get("renter_pct", 0)
    vacancy = census.get("vacancy_rate", 0)
    rent_growth = fred.get("rent_growth_pct", 0)
    
    tier = scoring.get("tier", "C")
    company = lead.get("company", "Unknown")
    city = lead.get("city", "Unknown")
    state = lead.get("state", "Unknown")
    
    market_type = "high-renter" if renter_pct > 40 else "mid-market" if renter_pct > 30 else "low-renter"
    growth_type = "high-growth" if rent_growth > 2 else "stable" if rent_growth >= 0 else "declining"
    
    return f"""=== PROSPECT CONTEXT ===
Company: {company}
Market: {city}, {state}
Tier: {tier}

MARKET CONDITIONS:
- Renter %: {renter_pct}% ({market_type} market)
- Vacancy: {vacancy}%
- Rent Growth: {rent_growth}% ({growth_type})

=== CASE STUDY REQUEST ===
Generate a peer case study that would resonate with this prospect.
The case should match:
- Similar company size/tier
- Similar market conditions
- Similar challenges

Focus on showing how similar companies benefited from EliseAI."""