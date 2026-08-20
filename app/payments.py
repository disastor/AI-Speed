"""
app/payments.py

Payment processing. Depends on auth (to identify the paying user) and
config (for gateway timeout/retry behavior).
"""
from app import auth, config


class PaymentError(Exception):
    pass


def charge(token: str, amount_cents: int) -> dict:
    if amount_cents <= 0:
        raise PaymentError("amount must be positive")

    username = auth.verify_token(token)  # raises ValueError if invalid

    timeout = config.get_payment_gateway_timeout()
    retries = config.get_max_retries()

    return {
        "user": username,
        "amount_cents": amount_cents,
        "status": "charged",
        "timeout_used": timeout,
        "retries_allowed": retries,
    }


def refund(token: str, charge_ref: dict) -> dict:
    username = auth.verify_token(token)
    if charge_ref["user"] != username:
        raise PaymentError("refund requester does not match original payer")
    return {"status": "refunded", "amount_cents": charge_ref["amount_cents"]}
