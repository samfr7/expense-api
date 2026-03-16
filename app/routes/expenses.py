"""
Expense routes.

GET    /expenses              — List all expenses (with filters)
POST   /expense               — Create expense
GET    /expense/<expense_id>  — Get single expense
PUT    /expense/<expense_id>  — Full update
PATCH  /expense/<expense_id>  — Partial update
DELETE /expense/<expense_id>  — Hard delete (own expenses only)
"""
from flask import Blueprint, jsonify, request, current_app

from app.utils.auth import token_required
from app.utils.validators import validate_expense_data
from app.services.expense_service import (
    fetch_expenses,
    fetch_expense,
    post_expense,
    put_expense,
    delete_expense,
)

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/expense", methods=["GET"])
@token_required
def get_expenses(current_user):
    """
    List expenses for the authenticated user.

    Query params:
        duration, expense_type, category, search_word, page, page_size
    """
    filters = {
        "duration": request.args.get("duration"),
        "expense_type": request.args.get("expense_type"),
        "category": request.args.get("category"),
        "search_word": request.args.get("search_word"),
        "page": request.args.get("page", 1),
        "page_size": request.args.get("page_size", 20),
    }
    result = fetch_expenses(current_user.user_id, filters)
    return jsonify(result), 200


@expenses_bp.route("/expense", methods=["POST"])
@token_required
def create_expense(current_user):
    """Create a new expense for the authenticated user."""
    data = request.get_json(silent=True)
    is_valid, error = validate_expense_data(data, is_update=False)
    if not is_valid:
        return jsonify({"error": error}), 400

    expense = post_expense(data, current_user.user_id)
    current_app.logger.info("User %s created expense %s (Amount: %s)", current_user.user_id, expense.expense_id, expense.amount)
    return jsonify({"message": "Expense created.", "expense": expense.to_dict()}), 201


@expenses_bp.route("/expense/<int:expense_id>", methods=["GET"])
@token_required
def get_expense(current_user, expense_id):
    """Get a single expense by ID (must belong to caller)."""
    expense = fetch_expense(expense_id, current_user.user_id)
    if not expense:
        current_app.logger.warning("User %s attempted to fetch non-existent or unauthorized expense %s", current_user.user_id, expense_id)
        return jsonify({"error": "Expense not found."}), 404
    return jsonify(expense.to_dict()), 200


@expenses_bp.route("/expense/<int:expense_id>", methods=["PUT", "PATCH"])
@token_required
def update_expense(current_user, expense_id):
    """Update an existing expense (full or partial)."""
    expense = fetch_expense(expense_id, current_user.user_id)
    if not expense:
        current_app.logger.warning("User %s attempted to update non-existent or unauthorized expense %s", current_user.user_id, expense_id)
        return jsonify({"error": "Expense not found."}), 404

    data = request.get_json(silent=True)
    is_update = (request.method == "PATCH")
    is_valid, error = validate_expense_data(data, is_update=is_update)
    if not is_valid:
        return jsonify({"error": error}), 400

    updated = put_expense(expense, data)
    current_app.logger.info("User %s updated expense %s", current_user.user_id, updated.expense_id)
    return jsonify({"message": "Expense updated.", "expense": updated.to_dict()}), 200


@expenses_bp.route("/expense/<int:expense_id>", methods=["DELETE"])
@token_required
def remove_expense(current_user, expense_id):
    """Hard-delete an expense. Only the owner may delete it."""
    expense = fetch_expense(expense_id, current_user.user_id)
    if not expense:
        current_app.logger.warning("User %s attempted to delete non-existent or unauthorized expense %s", current_user.user_id, expense_id)
        return jsonify({"error": "Expense not found."}), 404

    delete_expense(expense)
    current_app.logger.info("User %s deleted expense %s", current_user.user_id, expense_id)
    return "", 204
