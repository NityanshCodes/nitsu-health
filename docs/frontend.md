# NITSU Health — Frontend

React 19 + TypeScript + Vite SPA under `frontend/`. State via Zustand; server
data via a typed Axios API layer; charts via Recharts; routing via
React Router.

## Layout

```
frontend/
  src/
    components/ui/     # Reusable UI kit (plain CSS + design tokens)
    services/          # Typed API layer (api.ts is the Axios core)
    pages/             # One component per route
    styles/            # tokens.css + global styles
    App.tsx            # Routing + protected routes
  index.html
  vite.config.ts
  package.json
```

## UI kit

Small, reusable components built on plain CSS + design tokens (no Tailwind for
the kit — calm, premium health aesthetic, responsive):

`Button`, `Card`, `Input`, `Select`, `Textarea`, `Field/Label`, `Modal`,
`Spinner`, `EmptyState`, `ErrorBox`, `Stat`, `PageHeader`.

## Pages / routes

Landing, Onboarding (multi-step, skippable), Dashboard, Health (metrics CRUD),
Nutrition, Activity, Sleep, Goals, Medical Records, Reports, AI Assistant
(conversations), Insights, Notifications, Subscription, Settings, Profile.

A shared `MainLayout` provides the topbar + sidebar navigation; protected routes
redirect unauthenticated users to login.

## API layer

`src/services/api.ts` is the Axios core (base URL from `VITE_API_BASE_URL`,
JWT interceptor, error normalization). Domain endpoints are split into focused
modules under `src/services/`.

## Build & dev

```bash
cd frontend
npm install
npm run dev        # dev server
npm run build      # tsc -b && vite build (must pass cleanly)
npm run lint       # oxlint
npm run preview
```

## Environment

`VITE_API_BASE_URL` (see `frontend/.env.example`) — default
`http://localhost:8000`.
