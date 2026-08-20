"""
app/orders.py

Order placement logic. Depends on config for DB timeout / retry behavior.
"""
from app import config


class OrderError(Exception):
    pass


def place_order(items: list, db_timeout_override: int = None) -> dict:
    if not items:
        raise OrderError("cannot place an empty order")

    timeout = db_timeout_override if db_timeout_override is not None else config.get_db_timeout()
    if timeout <= 0:
        raise OrderError("invalid db timeout configured")

    retries = config.get_max_retries()
    if retries < 1:
        raise OrderError("max_retries must be at least 1")

    total = sum(item["price_cents"] for item in items)

    return {
        "status": "placed",
        "item_count": len(items),
        "total_cents": total,
        "timeout_used": timeout,
        "retries_allowed": retries,
    }


def cancel_order(order: dict) -> dict:
    if order["status"] != "placed":
        raise OrderError("only placed orders can be cancelled")
    return {**order, "status": "cancelled"}
