"""Unit tests for TokenService."""
import time

import pytest

from services.token_service import TokenService


@pytest.fixture
def ts():
    return TokenService("test-secret-key-at-least-32-bytes!", access_ttl_minutes=1, refresh_ttl_minutes=5)


def test_create_access_token(ts):
    token = ts.create_access_token("user-123")
    payload = ts.verify_token(token, expected_type="access")
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_create_refresh_token(ts):
    token = ts.create_refresh_token("user-456")
    payload = ts.verify_token(token, expected_type="refresh")
    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"
    assert "jti" in payload


def test_token_pair(ts):
    pair = ts.create_token_pair("user-789")
    assert "access_token" in pair
    assert "refresh_token" in pair
    assert pair["token_type"] == "bearer"
    assert pair["expires_in"] == 60


def test_wrong_token_type_rejected(ts):
    access = ts.create_access_token("user-1")
    with pytest.raises(ValueError, match="Expected refresh"):
        ts.verify_token(access, expected_type="refresh")


def test_revoke_refresh_token(ts):
    refresh = ts.create_refresh_token("user-2")
    ts.verify_token(refresh, expected_type="refresh")

    ts.revoke_refresh_token(refresh)
    with pytest.raises(ValueError, match="revoked"):
        ts.verify_token(refresh, expected_type="refresh")


def test_password_reset_token(ts):
    token = ts.create_password_reset_token("user-3")
    user_id = ts.verify_password_reset_token(token)
    assert user_id == "user-3"


def test_invalid_reset_token(ts):
    assert ts.verify_password_reset_token("garbage") is None


def test_invalid_token_string(ts):
    with pytest.raises(ValueError, match="Invalid token"):
        ts.verify_token("not.a.jwt")
