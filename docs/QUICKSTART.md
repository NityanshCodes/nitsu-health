# Quick Start Guide — NITSU Health

## Prerequisites

- Python 3.11+
- Node.js 18+
- Git

## Local Development Setup

### 1. Clone and set up

```bash
git clone <repository>
cd nitsu-health

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### 2. Start the backend

```bash
cd backend
source .venv/bin/activate
alembic upgrade head          # apply migrations (dev: tables auto-created anyway)
uvicorn app.main:app --reload --port 8000
```

Health check: `curl http://localhost:8000/health`

### 3. Start the frontend (new terminal)

```bash
cd frontend
npm run dev                    # http://localhost:5173
```

### 4. Full stack

```bash
./scripts/start.sh
# or with Docker:
docker compose -f docker/docker-compose.yml up --build
```

## Running tests

```bash
# Backend
cd backend
python -m pytest tests/ -q
# Expected: 88 passed, 2 skipped

# Frontend build
cd frontend
npm run build                  # tsc + vite (must pass cleanly)
```

## Configuration

Copy `.env.example` → `.env` in both the repo root and `backend/`. At minimum,
set a strong `JWT_SECRET_KEY` for production. Optional integrations:

- **AI:** `OPENAI_API_KEY` (falls back to a keyless dev provider)
- **Wearables:** `FITBIT_CLIENT_ID` / `FITBIT_CLIENT_SECRET`
- **Payments:** `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET`

See [environment-variables.md](environment-variables.md) for the full list.

## Common issues

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'app'` | Run from `backend/` with `PYTHONPATH=.` or activate the venv |
| CORS error in browser | Ensure `CORS_ORIGINS` includes `http://localhost:5173` |
| `database is locked` | Restart the backend; in dev, deleting `nitsu_health.db` recreates it |
| Password validation fails | Must have 8+ chars, uppercase, lowercase, digit, special char |

## Docs

- [Architecture](architecture.md)
- [API reference](api.md)
- [Database schema](database.md)
- [Security model](security.md)
- [AI layer](ai.md)
- [Deployment](deployment.md)
