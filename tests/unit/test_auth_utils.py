import time
import jwt
import pytest
from flask import current_app

from app.utils.auth import generate_access_token, decode_access_token


def test_generate_and_decode_token(app):
    with app.app_context():
        token = generate_access_token(user_id=42)
        payload = decode_access_token(token)
        
        assert payload["sub"] == 42
        assert "exp" in payload
        assert "iat" in payload


def test_decode_expired_token(app):
    with app.app_context():
        # Temporarily force expiry to testing min (5 mins in TestingConfig)
        current_app.config["ACCESS_TOKEN_EXPIRY_MINUTES"] = -1
        
        token = generate_access_token(user_id=1)
        
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(token)


def test_decode_invalid_token(app):
    with app.app_context():
        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token("this.is.not.a.valid.jwt")
