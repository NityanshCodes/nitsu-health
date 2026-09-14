# NITSU Health — Environment Variables

Values are read by `backend/app/core/config.py` from the environment, loading
`<repo-root>/.env` then `backend/.env`. The canonical template is
`backend/.env.example` (and the mirrored root `.env.example`).

## Core

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `production` disables auto `create_all` |
| `DEBUG` | `false` | Debug mode |
| `DATABASE_URL` | `sqlite:///./nitsu_health.db` | SQLAlchemy URL (Postgres in prod) |

## Auth (JWT)

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | dev placeholder | Signing secret — **must be strong in prod** |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime |

## CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:4173` | Comma-separated allowed origins |

## AI

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `development` | `development` (keyless) or `openai` |
| `OPENAI_API_KEY` | — | Required for `openai` provider |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name |

## Wearables (Fitbit — backend-only secrets)

| Variable | Default | Description |
|----------|---------|-------------|
| `FITBIT_CLIENT_ID` | — | Fitbit app client id |
| `FITBIT_CLIENT_SECRET` | — | Fitbit app client secret |
| `FITBIT_REDIRECT_URI` | `http://localhost:8000/wearables/fitbit/callback` | OAuth redirect |

## Payments (Razorpay — backend-only secrets)

| Variable | Default | Description |
|----------|---------|-------------|
| `RAZORPAY_KEY_ID` | — | Razorpay key id |
| `RAZORPAY_KEY_SECRET` | — | Razorpay key secret |
| `RAZORPAY_WEBHOOK_SECRET` | — | Webhook signature secret |
| `PREMIUM_PRICE` | `499` | Paid plan price |
| `PAYMENT_CURRENCY` | `INR` | Currency |
| `FRONTEND_BASE_URL` | `http://localhost:5173` | Frontend origin (redirects) |

## Security

| Variable | Default | Description |
|----------|---------|-------------|
| `TOKEN_ENCRYPTION_KEY` | — | Fernet key to encrypt wearable tokens at rest |

## Rate limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | `true` | Enable limiter |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Window |
| `RATE_LIMIT_MAX_REQUESTS` | `60` | Max requests per window |

## Feature entitlements (FREE tier limits)

| Variable | Default | Description |
|----------|---------|-------------|
| `FREE_REPORT_LIMIT` | `2` | Reports allowed on FREE |
| `FREE_INSIGHT_LIMIT` | `3` | Insights allowed on FREE |
| `FREE_AI_QUESTIONS_PER_DAY` | `10` | AI questions/day on FREE |

## Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend base URL (see `frontend/.env.example`) |

## Generation helpers

```bash
python -c "import secrets;print(secrets.token_urlsafe(48))"   # JWT_SECRET_KEY
python -c "import secrets;print(secrets.token_urlsafe(32))"   # TOKEN_ENCRYPTION_KEY
```
