"""Routes package"""
from .ai_routes import ai_bp
from .auth_routes import auth_bp
from .note_routes import note_bp
from .person_routes import person_bp

__all__ = ['auth_bp', 'person_bp', 'ai_bp', 'note_bp']
