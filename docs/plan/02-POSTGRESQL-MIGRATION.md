# Phase 2 — PostgreSQL Migration

**Goal**: Migrate from MongoDB/JSON storage to PostgreSQL with SQLAlchemy ORM, add Redis for caching and session storage.

**Duration**: 2-3 weeks
**Depends on**: Phase 0 (Production Hardening)

## Why PostgreSQL

| Concern | MongoDB (current) | PostgreSQL (target) |
|---------|-------------------|-------------------|
| ACID transactions | Limited (multi-doc txns are slow) | Full ACID, row-level locking |
| Relational integrity | None (manual) | Foreign keys, constraints, cascades |
| Billing/financial data | Not recommended | Industry standard for financial records |
| Full-text search | Basic `$text` index | `tsvector` + `GIN` index, ranked results |
| JSON flexibility | Native | `JSONB` column for flexible fields |
| Hosting cost | Atlas free tier: 512MB | Supabase/Neon free tier: 500MB |

## Schema Design

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    mfa_secret VARCHAR(64),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- People (contacts)
CREATE TABLE people (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    job_title VARCHAR(255),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    twitter_handle VARCHAR(100),
    website VARCHAR(500),
    details TEXT,
    how_we_met TEXT,
    profile_image_url VARCHAR(500),
    birthday DATE,
    anniversary DATE,
    met_at DATE,
    tags TEXT[] DEFAULT '{}',
    next_follow_up DATE,
    follow_up_frequency_days INTEGER DEFAULT 0,
    relationship_score DECIMAL(5,2) DEFAULT 0.0,
    relationship_status VARCHAR(20) DEFAULT 'new',
    last_interaction_at TIMESTAMPTZ,
    interaction_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_status CHECK (relationship_status IN ('new', 'warm', 'lukewarm', 'cold'))
);

CREATE INDEX idx_people_user_id ON people(user_id);
CREATE INDEX idx_people_tags ON people USING GIN(tags);
CREATE INDEX idx_people_follow_up ON people(next_follow_up) WHERE next_follow_up IS NOT NULL;
CREATE INDEX idx_people_search ON people USING GIN(
    to_tsvector('english', coalesce(name, '') || ' ' || coalesce(company, '') || ' ' || coalesce(details, ''))
);

-- Notes
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    note_type VARCHAR(20) DEFAULT 'general',
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_note_type CHECK (note_type IN ('general', 'meeting', 'call', 'email', 'event', 'follow_up'))
);

CREATE INDEX idx_notes_person ON notes(person_id, created_at DESC);
CREATE INDEX idx_notes_user ON notes(user_id, created_at DESC);
```

## Implementation Steps

### Step 1: Add SQLAlchemy Models

```python
# models/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

# models/person_model.py (SQLAlchemy version)
from sqlalchemy import Column, String, Integer, Float, DateTime, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

class PersonModel(Base):
    __tablename__ = 'people'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)
    # ... remaining fields
```

### Step 2: Create PostgreSQL Repository Implementations

```python
# repositories/pg_person_repository.py
class PgPersonRepository(BaseRepository):
    def __init__(self, session_factory):
        self.Session = session_factory

    def find_all(self, filters=None):
        with self.Session() as session:
            query = session.query(PersonModel)
            if filters and 'user_id' in filters:
                query = query.filter_by(user_id=filters['user_id'])
            return [self._to_domain(row) for row in query.all()]
```

The key insight: **services don't change**. Because the repository pattern abstracts storage, `PersonService` works identically with either `PersonRepository` (MongoDB/JSON) or `PgPersonRepository` (PostgreSQL). This is the payoff of clean architecture.

### Step 3: Data Migration Script

```python
# scripts/migrate_mongo_to_pg.py
"""
Migration script: MongoDB → PostgreSQL
Run once, then verify, then switch config.
"""

def migrate():
    # 1. Connect to both databases
    mongo_client = MongoClient(MONGO_URI)
    pg_engine = create_engine(PG_URI)

    # 2. Migrate users first (foreign key dependency)
    mongo_users = mongo_client.people_manager.users.find()
    for user in mongo_users:
        pg_user = map_user(user)
        pg_session.add(pg_user)

    # 3. Migrate people with user_id mapping
    # 4. Migrate notes with person_id + user_id mapping
    # 5. Verify counts match
    # 6. Verify sample records match
```

### Step 4: Dual-Write Period (Safety Net)

For 1-2 weeks, write to **both** MongoDB and PostgreSQL simultaneously:

```python
class DualWritePersonRepository(BaseRepository):
    def __init__(self, primary, secondary):
        self.primary = primary      # PostgreSQL (new)
        self.secondary = secondary  # MongoDB (old, for rollback)

    def create(self, entity):
        result = self.primary.create(entity)
        try:
            self.secondary.create(entity)
        except Exception as e:
            logger.warning(f"Secondary write failed: {e}")
        return result
```

### Step 5: Add Redis

```python
# Redis for:
# 1. Rate limiting (replace memory://)
# 2. Session storage (if keeping sessions alongside JWT)
# 3. Cache frequently-accessed data (dashboard stats, tag lists)

import redis

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
```

### Step 6: Alembic for Migrations

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## Done When

- [ ] PostgreSQL schema created via Alembic
- [ ] All three repository implementations (Person, User, Note) working with PostgreSQL
- [ ] Data migration script tested with real MongoDB data
- [ ] Dual-write period completed with zero discrepancies
- [ ] MongoDB dependency removed from `docker-compose.yml`
- [ ] Redis connected for rate limiting and caching
- [ ] Dashboard stats cached in Redis (30s TTL)
- [ ] Full-text search uses PostgreSQL `tsvector` instead of in-memory filtering

## Dependencies to Add

```
sqlalchemy>=2.0
psycopg2-binary>=2.9
alembic>=1.13
redis>=5.0
```

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| Dual-write period | Zero-downtime migration, easy rollback | Temporary complexity, slight write latency |
| UUID primary keys | No sequential ID leaking | Slightly larger than auto-increment integers |
| `TEXT[]` for tags | Simple, GIN-indexable | Not normalized — acceptable for read-heavy pattern |
| Alembic over raw SQL | Version-controlled schema changes | Learning curve — but essential for production |

## Rollback Plan

If issues arise during migration:
1. Switch `USE_POSTGRESQL` config flag back to `False`
2. MongoDB still has all data from dual-write period
3. No data loss possible because writes went to both
