from app.utils.validators import validate_expense_data, validate_user_update_data

def test_expense_validator_valid():
    data = {"type": "Debit", "title": "Coffee", "amount": 5, "category": "Groceries"}
    is_valid, error = validate_expense_data(data)
    assert is_valid is True
    assert error is None

def test_expense_validator_missing_fields():
    data = {"title": "Coffee"}
    is_valid, error = validate_expense_data(data)
    assert is_valid is False
    assert "Missing required fields" in error

def test_expense_validator_invalid_type():
    data = {"type": "Unknown", "title": "Coffee", "amount": 5}
    is_valid, error = validate_expense_data(data)
    assert is_valid is False
    assert "Invalid expense type" in error

def test_user_validator_blocked_fields():
    data = {"email_id": "new@example.com"}
    is_valid, error = validate_user_update_data(data)
    assert is_valid is False
    assert "cannot be modified" in error
