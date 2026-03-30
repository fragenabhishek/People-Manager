"""
Authentication middleware
Provides decorators for route protection
"""
from functools import wraps
from flask import session, redirect, url_for, request, jsonify


def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            return redirect(url_for('auth_routes.login'))
        return f(*args, **kwargs)
    return decorated_function
