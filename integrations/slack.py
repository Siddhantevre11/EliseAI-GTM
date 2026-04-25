"""
integrations/slack.py — Slack Integration for EliseAI GTM

Sends alerts to Slack when hot leads are detected.
Requires: SLACK_BOT_TOKEN, SLACK_USER_ID (for DM)
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_USER_ID = os.getenv("SLACK_USER_ID", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "")

SLACK_AVAILABLE = bool(SLACK_BOT_TOKEN)


def _get_slack_client():
    """Get Slack client."""
    if not SLACK_AVAILABLE:
        return None
    try:
        from slack_sdk import WebClient
        return WebClient(token=SLACK_BOT_TOKEN)
    except ImportError:
        return None


def send_lead_alert(result: dict, lead: dict) -> Optional[dict]:
    """
    Send lead alert to Slack.
    
    Args:
        result: Pipeline result
        lead: Original lead dict
    
    Returns:
        Slack API response or None
    """
    if not SLACK_AVAILABLE:
        return None
    
    client = _get_slack_client()
    if not client:
        return None
    
    tier = result.get("tier", "C")
    company = lead.get("company", "Unknown")
    city = lead.get("city", "")
    state = lead.get("state", "")
    score = result.get("priority_score", 0)
    
    # Build message
    if tier == "A":
        priority = "HOT LEAD"
    elif tier == "NEEDS_REVIEW":
        priority = "NEEDS REVIEW"
    else:
        priority = f"Tier {tier}"
    
    # Detect signals
    signals = result.get("buying_signals", {})
    signals_text = ""
    if signals:
        detected = []
        if signals.get("funding_detected"):
            detected.append("Funding")
        if signals.get("expansion_detected"):
            detected.append("Expansion")
        if signals.get("leadership_change"):
            detected.append("Leadership")
        if signals.get("portfolio_growth"):
            detected.append("Portfolio Growth")
        if detected:
            signals_text = " | ".join(detected)
    
    # Build blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{priority}: {company}",
                "emoji": False
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Location:*\n{city}, {state}"},
                {"type": "mrkdwn", "text": f"*Priority Score:*\n{score}"},
            ]
        },
    ]
    
    if signals_text:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Buying Signals:*\n{signals_text}"}
        })
    
    # Add key data points
    kdp = result.get("key_data_points", {})
    if kdp.get("renter_pct"):
        blocks.append({
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Renter %:*\n{kdp.get('renter_pct')}%"},
                {"type": "mrkdwn", "text": f"*Vacancy:*\n{kdp.get('vacancy_rate')}%"},
            ]
        })
    
    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*Score Rationale:*\n{result.get('score_rationale', 'N/A')}"}
    })
    
    try:
        # Send DM to user
        if SLACK_USER_ID:
            response = client.conversations_open(users=SLACK_USER_ID)
            if response["ok"]:
                channel_id = response["channel"]["id"]
                return client.chat_postMessage(
                    channel=channel_id,
                    blocks=blocks,
                    text=f"{priority}: {company}"
                )
        # Or post to channel
        elif SLACK_CHANNEL:
            return client.chat_postMessage(
                channel=SLACK_CHANNEL,
                blocks=blocks,
                text=f"{priority}: {company}"
            )
    except Exception as e:
        return {"error": str(e)}
    
    return None


def send_batch_summary(results: list[dict]) -> Optional[dict]:
    """Send batch processing summary to Slack."""
    if not SLACK_AVAILABLE:
        return None
    
    total = len(results)
    tier_a = sum(1 for r in results if r.get("tier") == "A")
    tier_b = sum(1 for r in results if r.get("tier") == "B")
    tier_c = sum(1 for r in results if r.get("tier") == "C")
    needs_review = sum(1 for r in results if r.get("_needs_manual_review"))
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Batch Processing Complete",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Total:*\n{total}"},
                {"type": "mrkdwn", "text": f"*Hot Leads:*\n{tier_a}"},
            ]
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Tier A:*\n{tier_a}"},
                {"type": "mrkdwn", "text": f"*Tier B:*\n{tier_b}"},
                {"type": "mrkdwn", "text": f"*Tier C:*\n{tier_c}"},
                {"type": "mrkdwn", "text": f"*Needs Review:*\n{needs_review}"},
            ]
        }
    ]
    
    client = _get_slack_client()
    if not client:
        return None
    
    try:
        if SLACK_USER_ID:
            response = client.conversations_open(users=SLACK_USER_ID)
            if response["ok"]:
                channel_id = response["channel"]["id"]
                return client.chat_postMessage(
                    channel=channel_id,
                    blocks=blocks,
                    text="Batch Processing Complete"
                )
    except Exception as e:
        return {"error": str(e)}
    
    return None


if __name__ == "__main__":
    print("Slack integration loaded.")
    print(f"Available: {SLACK_AVAILABLE}")
    print(f"User ID: {SLACK_USER_ID}")
    print(f"Channel: {SLACK_CHANNEL}")