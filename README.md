# People Manager

An AI-powered personal relationship management system. Track contacts, nurture relationships, and never miss a follow-up.

**Live Demo**: [https://people-manager-kebr.onrender.com/](https://people-manager-kebr.onrender.com/)

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

**Modern UI**
- Three-panel layout with sidebar, grid, and detail drawer
- Dark mode with persistence
- Keyboard shortcuts (N = new, / = search, Esc = close)
- Fully responsive (desktop, tablet, mobile)
- Toast notification system

## Quick Start

```bash
git clone https://github.com/fragenabhishek/People-Manager.git
cd People-Manager
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`. The app uses JSON file storage by default.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` | For cloud DB | MongoDB Atlas connection string |
| `GEMINI_API_KEY` | For AI features | Google Gemini API key |
| `SECRET_KEY` | Recommended | Flask session secret key |
| `FLASK_DEBUG` | No | Enable debug mode (True/False) |

## Project Structure

```
People-Manager/
├── app.py                    # Application factory
├── config/                   # Configuration
├── models/                   # Person, Note, User entities
├── repositories/             # Data access (MongoDB/JSON)
├── services/                 # Business logic
├── routes/                   # API endpoints
├── middleware/                # Auth, rate limiting
├── utils/                    # Validation, logging, responses
├── templates/                # HTML templates
├── static/                   # CSS, JS
├── docs/                     # Requirements + System Design
└── requirements.txt
```

## Architecture

- SOLID principles throughout
- Clean layered architecture (Models → Repos → Services → Routes)
- Repository pattern with dual storage (MongoDB/JSON)
- Dependency injection (wired in app factory)
- Rate limiting, session security, XSS prevention
- Structured logging and standardized API responses

See [ARCHITECTURE.md](ARCHITECTURE.md) | [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md) | [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)

## Tech Stack

- **Backend**: Python 3.11, Flask 3.0
- **Database**: MongoDB Atlas / JSON files
- **AI**: Google Gemini API
- **Frontend**: Vanilla JavaScript, CSS Custom Properties
- **Security**: Flask-Bcrypt, Flask-Limiter, Bleach
- **Hosting**: Render.com + Gunicorn

## License

MIT License
