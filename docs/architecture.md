# Architecture

## Backend — FastAPI modular monolith

- **Entrypoint:** `backend/app/main.py` — creates the FastAPI app, registers all
  routers, configures CORS middleware, and defines a lifespan that auto-creates
  tables in non-production environments.
- **Configuration:** `backend/app/core/config.py` — a single `Settings` class reads
  all config from environment variables (JWT, AI, wearables, payments, CORS, etc.).
- **Database:** `backend/app/database/` — SQLAlchemy engine (`database.py`), session
  dependency (`get_db`), and declarative `Base`. Alembic migrations in
  `backend/alembic/` own schema in production; `create_all` is a dev convenience.
- **Models:** `backend/app/models/` — 20 SQLAlchemy models, all registered in
  `__init__.py` so Alembic autogenerate sees them. Every user-owned table carries a
  `user_id` FK with an index.
- **Schemas:** `backend/app/schemas/` — Pydantic v2 request/response models.
- **API:** `backend/app/api/` — one router per domain (auth, users, profile, health,
  nutrition, activity, sleep, goals, analytics, dashboard, notifications, search, AI,
  medical records, reports, wearables, subscriptions, payments, admin). All
  registered in `main.py` via `include_router`.
- **Services:** `backend/app/services/` — business logic per domain, plus AI context
  builder, analytics, and the AI provider abstraction.
- **Providers:** `backend/app/providers/` — external integrations behind ABCs:
  - `payments/` — RazorpayProvider + DemoProvider
  - `wearables/` — FitbitProvider + DemoProvider
- **Middleware:** `backend/app/middleware/rate_limit.py` — in-memory per-client rate
  limiter (disabled in tests).
- **Utilities:** `backend/app/utils/` — audit logging (`log_action`), JWT auth
  helpers (`get_current_user`, `get_db`).
- **Tests:** `backend/tests/` — 88 passing + 2 skipped (OpenAI provider tests; httpx
  not in test venv). Fixtures in `conftest.py` use in-memory SQLite + `StaticPool`
  for per-test isolation.

## Frontend — React + TypeScript + Vite

- **Framework:** React 19, TypeScript, Vite 8, React Router.
- **State:** Page-local `useState` + `AuthContext` for auth state.
- **Styling:** Plain CSS with design tokens (`src/styles/tokens.css`). No Tailwind.
- **UI kit:** `src/components/ui/` — reusable `Button`, `Card`, `Input`, `Select`,
  `Modal`, `Spinner`, `EmptyState`, `ErrorBox`, `Stat`, `PageHeader`.
- **API layer:** `src/services/api.ts` — single Axios core with JWT interceptor and
  all endpoint calls. No separate service modules.
- **Pages:** One component per route — Landing, Onboarding, Dashboard, Health,
  Nutrition, Activity, Sleep, Goals, Medical Records, Reports, AI Assistant,
  Insights, Notifications, Subscription, Settings, Profile.
- **Layout:** `MainLayout` with topbar + sidebar navigation; protected routes
  redirect unauthenticated users.

## Data flow

```
Browser → React SPA → Axios (JWT header) → FastAPI router → service → SQLAlchemy → DB
                                                                        ↓
                                            Alembic migrations (production) / create_all (dev)
```

## Provider pattern

All external integrations (AI, payments, wearables) use a factory/ABC pattern:

1. An abstract interface defines the contract.
2. A production implementation calls the real API.
3. A dev/demo fallback works keyless.
4. A factory selects which implementation to use based on environment config.
5. `REQUIRES USER CONFIGURATION` markers indicate where real credentials are needed.

## Security model (overview)

- Passwords hashed with bcrypt (passlib).
- JWT (HS256) access tokens; `get_current_user` dependency validates and scopes.
- Ownership verification: every user-data endpoint queries by `current_user.id`.
- Admin routes require a `require_admin` dependency (DB role check).
- Rate limiting on sensitive endpoints.
- Audit logging on security-relevant events.
- Wearable OAuth tokens encrypted at rest (Fernet).
