"""
API auth routes — JSON-only, JWT-based.
"""
from fastapi import APIRouter, Depends, Request

from config import Config
from deps import require_jwt
from schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from utils import response_fastapi as R
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Auth (API)"])


@router.post("/register", status_code=201)
def api_register(body: RegisterRequest, request: Request):
    auth = request.app.state.auth_service
    tokens = request.app.state.token_service
    user = auth.register_user(body.username, body.password, body.confirm_password, body.email)
    pair = tokens.create_token_pair(user.id)
    return R.created({**pair, "user": user.to_safe_dict()}, "Account created successfully")


@router.post("/login")
def api_login(body: LoginRequest, request: Request):
    auth = request.app.state.auth_service
    tokens = request.app.state.token_service
    if not body.username or not body.password:
        return R.validation_error("Username and password are required")
    user = auth.authenticate_user(body.username, body.password)
    if not user:
        return R.unauthorized("Invalid username or password")
    pair = tokens.create_token_pair(user.id)
    return R.ok({**pair, "user": user.to_safe_dict()})


@router.post("/refresh")
def api_refresh(body: RefreshRequest, request: Request):
    tokens = request.app.state.token_service
    if not body.refresh_token:
        return R.validation_error("refresh_token is required")
    try:
        payload = tokens.verify_token(body.refresh_token, expected_type="refresh")
    except Exception:
        return R.unauthorized("Invalid or expired refresh token")
    tokens.revoke_refresh_token(body.refresh_token)
    return R.ok(tokens.create_token_pair(payload["sub"]))


@router.post("/logout")
def api_logout(body: LogoutRequest, request: Request, user_id: str = Depends(require_jwt)):
    if body.refresh_token:
        request.app.state.token_service.revoke_refresh_token(body.refresh_token)
    return R.ok(message="Logged out successfully")


@router.get("/me")
def api_me(request: Request, user_id: str = Depends(require_jwt)):
    user = request.app.state.auth_service.get_user_by_id(user_id)
    if not user:
        return R.not_found("User not found")
    return R.ok(user.to_safe_dict())


@router.post("/change-password")
def api_change_password(body: ChangePasswordRequest, request: Request, user_id: str = Depends(require_jwt)):
    request.app.state.auth_service.change_password(
        user_id, body.current_password, body.new_password, body.confirm_password
    )
    return R.ok(message="Password changed successfully")


@router.post("/forgot-password")
def api_forgot_password(body: ForgotPasswordRequest, request: Request):
    auth = request.app.state.auth_service
    tokens = request.app.state.token_service
    if not body.email:
        return R.validation_error("Email is required")
    user = auth.find_user_by_email(body.email)
    if not user:
        return R.ok(message="If an account exists with that email, a reset link has been sent.")
    reset_token = tokens.create_password_reset_token(user.id)
    logger.info(f"Password reset token generated for user {user.username}")
    testing = getattr(request.app.state, "testing", False)
    return R.ok({
        "message": "If an account exists with that email, a reset link has been sent.",
        "reset_token": reset_token if testing or Config.DEBUG else None,
    })


@router.post("/reset-password")
def api_reset_password(body: ResetPasswordRequest, request: Request):
    tokens = request.app.state.token_service
    auth = request.app.state.auth_service
    if not body.token or not body.new_password:
        return R.validation_error("token and new_password are required")
    user_id = tokens.verify_password_reset_token(body.token)
    if not user_id:
        return R.unauthorized("Invalid or expired reset token")
    auth.reset_password(user_id, body.new_password)
    return R.ok(message="Password has been reset successfully")
