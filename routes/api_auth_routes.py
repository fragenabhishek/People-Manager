"""
API authentication routes (JSON-only, JWT-based).
Separate from the HTML form-based auth_routes which use session cookies.
"""
from flask import Blueprint, current_app, g, request

from middleware.auth_middleware import jwt_required
from utils.logger import get_logger
from utils.response import APIResponse
from utils.validators import ValidationError

logger = get_logger(__name__)

api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/auth')


def _auth():
    return current_app.config['auth_service']


def _tokens():
    return current_app.config['token_service']


@api_auth_bp.route('/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    email = data.get('email', '').strip() or None

    user = _auth().register_user(username, password, confirm_password, email)
    tokens = _tokens().create_token_pair(user.id)
    return APIResponse.created({
        **tokens,
        'user': user.to_safe_dict(),
    }, 'Account created successfully')


@api_auth_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return APIResponse.validation_error('Username and password are required')

    user = _auth().authenticate_user(username, password)
    if not user:
        return APIResponse.unauthorized('Invalid username or password')

    tokens = _tokens().create_token_pair(user.id)
    return APIResponse.success({
        **tokens,
        'user': user.to_safe_dict(),
    })


@api_auth_bp.route('/refresh', methods=['POST'])
def api_refresh():
    data = request.get_json() or {}
    refresh_token = data.get('refresh_token', '')
    if not refresh_token:
        return APIResponse.validation_error('refresh_token is required')

    try:
        payload = _tokens().verify_token(refresh_token, expected_type='refresh')
    except Exception:
        return APIResponse.unauthorized('Invalid or expired refresh token')

    _tokens().revoke_refresh_token(refresh_token)
    new_tokens = _tokens().create_token_pair(payload['sub'])
    return APIResponse.success(new_tokens)


@api_auth_bp.route('/logout', methods=['POST'])
@jwt_required
def api_logout():
    data = request.get_json() or {}
    refresh_token = data.get('refresh_token', '')
    if refresh_token:
        _tokens().revoke_refresh_token(refresh_token)
    return APIResponse.success(message='Logged out successfully')


@api_auth_bp.route('/me', methods=['GET'])
@jwt_required
def api_me():
    user = _auth().get_user_by_id(g.user_id)
    if not user:
        return APIResponse.not_found('User not found')
    return APIResponse.success(user.to_safe_dict())


@api_auth_bp.route('/change-password', methods=['POST'])
@jwt_required
def api_change_password():
    data = request.get_json() or {}
    _auth().change_password(
        user_id=g.user_id,
        current_password=data.get('current_password', ''),
        new_password=data.get('new_password', ''),
        confirm_password=data.get('confirm_password', ''),
    )
    return APIResponse.success(message='Password changed successfully')


@api_auth_bp.route('/forgot-password', methods=['POST'])
def api_forgot_password():
    """Generate a password reset token.
    In production this would send an email. For now it returns the token
    directly (useful for dev/testing)."""
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    if not email:
        return APIResponse.validation_error('Email is required')

    user = _auth().find_user_by_email(email)
    if not user:
        return APIResponse.success(message='If an account exists with that email, a reset link has been sent.')

    reset_token = _tokens().create_password_reset_token(user.id)
    logger.info(f"Password reset token generated for user {user.username}")
    return APIResponse.success({
        'message': 'If an account exists with that email, a reset link has been sent.',
        'reset_token': reset_token if current_app.config.get('TESTING') or Config.DEBUG else None,
    })


@api_auth_bp.route('/reset-password', methods=['POST'])
def api_reset_password():
    data = request.get_json() or {}
    token = data.get('token', '')
    new_password = data.get('new_password', '')

    if not token or not new_password:
        return APIResponse.validation_error('token and new_password are required')

    user_id = _tokens().verify_password_reset_token(token)
    if not user_id:
        return APIResponse.unauthorized('Invalid or expired reset token')

    _auth().reset_password(user_id, new_password)
    return APIResponse.success(message='Password has been reset successfully')


from config import Config  # noqa: E402 — avoid circular import at module top
