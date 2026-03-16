from app.routes.auth import auth_bp
from app.routes.expenses import expenses_bp
from app.routes.users import users_bp
from app.routes.analytics import analytics_bp

__all__ = ["auth_bp", "expenses_bp", "users_bp", "analytics_bp"]
