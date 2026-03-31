"""
Authentication middleware
Supports dual auth: session cookies (browser) + JWT Bearer tokens (API clients).
"""
from functools import wraps

from flask import current_app, g, redirect, request, session, url_for

from utils.response import APIResponse


def _try_jwt_auth():
    """Attempt to authenticate via Authorization: Bearer <token>."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header[7:]
    token_service = current_app.config.get('token_service')
    if not token_service:
        return False
    try:
        payload = token_service.verify_token(token, expected_type='access')
        g.user_id = payload['sub']
        g.auth_method = 'jwt'
        return True
    except Exception:
        return False


def _try_session_auth():
    """Attempt to authenticate via Flask session cookie."""
    if session.get('logged_in') and session.get('user_id'):
        g.user_id = session['user_id']
        g.auth_method = 'session'
        return True
    return False


def login_required(f):
    """Protect routes — accepts session cookies OR JWT Bearer tokens."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if _try_jwt_auth() or _try_session_auth():
            session['user_id'] = g.user_id
            return f(*args, **kwargs)

        if request.is_json or request.path.startswith('/api/'):
            return APIResponse.unauthorized()
        return redirect(url_for('auth_routes.login'))
    return decorated_function


def jwt_required(f):
    """Strict JWT-only auth — for API-only endpoints like /api/auth/*."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if _try_jwt_auth():
            return f(*args, **kwargs)
        return APIResponse.unauthorized('Valid Bearer token required')
    return decorated_function
