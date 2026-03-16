"""
Expense DB service layer.
All database interactions for the Expense model live here.
"""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, or_

from app.extensions import db
from app.models.expense import Expense, ExpenseType, ExpenseCategory
# If ExpenseType or ExpenseCategory was not defined separately, another logic should have been written here


def fetch_expense(expense_id: int, user_id: int) -> Optional[Expense]:
    """Fetch a single expense by ID, scoped to the authenticated user."""
    return Expense.query.filter_by(expense_id=expense_id, user_id=user_id).first()


def fetch_expenses(user_id: int, filters: dict) -> dict:
    """
    Fetch paginated, filtered list of expenses for a user.

    Supported filter keys:
        duration     — 'lastweek', 'lastmonth', or 'YYYY-MM-DD,YYYY-MM-DD'
        expense_type — 'Credit' or 'Debit'
        category     — any ExpenseCategory value
        search_word  — partial match on title/description
        page         — page number (default 1)
        page_size    — items per page (default 20, max 100)
    """
    query = Expense.query.filter_by(user_id=user_id)

    # Duration filter
    duration = filters.get("duration")
    if duration:
        today = date.today()
        if duration == "lastweek":
            query = query.filter(Expense.created_on >= today - timedelta(days=7))
        elif duration == "lastmonth":
            query = query.filter(Expense.created_on >= today - timedelta(days=30))
        else:
            # Expect "YYYY-MM-DD,YYYY-MM-DD"
            try:
                start_str, end_str = duration.split(",")
                start = date.fromisoformat(start_str.strip())
                end = date.fromisoformat(end_str.strip())
                query = query.filter(Expense.created_on.between(start, end))
            except (ValueError, AttributeError):
                pass  # Ignore malformed date ranges

    # Expense type filter
    expense_type = filters.get("expense_type")
    if expense_type:
        try:
            query = query.filter(Expense.type == ExpenseType(expense_type))
        except ValueError:
            pass

    # Category filter
    category = filters.get("category")
    if category:
        try:
            query = query.filter(Expense.category == ExpenseCategory(category))
        except ValueError:
            pass

    # Search filter — title or description
    search_word = filters.get("search_word")
    if search_word:
        like_pattern = f"%{search_word}%"
        query = query.filter(
            or_(
                Expense.title.ilike(like_pattern),
                Expense.description.ilike(like_pattern),
            )
        )

    # Order by most recent first
    query = query.order_by(Expense.created_on.desc(), Expense.expense_id.desc())

    # Pagination
    try:
        page = max(1, int(filters.get("page", 1)))
        page_size = min(100, max(1, int(filters.get("page_size", 20))))
    except (TypeError, ValueError):
        page, page_size = 1, 20

    paginated = query.paginate(page=page, per_page=page_size, error_out=False)

    return {
        "expenses": [e.to_dict() for e in paginated.items],
        "total": paginated.total,
        "page": paginated.page,
        "page_size": page_size,
        "pages": paginated.pages,
    }


def post_expense(data: dict, user_id: int) -> Expense:
    """Create and persist a new expense."""
    expense = Expense(
        type=ExpenseType(data["type"]),
        title=data["title"].strip(),
        description=data.get("description"),
        category=ExpenseCategory(data["category"]),
        amount=int(data["amount"]),
        created_on=date.today(),
        user_id=user_id,
    )
    db.session.add(expense)
    db.session.commit()
    return expense


def put_expense(expense: Expense, data: dict) -> Expense:
    """Update mutable fields of an existing expense."""
    if "type" in data:
        expense.type = ExpenseType(data["type"])
    if "title" in data:
        expense.title = data["title"].strip()
    if "description" in data:
        expense.description = data["description"]
    if "category" in data:
        expense.category = ExpenseCategory(data["category"]) if data["category"] else None
    if "amount" in data:
        expense.amount = int(data["amount"])
    if "created_on" in data:
        expense.created_on = date.fromisoformat(data["created_on"])

    db.session.commit()
    return expense


def delete_expense(expense: Expense) -> None:
    """Hard-delete an expense record."""
    db.session.delete(expense)
    db.session.commit()


def fetch_money_spent_received(user_id: int) -> dict:
    """
    Return total Credit and Debit amounts for a user.

    Executes:
        SELECT type, SUM(amount) FROM expenses WHERE user_id=? GROUP BY type
    """
    results = (
        db.session.query(Expense.type, func.sum(Expense.amount))
        .filter(Expense.user_id == user_id)
        .group_by(Expense.type)
        .all()
    )

    totals = {"Credit": 0, "Debit": 0}
    for expense_type, total in results:
        totals[expense_type.value] = total or 0

    return totals
