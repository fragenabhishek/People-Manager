# Architecture Documentation

> For the full system design, see [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md).
> For product requirements, see [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

## Overview

People Manager follows **SOLID principles** and implements a **clean layered architecture** with strict separation of concerns. The codebase is organized into 7 layers.

## Architecture Layers

```
  Presentation (Templates + JS + CSS)
       ↓
  Routes (Flask Blueprints: auth, person, ai, notes)
       ↓
  Middleware (Auth, Rate Limiting)
       ↓
  Services (PersonService, NoteService, AIService, AuthService, ImportExportService)
       ↓
  Repositories (BaseRepository → PersonRepo, NoteRepo, UserRepo)
       ↓
  Models (Person, Note, User — dataclasses)
       ↓
  Storage (MongoDB Atlas or JSON files)
```

## SOLID Principles

| Principle | Implementation |
|-----------|---------------|
| **Single Responsibility** | Each module has one job: models define entities, repos handle data access, services contain logic, routes handle HTTP |
| **Open/Closed** | New storage backends implement `BaseRepository`. New features add services/routes without changing existing ones |
| **Liskov Substitution** | MongoDB and JSON repository implementations are interchangeable |
| **Interface Segregation** | Thin `BaseRepository` interface. Services only depend on methods they use |
| **Dependency Inversion** | Services depend on repository abstractions. All dependencies are injected in `app.py` |

## Design Patterns

1. **Repository Pattern** — Data access abstraction with dual MongoDB/JSON support
2. **Service Layer** — Business logic separated from HTTP handling
3. **Dependency Injection** — `create_app()` wires repositories → services → routes
4. **Application Factory** — `create_app()` produces configured Flask instances
5. **Blueprint Modular Routing** — Each domain is a separate Flask Blueprint

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Vanilla JS (no framework) | Zero build step, fast load, simple deployment, no dependency on framework lifecycle |
| Dual storage backend | JSON for zero-config local dev, MongoDB for production scalability |
| Relationship score at read time | No background jobs needed, always fresh data |
| AI output sanitization via bleach | Prevents XSS from LLM-generated HTML while preserving formatting |
| Tags as list on Person (not separate entity) | Simpler queries, no join overhead, good enough for personal CRM scale |
| Notes as separate entity | Enables timeline views, activity feeds, and per-note operations |
