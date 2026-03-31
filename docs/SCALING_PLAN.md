# People Manager - Scaling Plan

> Strategy for scaling the application from a personal tool to a production-grade service.
> Includes trade-offs, migration paths, and decision frameworks.
> Date: 2026-03-31

---

## Current State Assessment

### What Works Today
| Metric | Current Capability | Bottleneck |
|--------|-------------------|------------|
| Users | ~50 concurrent | Session storage in Flask memory |
| Contacts per user | ~500 | JSON file I/O, N+1 queries |
| Total contacts | ~2,000 | Full file reads on every operation |
| AI requests | ~20/min | Gemini API rate limits |
| Note operations | Adequate | Coupled to person list refresh |
| Deployment | Single instance (Render) | No horizontal scaling |

### Architecture Constraints
1. **JSON backend**: O(n) for every read/write operation
2. **In-memory rate limiter**: Resets on restart, per-worker only
3. **Synchronous AI calls**: Block request thread for 5-15 seconds
4. **No caching layer**: Every request hits storage
5. **Monolithic deployment**: Everything runs in one process

---

## Phase 1: Production Hardening (1-100 Users)

**Goal**: Make the current architecture reliable for small-scale production use.

### 1.1 Database: Mandatory MongoDB

| Action | Why | Effort |
|--------|-----|--------|
| Remove JSON backend option for production | Eliminate race conditions and O(n) reads | Low |
| Add MongoDB indexes | Speed up user_id lookups and text search | Low |
| Connection pooling | Prevent connection exhaustion | Low |

**MongoDB Indexes to Add**:
```javascript
db.people.createIndex({ "user_id": 1 })
db.people.createIndex({ "user_id": 1, "tags": 1 })
db.people.createIndex({ "user_id": 1, "next_follow_up": 1 })
db.people.createIndex({ "user_id": 1, "name": "text", "company": "text", "details": "text" })
db.notes.createIndex({ "person_id": 1, "user_id": 1 })
db.notes.createIndex({ "user_id": 1, "created_at": -1 })
db.users.createIndex({ "username": 1 }, { unique: true })
```

### 1.2 Fix N+1 Query Problem

**Current**: Loading 100 contacts → 100 note queries for relationship scoring.

**Fix**: Batch load all notes in one query, group in memory.

```python
def get_all_people(self, user_id):
    people = self.person_repo.find_all({'user_id': user_id})
    all_notes = self.note_repo.find_all({'user_id': user_id})
    notes_by_person = defaultdict(list)
    for note in all_notes:
        notes_by_person[note.person_id].append(note)
    for person in people:
        self._refresh_score(person, notes_by_person.get(person.id, []))
    return people
```

**Impact**: 100 queries → 2 queries. ~50x speedup.

### 1.3 Add Application Caching

| Cache Target | Strategy | TTL | Invalidation |
|-------------|----------|-----|--------------|
| Relationship scores | In-memory dict per user | 5 minutes | On note create/delete |
| Tag list | In-memory | 2 minutes | On tag add/remove |
| Dashboard stats | In-memory | 1 minute | On any write |

**Implementation**: Start with `cachetools.TTLCache`, upgrade to Redis later.

### 1.4 Security Hardening

- Enforce `SECRET_KEY` in production (refuse to start without it)
- Add `SESSION_COOKIE_SECURE = True` behind HTTPS
- Set `PERMANENT_SESSION_LIFETIME = 24 hours`
- Implement CSRF tokens or switch to Bearer token auth for APIs
- Add `uuid4()` for entity IDs

### 1.5 Error Handling & Monitoring

- Global Flask error handler for unhandled exceptions
- Structured JSON logging for log aggregation
- Sentry or similar for error tracking
- Health check that verifies DB connectivity

**Trade-offs**:
| Gain | Cost |
|------|------|
| Reliable for small production use | ~2-3 days of development |
| No data loss under concurrent access | JSON backend becomes dev-only |
| Faster queries with indexes | Minor MongoDB operational knowledge needed |

---

## Phase 2: Scaling to 1,000 Users (Multi-Instance)

**Goal**: Support multiple server instances behind a load balancer.

### 2.1 Session Store: Redis

**Why**: Flask's default cookie-based sessions work for single instance, but scaling horizontally requires shared session storage.

```
Current:  Browser → Flask Instance (sessions in memory)
Scaled:   Browser → Load Balancer → Flask Instance 1..N → Redis (sessions)
```

