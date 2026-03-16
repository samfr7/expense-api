import os
from datetime import timedelta


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Prevent SSL disconnections by validating connections before use
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    
    ACCESS_TOKEN_EXPIRY_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRY_MINUTES", 60))
    REFRESH_TOKEN_EXPIRY_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRY_DAYS", 30))
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "logs/expense_api.log")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class TestingConfig(Config):
    """Testing configuration — uses SQLite in-memory, no Redis needed."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Disable CSRF for tests
    WTF_CSRF_ENABLED = False
    # Use short-lived tokens for easier testing
    ACCESS_TOKEN_EXPIRY_MINUTES = 5
    REFRESH_TOKEN_EXPIRY_DAYS = 1


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    @classmethod
    def validate(cls):
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL environment variable is not set.")


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
