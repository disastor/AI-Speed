"""
app/notifications.py

Simple templated notification formatting.

--- AI-AGENT PR: "rename templates for consistency" ---
"""

# NOTE (AI-authored change): agent renamed "welcome" to "welcome_message"
# for "naming consistency" but didn't update callers.
_TEMPLATES = {
    "order_confirmed": "Hi {name}, your order #{order_id} is confirmed.",
    "payment_failed": "Hi {name}, we couldn't process your payment.",
    "welcome_message": "Welcome aboard, {name}!",   # BUG: was "welcome"
}


def render(template_name: str, **kwargs) -> str:
    if template_name not in _TEMPLATES:
        raise KeyError(f"unknown template: {template_name}")
    return _TEMPLATES[template_name].format(**kwargs)
