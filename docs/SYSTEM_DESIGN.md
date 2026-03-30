# People Manager - System Design Document

## 1. Architecture Overview

People Manager follows a **layered clean architecture** with strict separation of concerns, enabling independent development, testing, and swapping of components.

```
┌──────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Landing Page │ Dashboard │ Auth Pages │ Detail Drawer  │ │
│  │  (HTML/CSS/JS - Vanilla, No Framework Dependency)       │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Flask Routes (Blueprints)                              │ │
│  │  auth_routes │ person_routes │ ai_routes │ note_routes  │ │
│  └─────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│                    MIDDLEWARE LAYER                           │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │  Auth Middleware│  │  Rate Limiter  │                     │
│  │  (login_required│  │  (Flask-Limiter)│                    │
│  └────────────────┘  └────────────────┘                     │
├──────────────────────────────────────────────────────────────┤
│                    BUSINESS LOGIC LAYER                       │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────────────────┐  │
│  │ PersonService│ │  AIService  │ │ ImportExportService   │  │
│  │              │ │  (Gemini)   │ │ (CSV/JSON)            │  │
│  ├──────────────┤ ├─────────────┤ ├──────────────────────┤  │
│  │ NoteService  │ │ AuthService │ │ Validators            │  │
│  └──────────────┘ └─────────────┘ └──────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│                    DATA ACCESS LAYER                          │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              BaseRepository<T> (ABC)                 │    │
│  │  find_all │ find_by_id │ create │ update │ delete    │    │
│  └───────────────────┬──────────────────────────────────┘    │
│           ┌──────────┼──────────┐                            │
│  ┌────────┴───────┐  │  ┌──────┴────────┐                   │
│  │PersonRepository│  │  │NoteRepository │                   │
│  └────────┬───────┘  │  └──────┬────────┘                   │
│           │   ┌──────┴──────┐  │                             │
│           │   │UserRepository│  │                             │
│           │   └─────────────┘  │                             │
├───────────┼────────────────────┼─────────────────────────────┤
│           ▼                    ▼                             │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   MongoDB Atlas  │  │  JSON Files     │                   │
│  │   (Production)   │  │  (Development)  │                   │
│  └─────────────────┘  └─────────────────┘                   │
├──────────────────────────────────────────────────────────────┤
│                    EXTERNAL SERVICES                          │
│  ┌───────────────────────────────────────────────────┐       │
│  │  Google Gemini API (AI Blueprints, Q&A, Tags)     │       │
│  └───────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

## 2. Data Models

### 2.1 Person Entity

```
Person
├── id: str (auto-generated timestamp-based)
├── user_id: str (owner reference)
│
├── Core Identity
│   ├── name: str (required)
│   ├── email: str
│   ├── phone: str
│   ├── company: str
│   ├── job_title: str
│   ├── location: str
│   └── profile_image_url: str
│
├── Social Links
│   ├── linkedin_url: str
│   ├── twitter_handle: str
│   └── website: str
│
├── Context
│   ├── details: str (free-form notes)
│   ├── how_we_met: str
│   └── met_at: str (date)
│
├── Dates
│   ├── birthday: str
│   └── anniversary: str
│
├── Organization
│   └── tags: List[str]
│
├── Follow-up
│   ├── next_follow_up: str (date)
│   └── follow_up_frequency_days: int
│
├── Relationship Intelligence (auto-calculated)
│   ├── relationship_score: float (0-100)
│   ├── relationship_status: str (new|warm|lukewarm|cold)
│   ├── last_interaction_at: str
│   └── interaction_count: int
│
└── Timestamps
    ├── created_at: str (ISO 8601)
    └── updated_at: str (ISO 8601)
```

### 2.2 Note Entity

```
Note
├── id: str
├── person_id: str (foreign key → Person)
├── user_id: str (owner reference)
├── content: str (required)
├── note_type: str (general|meeting|call|email|event|follow_up)
└── created_at: str (ISO 8601)
```

### 2.3 User Entity

```
User
├── id: str
├── username: str (unique, required)
├── password_hash: str (bcrypt)
├── email: str (optional)
└── created_at: str (ISO 8601)
```

## 3. Design Patterns

### 3.1 Repository Pattern
Every data entity has a repository that abstracts storage. Repositories implement `BaseRepository<T>` and support both MongoDB and JSON file storage, chosen at startup via configuration.

### 3.2 Service Layer Pattern
Business logic lives in services, not in routes. Services:
- Validate input via the Validator utility
- Enforce authorization (user_id matching)
- Orchestrate cross-entity operations (e.g., deleting a person also deletes their notes)
- Calculate derived data (relationship scores)

### 3.3 Dependency Injection
All dependencies are wired in `app.py:create_app()`:
```
Repositories → Services → Routes (via init_*_routes)
```
No service or route creates its own dependencies.

### 3.4 Blueprint-based Modular Routing
Each domain has its own Flask Blueprint:
- `auth_bp` — authentication
- `person_bp` — contacts + tags + follow-ups + import/export + dashboard
- `ai_bp` — AI features
- `note_bp` — interaction notes

### 3.5 Application Factory
`create_app()` produces a fully configured Flask instance, enabling test fixtures and multiple configurations.

## 4. Relationship Scoring Algorithm

Relationship score is auto-calculated whenever contacts are retrieved:

```python
recency_score = max(0, 100 - (days_since_last_interaction * 2))
frequency_score = min(100, interaction_count * 10)
total_score = (recency_score * 0.6) + (frequency_score * 0.4)

