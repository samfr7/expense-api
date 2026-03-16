"""
Application logging configuration.
Sets up a RotatingFileHandler to write logs to a file,
and a StreamHandler to output to the console.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask


def setup_logging(app: Flask) -> None:
    """
    Configures the Flask logger with formatting and file rotation.
    Reads 'LOG_FILE_PATH' and 'LOG_LEVEL' from app.config.
    """
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    app.logger.setLevel(log_level)

    # Don't add handlers multiple times (e.g., during testing/reloading)
    if app.logger.handlers:
        return

    # Create log directory if it doesn't exist
    log_file_path = app.config.get("LOG_FILE_PATH", "logs/expense_api.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # File Handler: 10 MB per file, keep 5 backups
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Attach to the Flask app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # In production don't bubble up to the root logger to avoid duplicate logs in console
    app.logger.propagate = False
    
    app.logger.info("Logging initialized at level: %s", log_level_name)
