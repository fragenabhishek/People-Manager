# Phase 0 — Production Hardening

**Goal**: Make the current Flask app deployable, observable, and secure enough for early adopters.

**Duration**: 1-2 weeks

## What Changes

### 1. Containerization (Done)
- [x] `Dockerfile` with Python 3.11-slim, Gunicorn, health check
- [x] `docker-compose.yml` with app + MongoDB
- [x] `.dockerignore` to minimize image size

### 2. CI/CD Pipeline

Create `.github/workflows/ci.yml`:

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v4

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check .

  deploy:
    needs: [test, lint]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Deploy to Railway/Fly.io/Render
```

### 3. Environment Configuration

```
# .env.example (commit this, not .env)
SECRET_KEY=
MONGO_URI=mongodb+srv://...
GEMINI_API_KEY=
FLASK_DEBUG=False
PORT=5000
```

Validate all required env vars at startup (already partially done in `Config.validate()`).

### 4. Structured Logging

Replace scattered `logger.info`/`logger.error` with JSON-structured output for log aggregation:

```python
# utils/logger.py enhancement
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)
```

### 5. Monitoring & Alerting

Add `/health` endpoint enhancements (already done in refactor):
- DB connectivity check
- AI service reachability
- Response time percentiles

Integrate with a free-tier APM:
- **Option A**: Sentry (error tracking, free for 5K events/mo)
- **Option B**: Grafana Cloud (metrics + logs, free for 10K series)

### 6. Security Hardening

- [x] Session cookie: `Secure=True` in production, `HttpOnly`, `SameSite=Lax`
- [x] Secret key validation enforced for non-debug mode
- [ ] Add `Content-Security-Policy` header
- [ ] Add `X-Content-Type-Options: nosniff`
- [ ] Add `X-Frame-Options: DENY`
- [ ] Rate limit auth endpoints (already done: 10/min on login)

## Done When

- [ ] `docker compose up` starts the full stack locally
- [ ] GitHub Actions CI passes on every push
- [ ] Health endpoint returns `ok` / `degraded`
- [ ] Zero `print()` statements in production code
- [ ] All secrets loaded from env vars, never hardcoded
- [ ] Deploy to Railway/Fly.io with one `git push`

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| Gunicorn (sync) for now | Simple, proven | Blocks on AI calls — acceptable until Phase 4 (FastAPI) |
| memory:// rate limiter | Zero extra infra | Resets on restart, per-process only — acceptable for single-instance |
| Sentry free tier | Instant error visibility | 5K event limit — upgrade when needed |

## Files Changed

- `.github/workflows/ci.yml` (new)
- `utils/logger.py` (enhanced)
- `app.py` (security headers middleware)
- `.env.example` (new)
