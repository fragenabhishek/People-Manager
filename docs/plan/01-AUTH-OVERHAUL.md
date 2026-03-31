# Phase 1 — Authentication Overhaul

**Goal**: Replace session-based auth with JWT + refresh tokens, add OAuth2, password reset, and MFA foundation.

**Duration**: 2-3 weeks
**Depends on**: Phase 0 (Production Hardening)

## Why This Phase Matters

The current auth is the single biggest blocker for SaaS:
- No password reset flow (users locked out permanently)
- No OAuth/SSO (enterprises won't adopt without it)
- Session cookies don't work for mobile/API clients
- No MFA (regulatory concern for enterprise data)

## Architecture

```
┌─────────────┐     ┌────────────────┐     ┌──────────────┐
│  Client      │────▶│  Auth Service   │────▶│  User Repo    │
│  (Browser/   │◀────│                │◀────│  (DB)         │
│   Mobile)    │     │  JWT + Refresh  │     │               │
└─────────────┘     │  OAuth2 Flow    │     └──────────────┘
                    │  Password Reset │     ┌──────────────┐
                    │  MFA (TOTP)     │────▶│  Redis        │
                    └────────────────┘     │  (sessions,   │
                                           │   refresh tkn) │
                                           └──────────────┘
```

## Implementation Steps

### Step 1: JWT Token Service

```python
# services/token_service.py
from datetime import datetime, timedelta
import jwt

class TokenService:
    def __init__(self, secret_key: str, access_ttl=15, refresh_ttl=10080):
        self.secret = secret_key
        self.access_ttl = timedelta(minutes=access_ttl)     # 15 min
        self.refresh_ttl = timedelta(minutes=refresh_ttl)    # 7 days

    def create_access_token(self, user_id: str) -> str:
        return jwt.encode(
            {"sub": user_id, "exp": datetime.utcnow() + self.access_ttl, "type": "access"},
            self.secret, algorithm="HS256"
        )

    def create_refresh_token(self, user_id: str) -> str:
        return jwt.encode(
            {"sub": user_id, "exp": datetime.utcnow() + self.refresh_ttl, "type": "refresh"},
            self.secret, algorithm="HS256"
        )

    def verify_token(self, token: str, expected_type: str = "access") -> dict:
        payload = jwt.decode(token, self.secret, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise ValueError("Invalid token type")
        return payload
```

### Step 2: Update Auth Middleware

```python
# middleware/auth_middleware.py
from flask import request, g
from functools import wraps

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return APIResponse.unauthorized()
        token = auth_header[7:]
        try:
            payload = token_service.verify_token(token)
            g.user_id = payload["sub"]
        except Exception:
            return APIResponse.unauthorized("Token expired or invalid")
        return f(*args, **kwargs)
    return decorated
```

### Step 3: Auth Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/register` | POST | Create account |
| `/api/auth/login` | POST | Returns access + refresh tokens |
| `/api/auth/refresh` | POST | Exchange refresh token for new access token |
| `/api/auth/logout` | POST | Revoke refresh token (blacklist in Redis) |
| `/api/auth/forgot-password` | POST | Send reset email |
| `/api/auth/reset-password` | POST | Verify token + update password |
| `/api/auth/oauth/google` | GET | Initiate Google OAuth2 flow |
| `/api/auth/oauth/google/callback` | GET | Handle OAuth2 callback |

### Step 4: Password Reset Flow

1. User submits email to `/api/auth/forgot-password`
2. Generate time-limited token (stored in Redis, TTL 1 hour)
3. Send email via SendGrid/AWS SES (free tier)
4. User clicks link → `/api/auth/reset-password` with token
5. Validate token, update password hash, invalidate token

### Step 5: OAuth2 (Google)

Use `authlib` library:
```
pip install authlib
```

Register at Google Cloud Console → Credentials → OAuth 2.0 Client ID.

### Step 6: MFA Foundation (TOTP)

Use `pyotp` library for TOTP (Google Authenticator compatible):
```python
import pyotp

# Generate secret for user (store encrypted in DB)
secret = pyotp.random_base32()

# Verify code from authenticator app
totp = pyotp.TOTP(secret)
is_valid = totp.verify(user_submitted_code)
```

Ship MFA as opt-in initially. Make it mandatory for enterprise tier in Phase 6.

## Migration Strategy

Run **both** session auth and JWT auth simultaneously for 2 weeks:
1. New endpoints use JWT
2. Old session endpoints still work (backward compatible)
3. Frontend migrated to JWT
4. Remove session auth

## Done When

- [ ] Login returns JWT access + refresh tokens
- [ ] All API routes accept `Authorization: Bearer <token>`
- [ ] Password reset flow works end-to-end
- [ ] Google OAuth2 login works
- [ ] Refresh token rotation prevents replay attacks
- [ ] Old session auth removed
- [ ] Unit tests for all auth flows (>90% coverage on auth module)

## Dependencies to Add

```
PyJWT>=2.8
authlib>=1.3
pyotp>=2.9
redis>=5.0
```

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| JWT over sessions | Stateless, works for API/mobile clients | Token revocation requires Redis blacklist |
| Short access token (15m) | Limits exposure window | More refresh calls — acceptable |
| Google OAuth first | Largest user base | Need to add GitHub/Microsoft later for enterprise |
| TOTP over WebAuthn | Works everywhere, no hardware needed | Phishable — WebAuthn is stronger but harder to implement |
