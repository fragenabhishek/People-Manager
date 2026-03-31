"""
JWT token service
Handles creation and verification of access and refresh tokens.
"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from utils.logger import get_logger

logger = get_logger(__name__)


class TokenService:

    def __init__(self, secret_key: str, access_ttl_minutes: int = 15, refresh_ttl_minutes: int = 10080):
        self.secret = secret_key
        self.access_ttl = timedelta(minutes=access_ttl_minutes)
        self.refresh_ttl = timedelta(minutes=refresh_ttl_minutes)  # default 7 days
        self._revoked: set[str] = set()

    def create_access_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {"sub": user_id, "iat": now, "exp": now + self.access_ttl, "type": "access"},
            self.secret,
            algorithm="HS256",
        )

    def create_refresh_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        jti = secrets.token_hex(16)
        return jwt.encode(
            {"sub": user_id, "iat": now, "exp": now + self.refresh_ttl, "type": "refresh", "jti": jti},
            self.secret,
            algorithm="HS256",
        )

    def create_token_pair(self, user_id: str) -> dict:
        return {
            "access_token": self.create_access_token(user_id),
            "refresh_token": self.create_refresh_token(user_id),
            "token_type": "bearer",
            "expires_in": int(self.access_ttl.total_seconds()),
        }

    def verify_token(self, token: str, expected_type: str = "access") -> dict:
        """Verify and decode a JWT. Raises jwt.ExpiredSignatureError or ValueError."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}") from e

        if payload.get("type") != expected_type:
            raise ValueError(f"Expected {expected_type} token, got {payload.get('type')}")

        jti = payload.get("jti")
        if jti and jti in self._revoked:
            raise ValueError("Token has been revoked")

        return payload

    def revoke_refresh_token(self, token: str) -> None:
        """Add a refresh token's jti to the revocation set.
        In production this would use Redis with TTL matching the token expiry."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            jti = payload.get("jti")
            if jti:
                self._revoked.add(jti)
        except jwt.InvalidTokenError:
            pass

    def create_password_reset_token(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {"sub": user_id, "iat": now, "exp": now + timedelta(hours=1), "type": "password_reset"},
            self.secret,
            algorithm="HS256",
        )

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Returns user_id if valid, None otherwise."""
        try:
            payload = self.verify_token(token, expected_type="password_reset")
            return payload["sub"]
        except Exception:
            return None
