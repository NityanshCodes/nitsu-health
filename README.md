# NITSU Health

NITSU Health is an AI-assisted preventive health & wellness platform. It combines
longitudinal health tracking (nutrition, activity, sleep, vitals), goal setting,
an AI assistant with data-aware context, automated insights and reports, medical
record storage, wearable integration (Fitbit), and subscriptions/payments — all
behind a single FastAPI modular monolith with a React + TypeScript frontend.

> **Health AI disclaimer:** NITSU is a preventive-health and wellness tool, not a
> medical device. AI output is presented as *observations* (e.g. "recorded sleep
> duration decreased over the last 2 weeks"), never as diagnoses or treatment
> advice. Always consult a qualified health professional for medical decisions.

## Repo layout

```
backend/        FastAPI modular monolith (API, services, models, migrations, tests)
frontend/       React + TypeScript + Vite SPA (reusable UI kit + pages)
docs/           Architecture, API, database, security, AI, deployment docs
scripts/        start.sh, reset_db.sh, seed_db.sh, backup/deploy helpers
docker/         Dockerfiles + docker-compose.yml
ai-engine/      (reserved) future isolated AI service — not part of the runtime
```

## Quick start

Requirements: Python 3.11+, Node 18+.

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# local dev: sqlite works out of the box; set DATABASE_URL for Postgres
alembic upgrade head        # apply migrations
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs · Health: http://localhost:8000/health

### Frontend

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

### Full stack

```bash
./scripts/start.sh
# or containers:
docker compose -f docker/docker-compose.yml up --build
```

## Configuration

Copy `.env.example` → `.env` and set at minimum a strong `JWT_SECRET_KEY` for
production. Optional integrations (each with a `REQUIRES USER CONFIGURATION`
marker in its provider module):

- **AI:** `OPENAI_API_KEY` (falls back to a keyless deterministic dev provider)
- **Wearables:** `FITBIT_CLIENT_ID` / `FITBIT_CLIENT_SECRET` (Fitbit OAuth2)
- **Payments:** `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` (falls back to demo)
- **Encryption:** `TOKEN_ENCRYPTION_KEY` for wearable tokens at rest

See [docs/environment-variables.md](docs/environment-variables.md) for the full list.

## Docs

- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)
- [Database schema](docs/database.md)
- [Security model](docs/security.md)
- [AI layer](docs/ai.md)
- [Wearables / Fitbit](docs/wearables.md)
- [Payments & subscriptions](docs/payments.md)
- [Testing](docs/testing.md)
- [Deployment](docs/deployment.md)

## Status

The core platform is implemented end-to-end across all domains (see
[DEVELOPMENT_STATE.md](docs/DEVELOPMENT_STATE.md)). The pytest suite is written
and reconciled to the API contracts; run it with `python -m pytest backend/tests/ -q`.
