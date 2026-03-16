"""
Authentication routes.

POST /auth/register   — Register a new user
POST /auth/login      — Authenticate and receive tokens
POST /auth/refresh-token — Rotate tokens
POST /auth/logout     — Revoke the refresh token
"""
from flask import Blueprint, jsonify, request, current_app

from app.services.user_service import create_user, get_user_by_email
from app.services.token_service import (
    save_refresh_token,
    get_refresh_token,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.utils.auth import generate_access_token, generate_refresh_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Body (JSON):
        username    — string, required
        email_id    — string, required, unique
        password    — string, required
        monthly_budget — int, optional (default 0)
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    # Validate required fields
    for field in ("username", "email_id", "password"):
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required."}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    # Check uniqueness
    if get_user_by_email(data["email_id"]):
        current_app.logger.warning("Failed registration: email %s already exists", data["email_id"])
        return jsonify({"error": "A user with this email already exists."}), 409

    user = create_user(data)
    current_app.logger.info("New user registered: %s (ID: %s)", user.email_id, user.user_id)
    return jsonify({"message": "User registered successfully.", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user.

    Body (JSON):
        email_id — string, required
        password — string, required

    Returns:
        access_token, refresh_token, user info.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    email = data.get("email_id", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "email_id and password are required."}), 400

    user = get_user_by_email(email)
    if not user or not user.check_password(password):
        current_app.logger.warning("Failed login attempt for email: %s", email)
        return jsonify({"error": "Invalid email or password."}), 401

    # Generate tokens
    access_token = generate_access_token(user.user_id)
    refresh_token = generate_refresh_token()
    expiry_days = 30  # Will be read from config in service in prod

    save_refresh_token(user.user_id, refresh_token, expiry_days)

    current_app.logger.info("Successful login for user ID: %s", user.user_id)

    return jsonify({
        "message": "Login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    """
    Rotate tokens.

    Body (JSON):
        user_id       — int, required
        refresh_token — string, required

    Validates the refresh token against the DB.
    Returns a new access_token and refresh_token.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    user_id = data.get("user_id")
    token = data.get("refresh_token", "").strip()

    if not user_id or not token:
        return jsonify({"error": "user_id and refresh_token are required."}), 400

    rt = get_refresh_token(user_id, token)
    if not rt:
        current_app.logger.warning("Failed token refresh: invalid token for user ID %s", user_id)
        return jsonify({"error": "Invalid refresh token."}), 401

    if rt.is_expired():
        revoke_refresh_token(rt)
        current_app.logger.info("Failed token refresh: expired token revoked for user ID %s", user_id)
        return jsonify({"error": "Refresh token has expired. Please log in again."}), 401

    # Rotate
    new_refresh = generate_refresh_token()
    new_access = generate_access_token(user_id)
    rotate_refresh_token(rt, new_refresh, expiry_days=30)

    return jsonify({
        "access_token": new_access,
        "refresh_token": new_refresh,
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Revoke the user's refresh token.

    Body (JSON):
        user_id       — int, required
        refresh_token — string, required
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    user_id = data.get("user_id")
    token = data.get("refresh_token", "").strip()

    if not user_id or not token:
        return jsonify({"error": "user_id and refresh_token are required."}), 400

    rt = get_refresh_token(user_id, token)
    if rt:
        revoke_refresh_token(rt)
        current_app.logger.info("User ID %s logged out (token revoked)", user_id)

    # Always return 200 to avoid user enumeration
    return jsonify({"message": "Logged out successfully."}), 200
