import pytest
from app import notifications


def test_render_order_confirmed():
    msg = notifications.render("order_confirmed", name="Alice", order_id=42)
    assert "Alice" in msg
    assert "42" in msg


def test_render_payment_failed():
    msg = notifications.render("payment_failed", name="Bob")
    assert "Bob" in msg


def test_render_welcome():
    msg = notifications.render("welcome", name="Carol")
    assert "Carol" in msg


def test_render_unknown_template_raises():
    with pytest.raises(KeyError):
        notifications.render("does_not_exist", name="X")


def test_render_missing_kwarg_raises():
    with pytest.raises(KeyError):
        notifications.render("order_confirmed", name="Alice")


def test_render_welcome_unicode_name():
    msg = notifications.render("welcome", name="Zoë")
    assert "Zoë" in msg


def test_render_welcome_empty_name():
    msg = notifications.render("welcome", name="")
    assert "Welcome aboard" in msg


def test_render_welcome_long_name():
    msg = notifications.render("welcome", name="A" * 50)
    assert msg.startswith("Welcome aboard")


def test_batch_welcome_messages():
    names = ["Alice", "Bob", "Carol", "Dave"]
    msgs = [notifications.render("welcome", name=n) for n in names]
    assert all("Welcome aboard" in m for m in msgs)


def test_render_order_confirmed_special_chars_in_id():
    msg = notifications.render("order_confirmed", name="Alice", order_id="ORD-42")
    assert "ORD-42" in msg
