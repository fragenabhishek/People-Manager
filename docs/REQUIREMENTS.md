# People Manager - Product Requirements Document (PRD)

## Vision

People Manager is an AI-powered personal relationship management system that helps professionals remember every connection, nurture relationships, and never miss a follow-up. Unlike heavyweight enterprise CRMs, it is built for individuals who manage their own networks.

## Target Users

| Persona | Use Case |
|---------|----------|
| **Sales Professionals** | Track prospects, remember client details, follow-up automation |
| **Event Networkers** | Rapid capture after conferences, recall who they met and discussed |
| **Entrepreneurs** | Manage investors, advisors, partners, customers |
| **Recruiters** | Track candidates, interview details, talent pipeline |
| **Freelancers** | Client management, referral tracking, project history |
| **Students & Academics** | Professional network building, research contacts |

## Competitive Landscape

| Feature | Clay | Dex | Monica | Folk | **People Manager** |
|---------|------|-----|--------|------|---------------------|
| Structured contact fields | Yes | Yes | Yes | Yes | **Yes** |
| Tags/Labels | Yes | Yes | Yes | Yes | **Yes** |
| Follow-up reminders | Yes | Yes | Yes | Yes | **Yes** |
| Interaction notes timeline | Yes | Yes | Yes | No | **Yes** |
| Relationship scoring | Yes | Yes | No | No | **Yes** |
| AI blueprints/profiles | No | No | No | No | **Yes (unique)** |
| AI Q&A across contacts | No | No | No | No | **Yes (unique)** |
| AI auto-tag suggestions | No | No | No | No | **Yes (unique)** |
| CSV Import/Export | Yes | Yes | Yes | Yes | **Yes** |
| Dark mode | Yes | Yes | No | Yes | **Yes** |
| Self-hostable | No | No | Yes | No | **Yes** |
| Open source | No | No | Yes | No | **Yes** |
| Free tier | Paid | Paid | Free | Paid | **Free** |
| Price | $10-40/mo | $12/mo | Free | $20/mo | **Free** |

### Key Differentiators
1. **AI-Native**: Only personal CRM with AI person blueprints, cross-contact Q&A, and auto-tag suggestions
2. **Free + Open Source**: Full feature set at zero cost, self-hostable
3. **Modern Architecture**: Clean SOLID architecture, dual storage (cloud/local), professional codebase

---

## Functional Requirements

### FR-1: Contact Management (Core)
- **FR-1.1**: CRUD operations for contacts with structured fields
- **FR-1.2**: Structured fields: name, email, phone, company, job_title, location, linkedin, twitter, website, birthday, anniversary, how_we_met, met_at, profile_image_url
- **FR-1.3**: Free-form details/notes text field
- **FR-1.4**: Full-text search across all fields (name, company, tags, details, job_title)
- **FR-1.5**: Backward compatibility with existing data

### FR-2: Tags & Organization
- **FR-2.1**: Add/remove tags (comma-separated) on any contact
- **FR-2.2**: Filter contacts by tag
- **FR-2.3**: View all unique tags with counts
- **FR-2.4**: AI-suggested tags based on contact details

### FR-3: Interaction Notes Timeline
- **FR-3.1**: Add typed notes to contacts (general, meeting, call, email, event, follow_up)
- **FR-3.2**: Chronological timeline display on contact detail view
- **FR-3.3**: Delete individual notes
- **FR-3.4**: Activity feed across all contacts

### FR-4: Follow-up Reminders
- **FR-4.1**: Set next follow-up date on any contact
- **FR-4.2**: Optional recurring frequency (every N days)
- **FR-4.3**: Mark follow-up complete (auto-schedules next if recurring)
- **FR-4.4**: Dashboard widget showing due/overdue follow-ups

### FR-5: Relationship Scoring
- **FR-5.1**: Auto-calculated score based on recency (60%) and frequency (40%) of interactions
- **FR-5.2**: Status labels: warm (<=14 days), lukewarm (<=30 days), cold (>30 days), new
- **FR-5.3**: Visual status indicators on contact cards and detail views
- **FR-5.4**: Dashboard health chart showing distribution

