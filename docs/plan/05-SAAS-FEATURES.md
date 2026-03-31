# Phase 5 — SaaS Features

**Goal**: Add multi-tenancy, billing (Stripe), team workspaces, admin dashboard, and onboarding flow to turn the app into a revenue-generating SaaS product.

**Duration**: 4-6 weeks
**Depends on**: Phase 4 (Frontend Modernization — React UI ready)

## Why This Phase Is Last

Every prior phase was **infrastructure**. This phase adds **business value**:
- Multi-tenancy = charge per workspace
- Billing = revenue
- Admin dashboard = customer success tooling
- Onboarding = conversion funnel optimization

## Feature Breakdown

### 1. Multi-Tenancy (Workspace Model)

```
Organization (Workspace)
├── Members (Users with Roles)
│   ├── Owner (billing, settings, member mgmt)
│   ├── Admin (all data, member mgmt)
│   ├── Member (own data + shared team data)
│   └── Viewer (read-only)
├── Contacts (shared within workspace)
├── Notes (per-user, visible to workspace)
├── Subscription (Stripe)
└── Settings (AI preferences, integrations)
```

Schema additions:

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    max_contacts INTEGER DEFAULT 100,
    max_members INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE org_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    UNIQUE(org_id, user_id),
    CONSTRAINT valid_role CHECK (role IN ('owner', 'admin', 'member', 'viewer'))
);

-- Add org_id to people table
ALTER TABLE people ADD COLUMN org_id UUID REFERENCES organizations(id);
CREATE INDEX idx_people_org ON people(org_id);
```

### 2. Pricing & Billing (Stripe)

| Plan | Price | Contacts | Members | AI Queries | Features |
|------|-------|----------|---------|-----------|----------|
| Free | $0 | 100 | 1 | 10/month | Core CRM |
| Pro | $12/mo | Unlimited | 1 | 200/month | + AI Blueprints, Export |
| Team | $29/mo | Unlimited | 5 | 500/month | + Shared workspace, Activity feed |
| Enterprise | Custom | Unlimited | Unlimited | Unlimited | + SSO, Audit log, API access |

Integration flow:

```python
# services/billing_service.py
import stripe

class BillingService:
    def create_checkout_session(self, org_id: str, plan: str) -> str:
        session = stripe.checkout.Session.create(
            customer=org.stripe_customer_id,
            mode='subscription',
            line_items=[{'price': PLAN_PRICES[plan], 'quantity': 1}],
            success_url=f'{BASE_URL}/settings/billing?success=true',
            cancel_url=f'{BASE_URL}/settings/billing',
        )
        return session.url

    def handle_webhook(self, payload, sig_header):
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        match event['type']:
            case 'checkout.session.completed':
                self._activate_subscription(event['data']['object'])
            case 'invoice.payment_failed':
                self._handle_payment_failure(event['data']['object'])
            case 'customer.subscription.deleted':
                self._downgrade_to_free(event['data']['object'])
```

### 3. Usage Metering & Limits

```python
# middleware/usage_limiter.py
class UsageLimiter:
    async def check_contact_limit(self, org_id: str):
        org = await self.org_repo.find_by_id(org_id)
        current_count = await self.people_repo.count_by_org(org_id)
        if current_count >= org.max_contacts:
            raise UsageLimitError(
                f"Contact limit reached ({org.max_contacts}). "
                "Upgrade your plan for unlimited contacts."
            )

    async def check_ai_quota(self, org_id: str):
        month_key = f"ai_usage:{org_id}:{datetime.now().strftime('%Y-%m')}"
        usage = await self.redis.incr(month_key)
        if usage == 1:
            await self.redis.expire(month_key, 86400 * 35)  # 35-day TTL
        org = await self.org_repo.find_by_id(org_id)
        if usage > org.ai_quota:
            raise UsageLimitError("Monthly AI query limit reached.")
```

### 4. Onboarding Flow

First-time user experience:

```
Step 1: "What's your name?" → Create user
Step 2: "Name your workspace" → Create org
Step 3: "Import contacts" → CSV upload or manual add
Step 4: "Try AI" → Generate first blueprint
Step 5: "Invite teammates" → (if Team plan)
```

Track completion with `onboarding_step` field on user:

```sql
ALTER TABLE users ADD COLUMN onboarding_step INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN onboarding_completed_at TIMESTAMPTZ;
```

### 5. Admin Dashboard

For the product owner (you), not end users:

| Metric | Query |
|--------|-------|
| Total users | `SELECT COUNT(*) FROM users` |
| Active users (7d) | `SELECT COUNT(DISTINCT user_id) FROM notes WHERE created_at > NOW() - INTERVAL '7 days'` |
| MRR | Sum of active subscription amounts from Stripe |
| Churn rate | Users who cancelled / total users this month |
| AI usage | `GET ai_usage:*` from Redis |
| Feature adoption | % users who used AI, import, tags, follow-ups |

Build with a lightweight admin framework (e.g., Retool free tier, or a simple protected Next.js route).

### 6. Email Notifications

| Trigger | Email | Service |
|---------|-------|---------|
| Follow-up due | "You have 3 follow-ups due today" | Daily cron job |
| Contact going cold | "5 contacts need attention" | Weekly digest |
| AI blueprint ready | "Blueprint for John generated" | After async AI job |
| Team invite | "You've been invited to Acme workspace" | On invite |
| Payment failed | "Your payment couldn't be processed" | Stripe webhook |

Use SendGrid free tier (100 emails/day) or AWS SES ($0.10/1000 emails).

### 7. API Keys (for Enterprise)

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,  -- bcrypt hash of the key
    name VARCHAR(100) NOT NULL,
    permissions TEXT[] DEFAULT '{read}',
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Enterprise customers get REST API access with scoped API keys, enabling integrations with their CRM, email, or custom workflows.

## Done When

- [ ] Multi-tenancy: users belong to organizations, data scoped by org
- [ ] Stripe billing: checkout, subscription management, webhooks
- [ ] Usage limits: contact count, AI queries, member count enforced per plan
- [ ] Onboarding: guided 5-step flow for new users
- [ ] Admin dashboard: key metrics visible
- [ ] Email notifications: follow-up reminders working
- [ ] API keys: enterprise customers can access API programmatically
- [ ] GDPR: data export and account deletion endpoints

## Dependencies

```
stripe>=7.0
sendgrid>=6.11         # or boto3 for SES
celery>=5.3            # background tasks (emails, AI jobs)
redis>=5.0             # celery broker + result backend
```

## Revenue Projections

| Milestone | Users | Paying (~5%) | MRR | Timeline |
|-----------|-------|-------------|-----|----------|
| Launch | 100 | 5 | $60 | Month 1 |
| Traction | 500 | 25 | $300 | Month 3 |
| Growth | 2,000 | 100 | $1,200 | Month 6 |
| Scale | 10,000 | 500 | $6,000 | Month 12 |

At ~94% gross margin ($12/mo plan, ~$0.70 COGS), $6K MRR = $5,640 gross profit.

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| Stripe over Paddle/Lemon Squeezy | Most developer-friendly, best docs | Requires handling tax compliance separately |
| Per-workspace billing (not per-seat) | Simpler pricing, lower friction | Less revenue per large team — add seat-based pricing later |
| Celery for background tasks | Proven, massive ecosystem | Adds Redis dependency (already have it from Phase 2) |
| Free tier included | Funnel for paid conversion | Cost of hosting free users — limit to 100 contacts |
| SendGrid over self-hosted email | Deliverability, no IP warming | Free tier limit (100/day) — sufficient for early stage |
