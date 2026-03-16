"""
JWT utilities and the token_required decorator.

Uses PyJWT for access tokens and secrets.token_urlsafe() for refresh tokens.
"""
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Callable

import jwt
from flask import current_app, jsonify, request


def generate_access_token(user_id: int) -> str:
    """
    Generate a short-lived JWT access token.

    Payload:
        sub  — user primary key
        iat  — issued at (UTC)
        exp  — expiry (UTC)
    """
    expiry_minutes = current_app.config.get("ACCESS_TOKEN_EXPIRY_MINUTES", 60)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=expiry_minutes),
    }
    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return token


def generate_refresh_token() -> str:
    """
    Generate a cryptographically secure refresh token string.
    Not a JWT — stored in the DB and compared on refresh.
    """
    return secrets.token_urlsafe(64)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Returns:
        Decoded payload dict.

    Raises:
        jwt.ExpiredSignatureError  — token is expired
        jwt.InvalidTokenError      — token is otherwise invalid
    """
    return jwt.decode(
        token,
        current_app.config["SECRET_KEY"],
        algorithms=["HS256"],
    )


def token_required(f: Callable) -> Callable:
    """
    Decorator that validates the JWT access token from the
    Authorization: Bearer <token> header and injects the
    authenticated user as `current_user` into the route.

    Usage::

        @expenses_bp.route("/expenses")
        @token_required
        def get_expenses(current_user):
            ...
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"error": "Unauthorized", "message": "Missing or malformed Authorization header."}),
                401,
            )

        token = auth_header.split(" ", 1)[1]

        try:
            payload = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            return (
                jsonify({"error": "Unauthorized", "message": "Access token has expired."}),
                401,
            )
        except jwt.InvalidTokenError as exc:
            return (
                jsonify({"error": "Unauthorized", "message": f"Invalid token: {exc}"}),
                401,
            )

        # Lazy import to avoid circular dependency
        from app.services.user_service import get_user

        user = get_user(payload["sub"])
        if user is None:
            return (
                jsonify({"error": "Unauthorized", "message": "User not found."}),
                401,
            )

        return f(current_user=user, *args, **kwargs)

    return decorated
