# Phase 3 — FastAPI Migration

**Status**: ✅ COMPLETED  
**Goal**: Migrate from Flask (synchronous) to FastAPI (async-capable) for non-blocking AI calls, automatic OpenAPI docs, and Pydantic request/response validation.

## What Was Done

### 1. Dependencies Replaced
- **Removed**: Flask, Flask-Bcrypt, Flask-Limiter, Flask-WTF, gunicorn
- **Added**: `fastapi`, `uvicorn[standard]`, `python-multipart`, `jinja2`, `itsdangerous`, `bcrypt`, `httpx` (dev)
- `requirements.txt` and `requirements-dev.txt` updated

### 2. Pydantic Schemas (`schemas/`)
- `auth.py` — `RegisterRequest`, `LoginRequest`, `TokenPair`, `RefreshRequest`, `LogoutRequest`, `ChangePasswordRequest`, `ForgotPasswordRequest`, `ResetPasswordRequest`, `UserProfile`
- `person.py` — `PersonCreate` (with `tags` string/list coercion via `@field_validator`), `PersonUpdate` (all-optional for PATCH semantics), `TagsRequest`, `FollowUpRequest`
- `note.py` — `NoteCreate`, `AskRequest`

### 3. FastAPI Routers (`routers/`)
All Flask Blueprints replaced with FastAPI `APIRouter` instances:

| Old (Flask)               | New (FastAPI)            | Notes                    |
|---------------------------|--------------------------|--------------------------|
| `routes/auth_routes.py`   | `routers/auth.py`        | HTML form login/register |
| `routes/api_auth_routes.py`| `routers/api_auth.py`   | JWT register/login/refresh/logout |
| `routes/person_routes.py` | `routers/people.py`      | CRUD, tags, follow-ups, import/export |
| `routes/note_routes.py`   | `routers/notes.py`       | Notes CRUD, activity feed |
| `routes/ai_routes.py`     | `routers/ai.py`          | AI summary, Q&A, tag suggestions |

### 4. Dependency Injection (`deps.py`)
- `get_current_user(request)` — dual auth: JWT Bearer token OR session cookie
- `get_current_user_optional(request)` — returns None instead of 401
- `require_jwt(request)` — strict JWT-only for `/api/auth/*`
- All services accessed via `request.app.state.*`

### 5. Response Helpers (`utils/response_fastapi.py`)
- Same JSON envelope as Flask version (`{success, data, error, timestamp}`)
- Frontend JavaScript unchanged — response format is identical

### 6. Password Hashing (`utils/hashing.py`)
- Standalone `PasswordHasher` using `bcrypt` directly — no Flask dependency
- Returns bytes (matching Flask-Bcrypt interface for backward compat)

### 7. Template Compatibility (`utils/templating.py`)
- Shared `Jinja2Templates` instance for all routers
- Custom `url_for` Jinja2 global that bridges Flask-style `url_for('static', filename=...)` and `url_for('auth_routes.login')` to FastAPI's URL routing
- Templates unchanged — zero frontend modifications needed

### 8. App Factory (`main.py`)
- `create_app()` returns `FastAPI` instance
- `SessionMiddleware` for cookie-based sessions
- Lifespan context manager for startup/shutdown
- Security headers middleware (same headers as Flask version)
- Global exception handlers for `ValidationError`, `ValueError`, and generic `Exception`
- Auto-generated OpenAPI docs at `/docs` and `/redoc`

### 9. Dockerfile
- `CMD` changed from `gunicorn ... app:app` to `uvicorn main:app --workers 4`

### 10. Test Migration
- `conftest.py` — `TestClient(app)` from `httpx` replaces Flask's `app.test_client()`
- `resp.get_json()` → `resp.json()`; `resp.data` → `resp.text`/`resp.content`
- Form POST uses `data={}` dict; JSON POST uses `json={}`
- File upload uses `files={"file": ("name.csv", content, "text/csv")}`
- All 107 tests pass, zero lint warnings

## Architecture After Migration

```
main.py (FastAPI app factory)
├── routers/
│   ├── auth.py          (HTML form login/register — Jinja2 templates)
│   ├── api_auth.py      (JWT login/register/refresh/logout)
│   ├── people.py        (CRUD, tags, follow-ups, import/export)
│   ├── notes.py         (CRUD, activity feed)
│   └── ai.py            (blueprints, Q&A, tag suggestions)
├── schemas/             (Pydantic request/response models)
├── deps.py              (FastAPI Depends — auth, services)
├── services/            (Business logic — UNCHANGED)
├── repositories/        (Data access — UNCHANGED)
├── models/              (Domain entities — UNCHANGED)
├── utils/
│   ├── response_fastapi.py  (JSON envelope helpers)
│   ├── hashing.py           (bcrypt standalone)
│   ├── templating.py        (shared Jinja2 + url_for bridge)
│   └── ...                  (logger, validators — UNCHANGED)
├── templates/           (Jinja2 HTML — UNCHANGED)
└── static/              (CSS, JS — UNCHANGED)
```

## What's Free Now

- **OpenAPI docs**: Visit `/docs` (Swagger UI) or `/redoc` for auto-generated API documentation
- **Pydantic validation**: Request bodies are validated before reaching route handlers
- **Async-ready**: Routes can be `async def` when needed (AI routes use `run_in_executor`)
- **Type safety**: Full type hints on all request/response payloads

## Deferred

- [ ] Make AI service truly async (`await genai.generate_content_async()` when SDK supports it)
- [ ] Rate limiting (slowapi or custom middleware)
- [ ] WebSocket support for real-time updates
- [ ] Background tasks (Celery integration) via FastAPI's `BackgroundTasks`

## Test Results

```
107 passed in ~48s
0 lint warnings (ruff)
```
