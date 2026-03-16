import pytest
from app.services.user_service import create_user, get_user_by_email
from app.services.expense_service import post_expense, fetch_expenses


def test_user_service_create(app):
    with app.app_context():
        data = {
            "username": "Bob",
            "email_id": "bob@example.com",
            "password": "secure"
        }
        user = create_user(data)
        assert user.user_id is not None
        assert user.username == "Bob"
        
        # Verify check_password works after creation
        assert user.check_password("secure") is True


def test_expense_service_post_and_fetch(app, test_user):
    with app.app_context():
        # The test_user fixture creates user with ID 1 usually
        user = get_user_by_email("test@example.com")
        
        data = {
            "type": "Debit",
            "title": "Pizza",
            "amount": 20,
            "category": "Groceries"
        }
        
        expense = post_expense(data, user.user_id)
        assert expense.expense_id is not None
        assert expense.amount == 20
        
        # Test fetch
        results = fetch_expenses(user.user_id, filters={"expense_type": "Debit"})
        assert results["total"] == 1
        assert results["expenses"][0]["title"] == "Pizza"
