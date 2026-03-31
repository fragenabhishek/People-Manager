# People Manager - Comprehensive Design Document

> Full technical design reference covering architecture, data modeling, API design, security, and operational concerns.
> Version: 2.0 | Date: 2026-03-31

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Data Model](#3-data-model)
4. [API Design](#4-api-design)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [AI Integration](#6-ai-integration)
7. [Storage Strategy](#7-storage-strategy)
8. [Frontend Architecture](#8-frontend-architecture)
9. [Security Architecture](#9-security-architecture)
10. [Observability](#10-observability)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Design Decisions & Trade-offs](#12-design-decisions--trade-offs)
13. [Component Interaction Diagrams](#13-component-interaction-diagrams)

---

## 1. System Overview

### Purpose
People Manager is an AI-powered personal CRM for individuals who manage professional networks. It tracks contacts, interaction history, relationship health, and provides AI-driven insights.

### Core Capabilities
- **Contact Management**: Structured storage of contact information with 20+ fields
- **Interaction Timeline**: Typed notes (meeting, call, email, event, follow-up) attached to contacts
- **Relationship Intelligence**: Auto-calculated scores based on recency and frequency
- **Follow-up System**: Date-based reminders with optional recurring schedules
- **AI Features**: Person blueprints, cross-contact Q&A, tag suggestions (Google Gemini)
- **Import/Export**: CSV import with column mapping, CSV/JSON export
- **Dashboard**: Aggregated analytics (stats, health distribution, tag breakdown)

### Technical Stack
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Runtime | Python 3.11 | Server-side language |
| Framework | Flask 3.0 | HTTP routing, templating, sessions |
| Database (prod) | MongoDB Atlas | Document storage, cloud-hosted |
| Database (dev) | JSON files | Zero-config local development |
| AI | Google Gemini API | LLM-powered analysis |
| Auth | Flask-Bcrypt | Password hashing |
| Rate Limiting | Flask-Limiter | Request throttling |
| XSS Prevention | Bleach + Markdown | AI output sanitization |
| Frontend | Vanilla JS + CSS | No build step, no framework |
| Deployment | Render.com + Gunicorn | Production hosting |

---

## 2. Architecture

### 2.1 Layered Architecture

The application follows a strict layered architecture where each layer only communicates with the layer directly below it:

```
┌────────────────────────────────────────────────────────────────┐
│  LAYER 1: PRESENTATION                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  HTML Templates (Jinja2) + CSS + Vanilla JavaScript      │  │
│  │  • dashboard.html — main SPA shell                       │  │
│  │  • landing.html   — marketing page                       │  │
│  │  • login/register — auth pages                           │  │
│  │  • script.js      — all frontend logic (~480 lines)      │  │
│  │  • style.css      — full styling + dark mode             │  │
│  └──────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│  LAYER 2: HTTP ROUTING                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ auth_bp  │ │person_bp │ │  ai_bp   │ │    note_bp       │  │
│  │ /login   │ │/api/people│ │ /api/ask │ │ /api/notes       │  │
│  │ /register│ │ + tags   │ │ +summary │ │ + person/:id     │  │
│  │ /logout  │ │ +followup│ │ +suggest │ │ + activity       │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│  LAYER 3: MIDDLEWARE                                           │
│  ┌─────────────────┐  ┌──────────────────┐                    │
│  │ login_required   │  │ Flask-Limiter    │                    │
│  │ (auth decorator) │  │ (rate limiting)  │                    │
│  └─────────────────┘  └──────────────────┘                    │
├────────────────────────────────────────────────────────────────┤
│  LAYER 4: BUSINESS LOGIC (SERVICES)                            │
│  ┌──────────────┐ ┌────────────┐ ┌──────────────────────────┐ │
│  │PersonService │ │ AIService  │ │ ImportExportService      │ │
│  │ • CRUD       │ │ • Blueprint│ │ • CSV import/export      │ │
│  │ • Tags       │ │ • Q&A      │ │ • JSON export            │ │
│  │ • Follow-ups │ │ • Auto-tag │ │ • Column mapping         │ │
│  │ • Scoring    │ │ • Sanitize │ └──────────────────────────┘ │
│  │ • Dashboard  │ ├────────────┤ ┌──────────────────────────┐ │
│  ├──────────────┤ │AuthService │ │ Validators               │ │
│  │ NoteService  │ │ • Register │ │ • Required fields        │ │
│  │ • CRUD       │ │ • Login    │ │ • Length checks          │ │
│  │ • Activity   │ │ • Password │ │ • Email/URL format       │ │
│  └──────────────┘ └────────────┘ └──────────────────────────┘ │
├────────────────────────────────────────────────────────────────┤
│  LAYER 5: DATA ACCESS (REPOSITORIES)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              BaseRepository<T> (ABC, Generic)             │  │
│  │  find_all() | find_by_id() | create() | update()         │  │
│  │  delete()   | exists()                                    │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│           ┌─────────┼─────────────┐                            │
│  ┌────────┴───────┐ ┌─────────┐ ┌┴───────────────┐            │
│  │PersonRepository│ │UserRepo │ │ NoteRepository  │            │
│  │ + search()     │ │+findBy  │ │ + findByPerson()│            │
│  │ + findByTag()  │ │ Username│ │ + deleteByPerson│            │
│  │ + findDue()    │ └─────────┘ │ + countByPerson │            │
│  │ + getAllTags() │              └─────────────────┘            │
│  └────────────────┘                                            │
├────────────────────────────────────────────────────────────────┤
│  LAYER 6: MODELS (DOMAIN ENTITIES)                             │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐                   │
│  │   Person   │  │   Note   │  │   User   │                   │
│  │ (dataclass)│  │(dataclass│  │(dataclass│                   │
│  │ to_dict()  │  │ to_dict()│  │ to_dict()│                   │
│  │ from_dict()│  │from_dict()│ │from_dict()│                  │
│  │ update()   │  └──────────┘  │to_safe() │                   │
│  └────────────┘                └──────────┘                    │
├────────────────────────────────────────────────────────────────┤
│  LAYER 7: STORAGE                                              │
│  ┌─────────────────┐  ┌─────────────────┐                     │
│  │  MongoDB Atlas   │  │  JSON Files     │                     │
│  │  (if MONGO_URI)  │  │  (default)      │                     │
│  └─────────────────┘  └─────────────────┘                     │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 Design Patterns Used

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Application Factory** | `app.py:create_app()` | Configurable app creation, test-friendly |
| **Repository Pattern** | `repositories/` | Abstract storage behind a uniform interface |
| **Service Layer** | `services/` | Isolate business logic from HTTP handling |
| **Dependency Injection** | `create_app()` wiring | Services receive repos, routes receive services |
| **Blueprint Routing** | `routes/` | Modular, domain-separated route namespaces |
| **Strategy Pattern** | MongoDB vs JSON in repos | Runtime storage backend selection |
| **Decorator Pattern** | `@login_required` | Cross-cutting auth concern |
| **Factory Method** | `Person.from_dict()` | Construct entities from raw data |

### 2.3 Dependency Graph

```
create_app()
├── Config.validate()
├── initialize_repositories()
│   ├── PersonRepository(collection or file)
│   ├── UserRepository(collection or file)
│   └── NoteRepository(collection or file)
├── AuthService(user_repo, bcrypt)
├── PersonService(person_repo, note_repo)
├── AIService()  ← standalone, reads Config
├── NoteService(note_repo, person_repo)
├── ImportExportService(person_repo)
├── init_auth_routes(auth_service)
├── init_person_routes(person_service, ie_service)
├── init_ai_routes(ai_service, person_service, note_service)
└── init_note_routes(note_service)
```

---

## 3. Data Model

### 3.1 Entity Relationship Diagram

```
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│    User      │        │   Person    │        │    Note      │
├─────────────┤        ├─────────────┤        ├─────────────┤
│ id (PK)     │──┐     │ id (PK)     │──┐     │ id (PK)     │
│ username    │  │     │ user_id (FK)│  │     │ person_id(FK│
│ password_   │  ├────→│ name        │  ├────→│ user_id (FK)│
│   hash      │  │     │ email       │  │     │ content     │
│ email       │  │     │ phone       │  │     │ note_type   │
│ created_at  │  │     │ company     │  │     │ created_at  │
└─────────────┘  │     │ job_title   │  │     └─────────────┘
                 │     │ location    │  │
                 │     │ tags[]      │  │     Cardinality:
                 │     │ ...30 fields│  │     User 1──→ N Person
                 │     │ created_at  │  │     Person 1──→ N Note
                 │     │ updated_at  │  │     User 1──→ N Note
                 │     └─────────────┘  │
                 │                      │
                 └──────────────────────┘
```

### 3.2 Person Entity (Complete Field Reference)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Auto | Timestamp-based unique ID |
| `user_id` | string | Yes | Owner reference (FK → User) |
| `name` | string | Yes | Contact's full name |
| `email` | string | No | Email address |
| `phone` | string | No | Phone number |
| `company` | string | No | Company/organization name |
| `job_title` | string | No | Professional title |
| `location` | string | No | City/region |
| `linkedin_url` | string | No | LinkedIn profile URL |
| `twitter_handle` | string | No | Twitter/X handle |
| `website` | string | No | Personal/company website |
| `details` | string | No | Free-form notes (up to 50K chars) |
| `how_we_met` | string | No | Context of first meeting |
| `profile_image_url` | string | No | Avatar image URL |
| `birthday` | string | No | Date (YYYY-MM-DD) |
| `anniversary` | string | No | Date (YYYY-MM-DD) |
| `met_at` | string | No | Date first met (YYYY-MM-DD) |
| `tags` | string[] | No | Categorization labels |
| `next_follow_up` | string | No | Next follow-up date (YYYY-MM-DD) |
| `follow_up_frequency_days` | int | No | Recurring interval (0 = one-time) |
| `relationship_score` | float | Auto | 0-100, calculated from interactions |
| `relationship_status` | string | Auto | new/warm/lukewarm/cold |
| `last_interaction_at` | string | Auto | ISO 8601 timestamp |
| `interaction_count` | int | Auto | Total notes count |
| `created_at` | string | Auto | ISO 8601 timestamp |
| `updated_at` | string | Auto | ISO 8601 timestamp |

### 3.3 Relationship Scoring Algorithm

```
Input:
  - notes[]: All interaction notes for this person
  - now: Current datetime

Algorithm:
  1. Count interactions: interaction_count = len(notes)
  2. Find latest note: latest = max(notes, key=created_at)
  3. Calculate days since: days = (now - latest.created_at).days
  4. Recency score (0-100):  max(0, 100 - days * 2)
     → Full score at 0 days, zero at 50+ days
  5. Frequency score (0-100): min(100, interaction_count * 10)
     → Caps at 10+ interactions
  6. Total: (recency * 0.6) + (frequency * 0.4)

Status mapping:
  - days <= 14  → warm
  - days <= 30  → lukewarm
  - days >  30  → cold
  - no notes    → new (or cold if has details)

Trigger: Calculated at read time (no background jobs)
Persistence: Saved back to storage when changed
```

---

## 4. API Design

### 4.1 Conventions

- **Base path**: `/api/` for all JSON endpoints
- **Auth**: Session-based (cookie)
- **Content-Type**: `application/json` for request/response bodies
- **Response format** (standardized via `APIResponse`):

```json
// Success
{
    "success": true,
    "data": { ... },
    "message": "Optional message",
    "timestamp": "2026-03-31T10:00:00"
}

// Error
{
    "success": false,
    "error": "Human-readable message",
    "error_code": "VALIDATION_ERROR",
    "timestamp": "2026-03-31T10:00:00"
}
```

### 4.2 Complete API Reference

#### Authentication (HTML form-based)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET/POST | `/register` | No | Registration page/handler |
| GET/POST | `/login` | No | Login page/handler |
| GET | `/logout` | Yes | Clear session, redirect |

#### Contacts CRUD
| Method | Endpoint | Auth | Request | Response |
|--------|----------|------|---------|----------|
| GET | `/api/people` | Yes | `?tag=X` (optional) | `Person[]` |
| GET | `/api/people/:id` | Yes | — | `Person` |
| GET | `/api/people/search/:q` | Yes | — | `Person[]` |
| POST | `/api/people` | Yes | `Person` fields | `{success, data: Person}` |
| PUT | `/api/people/:id` | Yes | Partial `Person` | `Person` |
| DELETE | `/api/people/:id` | Yes | — | `{message}` |

#### Tags
| Method | Endpoint | Auth | Request | Response |
|--------|----------|------|---------|----------|
| GET | `/api/people/tags` | Yes | — | `string[]` |
| POST | `/api/people/:id/tags` | Yes | `{tags: [...]}` | `Person` |
| DELETE | `/api/people/:id/tags/:tag` | Yes | — | `Person` |

#### Follow-ups
| Method | Endpoint | Auth | Request | Response |
|--------|----------|------|---------|----------|
| GET | `/api/people/followups` | Yes | — | `Person[]` |
| PUT | `/api/people/:id/followup` | Yes | `{date, frequency_days}` | `Person` |
| POST | `/api/people/:id/followup/complete` | Yes | — | `Person` |

#### Notes
| Method | Endpoint | Auth | Request | Response |
|--------|----------|------|---------|----------|
| GET | `/api/notes/person/:id` | Yes | — | `Note[]` |
| POST | `/api/notes/person/:id` | Yes | `{content, note_type}` | `{success, data: Note}` |
| DELETE | `/api/notes/:id` | Yes | — | `{message}` |
| GET | `/api/notes/activity` | Yes | `?limit=N` | `Activity[]` |

#### AI Features
| Method | Endpoint | Auth | Request | Response |
|--------|----------|------|---------|----------|
| POST | `/api/people/:id/summary` | Yes | — | `{summary, generated_at}` |
| POST | `/api/ask` | Yes | `{question}` | `{question, answer, generated_at}` |
| POST | `/api/people/:id/suggest-tags` | Yes | — | `{tags: [...]}` |

#### System
| Method | Endpoint | Auth | Response |
|--------|----------|------|----------|
| GET | `/health` | No | `{status, storage, ai}` |
| GET | `/api/people/dashboard/stats` | Yes | `DashboardStats` |
| POST | `/api/people/import/csv` | Yes | `{imported, skipped, errors}` |
| GET | `/api/people/export/csv` | Yes | CSV file download |
| GET | `/api/people/export/json` | Yes | JSON file download |

---

## 5. Authentication & Authorization

### 5.1 Authentication Flow

```
Register:
  Browser → POST /register (username, password, confirm, email)
         → AuthService.register_user()
         → Validator.validate_user_registration()
         → UserRepository.find_by_username() → check uniqueness
         → bcrypt.generate_password_hash()
         → UserRepository.create(User)
         → redirect to /login

Login:
  Browser → POST /login (username, password)
         → AuthService.authenticate_user()
         → UserRepository.find_by_username()
         → bcrypt.check_password_hash()
         → Set session: {logged_in, user_id, username}
         → redirect to /dashboard

Protected Route:
  Browser → GET /api/people
         → @login_required decorator
         → Check session['logged_in']
         → If missing: return 401 (API) or redirect to /login (page)
         → If present: proceed to handler
```

### 5.2 Authorization Model

- **Data isolation**: Every query filters by `session['user_id']`
- **Ownership verification**: Services check `person.user_id == user_id` before returning/modifying
- **No role-based access**: Single-user-type system (all users are equal)

---

## 6. AI Integration

### 6.1 Architecture

```
┌──────────────────────────────────────────────┐
│                  AIService                    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  generate_person_blueprint()         │    │
│  │  ├─ Build structured prompt          │    │
│  │  │  (contact fields + notes history) │    │
│  │  ├─ genai.GenerativeModel.generate() │───→ Google Gemini API
│  │  ├─ markdown.markdown(response)      │    │
│  │  └─ bleach.clean(html)               │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  answer_question()                   │    │
│  │  ├─ Build context from all contacts  │    │
│  │  ├─ genai.GenerativeModel.generate() │───→ Google Gemini API
│  │  └─ sanitize output                  │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  suggest_tags()                      │    │
│  │  ├─ Prompt for comma-separated tags  │    │
│  │  ├─ genai.GenerativeModel.generate() │───→ Google Gemini API
│  │  └─ Parse comma-separated response   │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  Safety: All Gemini harm categories set to   │
│  BLOCK_NONE (personal data context requires  │
│  flexibility in content analysis)            │
│                                              │
│  Graceful Degradation: When GEMINI_API_KEY   │
│  is not set, all AI endpoints return 503     │
│  with a descriptive message.                 │
└──────────────────────────────────────────────┘
```

### 6.2 Output Sanitization Pipeline

```
AI Raw Text → markdown.markdown() → HTML → bleach.clean() → Safe HTML

Allowed tags: p, br, strong, em, ul, ol, li, h1-h4,
              blockquote, code, pre, hr, a, span
Allowed attrs: a[href, title], span[class]
```

---

## 7. Storage Strategy

### 7.1 Dual Backend Design

```
Environment Variable MONGO_URI
    │
    ├─ SET ──→ MongoDB Atlas
    │          • 3 collections: people, users, notes
    │          • Cloud-hosted, horizontally scalable
    │          • PyMongo driver with native operations
    │
    └─ NOT SET ──→ JSON Files
                   • 3 files: data.json, users.json, notes.json
                   • Auto-created if missing
                   • Full file read/write on every operation
                   • Zero configuration needed
```

### 7.2 Repository Interface

All three repositories implement `BaseRepository<T>`:

```python
class BaseRepository(ABC, Generic[T]):
    find_all(filters: dict) -> List[T]
    find_by_id(entity_id: str) -> Optional[T]
    create(entity: T) -> T
    update(entity_id: str, entity: T) -> Optional[T]
    delete(entity_id: str) -> bool
    exists(filters: dict) -> bool
```

Extended methods per repository:
- **PersonRepository**: `search()`, `find_by_tag()`, `find_due_followups()`, `get_all_tags()`
- **NoteRepository**: `find_by_person()`, `delete_by_person()`, `count_by_person()`
- **UserRepository**: `find_by_username()`

---

## 8. Frontend Architecture

### 8.1 Single-Page Application (SPA-like)

The dashboard is a single HTML page (`dashboard.html`) that acts as an SPA shell. JavaScript handles all navigation via view switching:

```
Views (tab-based, one visible at a time):
├── Contacts View (default)
│   ├── Search bar
│   ├── AI Q&A collapsible bar
│   ├── Tag filter indicator
│   └── People grid (card-based)
├── Dashboard View
│   ├── Stats cards (total, weekly, follow-ups, cold)
│   ├── Health chart (horizontal bars)
│   ├── Follow-up list
│   ├── Recently added
│   └── Tag breakdown
└── Activity View
    └── Chronological note feed

Overlays:
├── Person Modal (add/edit form)
├── Note Modal (add interaction)
├── Import Modal (CSV upload)
├── Confirm Dialog
└── Person Detail Drawer (slides from right)
```

### 8.2 State Management

```
Global State (module-level variables):
  allPeople[]        — cached contact list
  currentPersonId    — active drawer contact
  currentTagFilter   — active tag filter
  confirmResolve     — promise resolver for confirm dialog
```

### 8.3 Dark Mode

- Toggle: Button in topbar
- Persistence: `localStorage.darkMode`
- Implementation: `.dark` class on `<body>` switches CSS custom properties

---

## 9. Security Architecture

| Layer | Mechanism | Configuration |
|-------|-----------|---------------|
| **Password Storage** | bcrypt hash | Via Flask-Bcrypt |
| **Session Management** | Server-side Flask sessions | HttpOnly, SameSite=Lax |
| **Rate Limiting** | Flask-Limiter | 200/day default, 10/min login, 60/min API, 20/min AI |
| **XSS Prevention** | Bleach sanitization | AI outputs only; frontend uses `escapeHtml()` |
| **Input Validation** | Centralized Validator class | Required fields, length, format |
| **Data Isolation** | user_id scoping | All queries filtered by authenticated user |
| **Error Handling** | Generic error messages | Internal details logged, not exposed |
| **Configuration** | dotenv + environment variables | No hardcoded secrets |

---

## 10. Observability

### 10.1 Logging

```
Logger: Python stdlib logging
Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
Output: stdout (console handler)
Levels:
  - INFO: User actions (login, register, CRUD)
  - WARNING: Auth failures, validation errors
  - ERROR: Storage/API failures
  - DEBUG: Query results, counts
```

### 10.2 Health Check

```
GET /health → {
    "status": "ok",
    "storage": "mongodb" | "json",
    "ai": true | false
}
```

---

## 11. Deployment Architecture

### 11.1 Production (Render.com)

```
Internet → Render.com → Gunicorn (WSGI) → Flask App
                                              ↓
                                         MongoDB Atlas (DB)
                                              ↓
                                         Google Gemini (AI)
```

### 11.2 Local Development

```
Browser → Flask Dev Server (port 5000) → JSON Files
                                          ↓
                                     Google Gemini (optional)
```

---

## 12. Design Decisions & Trade-offs

### 12.1 Vanilla JS vs Framework (React/Vue/Svelte)

| Aspect | Vanilla JS (chosen) | Framework |
|--------|---------------------|-----------|
| Bundle size | 0 KB framework overhead | 30-100 KB |
| Build step | None | Required (Webpack/Vite) |
| Load time | Instant | Depends on bundle |
| Maintainability | Harder at scale | Better at scale |
| Component reuse | Manual | Built-in |
| Developer productivity | Lower for complex UI | Higher |
| Learning curve | None | Framework-specific |

**Decision**: Vanilla JS was chosen for simplicity, zero build step, and fast deployment. The frontend is ~480 lines, which is manageable without a framework. If the UI grows significantly (e.g., drag-and-drop, real-time collaboration), a framework migration should be considered.

### 12.2 MongoDB + JSON Dual Backend vs Single Backend

| Aspect | Dual (chosen) | Single |
|--------|---------------|--------|
| Dev experience | Zero-config JSON locally | Need DB locally |
| Production ready | MongoDB for scale | Same as prod |
| Code complexity | 2x repository methods | 1x |
| Test parity | Dev ≠ Prod behavior | Dev = Prod |
| Maintenance | Higher | Lower |

**Decision**: Dual backend prioritizes developer experience (clone → run → works). The trade-off is behavioral differences between JSON and MongoDB (sorting, filtering, concurrency).

### 12.3 Session-Based Auth vs JWT

| Aspect | Sessions (chosen) | JWT |
|--------|-------------------|-----|
| State | Server-side | Stateless |
| Scalability | Sticky sessions or shared store | Any server |
| Revocation | Immediate | Hard (needs blacklist) |
| CSRF | Vulnerable (needs tokens) | Not vulnerable |
| Implementation | Simpler (Flask built-in) | More code |

**Decision**: Sessions are simpler for a server-rendered app. The trade-off is CSRF vulnerability and scaling limitations (session store needed for multi-server).

### 12.4 Relationship Score at Read Time vs Background Job

| Aspect | Read-time (chosen) | Background |
|--------|---------------------|------------|
| Freshness | Always current | Eventually consistent |
| Complexity | No job infrastructure | Need scheduler |
| Performance | Slower reads | Faster reads |
| Infrastructure | None | Redis/Celery needed |

**Decision**: Read-time calculation avoids background infrastructure. The trade-off is O(n) note queries per contact list load (see N+1 issue in IMPROVEMENTS.md).

### 12.5 Tags as Array on Person vs Separate Entity

| Aspect | Array (chosen) | Separate entity |
|--------|----------------|-----------------|
| Query simplicity | Single document read | Join/lookup needed |
| Tag management | In-place update | Dedicated CRUD |
| Storage | Denormalized | Normalized |
| Tag metadata | Not possible | Can add color, description |
| Scale | Good for < 50 tags/person | Better for complex taxonomies |

**Decision**: Embedded array is simpler for a personal CRM where tags are lightweight labels. If tags need metadata (color, visibility, shared across users), migration to a separate entity is needed.

---

## 13. Component Interaction Diagrams

### 13.1 Contact Creation Flow

```
User clicks "Add Contact"
  → openPersonModal() [script.js]
  → User fills form, clicks "Save"
  → handlePersonSubmit() [script.js]
  → POST /api/people with JSON body
  → auth_middleware: verify session
  → person_routes.add_person()
  → PersonService.create_person()
    → Validator.validate_person_data()
    → Parse tags from comma-separated string
    → Build Person dataclass
    → PersonRepository.create()
      → Generate timestamp ID
      → MongoDB: insert_one() / JSON: read-append-write
  → Return 201 with Person data
  → Frontend: close modal, show toast, reload list
```

### 13.2 Dashboard Load Flow

```
User clicks "Dashboard" tab
  → switchView('dashboard') [script.js]
  → loadDashboard() [script.js]
  → GET /api/people/dashboard/stats
  → person_routes.dashboard_stats()
  → PersonService.get_dashboard_stats()
    → get_all_people() [triggers relationship score refresh]
    → Calculate: total, weekly additions, due follow-ups, cold contacts
    → Aggregate: tag counts, status distribution
    → Return: stats object with lists
  → Frontend: populate stat cards, health chart, lists
```

### 13.3 AI Blueprint Generation Flow

```
User clicks "Generate Blueprint" in drawer
  → generateBlueprint(personId) [script.js]
  → POST /api/people/:id/summary
  → ai_routes.generate_summary()
  → PersonService.get_person_by_id() → verify ownership
  → NoteService.get_notes_for_person() → get interaction history
  → AIService.generate_person_blueprint(person, notes)
    → Build structured prompt with contact fields + notes
    → genai.GenerativeModel.generate_content(prompt)
    → Wait for Gemini API response
    → markdown.markdown(response.text) → convert to HTML
    → bleach.clean(html) → sanitize for XSS
  → Return {summary: sanitized_html, generated_at: timestamp}
  → Frontend: render HTML in drawer section
```

---

*This document should be kept in sync with code changes. Last updated: 2026-03-31.*