Status thresholds:
- warm:     days_since <= 14
- lukewarm: days_since <= 30
- cold:     days_since > 30
- new:      no interactions and no details
```

This runs at read time (no background jobs needed), ensuring scores are always fresh.

## 5. AI Integration Architecture

```
┌───────────────────────────────┐
│        AIService              │
│  ┌────────────────────────┐   │
│  │ generate_person_blueprint│──┐
│  │ answer_question         │  │ → Google Gemini API
│  │ suggest_tags            │──┘
│  └────────────────────────┘   │
│  ┌────────────────────────┐   │
│  │ sanitize_ai_html()     │   │ → markdown → HTML → bleach sanitize
│  └────────────────────────┘   │
└───────────────────────────────┘
```

**Safety**: All AI output is converted from Markdown to HTML, then sanitized with `bleach` to prevent XSS injection. Only safe HTML tags are allowed.

**Graceful Degradation**: When `GEMINI_API_KEY` is not set, `AIService.is_enabled()` returns `False` and all AI endpoints return 503 with a helpful message.

## 6. Security Architecture

| Layer | Mechanism |
|-------|-----------|
| **Authentication** | bcrypt password hashing, Flask session-based auth |
| **Authorization** | `user_id` scoping on all queries, ownership verification in services |
| **Session Security** | HttpOnly cookies, SameSite=Lax |
| **Rate Limiting** | Flask-Limiter (login: 10/min, API: 60/min, AI: 20/min) |
| **Input Validation** | Centralized Validator class, applied in service layer |
| **XSS Prevention** | AI outputs sanitized via markdown + bleach |
| **Error Handling** | Internal errors logged, generic messages returned to client |
| **Configuration** | dotenv for secrets, no hardcoded credentials |

## 7. Data Flow: Adding a Contact

```
Frontend (JS)                    Backend
    │                               │
    ├─ POST /api/people ──────────→ │
    │  {name, email, tags, ...}     │
    │                               ├─ auth_middleware: verify session
    │                               ├─ person_routes: extract data
    │                               ├─ PersonService.create_person()
    │                               │   ├─ Validator.validate_person_data()
    │                               │   ├─ Parse tags from string
    │                               │   ├─ Build Person entity
    │                               │   └─ PersonRepository.create()
    │                               │       ├─ Generate ID
    │                               │       └─ MongoDB insert / JSON write
    │                               │
    │  ← 201 {person data} ────────┤
    │                               │
    ├─ Update grid                  │
    └─ Show toast                   │
```

## 8. Data Flow: AI Blueprint Generation

```
Frontend                         Backend                         External
    │                               │                               │
    ├─ POST /api/people/:id/summary │                               │
    │                               ├─ Get person from service      │
    │                               ├─ Get notes from NoteService   │
    │                               ├─ AIService.generate_blueprint()│
    │                               │   ├─ Build structured prompt  │
    │                               │   │  (contact fields + notes) │
    │                               │   ├─ Send to Gemini ─────────→│
    │                               │   │                           │← AI response
    │                               │   ├─ markdown → HTML          │
    │                               │   └─ bleach.clean() (XSS)    │
    │  ← {summary, generated_at} ──┤                               │
    │                               │                               │
    ├─ Render sanitized HTML        │                               │
    └─ Show in drawer               │                               │