**Implementation**: `Flask-Session` with Redis backend.

```python
from flask_session import Session

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host=REDIS_URL)
Session(app)
```

### 2.2 Rate Limiter: Redis Backend

Replace `storage_uri="memory://"` with Redis:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=f"redis://{REDIS_URL}",
)
```

### 2.3 Caching: Redis

Centralized cache that all instances share:

```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': REDIS_URL,
    'CACHE_DEFAULT_TIMEOUT': 300
})

@cache.cached(timeout=60, key_prefix=lambda: f"dashboard:{session['user_id']}")
def get_dashboard_stats(user_id):
    ...
```

### 2.4 Background Tasks: Celery + Redis

Move slow operations off the request thread:

| Task | Current | With Celery |
|------|---------|-------------|
| AI Blueprint | Blocks 5-15s | Returns task ID, polls for result |
| CSV Import (5000 rows) | Blocks 30-60s | Background job with progress |
| Relationship scoring | On every list load | Periodic batch job (every 5 min) |
| Export generation | Blocks for large datasets | Pre-generate, serve from cache |

**Architecture**:
```
Browser → Flask → Create Celery Task → Return task_id
                                           ↓
                  Redis Queue → Celery Worker → Process → Store Result
                                                            ↓
Browser ← Poll GET /api/tasks/:id ← Flask ← Redis Result
```

### 2.5 Full-Text Search: MongoDB Atlas Search

Replace Python-side filtering with MongoDB Atlas Search:

```javascript
// Atlas Search index
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "name": { "type": "string", "analyzer": "lucene.standard" },
      "company": { "type": "string" },
      "details": { "type": "string" },
      "tags": { "type": "string" }
    }
  }
}
```

```python
def search(self, query, user_id):
    pipeline = [
        {"$search": {"text": {"query": query, "path": ["name", "company", "details", "tags"]}}},
        {"$match": {"user_id": user_id}},
        {"$limit": 50}
    ]
    return list(self.collection.aggregate(pipeline))
```

### 2.6 Infrastructure

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │  (Render/AWS)   │
                    └────────┬────────┘
               ┌─────────────┼─────────────┐
          ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
          │ Flask 1 │   │ Flask 2 │   │ Flask 3 │
          └────┬────┘   └────┬────┘   └────┬────┘
               └─────────────┼─────────────┘
                    ┌────────┼────────┐
               ┌────┴────┐  ┌───┴───┐  ┌────┴────┐
               │ MongoDB │  │ Redis │  │ Celery  │
               │ Atlas   │  │       │  │ Workers │
               └─────────┘  └───────┘  └─────────┘
```

**Trade-offs**:

| Gain | Cost |
|------|------|
| Horizontal scaling | Redis infrastructure ($5-20/mo) |
| Non-blocking AI/import | Celery complexity, worker management |
| Real full-text search | MongoDB Atlas Search (M10+ tier, ~$57/mo) |
| Shared sessions/cache | Single point of failure (Redis) |
| True rate limiting | Additional dependency |

---

## Phase 3: Scaling to 10,000+ Users (Production Scale)

### 3.1 API Gateway

Add an API gateway for:
- Request routing
- Authentication (JWT at gateway level)
- Rate limiting (centralized)
- Request/response transformation
- API versioning

**Options**: Kong, AWS API Gateway, Nginx with Lua

### 3.2 Database Sharding Strategy

**Shard key**: `user_id` (all queries are user-scoped, natural shard key)

```
Shard 1: user_ids A-M
Shard 2: user_ids N-Z
```

**Alternative**: MongoDB Atlas auto-sharding (available on M30+ tier, ~$200/mo)

### 3.3 Microservice Decomposition

If the monolith becomes a bottleneck, consider splitting:

```
Current Monolith:
├── Auth Service      → Extract first (standard, stable)
├── Contact Service   → Core CRUD, keep in main
├── AI Service        → Extract (different scaling needs)
├── Import/Export     → Extract (batch processing)
└── Analytics         → Extract (read-heavy, can be eventually consistent)
```

**When to decompose**: Only when specific components need independent scaling. Premature microservices add complexity without benefit.

### 3.4 Event-Driven Architecture

Replace direct service calls with events:

```
NoteService.create_note()
  → Publish: NoteCreated(person_id, user_id, note_type)
    → Subscriber: RelationshipScorer.update_score()
    → Subscriber: ActivityFeed.add_entry()
    → Subscriber: NotificationService.check_triggers()
```

