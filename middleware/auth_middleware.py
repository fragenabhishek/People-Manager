"""
Authentication middleware
Provides decorators for route protection
"""
from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """
    Decorator to protect routes that require authentication
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "This is protected"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_routes.login'))
        return f(*args, **kwargs)
    return decorated_function

