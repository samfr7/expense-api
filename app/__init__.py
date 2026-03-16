"""
App factory — creates and configures the Flask application.
"""
import os
from flask import Flask
from dotenv import load_dotenv

# Load env vars BEFORE importing config!
load_dotenv()

from app.extensions import db, migrate, cors
from app.logger import setup_logging
from config import config_map


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function.

    Args:
        config_name: One of 'development', 'testing', 'production'.
                     Falls back to FLASK_ENV env var, then 'default'.

    Returns:
        A configured Flask application instance.
    """
    app = Flask(__name__)
    
    # Determine config to load
    env = config_name or os.environ.get("FLASK_ENV", "development")
    cfg = config_map.get(env, config_map["default"])
    app.config.from_object(cfg)

    # Setup Logging
    setup_logging(app)

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    return app


def _register_blueprints(app: Flask) -> None:
    from app.routes.auth import auth_bp
    from app.routes.expenses import expenses_bp
    from app.routes.users import users_bp
    from app.routes.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(analytics_bp)


def _register_error_handlers(app: Flask) -> None:
    from flask import jsonify

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": str(e)}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "message": str(e)}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": str(e)}), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({"error": "Conflict", "message": str(e)}), 409

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
        
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Catch hard crashes (like DB disconnects) and force JSON instead of HTML
        return jsonify({"error": "Unexpected Server Error", "message": "The server encountered an unexpected condition that prevented it from fulfilling the request."}), 500
