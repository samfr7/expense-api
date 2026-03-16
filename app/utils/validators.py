"""
Input validation helpers for expenses and users.
Returns (is_valid: bool, error_message: str | None).
"""
from app.models.expense import ExpenseType, ExpenseCategory


# ---------------------------------------------------------------------------
# Expense validation
# ---------------------------------------------------------------------------

EXPENSE_REQUIRED_FIELDS = {"type", "title", "amount"}
VALID_EXPENSE_TYPES = {e.value for e in ExpenseType}
VALID_EXPENSE_CATEGORIES = {c.value for c in ExpenseCategory}


def validate_expense_data(data: dict, is_update: bool = False) -> tuple[bool, str | None]:
    """
    Validate expense payload.

    Args:
        data:      Request JSON body.
        is_update: If True, required fields are not enforced (partial update).

    Returns:
        (True, None) if valid, (False, error_message) otherwise.
    """
    if not data:
        return False, "Request body must be JSON."

    if not is_update:
        missing = EXPENSE_REQUIRED_FIELDS - data.keys()
        if missing:
            return False, f"Missing required fields: {', '.join(sorted(missing))}."

    # Validate type enum
    if "type" in data:
        if data["type"] not in VALID_EXPENSE_TYPES:
            return (
                False,
                f"Invalid expense type '{data['type']}'. "
                f"Must be one of: {', '.join(sorted(VALID_EXPENSE_TYPES))}.",
            )

    # Set default category to 'Others' if missing or invalid
    if data.get("category") not in VALID_EXPENSE_CATEGORIES:
        data["category"] = "Others"

    # Validate amount
    if "amount" in data:
        try:
            amount = int(data["amount"])
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return False, "Amount must be a positive integer."

    # Validate title
    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return False, "Title must be a non-empty string."

    return True, None


# ---------------------------------------------------------------------------
# User validation
# ---------------------------------------------------------------------------

USER_ALLOWED_UPDATE_FIELDS = {"username", "monthly_budget"}
USER_BLOCKED_FIELDS = {"email_id", "email", "password", "password_hash", "role"}


def validate_user_update_data(data: dict) -> tuple[bool, str | None]:
    """
    Validate user update payload.
    Email modification is explicitly blocked.

    Returns:
        (True, None) if valid, (False, error_message) otherwise.
    """
    if not data:
        return False, "Request body must be JSON."

    blocked = USER_BLOCKED_FIELDS & data.keys()
    if blocked:
        return (
            False,
            f"The following fields cannot be modified: {', '.join(sorted(blocked))}.",
        )

    unknown = data.keys() - USER_ALLOWED_UPDATE_FIELDS
    if unknown:
        return (
            False,
            f"Unknown or disallowed fields: {', '.join(sorted(unknown))}. "
            f"Allowed fields: {', '.join(sorted(USER_ALLOWED_UPDATE_FIELDS))}.",
        )

    if "username" in data:
        if not isinstance(data["username"], str) or not data["username"].strip():
            return False, "Username must be a non-empty string."
        if len(data["username"]) > 120:
            return False, "Username must not exceed 120 characters."

    if "monthly_budget" in data:
        try:
            budget = int(data["monthly_budget"])
            if budget < 0:
                raise ValueError
        except (TypeError, ValueError):
            return False, "Monthly budget must be a non-negative integer."

    return True, None
