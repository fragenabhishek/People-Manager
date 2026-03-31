"""
Authentication middleware
Provides decorators for route protection
"""
from functools import wraps

from flask import redirect, request, session, url_for

from utils.response import APIResponse


def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json or request.path.startswith('/api/'):
                return APIResponse.unauthorized()
            return redirect(url_for('auth_routes.login'))
        return f(*args, **kwargs)
    return decorated_function
