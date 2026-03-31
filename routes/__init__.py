"""Routes package"""
from .auth_routes import auth_bp, init_auth_routes
from .person_routes import person_bp, init_person_routes
from .ai_routes import ai_bp, init_ai_routes
from .note_routes import note_bp, init_note_routes

__all__ = [
    'auth_bp', 'person_bp', 'ai_bp', 'note_bp',
    'init_auth_routes', 'init_person_routes', 'init_ai_routes', 'init_note_routes',
]
