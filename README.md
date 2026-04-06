# People Manager

An AI-powered personal relationship management system. Track contacts, nurture relationships, and never miss a follow-up.

## Features

**Contact Management**
- Structured contact fields: name, email, phone, company, job title, location, social links, birthday
- Full-text search across all fields
- Tags and labels for organization
- Filter contacts by tag

**Interaction Timeline**
- Add typed notes: meetings, calls, emails, events, follow-ups
- Chronological timeline per contact
- Activity feed across all contacts

**Relationship Intelligence**
- Auto-calculated relationship score based on interaction recency and frequency
- Visual status indicators: warm, lukewarm, cold
- Dashboard showing relationship health distribution

**Follow-up Reminders**
- Set follow-up dates on any contact
- Optional recurring frequency
- Mark complete with auto-reschedule
- Dashboard widget for due/overdue follow-ups

**AI Features** (powered by Google Gemini)
- Person Blueprint: comprehensive personality profile from notes
- Central Q&A: ask questions across all contacts
- AI tag suggestions based on contact details

**Import/Export**
- CSV import with intelligent column mapping
- CSV and JSON export

**Dashboard & Analytics**
- Total contacts, weekly additions, follow-ups due, cold contacts
- Relationship health chart
- Tag breakdown with counts
- Recently added contacts

**Authentication**
- Dual auth: session cookies (browser) + JWT Bearer tokens (API)
- Password change and reset flows
- Per-user data isolation

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: PostgreSQL (via SQLAlchemy + Alembic) / MongoDB / JSON files
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS v4, Zustand
- **AI**: Google Gemini API
- **Security**: bcrypt, PyJWT, Pydantic validation, security headers
- **CI/CD**: GitHub Actions (lint, test, Docker build)
- **Deployment**: Docker, Render.com

## Quick Start

### Backend

```bash
git clone https://github.com/fragenabhishek/People-Manager.git
cd People-Manager
pip install -r requirements.txt
uvicorn main:app --port 5000 --reload
```

The backend runs at `http://localhost:5000`. It uses JSON file storage by default — no database setup needed.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000` and proxies API calls to the backend.

### With Docker (PostgreSQL)

```bash
docker compose up
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | In production | Session + JWT signing key |
| `DATABASE_URL` | For PostgreSQL | e.g. `postgresql://user:pass@host:5432/dbname` |
| `MONGO_URI` | For MongoDB | MongoDB connection string (fallback if no DATABASE_URL) |
| `GEMINI_API_KEY` | For AI features | Google Gemini API key |
| `FLASK_DEBUG` | No | Enable debug mode (`True`/`False`) |
| `JWT_ACCESS_TOKEN_MINUTES` | No | Access token TTL (default: 15) |
| `JWT_REFRESH_TOKEN_MINUTES` | No | Refresh token TTL (default: 10080 / 7 days) |

Database priority: `DATABASE_URL` (SQL) > `MONGO_URI` (MongoDB) > JSON files (default).

## Project Structure

```
People-Manager/
├── main.py                    # FastAPI application factory
├── deps.py                    # FastAPI dependency injection (auth, services)
├── config/                    # Configuration with env validation
├── models/                    # Person, Note, User entities + SQLAlchemy tables
├── schemas/                   # Pydantic request/response models
├── repositories/              # Data access (SQL / MongoDB / JSON)
├── services/                  # Business logic
├── routers/                   # FastAPI API endpoints
├── utils/                     # Validation, logging, hashing, responses
├── alembic/                   # Database migrations
├── templates/                 # Jinja2 HTML (legacy browser UI)
├── static/                    # CSS, JS (legacy browser UI)
├── tests/                     # Pytest suite (107+ tests)
├── frontend/                  # Next.js React application
│   ├── src/app/               # App Router pages
│   ├── src/components/        # UI components
│   ├── src/lib/               # API client, utilities
│   └── src/stores/            # Zustand state management
├── Dockerfile                 # Production container
├── docker-compose.yml         # Docker with PostgreSQL
└── .github/workflows/ci.yml   # CI pipeline
```

## API Documentation

FastAPI provides auto-generated interactive API docs:
- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

## Architecture

- SOLID principles throughout
- Clean layered architecture (Models -> Repos -> Services -> Routers)
- Repository pattern with three storage backends (SQL, MongoDB, JSON)
- Dependency injection via FastAPI's `Depends` + `app.state`
- Pydantic validation on all request/response payloads
- Security headers, session cookies, JWT tokens
- Structured logging (JSON in production, human-readable in dev)
- 107+ automated tests with coverage reporting

See [ARCHITECTURE.md](ARCHITECTURE.md) | [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md) | [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)

## License

MIT License
