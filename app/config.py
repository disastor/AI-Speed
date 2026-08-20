"""
app/config.py

Central configuration for retry/timeout behavior used by orders and payments.
"""

_DEFAULTS = {
    "db_timeout_seconds": 5,
    "max_retries": 3,
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
