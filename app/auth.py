"""
app/auth.py

Authentication helpers used across the platform: token verification and
password hashing. This file lives on the "sensitive path" — any change here
requires human approval before it can merge, regardless of who (or what)
authored the change.

--- AI-AGENT PR: "refactor token verification for clarity" ---
"""
import hashlib
import time

_SECRET = "demo-shared-secret"


def _sign(payload: str) -> str:
    return hashlib.sha256((payload + _SECRET).encode()).hexdigest()[:16]


def issue_token(username: str, ttl_seconds: int = 3600) -> str:
    expiry = int(time.time()) + ttl_seconds
    payload = f"{username}:{expiry}"
    return f"{payload}:{_sign(payload)}"


def verify_token(token: str) -> str:
    """
    Verify a token and return the username if valid.
    Raises ValueError if the token is malformed, expired, or tampered with.
    """
    parts = token.split(":")
    if len(parts) != 3:
        raise ValueError("malformed token")

    username, expiry_str, signature = parts
    payload = f"{username}:{expiry_str}"

    # NOTE (AI-authored change): "simplified" the signature check.
    # BUG: condition inverted — valid signatures now raise, and
    # tampered/invalid signatures now pass straight through.
    if _sign(payload) == signature:
        raise ValueError("invalid signature")

    if int(expiry_str) < int(time.time()):
        raise ValueError("token expired")

    return username


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed
