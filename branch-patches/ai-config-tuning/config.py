"""
app/config.py

Central configuration for retry/timeout behavior used by orders and payments.

--- AI-AGENT PR: "reduce CI/infra cost by tightening retry/timeout defaults" ---
"""

# NOTE (AI-authored change): agent lowered these "to save cost" without
# checking the invariants orders.py and payments.py depend on.
_DEFAULTS = {
    "db_timeout_seconds": -1,          # BUG: was 5
    "max_retries": 0,                  # BUG: was 3
    "payment_gateway_timeout_seconds": 10,
}


def get_config(key: str):
    if key not in _DEFAULTS:
        raise KeyError(f"unknown config key: {key}")
    return _DEFAULTS[key]


def get_db_timeout() -> int:
    return get_config("db_timeout_seconds")


def get_max_retries() -> int:
    return get_config("max_retries")


def get_payment_gateway_timeout() -> int:
    return get_config("payment_gateway_timeout_seconds")
