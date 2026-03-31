# Phase 1 — Authentication Overhaul

**Goal**: Add JWT-based API auth alongside existing session auth, plus password reset and change-password flows.

**Status**: COMPLETED

**Depends on**: Phase 0 (Production Hardening)

## What Was Done

### 1. JWT Token Service (`services/token_service.py`)
- [x] `TokenService` with HS256 signing, configurable TTLs
- [x] Access tokens (15 min default) + refresh tokens (7 days default, with `jti` for revocation)
- [x] `create_token_pair()` returns access + refresh + metadata
- [x] In-memory revocation set (production would use Redis with TTL)
- [x] Password reset token generation and verification (1-hour expiry)
- [x] Timezone-aware `datetime.now(timezone.utc)` throughout

### 2. User Model Enhancements (`models/user.py`)
- [x] Added `mfa_secret`, `mfa_enabled`, `is_active` fields (MFA foundation)
- [x] Backward-compatible `from_dict()` with defaults for new fields
- [x] `to_safe_dict()` now includes `mfa_enabled`

### 3. Dual Auth Middleware (`middleware/auth_middleware.py`)
- [x] `login_required` now checks JWT Bearer tokens first, then session cookies
- [x] Sets `g.user_id` and `g.auth_method` for downstream use
- [x] New `jwt_required` decorator for API-only endpoints
- [x] Browser routes still redirect to login page; API routes return 401 JSON

### 4. API Auth Endpoints (`routes/api_auth_routes.py`)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register` | POST | Create account, returns JWT pair |
| `/api/auth/login` | POST | Authenticate, returns JWT pair |
| `/api/auth/refresh` | POST | Exchange refresh token (old one revoked) |
| `/api/auth/logout` | POST | Revoke refresh token |
| `/api/auth/me` | GET | Get current user profile |
| `/api/auth/change-password` | POST | Change password (requires current) |
| `/api/auth/forgot-password` | POST | Generate reset token (by email) |
| `/api/auth/reset-password` | POST | Reset password with token |

### 5. Auth Service Enhancements (`services/auth_service.py`)
- [x] `change_password()` — validates current password then updates
- [x] `reset_password()` — sets new password (token verified by caller)
- [x] `find_user_by_email()` — lookup for forgot-password flow

### 6. Configuration (`config/config.py`)
- [x] `JWT_ACCESS_TOKEN_MINUTES` (env-configurable, default 15)
- [x] `JWT_REFRESH_TOKEN_MINUTES` (env-configurable, default 10080 = 7 days)

### 7. Test Coverage
- [x] `tests/test_token_service.py` — 8 unit tests for token creation, verification, revocation
- [x] `tests/test_api_auth.py` — 19 integration tests covering all endpoints
- [x] JWT cross-compatibility test (JWT tokens work with existing `/api/people` routes)
- [x] **81 total tests, all passing**

## Migration Strategy (Dual Auth)

Both session auth and JWT auth run simultaneously:
- Browser UI continues using session cookies (no frontend changes needed yet)
- API clients can use `Authorization: Bearer <token>` for all routes
- The `login_required` decorator transparently accepts either method

## Files Added/Changed

| File | Status |
|------|--------|
| `services/token_service.py` | New |
| `routes/api_auth_routes.py` | New |
| `tests/test_token_service.py` | New |
| `tests/test_api_auth.py` | New |
| `requirements.txt` | Updated (added PyJWT) |
| `config/config.py` | Updated (JWT TTL settings) |
| `models/user.py` | Updated (MFA/active fields) |
| `middleware/auth_middleware.py` | Updated (dual auth) |
| `middleware/__init__.py` | Updated (export jwt_required) |
| `services/auth_service.py` | Updated (change/reset password, find by email) |
| `services/__init__.py` | Updated (export TokenService) |
| `routes/__init__.py` | Updated (export api_auth_bp) |
| `app.py` | Updated (wire TokenService + api_auth_bp) |
| `conftest.py` | Updated (longer test secret key) |

## What's Deferred to Later

- **OAuth2 (Google/GitHub)**: Requires external provider registration and `authlib` — planned for Phase 5 (SaaS Features)
- **MFA (TOTP)**: Foundation fields added; activation UI/flow in Phase 5
- **Redis token store**: In-memory revocation set works for single-instance; Redis needed at scale (Phase 2+)
- **Email sending**: Forgot-password generates tokens but doesn't email yet; needs SendGrid/SES integration

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| Dual auth (session + JWT) | Zero-downtime migration, browser UI unchanged | Slightly more complex middleware |
| In-memory revocation | No Redis dependency for now | Lost on restart, single-instance only |
| Short access tokens (15m) | Limits exposure if token leaked | More refresh calls — acceptable |
| Password reset token in JWT | Stateless, no DB column needed | Can't invalidate without revocation list |
