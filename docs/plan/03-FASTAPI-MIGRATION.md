# Phase 3 — FastAPI Migration

**Goal**: Migrate from Flask (synchronous) to FastAPI (async) for non-blocking AI calls, automatic OpenAPI docs, and Pydantic request/response validation.

**Duration**: 2-3 weeks
**Depends on**: Phase 1 (Auth — JWT middleware), Phase 2 (PostgreSQL — async-compatible ORM)

## Why FastAPI

| Problem with Flask | How FastAPI Solves It |
|-------------------|-----------------------|
| Gemini API calls (5-15s) block a Gunicorn worker | `async/await` — thousands of concurrent AI requests |
| No request validation (manual in every route) | Pydantic models validate automatically |
| No auto-generated API docs | OpenAPI/Swagger UI at `/docs` for free |
| No type hints on request/response | Full type safety end-to-end |

## Architecture

```
FastAPI App
├── routers/
│   ├── auth.py          (JWT login, register, OAuth)
│   ├── people.py        (CRUD, tags, follow-ups)
│   ├── notes.py         (CRUD, activity feed)
│   └── ai.py            (blueprints, Q&A, tag suggestions)
├── schemas/             (Pydantic request/response models)
│   ├── auth.py
│   ├── person.py
│   └── note.py
├── services/            (Business logic — mostly unchanged!)
├── repositories/        (PostgreSQL — from Phase 2)
├── middleware/
│   ├── auth.py          (JWT dependency)
│   └── rate_limit.py    (slowapi or custom)
└── main.py              (app factory, lifespan events)
```

## Implementation Steps

### Step 1: Pydantic Schemas

```python
# schemas/person.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

class PersonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = []
    details: Optional[str] = None
    next_follow_up: Optional[date] = None
    follow_up_frequency_days: int = 0

class PersonResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    location: Optional[str]
    tags: List[str]
    relationship_score: float
    relationship_status: str
    interaction_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class PersonList(BaseModel):
    data: List[PersonResponse]
    total: int
```

### Step 2: FastAPI Routers (Port from Flask Blueprints)

```python
# routers/people.py
from fastapi import APIRouter, Depends, HTTPException, Query
from schemas.person import PersonCreate, PersonResponse, PersonList
from services.person_service import PersonService
from dependencies import get_person_service, get_current_user

router = APIRouter(prefix="/api/people", tags=["People"])

@router.get("", response_model=PersonList)
async def get_people(
    tag: Optional[str] = Query(None),
    service: PersonService = Depends(get_person_service),
    user_id: str = Depends(get_current_user),
):
    if tag:
        people = await service.get_by_tag(tag, user_id)
    else:
        people = await service.get_all_people(user_id)
    return PersonList(data=people, total=len(people))

@router.post("", response_model=PersonResponse, status_code=201)
async def create_person(
    data: PersonCreate,   # <-- Pydantic validates automatically!
    service: PersonService = Depends(get_person_service),
    user_id: str = Depends(get_current_user),
):
    return await service.create_person(user_id=user_id, **data.model_dump())
```

### Step 3: Async AI Service

```python
# services/ai_service.py (async version)
import google.generativeai as genai
import asyncio

class AIService:
    async def generate_person_blueprint(self, person, notes):
        loop = asyncio.get_event_loop()
        # Run blocking Gemini SDK call in thread pool
        result = await loop.run_in_executor(
            None, self._sync_generate, person, notes
        )
        return result
```

When `google-generativeai` adds native async support, switch to `await genai.generate_content_async(...)`.

### Step 4: Dependency Injection (FastAPI-native)

```python
# dependencies.py
from fastapi import Depends, HTTPException, Header
from services.token_service import TokenService

async def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid auth header")
    token = authorization[7:]
    try:
        payload = token_service.verify_token(token)
        return payload["sub"]
    except Exception:
        raise HTTPException(401, "Token expired or invalid")

def get_person_service() -> PersonService:
    return app.state.person_service
```

### Step 5: Run Both Servers in Parallel

During migration, run Flask on port 5000 and FastAPI on port 8000:

```yaml
# docker-compose.yml during migration
services:
  flask-legacy:
    build: .
    ports: ["5000:5000"]
    command: gunicorn app:app

  fastapi:
    build: .
    ports: ["8000:8000"]
    command: uvicorn main:app --host 0.0.0.0 --port 8000

  nginx:
    image: nginx:alpine
    # Route /api/v2/* → fastapi, everything else → flask
```

### Step 6: Performance Testing

Benchmark the async advantage:

```bash
# Test Flask: 4 concurrent AI calls
wrk -t4 -c4 -d30s http://localhost:5000/api/people/123/summary

# Test FastAPI: 100 concurrent AI calls
wrk -t4 -c100 -d30s http://localhost:8000/api/v2/people/123/summary
```

Expected result: Flask handles 4 concurrent AI calls (= number of workers). FastAPI handles 100+ because async doesn't block threads.

## Done When

- [ ] All API endpoints ported to FastAPI routers
- [ ] Pydantic schemas for all request/response payloads
- [ ] Auto-generated OpenAPI docs at `/docs`
- [ ] JWT auth middleware using FastAPI `Depends()`
- [ ] AI endpoints are async (no worker blocking)
- [ ] Rate limiting via `slowapi` or custom middleware
- [ ] Performance benchmark: 10x concurrency improvement on AI routes
- [ ] Flask app decommissioned, single FastAPI entry point

## Dependencies

```
fastapi>=0.110
uvicorn[standard]>=0.27
pydantic[email]>=2.5
slowapi>=0.1
httptools>=0.6
```

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| `run_in_executor` for Gemini SDK | Works now, no SDK changes needed | Not true async — but unblocks the event loop |
| API versioning (`/api/v2/`) | No breaking changes for existing clients | Temporary duplication during migration |
| Uvicorn over Gunicorn+Uvicorn | Simpler config for async | Less battle-tested for process management — use `--workers` flag |
| Pydantic v2 | 5-50x faster validation | Slightly different API from v1 docs — use `model_` prefix methods |

## What Carries Over Unchanged

The clean architecture pays off here:
- **Services**: Business logic is framework-agnostic. `PersonService`, `NoteService`, `AIService` work in both Flask and FastAPI.
- **Repositories**: Data access layer is unchanged — just injected differently.
- **Models**: Domain entities (`Person`, `User`, `Note`) stay the same.
- **Config**: `Config` class works identically.

Only **routes** and **middleware** need rewriting.
