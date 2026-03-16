"""
RefreshToken DB service layer.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.extensions import db
from app.models.token import RefreshToken


def _expiry(days: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def save_refresh_token(
    user_id: int,
    token: str,
    expiry_days: int,
) -> RefreshToken:
    """Persist a new refresh token."""
    rt = RefreshToken(
        user_id=user_id,
        refresh_token=token,
        expiry_time=_expiry(expiry_days),
    )
    db.session.add(rt)
    db.session.commit()
    return rt


def get_refresh_token(user_id: int, token: str) -> Optional[RefreshToken]:
    """Look up a specific refresh token for a user."""
    return RefreshToken.query.filter_by(
        user_id=user_id, refresh_token=token
    ).first()


def revoke_refresh_token(rt: RefreshToken) -> None:
    """Delete (revoke) a single refresh token."""
    db.session.delete(rt)
    db.session.commit()


def revoke_all_user_tokens(user_id: int) -> None:
    """Revoke ALL refresh tokens for a user (e.g. password change, account lock)."""
    RefreshToken.query.filter_by(user_id=user_id).delete()
    db.session.commit()


def rotate_refresh_token(
    old_rt: RefreshToken,
    new_token: str,
    expiry_days: int,
) -> RefreshToken:
    """
    Token rotation: delete the old refresh token and issue a new one.
    This prevents refresh token reuse.
    """
    user_id = old_rt.user_id
    db.session.delete(old_rt)
    db.session.flush()  # Ensure old is gone before inserting new

    new_rt = RefreshToken(
        user_id=user_id,
        refresh_token=new_token,
        expiry_time=_expiry(expiry_days),
    )
    db.session.add(new_rt)
    db.session.commit()
    return new_rt
