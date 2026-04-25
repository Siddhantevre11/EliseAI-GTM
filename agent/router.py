"""
agent/router.py — Lead Router Agent

Decides which enrichment strategy to use (A/B/C) based on company and market signals.
Strategy A: Full (Census + FRED + News)
Strategy B: Core (Census + News)  
Strategy C: Minimal (Census only)
"""

import json
import os
from typing import Literal, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY", "").strip())
MODEL = "llama-3.1-8b-instant"

from config.strategies import get_strategy as _rule_based_strategy, get_apis_for_strategy


SYSTEM_PROMPT = """You are the Lead Router for EliseAI's enrichment pipeline. Your job is to classify leads into one of three enrichment strategies.

STRATEGIES:
- Strategy A (Full): Known national operators OR major metros. Call Census + FRED + News APIs.
- Strategy B (Core): Mid-market companies in growing markets. Call Census + News APIs.
- Strategy C (Minimal): Small/rural operations. Call Census only.

OUTPUT RULES:
Return a valid JSON object with keys: strategy, reasoning, apis_to_call.

{
  "strategy": "A" | "B" | "C",
  "reasoning": "2-3 sentences explaining the routing decision",
  "apis_to_call": ["census", "fred", "news"] | ["census", "news"] | ["census"]
}

Be concise and decisive. Default to B for ambiguous cases."""


def route_lead(company: str, city: str, state: str, use_llm: bool = True) -> dict:
    """
    Route a lead to the appropriate enrichment strategy.
    
    Uses a fast rule-based check first, then optionally enhances with LLM reasoning
    for edge cases.
    
    Returns:
        dict with keys: strategy, reasoning, apis_to_call
    """
    rule_strategy = _rule_based_strategy(company, city, state)
    rule_apis = get_apis_for_strategy(rule_strategy)
    
    if not use_llm:
        reasoning_map = {
            "A": f"{company} detected as priority target in {city} — full enrichment",
            "B": f"{city} is a growing market for {company} — core enrichment",
            "C": f"{company} in {city} — minimal enrichment sufficient",
        }
        return {
            "strategy": rule_strategy,
            "reasoning": reasoning_map.get(rule_strategy, "Rule-based routing"),
            "apis_to_call": rule_apis,
        }
    
    data_block = f"""LEAD:
  Company: {company}
  City: {city}
  State: {state}

RULE-BASED SUGGESTION: Strategy {rule_strategy} ({', '.join(rule_apis)})

Decide if this is correct, or override based on your knowledge of the company/market.
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": data_block},
            ],
            response_format={"type": "json_object"},
            max_tokens=256,
            temperature=0.1,
        )
        text = (response.choices[0].message.content or "").strip()
        
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]).strip()
        
        result = json.loads(text)
        
        if result.get("strategy") not in ("A", "B", "C"):
            result["strategy"] = rule_strategy
            result["apis_to_call"] = rule_apis
        
        return result
        
    except Exception as e:
        return {
            "strategy": rule_strategy,
            "reasoning": f"LLM routing failed ({e}), falling back to rules",
            "apis_to_call": rule_apis,
        }


def route_lead_fast(company: str, city: str, state: str) -> dict:
    """Fast rule-based routing (no LLM call)."""
    return route_lead(company, city, state, use_llm=False)


if __name__ == "__main__":
    test_leads = [
        ("Greystar", "Austin", "TX"),
        ("Bell Partners", "Orlando", "FL"),
        ("Local Management Co", "Boise", "ID"),
    ]
    
    print("=== Lead Router Test ===\n")
    for company, city, state in test_leads:
        result = route_lead_fast(company, city, state)
        print(f"{company} | {city}, {state}")
        print(f"  Strategy: {result['strategy']}")
        print(f"  APIs: {result['apis_to_call']}")
        print(f"  Reasoning: {result['reasoning']}\n")