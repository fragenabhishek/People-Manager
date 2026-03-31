"""
FastAPI dependency injection.
Provides get_current_user (JWT or session) and service accessors via app.state.
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request

from utils.logger import get_logger

logger = get_logger(__name__)


def _extract_bearer(request: Request) -> Optional[str]:
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def get_current_user(request: Request) -> str:
    """Resolve user_id from JWT Bearer token OR session cookie."""
    token = _extract_bearer(request)
    if token:
        ts = request.app.state.token_service
        try:
            payload = ts.verify_token(token, expected_type="access")
            return payload["sub"]
        except Exception:
            raise HTTPException(401, "Token expired or invalid")

    user_id = request.session.get("user_id")
    if user_id and request.session.get("logged_in"):
        return user_id

    raise HTTPException(401, "Unauthorized")


def get_current_user_optional(request: Request) -> Optional[str]:
    """Like get_current_user but returns None instead of raising."""
    try:
        return get_current_user(request)
    except HTTPException:
        return None


def require_jwt(request: Request) -> str:
    """Strict JWT-only — for /api/auth/* endpoints."""
    token = _extract_bearer(request)
    if not token:
        raise HTTPException(401, "Valid Bearer token required")
    ts = request.app.state.token_service
    try:
        payload = ts.verify_token(token, expected_type="access")
        return payload["sub"]
    except Exception:
        raise HTTPException(401, "Token expired or invalid")
