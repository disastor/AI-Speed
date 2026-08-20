import pytest
from app import auth, payments


def _token():
    return auth.issue_token("alice")


def test_charge_returns_charged_status():
    result = payments.charge(_token(), 500)
    assert result["status"] == "charged"


def test_charge_includes_username():
    result = payments.charge(_token(), 500)
    assert result["user"] == "alice"


def test_charge_rejects_zero_amount():
    with pytest.raises(payments.PaymentError):
        payments.charge(_token(), 0)


def test_charge_rejects_negative_amount():
    with pytest.raises(payments.PaymentError):
        payments.charge(_token(), -100)


def test_charge_rejects_invalid_token():
    with pytest.raises(ValueError):
        payments.charge("garbage-token", 500)


def test_charge_uses_configured_timeout():
    result = payments.charge(_token(), 500)
    assert result["timeout_used"] == 10


def test_charge_uses_configured_retries():
    result = payments.charge(_token(), 500)
    assert result["retries_allowed"] == 3


def test_refund_matches_original_payer():
    charge_ref = payments.charge(_token(), 500)
    result = payments.refund(_token(), charge_ref)
    assert result["status"] == "refunded"


def test_refund_rejects_mismatched_payer():
    charge_ref = payments.charge(_token(), 500)
    bob_token = auth.issue_token("bob")
    with pytest.raises(payments.PaymentError):
        payments.refund(bob_token, charge_ref)


def test_refund_preserves_amount():
    charge_ref = payments.charge(_token(), 750)
    result = payments.refund(_token(), charge_ref)
    assert result["amount_cents"] == 750


def test_charge_large_amount():
    result = payments.charge(_token(), 1_000_000)
    assert result["amount_cents"] == 1_000_000


def test_charge_returns_amount_field():
    result = payments.charge(_token(), 500)
    assert "amount_cents" in result
