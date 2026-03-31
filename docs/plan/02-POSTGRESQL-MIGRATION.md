# Phase 2 — PostgreSQL Migration

**Goal**: Add SQLAlchemy ORM as a third storage backend (alongside JSON and MongoDB), with Alembic for schema migrations. Setting `DATABASE_URL` activates the SQL path.

**Status**: COMPLETED

**Depends on**: Phase 0 (Production Hardening)

## What Was Done

### 1. SQLAlchemy ORM Models (`models/database.py`, `models/tables.py`)
- [x] `Base` declarative base, `init_db()`, `create_tables()`, `drop_tables()`
- [x] `UserRow` — maps to `users` table (all fields including MFA)
- [x] `PersonRow` — maps to `people` table (all 25+ fields, tags stored as CSV)
- [x] `NoteRow` — maps to `notes` table with FK cascades
- [x] Relationships: `UserRow.people`, `UserRow.notes`, `PersonRow.notes`
- [x] Indexes on `user_id`, `person_id` for efficient lookups

### 2. SQL Repository Implementations
| File | Description |
|------|-------------|
| `repositories/sql_user_repository.py` | Full CRUD + `find_by_username` |
| `repositories/sql_person_repository.py` | Full CRUD + search, tags, follow-ups |
| `repositories/sql_note_repository.py` | Full CRUD + `find_by_person`, `delete_by_person`, `count_by_person` |

All three implement the same `BaseRepository` interface — services are completely unaware of the storage backend.

### 3. Configuration (`config/config.py`)
- [x] `DATABASE_URL` env var — when set, activates SQL storage
- [x] Priority: `DATABASE_URL` (SQL) > `MONGO_URI` (MongoDB) > JSON files
- [x] `Config.validate()` reports the active storage backend in logs

### 4. App Factory (`app.py`)
- [x] `_init_repositories()` now has three branches: SQL → MongoDB → JSON
- [x] When `USE_SQL` is true, calls `init_db()` + `create_tables()` at startup
- [x] Health endpoint reports `postgresql` as storage type

### 5. Alembic Migrations
- [x] `alembic/` directory initialized with `env.py` configured for our models
- [x] `env.py` reads `DATABASE_URL` from environment
- [x] Initial migration auto-generated: `users`, `people`, `notes` tables with indexes
- [x] `alembic upgrade head` works against any supported database

### 6. Docker Compose
- [x] `docker-compose.yml` — now uses PostgreSQL 16 instead of MongoDB
- [x] `docker-compose.mongo.yml` — legacy MongoDB setup preserved as separate file
- [x] PostgreSQL healthcheck via `pg_isready`

### 7. Test Coverage
- [x] `tests/test_sql_repos.py` — 18 unit tests (SQLite in-memory) covering all repo methods
- [x] `tests/test_sql_integration.py` — 8 integration tests running the full Flask app with SQLite backend
- [x] Existing JSON-based tests (81) continue to pass unchanged
- [x] **107 total tests, all passing, zero lint warnings**

## Architecture: Three Storage Backends

```
Config.DATABASE_URL set?  ──▶ SQLAlchemy repos (PostgreSQL / SQLite)
                    │
                    ▼ no
Config.MONGO_URI set?     ──▶ MongoDB repos (existing)
                    │
                    ▼ no
                          ──▶ JSON file repos (existing)
```

Services (`PersonService`, `AuthService`, etc.) have zero knowledge of which backend is active. This is the payoff of the Repository Pattern.

## Files Added/Changed

| File | Status |
|------|--------|
| `models/database.py` | New — engine, session factory, Base |
| `models/tables.py` | New — ORM table definitions |
| `repositories/sql_user_repository.py` | New |
| `repositories/sql_person_repository.py` | New |
| `repositories/sql_note_repository.py` | New |
| `tests/test_sql_repos.py` | New — 18 unit tests |
| `tests/test_sql_integration.py` | New — 8 integration tests |
| `alembic/` | New — migration framework |
| `alembic.ini` | New — Alembic config |
| `docker-compose.mongo.yml` | New — legacy Mongo setup |
| `requirements.txt` | Updated — SQLAlchemy, alembic, psycopg2-binary |
| `config/config.py` | Updated — DATABASE_URL, USE_SQL |
| `app.py` | Updated — SQL repo wiring, health endpoint |
| `docker-compose.yml` | Updated — PostgreSQL 16 replaces MongoDB |
| `.env.example` | Updated — DATABASE_URL documented |
| `.gitignore` | Updated — *.db excluded |
| `pyproject.toml` | Updated — Alembic files excluded from lint |
| `repositories/__init__.py` | Updated — exports SQL repos |

## How to Use

```bash
# Local dev with JSON files (default, no config needed)
python app.py

# Local dev with SQLite
DATABASE_URL=sqlite:///people_manager.db python app.py

# Production with PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/dbname python app.py

# Docker (PostgreSQL included)
docker compose up

# Run Alembic migrations (production)
DATABASE_URL=postgresql://... alembic upgrade head
```

## What's Deferred
- **Redis**: Rate limiting and caching still use in-memory. Redis integration planned when scaling demands it.
- **Data migration script**: `scripts/migrate_mongo_to_pg.py` — not needed until users actually migrate from Mongo to Postgres.
- **Dual-write period**: Not implemented since backends are switched via config, not migrated live.
- **Full-text search**: Uses `ILIKE` for now. PostgreSQL `tsvector` + `GIN` index can be added when search volume warrants it.

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| Tags as CSV column | Simple, portable across SQLite/PostgreSQL | No GIN index on tags (filter in Python for now) |
| `create_tables()` at startup | Zero-config for dev, works without Alembic | Production should use Alembic for versioned migrations |
| Three backends | Maximum flexibility, easy testing | More code to maintain |
| SQLite for tests | Fast, no infrastructure needed | Doesn't catch PostgreSQL-specific issues |
