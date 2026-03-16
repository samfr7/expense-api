"""
Analytics routes.

GET /analytics/<user_id> — Summary of spending vs. budget
"""
from flask import Blueprint, jsonify, current_app

from app.utils.auth import token_required
from app.services.expense_service import fetch_money_spent_received
from app.services.user_service import get_user

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics/<int:user_id>", methods=["GET"])
@token_required
def get_analytics(current_user, user_id):
    """
    Return spending analytics for a user.

    Response:
        money_spent    — total Debit amount
        money_received — total Credit amount
        monthly_budget — from Redis cache (falls back to DB value)
        balance        — monthly_budget - money_spent + money_received
    """
    if current_user.user_id != user_id and current_user.role.value != "admin":
        current_app.logger.warning("Unauthorized analytics access attempt: User %s tried to view User %s", current_user.user_id, user_id)
        return jsonify({"error": "Access denied."}), 403

    user = get_user(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Aggregate spend/received from DB
    totals = fetch_money_spent_received(user_id)
    money_spent = totals.get("Debit", 0)
    money_received = totals.get("Credit", 0)

    # Try Redis first, fall back to DB
    # Pertaining to user feedback: user is already fetched, no need for Redis
    monthly_budget = user.monthly_budget or 0

    balance = monthly_budget - money_spent + money_received
    
    current_app.logger.info("User %s requested analytics for User %s", current_user.user_id, user_id)

    return jsonify({
        "user_id": user_id,
        "monthly_budget": monthly_budget,
        "money_spent": money_spent,
        "money_received": money_received,
        "balance": balance,
    }), 200
