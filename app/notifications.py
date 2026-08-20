"""
app/notifications.py

Simple templated notification formatting. Deliberately independent of
auth/config so it demonstrates an isolated third root cause.
"""

_TEMPLATES = {
    "order_confirmed": "Hi {name}, your order #{order_id} is confirmed.",
    "payment_failed": "Hi {name}, we couldn't process your payment.",
    "welcome": "Welcome aboard, {name}!",
}


def render(template_name: str, **kwargs) -> str:
    if template_name not in _TEMPLATES:
        raise KeyError(f"unknown template: {template_name}")
    return _TEMPLATES[template_name].format(**kwargs)
