"""
Expense model.
"""
import enum
from datetime import date
from app.extensions import db


class ExpenseType(enum.Enum):
    Credit = "Credit"
    Debit = "Debit"


class ExpenseCategory(enum.Enum):
    Groceries = "Groceries"
    Leisure = "Leisure"
    Electronics = "Electronics"
    Utilities = "Utilities"
    Clothing = "Clothing"
    Health = "Health"
    Others = "Others"


class Expense(db.Model):
    __tablename__ = "expenses"

    expense_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_on = db.Column(db.Date, nullable=False, default=date.today)
    type = db.Column(db.Enum(ExpenseType), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(
        db.Enum(ExpenseCategory), nullable=True, default=ExpenseCategory.Others
    )
    amount = db.Column(db.Integer, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "expense_id": self.expense_id,
            "created_on": self.created_on.isoformat() if self.created_on else None,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "category": self.category.value if self.category else None,
            "amount": self.amount,
            "user_id": self.user_id,
        }

    def __repr__(self) -> str:
        return f"<Expense {self.expense_id}: {self.title} ({self.type.value})>"
