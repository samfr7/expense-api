"""
User routes.

GET   /users/<user_id>  — Get user profile
PUT   /users/<user_id>  — Full update of allowed fields
PATCH /users/<user_id>  — Partial update of allowed fields
"""
from flask import Blueprint, jsonify, request, current_app

from app.utils.auth import token_required
from app.utils.validators import validate_user_update_data
from app.services.user_service import get_user, put_user

users_bp = Blueprint("users", __name__)


@users_bp.route("/users/<int:user_id>", methods=["GET"])
@token_required
def get_user_profile(current_user, user_id):
    """
    Fetch user details.
    Any authenticated user can view their own profile.
    Admins can view any user's profile.
    """
    if current_user.user_id != user_id and current_user.role.value != "admin":
        current_app.logger.warning("Unauthorized profile view attempt: User %s tried to view User %s", current_user.user_id, user_id)
        return jsonify({"error": "Access denied."}), 403

    user = get_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    return jsonify(user.to_dict()), 200


@users_bp.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
@token_required
def update_user_profile(current_user, user_id):
    """
    Update user profile.
    Only the account owner (or admin) may update.
    Email cannot be changed.
    On budget change, the Redis cache is updated.
    """
    if current_user.user_id != user_id and current_user.role.value != "admin":
        current_app.logger.warning("Unauthorized profile update attempt: User %s tried to update User %s", current_user.user_id, user_id)
        return jsonify({"error": "Access denied."}), 403

    user = get_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    data = request.get_json(silent=True)
    is_valid, error = validate_user_update_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    updated = put_user(user, data)
        
    current_app.logger.info("User %s updated profile for User %s", current_user.user_id, updated.user_id)

    return jsonify({"message": "User updated.", "user": updated.to_dict()}), 200
