# Phase 4 — Frontend Modernization

**Goal**: Migrate from Vanilla JS (~500 LOC) to React/Next.js with a component library, proper state management, and server-side rendering.

**Duration**: 3-4 weeks
**Depends on**: Phase 3 (FastAPI — stable API with OpenAPI spec)

## Why React/Next.js

| Problem with Vanilla JS | How React/Next.js Solves It |
|-------------------------|----------------------------|
| Single 500-line file, all state in globals | Component tree with local state, props, hooks |
| Manual DOM manipulation (`innerHTML`) | Declarative rendering, virtual DOM diffing |
| No routing (view switching via CSS classes) | File-based routing with `next/router` |
| No build step (no minification, tree-shaking) | Webpack/Turbopack with automatic optimization |
| No TypeScript | Full TypeScript support, type-safe API calls |
| No testing | React Testing Library + Vitest |

## Architecture

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx           # Root layout (sidebar, nav)
│   │   ├── page.tsx             # Landing page
│   │   ├── dashboard/
│   │   │   └── page.tsx         # Dashboard view
│   │   ├── contacts/
│   │   │   ├── page.tsx         # Contact grid
│   │   │   └── [id]/
│   │   │       └── page.tsx     # Contact detail
│   │   ├── activity/
│   │   │   └── page.tsx         # Activity feed
│   │   └── auth/
│   │       ├── login/page.tsx
│   │       └── register/page.tsx
│   ├── components/
│   │   ├── ui/                  # Primitives (Button, Input, Card, Modal)
│   │   ├── contacts/            # ContactCard, ContactGrid, ContactDrawer
│   │   ├── notes/               # NoteForm, NoteTimeline
│   │   ├── ai/                  # BlueprintPanel, QAChat
│   │   └── layout/              # Sidebar, TopBar, MobileNav
│   ├── hooks/
│   │   ├── useContacts.ts       # SWR/React Query hook for contacts
│   │   ├── useNotes.ts
│   │   └── useAuth.ts
│   ├── lib/
│   │   ├── api.ts               # Type-safe API client (generated from OpenAPI)
│   │   └── utils.ts
│   ├── stores/                  # Zustand stores (global state)
│   │   └── app-store.ts
│   └── types/                   # TypeScript types (generated from Pydantic)
│       └── api.d.ts
├── public/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.ts
```

## Implementation Steps

### Step 1: Scaffold Next.js Project

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir
cd frontend
npm install @tanstack/react-query zustand
npm install -D openapi-typescript openapi-fetch
```

### Step 2: Generate TypeScript Types from OpenAPI

Since FastAPI (Phase 3) auto-generates OpenAPI spec:

```bash
# Generate types from FastAPI's /openapi.json
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.d.ts
```

This gives type-safe API calls for free:

```typescript
// lib/api.ts
import createClient from 'openapi-fetch';
import type { paths } from '@/types/api';

export const api = createClient<paths>({ baseUrl: '/api/v2' });

// Usage — fully typed!
const { data } = await api.GET('/people', { params: { query: { tag: 'mentor' } } });
// data is typed as PersonList automatically
```

### Step 3: Component-by-Component Migration

Port each "view" from the monolithic `script.js`:

| Vanilla JS Function | React Component | Notes |
|--------------------|-----------------|-------|
| `renderPeople()` | `<ContactGrid />` | Uses `useContacts()` hook with React Query |
| `openDrawer()` / `renderDrawerContent()` | `<ContactDrawer />` | Sheet component with `useParams()` |
| `openPersonModal()` / `handlePersonSubmit()` | `<ContactForm />` | React Hook Form + Zod validation |
| `loadDashboard()` | `<DashboardPage />` | Server component with streaming |
| `loadActivity()` | `<ActivityFeed />` | Infinite scroll with React Query |
| `generateBlueprint()` | `<BlueprintPanel />` | Streaming AI response |
| `askAI()` | `<QAChat />` | Chat-style UI with message history |
| `handleSearch()` | `<SearchInput />` | Already debounced, add `useDeferredValue` |
| `showToast()` | `<Toaster />` | Use `sonner` or `react-hot-toast` |

### Step 4: State Management

```typescript
// stores/app-store.ts
import { create } from 'zustand';

interface AppStore {
    currentTagFilter: string | null;
    setTagFilter: (tag: string | null) => void;
    darkMode: boolean;
    toggleDarkMode: () => void;
}

export const useAppStore = create<AppStore>((set) => ({
    currentTagFilter: null,
    setTagFilter: (tag) => set({ currentTagFilter: tag }),
    darkMode: localStorage.getItem('darkMode') === 'true',
    toggleDarkMode: () => set((s) => {
        localStorage.setItem('darkMode', String(!s.darkMode));
        return { darkMode: !s.darkMode };
    }),
}));
```

### Step 5: Run Next.js Alongside Flask Templates

During migration, serve both:

```
nginx
├── /app/*        → Next.js (port 3000) — new React UI
├── /api/*        → FastAPI (port 8000) — API
└── /*            → Flask (port 5000)   — legacy templates (gradually removed)
```

Users can opt into the new UI at `/app/`. Once all features are ported, redirect `/` → `/app/`.

### Step 6: Accessibility & Performance

- All interactive elements have `aria-labels`
- Keyboard navigation (Tab, Enter, Escape) for modals/drawers
- Lighthouse score target: >90 on all metrics
- Images: `next/image` with automatic optimization
- Code splitting: each route lazy-loaded

## Done When

- [ ] All views ported to React components
- [ ] TypeScript types auto-generated from OpenAPI
- [ ] Dark mode works with system preference detection
- [ ] Keyboard shortcuts preserved (N, /, Escape)
- [ ] Contact search with debounce and loading states
- [ ] AI blueprint shows streaming response (not all-at-once)
- [ ] Mobile-responsive layout matching current design
- [ ] Lighthouse: Performance >90, Accessibility >90
- [ ] Flask templates removed, Next.js serves all pages
- [ ] Unit tests for key components (React Testing Library)

## Dependencies

```json
{
  "dependencies": {
    "next": "^15",
    "react": "^19",
    "@tanstack/react-query": "^5",
    "zustand": "^5",
    "openapi-fetch": "^0.10",
    "tailwindcss": "^4",
    "sonner": "^1",
    "react-hook-form": "^7",
    "@hookform/resolvers": "^3",
    "zod": "^3"
  }
}
```

## Trade-offs

| Decision | Pro | Con |
|----------|-----|-----|
| Next.js App Router | SSR, streaming, server components | More complex than SPA; steeper learning curve |
| Tailwind over CSS-in-JS | Utility-first, no runtime cost, great DX | HTML class clutter — use `cn()` helper |
| React Query over Redux | Server-state caching built in, less boilerplate | Another library to learn — but simpler than Redux |
| OpenAPI codegen | Type-safe API calls, catches breaking changes | Build step dependency — acceptable |
| Incremental migration | No big-bang rewrite, users can use both UIs | Temporary nginx routing complexity |
