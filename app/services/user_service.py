"""
User DB service layer.
"""
from typing import Optional

from app.extensions import db
from app.models.user import User


def create_user(data: dict) -> User:
    """
    Create and persist a new user.

    Args:
        data: dict with keys: username, email_id, password,
              optionally: role, monthly_budget
    """
    user = User(
        username=data["username"].strip(),
        email_id=data["email_id"].strip().lower(),
        role=data.get("role", "user"),
        monthly_budget=data.get("monthly_budget", 0),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    
    db.session.refresh(user)
    
    return user


def get_user(user_id: int) -> Optional[User]:
    """Fetch a user by primary key."""
    return User.query.get(user_id)


def get_user_by_email(email: str) -> Optional[User]:
    """Fetch a user by email (case-insensitive)."""
    return User.query.filter(
        User.email_id == email.strip().lower()
    ).first()


def put_user(user: User, data: dict) -> User:
    """
    Update allowed user fields.
    Caller must have already validated that email is not in data.
    """
    if "username" in data:
        user.username = data["username"].strip()
    if "monthly_budget" in data:
        user.monthly_budget = int(data["monthly_budget"])

    db.session.commit()
    return user


def delete_user(user: User) -> None:
    """Hard-delete a user (cascade removes expenses and tokens)."""
    db.session.delete(user)
    db.session.commit()
