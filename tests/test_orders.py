import pytest
from app import orders


def _items():
    return [{"sku": "A1", "price_cents": 500}, {"sku": "B2", "price_cents": 250}]


def test_place_order_returns_placed_status():
    result = orders.place_order(_items())
    assert result["status"] == "placed"


def test_place_order_sums_total():
    result = orders.place_order(_items())
    assert result["total_cents"] == 750


def test_place_order_counts_items():
    result = orders.place_order(_items())
    assert result["item_count"] == 2


def test_place_order_rejects_empty():
    with pytest.raises(orders.OrderError):
        orders.place_order([])


def test_place_order_uses_configured_timeout():
    result = orders.place_order(_items())
    assert result["timeout_used"] == 5


@pytest.mark.slow
def test_place_order_uses_configured_retries():
    result = orders.place_order(_items())
    assert result["retries_allowed"] == 3


def test_place_order_honors_timeout_override():
    result = orders.place_order(_items(), db_timeout_override=15)
    assert result["timeout_used"] == 15


def test_cancel_order_changes_status():
    order = orders.place_order(_items())
    cancelled = orders.cancel_order(order)
    assert cancelled["status"] == "cancelled"


def test_cancel_order_rejects_already_cancelled():
    order = orders.place_order(_items())
    cancelled = orders.cancel_order(order)
    with pytest.raises(orders.OrderError):
        orders.cancel_order(cancelled)


def test_place_order_single_item():
    result = orders.place_order([{"sku": "Z9", "price_cents": 100}])
    assert result["total_cents"] == 100
