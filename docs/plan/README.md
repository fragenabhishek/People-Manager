# Migration Plan — People Manager to Production SaaS

## Vision

Migrate the current Flask/MongoDB/Vanilla-JS prototype into a production-grade SaaS platform on the **recommended target stack**: FastAPI + PostgreSQL + Redis + React/Next.js.

## Guiding Principles

1. **Ship value incrementally** — every phase produces a deployable, testable system
2. **No big-bang rewrites** — migrate one layer at a time while the old one keeps running
3. **Prove demand before investing** — infrastructure investment follows user adoption
4. **Keep the architecture modular** — the clean service/repository pattern carries forward

## Phase Overview

| Phase | Document | What Changes | Duration | Prerequisite |
|-------|----------|-------------|----------|-------------|
| 1 | [00-PRODUCTION-HARDENING](./00-PRODUCTION-HARDENING.md) | Docker, CI/CD, env config, logging, monitoring | 1-2 weeks | None |
| 2 | [01-AUTH-OVERHAUL](./01-AUTH-OVERHAUL.md) | JWT, OAuth2, password reset, MFA foundation | 2-3 weeks | Phase 1 |
| 3 | [02-POSTGRESQL-MIGRATION](./02-POSTGRESQL-MIGRATION.md) | PostgreSQL + SQLAlchemy, data migration, Redis cache | 2-3 weeks | Phase 1 |
| 4 | [03-FASTAPI-MIGRATION](./03-FASTAPI-MIGRATION.md) | Flask → FastAPI, async I/O, Pydantic schemas | 2-3 weeks | Phases 2 & 3 |
| 5 | [04-FRONTEND-MODERNIZATION](./04-FRONTEND-MODERNIZATION.md) | Vanilla JS → React/Next.js, component library | 3-4 weeks | Phase 4 |
| 6 | [05-SAAS-FEATURES](./05-SAAS-FEATURES.md) | Multi-tenancy, billing, admin, onboarding | 4-6 weeks | Phase 5 |

**Total estimated timeline**: 14-21 weeks (3.5 - 5 months) for a solo developer.

## Dependency Graph

```
Phase 1 (Production Hardening)
    ├── Phase 2 (Auth Overhaul)
    └── Phase 3 (PostgreSQL Migration)
            └── Phase 4 (FastAPI Migration) ← also depends on Phase 2
                    └── Phase 5 (Frontend Modernization)
                            └── Phase 6 (SaaS Features)
```

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data loss during DB migration | Dual-write period + rollback scripts in Phase 3 |
| Breaking API changes | Versioned API (`/api/v2/`) running parallel to `/api/` in Phase 4 |
| Frontend regression | Phase 5 runs new React app on `/app/` while old UI stays on `/` |
| Scope creep | Each phase has a "Done when" checklist — ship when met, not when perfect |
| Solo developer bottleneck | Phases 1-3 are independent enough to parallelize with a second dev |

## Decision Log

Track all architectural decisions here as they're made:

| Date | Decision | Rationale | Phase |
|------|---------|-----------|-------|
| 2026-03-31 | Modular monolith (no microservices) | <2K LOC, single team, shared DB | All |
| 2026-03-31 | FastAPI over Django | Async needed for AI calls, lighter framework | 4 |
| 2026-03-31 | PostgreSQL over MongoDB for SaaS | ACID transactions, relational integrity for billing | 3 |
| 2026-03-31 | React/Next.js over Vue/Svelte | Largest ecosystem, best for hiring | 5 |
