# NITSU Health — Backend

A FastAPI **modular monolith** under `backend/`. Python 3.11+; SQLAlchemy 2.0 +
Pydantic v2; JWT auth (python-jose) + bcrypt (passlib); Alembic migrations.

## Layout

```
backend/
  app/
    main.py               # FastAPI app: lifespan, CORS, router registration, /health
    core/config.py        # Settings from env (Settings class)
    database/             # engine, session (get_db), Base
    models/               # SQLAlchemy models (all registered in __init__)
    schemas/              # Pydantic request/response models
    api/                  # Routers (one per domain)
    services/             # Business logic (per domain + ai, analytics, etc.)
    providers/            # External integrations
      ai/                 # (AI provider lives in services/ai_provider.py)
      payments/           # ABC + razorpay + demo
      wearables/          # ABC + fitbit + demo
    middleware/           # rate limiting
    utils/                # audit logging, auth helpers, ai context builder
  alembic/                # migrations (env.py wired to settings + models)
  tests/                  # pytest suite
  requirements.txt
```

## Design principles

- **Ownership verification** on every user-data endpoint — queries are scoped to
  `current_user.id`.
- **No fake implementations disguised as real ones.** External integrations use
  provider abstractions with clearly-labeled dev/demo fallbacks and
  `REQUIRES USER CONFIGURATION` markers where credentials are required.
- **Provider abstractions** for AI, payments, and wearables, each with a
  `is_configured()` check and a graceful dev path.
- **Secrets backend-only** — OAuth/payment keys are read from env and never
  returned in responses; wearable tokens are encrypted at rest.

## Entry point

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Environment

Copy `backend/.env.example` → `.env` (values are also read from the repo-root
`.env`). See `docs/environment-variables.md`.

## Optional dependencies

`httpx`, `python-dotenv`, and `email-validator` are **soft** dependencies: the
app imports and the development path runs even when they are absent (useful in
constrained/offline environments). They remain in `requirements.txt` for
production and full-featured use.
