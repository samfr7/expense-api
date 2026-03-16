"""
RefreshToken model.
"""
from app.extensions import db


class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=False
    )
    refresh_token = db.Column(db.Text, nullable=False, unique=True)
    expiry_time = db.Column(db.DateTime, nullable=False)

    def is_expired(self) -> bool:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expiry_time.replace(
            tzinfo=timezone.utc
        )

    def to_dict(self) -> dict:
        return {
            "token_id": self.token_id,
            "user_id": self.user_id,
            "expiry_time": self.expiry_time.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<RefreshToken {self.token_id} for user {self.user_id}>"
