"""
app/users.py

Basic user registration/login built on top of app.auth.
"""
from app import auth

_USERS = {}


class UserError(Exception):
    pass


def register(username: str, password: str) -> None:
    if username in _USERS:
        raise UserError("username already taken")
    _USERS[username] = auth.hash_password(password)


def login(username: str, password: str) -> str:
    if username not in _USERS:
        raise UserError("no such user")
    if not auth.check_password(password, _USERS[username]):
        raise UserError("incorrect password")
    return auth.issue_token(username)


def whoami(token: str) -> str:
    return auth.verify_token(token)