**Message broker**: Redis Streams (simple) → RabbitMQ (reliable) → Kafka (scale)

### 3.5 CDN for Static Assets

```
Browser → CDN (CloudFront/Fastly) → Origin (Flask)
          ↑
          CSS, JS, images cached at edge
```

### 3.6 Auth Migration to JWT

For multi-service architecture, JWT is more practical:

```
Login → Auth Service → Issue JWT
Subsequent requests → API Gateway → Verify JWT → Forward to service
```

**Trade-offs**:

| Gain | Cost |
|------|------|
| True horizontal scale | Significant infrastructure complexity |
| Service independence | Distributed system debugging difficulty |
| Better fault isolation | Network latency between services |
| Technology flexibility | Operational overhead |

---

## Phase 4: Enterprise Features

### 4.1 Multi-Tenancy

```
Current:  user_id scoping
Phase 4:  organization_id → user_id → data scoping

Organization
├── Admin users (manage org)
├── Regular users (manage own contacts)
├── Shared contact lists
└── Org-wide AI Q&A
```

### 4.2 Real-Time Features

| Feature | Technology |
|---------|-----------|
| Live contact updates | WebSocket (Flask-SocketIO) |
| Collaborative editing | Operational Transform or CRDT |
| Presence indicators | Redis Pub/Sub |
| Push notifications | Web Push API + service worker |

### 4.3 Integrations

| Integration | Value | Complexity |
|-------------|-------|-----------|
| Gmail/Outlook | Auto-log email interactions | High (OAuth + API parsing) |
| Google Calendar | Auto-create notes from meetings | Medium |
| LinkedIn | Profile enrichment | High (scraping or API) |
| Zapier/n8n | User-defined automations | Medium (webhook endpoints) |
| Slack | Follow-up notifications | Low (webhook) |

### 4.4 Mobile App

**Options**:
1. **PWA** (recommended first): Add service worker, manifest, offline support. Works on all platforms with minimal effort.
2. **React Native / Flutter**: Full native experience, push notifications, contacts sync. Higher development cost.
3. **Responsive web only**: Current approach, adequate for mobile browser use.

---

## Migration Path Summary

```
Phase 1 (Now → 2 weeks)
├── MongoDB mandatory for production
├── Add indexes
├── Fix N+1 queries
├── UUID for IDs
├── Secret key enforcement
├── Basic caching (in-memory)
└── Global error handler

Phase 2 (2-4 weeks)
├── Redis for sessions + cache + rate limiting
├── Celery for background tasks
├── Atlas Search for full-text
├── Pagination on all list endpoints
└── WebSocket for real-time updates

Phase 3 (When needed - 10K+ users)
├── API Gateway
├── JWT authentication
├── Service decomposition (AI, Import/Export)
├── CDN for static assets
└── Database sharding

Phase 4 (Product evolution)
├── Multi-tenancy
├── Integrations (email, calendar)
├── Mobile app (PWA first)
└── Real-time collaboration
```

---

## Cost Estimation

| Phase | Infrastructure | Monthly Cost |
|-------|---------------|-------------|
| Current | Render free tier + MongoDB free tier | $0 |
| Phase 1 | Render paid ($7) + MongoDB M0 (free) | ~$7/mo |
| Phase 2 | Render ($25) + MongoDB M10 ($57) + Redis ($15) | ~$100/mo |
| Phase 3 | AWS/GCP ($200-500) + MongoDB Atlas ($200+) + Redis ($30) | ~$500/mo |
| Phase 4 | Full cloud ($1000+) | $1000+/mo |

---

## Decision Framework

**When to move to Phase 2**:
- Response times exceed 2 seconds for contact list
- AI requests timeout frequently
- CSV imports of 1000+ rows fail
- Multiple team members need concurrent access

**When to move to Phase 3**:
- 5000+ active users
- 99.9% uptime SLA required
- Single server can't handle request volume
- Need independent service scaling

**When NOT to scale prematurely**:
- < 100 users → Phase 1 is sufficient
- < 1000 users → Phase 2 handles it
- The app is a personal tool → Current architecture with Phase 1 fixes is plenty

---

*"Premature optimization is the root of all evil" — Donald Knuth.
Scale when you have evidence of bottlenecks, not in anticipation of them.*