### FR-6: AI Features (powered by Google Gemini)
- **FR-6.1**: Person Blueprint generation from details + notes
- **FR-6.2**: Central Q&A across all contacts
- **FR-6.3**: AI tag suggestions
- **FR-6.4**: Sanitized HTML output (XSS prevention via bleach)
- **FR-6.5**: Graceful degradation when API key is not configured

### FR-7: Import/Export
- **FR-7.1**: CSV import with intelligent column mapping
- **FR-7.2**: CSV export of all contacts
- **FR-7.3**: JSON export of all contacts
- **FR-7.4**: Max 5,000 rows per import

### FR-8: Dashboard & Analytics
- **FR-8.1**: Total contacts count
- **FR-8.2**: Contacts added this week/month
- **FR-8.3**: Follow-ups due count and quick list
- **FR-8.4**: Cold contacts count and quick list
- **FR-8.5**: Relationship health distribution chart
- **FR-8.6**: Tag breakdown with counts
- **FR-8.7**: Recently added contacts

### FR-9: Authentication & Authorization
- **FR-9.1**: User registration with username, password, optional email
- **FR-9.2**: Password hashing with bcrypt
- **FR-9.3**: Session-based authentication
- **FR-9.4**: Per-user data isolation (contacts scoped to user_id)
- **FR-9.5**: Login/logout with smart landing page routing

### FR-10: User Interface
- **FR-10.1**: Three-panel layout (sidebar, contacts grid, detail drawer)
- **FR-10.2**: Dark mode toggle with persistence
- **FR-10.3**: Keyboard shortcuts (N = new, / = search, Esc = close)
- **FR-10.4**: Responsive design (desktop, tablet, mobile)
- **FR-10.5**: Professional landing page for unauthenticated users
- **FR-10.6**: Toast notification system

---

## Non-Functional Requirements

### NFR-1: Security
- Rate limiting on all endpoints (200/day default, 10/min login, 60/min API, 20/min AI)
- HttpOnly, SameSite session cookies
- XSS prevention via HTML sanitization on AI outputs
- Password hashing with bcrypt
- Error messages do not leak internal details to clients
- Input validation on all user inputs

### NFR-2: Performance
- Contact list loads < 2 seconds for up to 1,000 contacts
- Search results appear in real-time (debounced client-side)
- AI responses stream within timeout limits

### NFR-3: Reliability
- Dual storage backend (MongoDB for production, JSON for local/dev)
- Graceful degradation when AI API is unavailable
- Health check endpoint at /health

### NFR-4: Maintainability
- SOLID principles throughout
- Clean architecture with layered separation
- Type hints on all Python code
- Structured logging
- Standardized API response format

### NFR-5: Deployability
- Single-command deployment to Render.com
- Environment variable configuration
- Gunicorn production server
- Docker-compatible

---

## API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |

### Contacts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/people` | List all contacts (optional `?tag=` filter) |
| GET | `/api/people/<id>` | Get contact by ID |
| GET | `/api/people/search/<query>` | Full-text search |
| POST | `/api/people` | Create contact |
| PUT | `/api/people/<id>` | Update contact |
| DELETE | `/api/people/<id>` | Delete contact and notes |

### Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/people/tags` | List all unique tags |
| POST | `/api/people/<id>/tags` | Add tags to contact |
| DELETE | `/api/people/<id>/tags/<tag>` | Remove tag from contact |

### Follow-ups
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/people/followups` | List due follow-ups |
| PUT | `/api/people/<id>/followup` | Set follow-up date/frequency |
| POST | `/api/people/<id>/followup/complete` | Complete follow-up |

### Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notes/person/<id>` | Get notes for contact |
| POST | `/api/notes/person/<id>` | Add note to contact |
| DELETE | `/api/notes/<id>` | Delete note |
| GET | `/api/notes/activity` | Recent activity feed |

### AI Features
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/people/<id>/summary` | Generate AI blueprint |
| POST | `/api/ask` | Central AI Q&A |
| POST | `/api/people/<id>/suggest-tags` | AI tag suggestions |

### Dashboard & Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/people/dashboard/stats` | Dashboard statistics |
| POST | `/api/people/import/csv` | Import contacts from CSV |
| GET | `/api/people/export/csv` | Export contacts as CSV |
| GET | `/api/people/export/json` | Export contacts as JSON |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
