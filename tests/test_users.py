import pytest
from app import users


def _fresh(monkeypatch):
    monkeypatch.setattr(users, "_USERS", {})


def test_register_new_user(monkeypatch):
    _fresh(monkeypatch)
    users.register("carol", "hunter2")
    assert "carol" in users._USERS


def test_register_duplicate_raises(monkeypatch):
    _fresh(monkeypatch)
    users.register("carol", "hunter2")
    with pytest.raises(users.UserError):
        users.register("carol", "other-pw")


def test_login_returns_token(monkeypatch):
    _fresh(monkeypatch)
    users.register("carol", "hunter2")
    token = users.login("carol", "hunter2")
    assert isinstance(token, str)


def test_login_wrong_password_raises(monkeypatch):
    _fresh(monkeypatch)
    users.register("carol", "hunter2")
    with pytest.raises(users.UserError):
        users.login("carol", "wrong-password")


def test_login_unknown_user_raises(monkeypatch):
    _fresh(monkeypatch)
    with pytest.raises(users.UserError):
        users.login("ghost", "whatever")


def test_whoami_returns_username(monkeypatch):
    _fresh(monkeypatch)
    users.register("carol", "hunter2")
    token = users.login("carol", "hunter2")
    assert users.whoami(token) == "carol"


def test_whoami_rejects_garbage_token(monkeypatch):
    _fresh(monkeypatch)
    with pytest.raises(ValueError):
        users.whoami("not-a-token")

def test_register_then_login_roundtrip(monkeypatch):
    _fresh(monkeypatch)
    users.register("dave", "correct-horse")
    token = users.login("dave", "correct-horse")
    assert users.whoami(token) == "dave"
