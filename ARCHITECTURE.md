# Architecture Documentation

> For the full system design, see [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md).
> For product requirements, see [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).
> For the migration roadmap, see [docs/plan/README.md](docs/plan/README.md).

## Overview

People Manager follows **SOLID principles** and implements a **clean layered architecture** with strict separation of concerns.

## Architecture Layers

```
  Frontend (Next.js 16 + React 19 + TypeScript + Tailwind)
       ↓ HTTP (proxied /api/* calls)
  Routers (FastAPI APIRouter: auth, api_auth, people, notes, ai)
       ↓
  Dependency Injection (deps.py — auth resolution, service access via app.state)
       ↓
  Schemas (Pydantic — request validation + response serialization)
       ↓
  Services (PersonService, NoteService, AIService, AuthService, ImportExportService, TokenService)
       ↓
  Repositories (BaseRepository → SQL / MongoDB / JSON implementations)
       ↓
  Models (Person, Note, User — dataclasses) + SQLAlchemy ORM (tables.py)
       ↓
  Storage (PostgreSQL / MongoDB / JSON files)
```

## Storage Backends

Three interchangeable backends, selected by environment variables:

```
DATABASE_URL set?  ──▶ SQLAlchemy repos (PostgreSQL / SQLite)
                │
                ▼ no
MONGO_URI set?     ──▶ MongoDB repos
                │
                ▼ no
                   ──▶ JSON file repos (zero-config default)
```

Services are completely unaware of which backend is active — this is the payoff of the Repository Pattern.

## SOLID Principles

| Principle | Implementation |
|-----------|---------------|
| **Single Responsibility** | Each module has one job: models define entities, repos handle data access, services contain logic, routers handle HTTP |
| **Open/Closed** | New storage backends implement `BaseRepository`. New features add services/routers without changing existing ones |
| **Liskov Substitution** | SQL, MongoDB, and JSON repository implementations are interchangeable |
| **Interface Segregation** | Thin `BaseRepository` interface. Services only depend on methods they use |
| **Dependency Inversion** | Services depend on repository abstractions. All dependencies are injected in `main.py` |

## Design Patterns

1. **Repository Pattern** — Data access abstraction with SQL/MongoDB/JSON backends
2. **Service Layer** — Business logic separated from HTTP handling
3. **Dependency Injection** — `create_app()` wires repos → services → `app.state`; FastAPI `Depends` resolves auth
4. **Application Factory** — `create_app()` produces configured FastAPI instances
5. **Dual Authentication** — Session cookies (browser) + JWT Bearer tokens (API) coexist transparently

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| FastAPI over Flask | Async-capable for AI calls, auto OpenAPI docs, Pydantic validation |
| Next.js React frontend | Type-safe, component architecture, SSR-capable, largest ecosystem |
| Three storage backends | JSON for zero-config dev, MongoDB for existing users, PostgreSQL for production scale |
| Relationship score at read time | No background jobs needed, always fresh data |
| AI output sanitization via bleach | Prevents XSS from LLM-generated HTML while preserving formatting |
| Tags as list/CSV on Person | Simpler queries, no join overhead, good enough for personal CRM scale |
| Notes as separate entity | Enables timeline views, activity feeds, and per-note operations |
| Dual auth (session + JWT) | Zero-downtime migration, browser UI and API clients both work |
