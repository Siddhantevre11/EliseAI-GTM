"""
integrations/__init__.py — Integration registry for EliseAI GTM

Manages all external integrations: Google Sheets, Slack, Webhook.
"""

from typing import Optional, Callable
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

import os
SLACK_ENABLED = bool(os.getenv("SLACK_BOT_TOKEN"))
WEBHOOK_ENABLED = bool(os.getenv("WEBHOOK_URL"))
SHEETS_ENABLED = bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))


class IntegrationRegistry:
    """Registry for managing integration callbacks."""
    
    def __init__(self):
        self._callbacks = {}
        self._enabled = {}
    
    def register(self, name: str, enabled: bool = True):
        """Decorator to register an integration."""
        def decorator(func: Callable):
            self._callbacks[name] = func
            self._enabled[name] = enabled
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not enabled:
                    return None
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def is_enabled(self, name: str) -> bool:
        """Check if integration is enabled."""
        return self._enabled.get(name, False)
    
    def execute(self, name: str, *args, **kwargs):
        """Execute an integration callback."""
        if not self._enabled.get(name, False):
            return None
        callback = self._callbacks.get(name)
        if callback:
            return callback(*args, **kwargs)
        return None
    
    def list_integrations(self) -> list[str]:
        """List all registered integrations."""
        return list(self._callbacks.keys())


# Global registry
registry = IntegrationRegistry()


# Import and register integrations
def _init_integrations():
    """Initialize and register integrations."""
    global registry
    
    # Register Slack
    if SLACK_ENABLED:
        from integrations.slack import send_lead_alert as slack_callback
        registry._callbacks["slack"] = slack_callback
        registry._enabled["slack"] = True
    
    # Register Webhook
    if WEBHOOK_ENABLED:
        from integrations.webhook import send_to_webhook as webhook_callback
        registry._callbacks["webhook"] = webhook_callback
        registry._enabled["webhook"] = True
    
    # Register Sheets
    if SHEETS_ENABLED:
        from integrations.sheets import write_result_to_sheet as sheets_callback
        registry._callbacks["sheets"] = sheets_callback
        registry._enabled["sheets"] = True


def trigger_integrations(result: dict, lead: dict) -> dict:
    """Trigger all enabled integrations for a result."""
    triggered = []
    
    # Initialize integrations
    _init_integrations()
    
    # Slack: Alert on Tier A or NEEDS_REVIEW
    if registry.is_enabled("slack"):
        tier = result.get("tier")
        if tier == "A" or result.get("_needs_manual_review"):
            try:
                slack_result = registry.execute("slack", result, lead)
                if slack_result:
                    triggered.append("slack")
            except Exception:
                pass
    
    # Webhook: POST on Tier A
    if registry.is_enabled("webhook"):
        if result.get("tier") == "A":
            try:
                webhook_result = registry.execute("webhook", result, lead)
                if webhook_result:
                    triggered.append("webhook")
            except Exception:
                pass
    
    # Sheets: Write all results (handled separately)
    if registry.is_enabled("sheets"):
        try:
            sheets_result = registry.execute("sheets", result, lead)
            if sheets_result:
                triggered.append("sheets")
        except Exception:
            pass
    
    result["_integrations_triggered"] = triggered
    return result


__all__ = ["IntegrationRegistry", "registry", "trigger_integrations", "SLACK_ENABLED", "WEBHOOK_ENABLED", "SHEETS_ENABLED"]