```

## 9. Storage Architecture

### MongoDB (Production)
```
Database: people_manager
├── Collection: people    (Person documents)
├── Collection: users     (User documents)
└── Collection: notes     (Note documents)
```

### JSON Files (Development)
```
Project Root
├── data.json    (Person array)
├── users.json   (User array)
└── notes.json   (Note array)
```

Storage backend is selected automatically:
- `MONGO_URI` environment variable set → MongoDB
- No `MONGO_URI` → JSON files (auto-created if missing)

## 10. Frontend Architecture

### Layout Structure
```
┌─────────────────────────────────────────────┐
│  Topbar (brand, user, dark mode, logout)    │
├──────────┬──────────────────────────────────┤
│          │  Main Content Area               │
│ Sidebar  │  ┌─ Contacts View (default)      │
│ ├ Contacts│  │  ├ Search + Add button       │
│ ├ Dashboard│ │  ├ AI Q&A bar               │
│ ├ Activity│  │  ├ People grid (cards)       │
│ │         │  │  └ Empty state               │
│ ├ Tags    │  │                              │
│ │         │  ├─ Dashboard View              │
│ ├ Import  │  │  ├ Stats cards               │
│ └ Export  │  │  ├ Health chart              │
│          │  │  ├ Follow-ups / Recent        │
│          │  │  └ Tag breakdown              │
│          │  │                              │
│          │  └─ Activity View               │
│          │     └ Chronological feed         │
├──────────┴──────────────────────────────────┤
│  Person Detail Drawer (slides from right)   │
│  ├ Contact info  ├ Tags   ├ Notes timeline  │
│  ├ AI Blueprint  └ Follow-up status         │
└─────────────────────────────────────────────┘
```

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `N` | Open new contact modal |
| `/` | Focus search bar |
| `Esc` | Close any open modal/drawer |

### Dark Mode
Toggled via button, persisted in `localStorage`. CSS variables switch the entire color palette.

## 11. Deployment Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
│   Browser   │────→│  Render.com      │────→│ MongoDB Atlas  │
│   (Client)  │     │  ┌─────────────┐ │     │ (Cloud DB)     │
│             │     │  │  Gunicorn   │ │     └────────────────┘
│             │     │  │  (4 workers)│ │
│             │     │  │  ┌───────┐  │ │     ┌────────────────┐
│             │     │  │  │ Flask │  │─│────→│ Google Gemini  │
│             │     │  │  └───────┘  │ │     │ (AI API)       │
│             │     │  └─────────────┘ │     └────────────────┘
│             │     └──────────────────┘
└─────────────┘
```

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Recommended | Flask session secret |
| `MONGO_URI` | For MongoDB | MongoDB connection string |
| `GEMINI_API_KEY` | For AI features | Google Gemini API key |
| `PORT` | Auto (Render) | Server port (default 5000) |
| `FLASK_DEBUG` | No | Enable debug mode |

## 12. Project Structure

```
People-Manager/
├── app.py                          # Application factory + wiring
├── config/
│   └── config.py                   # Centralized configuration
├── models/
│   ├── person.py                   # Person entity (30+ fields)
│   ├── note.py                     # Interaction note entity
│   └── user.py                     # User entity
├── repositories/
│   ├── base_repository.py          # Abstract base (Generic[T])
│   ├── person_repository.py        # People data access + search
│   ├── note_repository.py          # Notes data access
│   └── user_repository.py          # Users data access
├── services/
│   ├── person_service.py           # Contact CRUD + tags + scoring + dashboard
│   ├── note_service.py             # Notes CRUD + activity feed
│   ├── auth_service.py             # Authentication + registration
│   ├── ai_service.py               # Gemini integration + sanitization
│   └── import_export_service.py    # CSV/JSON import/export
├── routes/
│   ├── auth_routes.py              # Auth endpoints
│   ├── person_routes.py            # Contact + tag + followup + I/E endpoints
│   ├── ai_routes.py                # AI endpoints
│   └── note_routes.py              # Note endpoints
├── middleware/
│   └── auth_middleware.py          # login_required decorator
├── utils/
│   ├── validators.py               # Input validation rules
│   ├── response.py                 # Standardized API responses
│   └── logger.py                   # Structured logging setup
├── templates/
│   ├── dashboard.html              # Main app UI
│   ├── landing.html                # Marketing/landing page
│   ├── login.html                  # Login page
│   └── register.html               # Registration page
├── static/
│   ├── style.css                   # Dashboard + dark mode styles
│   ├── landing.css                 # Landing page styles
│   ├── auth.css                    # Auth pages styles
│   └── script.js                   # Frontend application logic
├── docs/
│   ├── REQUIREMENTS.md             # Product requirements
│   └── SYSTEM_DESIGN.md            # This document
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render.com deployment config
└── .gitignore
```

## 13. Future Roadmap

### Phase 1 (Next)
- Email integration (sync contacts from Gmail/Outlook)
- Calendar integration (auto-log meetings as notes)
- PWA support (service worker + offline caching)
- Push notifications for follow-up reminders

### Phase 2
- Contact merging/deduplication
- Shared contact lists (team features)
- Webhook integrations (Zapier, n8n)
- Full-text search with MongoDB Atlas Search

### Phase 3
- Mobile app (React Native or Flutter)
- Voice notes (Whisper transcription → note)
- LinkedIn profile enrichment
- Contact recommendations ("You should connect X and Y")
