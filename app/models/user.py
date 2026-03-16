"""
User model.
"""
import enum
import bcrypt
from app.extensions import db


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), nullable=False)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.user)
    monthly_budget = db.Column(db.Integer, nullable=True, default=0)

    # Relationships
    expenses = db.relationship(
        "Expense", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    refresh_tokens = db.relationship(
        "RefreshToken", backref="owner", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, plain_password: str) -> None:
        """Hash and store the password using bcrypt."""
        self.password_hash = bcrypt.hashpw(
            plain_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email_id": self.email_id,
            "role": self.role.value,
            "monthly_budget": self.monthly_budget,
        }

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email_id})>"
