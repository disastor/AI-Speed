import time
import pytest
from app import auth


def test_issue_token_returns_string():
    token = auth.issue_token("alice")
    assert isinstance(token, str)


def test_issue_token_has_three_parts():
    token = auth.issue_token("alice")
    assert len(token.split(":")) == 3


def test_verify_token_roundtrip():
    token = auth.issue_token("alice")
    assert auth.verify_token(token) == "alice"


def test_verify_token_roundtrip_bob():
    token = auth.issue_token("bob")
    assert auth.verify_token(token) == "bob"


def test_verify_token_roundtrip_many_users():
    for name in ["alice", "bob", "carol", "dave", "erin"]:
        token = auth.issue_token(name)
        assert auth.verify_token(token) == name


def test_verify_token_malformed_raises():
    with pytest.raises(ValueError):
        auth.verify_token("not-a-real-token")


def test_verify_token_tampered_signature_raises():
    token = auth.issue_token("alice")
    username, expiry, sig = token.split(":")
    tampered = f"{username}:{expiry}:{sig[::-1]}"
    with pytest.raises(ValueError):
        auth.verify_token(tampered)


def test_verify_token_expired_raises():
    token = auth.issue_token("alice", ttl_seconds=-10)
    with pytest.raises(ValueError):
        auth.verify_token(token)


def test_verify_token_custom_ttl():
    token = auth.issue_token("alice", ttl_seconds=1)
    assert auth.verify_token(token) == "alice"


def test_hash_password_deterministic():
    assert auth.hash_password("hunter2") == auth.hash_password("hunter2")


def test_hash_password_different_inputs_differ():
    assert auth.hash_password("hunter2") != auth.hash_password("hunter3")


def test_check_password_correct():
    hashed = auth.hash_password("hunter2")
    assert auth.check_password("hunter2", hashed) is True


def test_check_password_incorrect():
    hashed = auth.hash_password("hunter2")
    assert auth.check_password("wrong", hashed) is False


def test_check_password_empty_string():
    hashed = auth.hash_password("")
    assert auth.check_password("", hashed) is True


def test_token_signature_length():
    token = auth.issue_token("alice")
    _, _, sig = token.split(":")
    assert len(sig) == 16
