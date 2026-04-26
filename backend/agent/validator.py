"""
agent/validator.py — Output Validator for SDR Toolkit

Validates complete SDR outputs: email has data points, tier valid,
all deal-closing context present, ROI calculations valid.
"""

from typing import Optional


VALIDATION_RULES = {
    "email_min_data_points": 2,
    "rationale_min_length": 50,
    "tier_must_exist": True,
    "talking_points_min": 3,
    "buying_signals_required": True,
    "objection_handling_required": True,
    "roi_required_fields": ["prospect_units", "monthly_savings", "annual_savings"],
}


def validate_result(result: dict) -> dict:
    """
    Validate complete SDR toolkit output.
    """
    errors = []
    warnings = []
    score = 100

    email_draft = result.get("email_draft", {})
    tier = result.get("tier", "")
    rationale = result.get("score_rationale", "")
    talking_points = result.get("talking_points", [])
    key_data_points = result.get("key_data_points", {})
    buying_signals = result.get("buying_signals", {})
    objection_handling = result.get("objection_handling", {})
    roi_estimate = result.get("roi_estimate", {})
    sales_signal = result.get("sales_signal", "")

    if isinstance(email_draft, str):
        email_body = email_draft
    else:
        email_body = email_draft.get("body", "") if isinstance(email_draft, dict) else ""

    if not email_body:
        errors.append("email_draft body is empty")
        score -= 25
    else:
        data_point_count = _count_data_points_in_email(email_body, key_data_points)
        if data_point_count < VALIDATION_RULES["email_min_data_points"]:
            errors.append(
                f"Email references only {data_point_count} data point(s), need ≥{VALIDATION_RULES['email_min_data_points']}"
            )
            score -= 15

    if not tier or tier not in ("A", "B", "C"):
        errors.append("tier must be A, B, or C")
        score -= 25
    elif tier == "C":
        warnings.append("Tier C assigned — verify this is correct for your ICP")
        score -= 5

    if not rationale or len(rationale.strip()) < VALIDATION_RULES["rationale_min_length"]:
        errors.append(
            f"score_rationale too short ({len(rationale.strip())} chars, need ≥{VALIDATION_RULES['rationale_min_length']})"
        )
        score -= 15

    if not talking_points or len(talking_points) < VALIDATION_RULES["talking_points_min"]:
        errors.append(
            f"Only {len(talking_points)} talking point(s), need ≥{VALIDATION_RULES['talking_points_min']}"
        )
        score -= 10

    if not buying_signals:
        warnings.append("No buying_signals detected — may indicate low signal")
        score -= 5

    if not objection_handling:
        warnings.append("No objection_handling provided — SDR may need more support")
        score -= 5

    roi_fields = VALIDATION_RULES["roi_required_fields"]
    missing_roi = [f for f in roi_fields if roi_estimate.get(f) is None]
    if missing_roi:
        warnings.append(f"ROI missing fields: {missing_roi}")
        score -= 10

    if not sales_signal:
        warnings.append("No sales_signal summary — SDR quick-read unavailable")
        score -= 5

    if key_data_points:
        null_count = sum(1 for v in key_data_points.values() if v is None)
        if null_count > 5:
            warnings.append(f"{null_count} null key_data_points — enrichment may be weak")
            score -= 10

    if "error" in result:
        errors.append(f"Pipeline error: {result['error']}")
        score = 0

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "score": max(0, score),
        "quality_grade": _get_grade(max(0, score)),
    }


def _count_data_points_in_email(email: str, key_data_points: dict) -> int:
    """Count how many data points are referenced in the email."""
    email_lower = email.lower()
    count = 0

    markers = [
        ("renter", key_data_points.get("renter_pct")),
        ("vacancy", key_data_points.get("vacancy_rate")),
        ("rent growth", key_data_points.get("rent_growth_pct")),
        ("income", key_data_points.get("median_income")),
        ("news", key_data_points.get("top_news_headline")),
    ]

    for keyword, value in markers:
        if value is not None and keyword in email_lower:
            count += 1

    return count


def _get_grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 40:
        return "D"
    return "F"


if __name__ == "__main__":
    test_result = {
        "tier": "A",
        "priority_score": 85,
        "score_rationale": "Travis County is a 47% renter market with 2.5% vacancy and 2.56% YoY rent growth — a competitive leasing environment where response speed matters. Greystar manages 80,000+ units nationally and recently expanded their Austin portfolio.",
        "talking_points": [
            "Travis County is 47% renters with 2.5% vacancy — every inquiry counts toward revenue goals",
            "Greystar recently expanded their Austin portfolio, indicating active growth",
            "With 2.56% rent growth YoY, operators who respond fastest win the lease"
        ],
        "email_draft": {
            "subject": "Travis County's 47% renter market — how Greystar handles 24/7 leasing",
            "body": "Hi Sarah,\n\nTravis County is a 47% renter market with only 2.5% vacancy — every inquiry counts.\n\nEliseAI helps operators like Greystar respond to prospects 24/7, reducing time-to-lease by 30%.\n\nOpen to a 10-min call?\n\nBest,\nAlex"
        },
        "buying_signals": {
            "expansion_detected": True,
            "expansion_detail": "Greystar expanded Austin portfolio",
            "funding_detected": False,
            "funding_detail": None,
            "leadership_change": False,
            "leadership_detail": None,
            "portfolio_growth": True,
            "portfolio_detail": "80,000+ units managed nationally"
        },
        "objection_handling": {
            "has_yardi": "EliseAI integrates with Yardi — we automate conversations while your ops stack handles transactions",
            "too_expensive": "Most operators see 30% reduction in cost-per-lease",
            "have_team": "EliseAI augments your team — handles after-hours inquiries"
        },
        "roi_estimate": {
            "prospect_units": 5000,
            "inquiries_per_month_est": 500,
            "avg_inquiry_handling_min": 5,
            "time_saved_hours_month": 42,
            "staff_cost_per_hour": 25,
            "monthly_savings": 1050,
            "eliseai_cost_monthly": 5000,
            "net_monthly_roi": -3950,
            "annual_savings": -47400
        },
        "key_data_points": {
            "renter_pct": 47.1,
            "vacancy_rate": 2.5,
            "rent_growth_pct": 2.56,
            "median_income": 85000,
            "total_renter_units": 150000
        },
        "sales_signal": "Market: 47% renters, 2.5% vacancy, $85k income | Trend: 2.56% growth | News: Greystar expands Austin"
    }

    validation = validate_result(test_result)
    print("=== Validator Test ===")
    print(f"Is Valid: {validation['is_valid']}")
    print(f"Score: {validation['score']}/100 ({validation['quality_grade']})")
    print(f"Errors: {validation['errors']}")
    print(f"Warnings: {validation['warnings']}")