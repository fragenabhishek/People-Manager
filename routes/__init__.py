"""Routes package"""
from .auth_routes import auth_bp
from .person_routes import person_bp
from .ai_routes import ai_bp

__all__ = ['auth_bp', 'person_bp', 'ai_bp']

