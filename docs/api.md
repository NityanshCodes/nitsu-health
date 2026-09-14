# NITSU Health — API Reference

Base URL: `http://localhost:8000` (dev). All business endpoints live under the
routers registered in `backend/app/main.py` (paths shown below are the full
paths as served; the OpenAPI spec is available at `/openapi.json`, interactive
docs at `/docs`).

Authentication: most endpoints require `Authorization: Bearer <JWT>` obtained
from `POST /auth/register` or `POST /auth/login`. All user-owned data is scoped
to the authenticated user's id — no endpoint reads or writes another user's
records.

## System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/health/ready` | Readiness probe (DB connectivity + status) |
| GET | `/docs`, `/redoc`, `/openapi.json` | OpenAPI / interactive docs |

## Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create account (`email`, `username`, `password`, optional names) |
| POST | `/auth/login` | Log in → returns JWT access token |
| POST | `/auth/logout` | Log out (audit-logged) |

## Users & Profile

| Method | Path | Description |
|--------|------|-------------|
| GET/PUT | `/users/me` | Read / update own account |
| PATCH | `/users/me/password` | Change password (`current_password`, `new_password`) |
| GET/PUT | `/profile` | Read / update health profile (auto-created) |
| GET/POST | `/profile/family-history` | List / add family history |
| PUT/DELETE | `/profile/family-history/{entry_id}` | Update / delete family history |

## Health metrics (longitudinal)

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/health/metrics` | List (filter `?type=&from=&to=&page=`) / record a metric |
| GET | `/health/metrics/types` | Known metric types |
| GET/PUT/DELETE | `/health/metrics/{metric_id}` | Read / update / delete a metric |

## Nutrition / Activity / Sleep

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/nutrition` | List (filter `?date=&page=`) / log food |
| GET | `/nutrition/today` | Today's aggregate |
| GET | `/nutrition/trends` | Daily trend summaries |
| GET/PUT/DELETE | `/nutrition/{entry_id}` | Read / update / delete |
| GET/POST | `/activity` | List / log activity |
| GET | `/activity/today`, `/activity/weekly` | Aggregates |
| GET/PUT/DELETE | `/activity/{entry_id}` | Read / update / delete |
| GET/POST | `/sleep` | List / log sleep |
| GET | `/sleep/weekly` | Weekly averages |
| GET/PUT/DELETE | `/sleep/{entry_id}` | Read / update / delete |

## Goals & Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/goals` | List / create goal |
| GET/PUT/DELETE | `/goals/{goal_id}` | Read / update / delete |
| POST | `/goals/{goal_id}/progress` | Update progress (auto-completes at target) |
| GET | `/analytics/summary` | Daily/weekly/monthly summaries + data completeness |
| GET | `/analytics/trends/{metric_type}` | Trend over a window (observation-based) |
| GET | `/analytics/goals` | Goal progress breakdown |

## Dashboard, Notifications, Search

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard` | Overview (metrics, today's nutrition, activity, sleep, goals, insights, unread count) |
| GET | `/notifications` | List notifications |
| POST | `/notifications/{notification_id}/read` | Mark one read |
| POST | `/notifications/read-all` | Mark all read |
| GET | `/search` | Unified search across user's data (`?q=` minimum 2 chars) |

## AI

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ai/chat` | Ask the assistant (`question`, optional `conversation_id`) |
| GET | `/ai/conversations` | List conversations |
| GET | `/ai/conversations/{id}` | Read a conversation |
| POST | `/ai/insights/generate` | Derive insights from actual data |
| GET | `/ai/insights` | List insights |
| POST | `/ai/insights/{id}/read` | Mark insight read |
| GET | `/ai/health` | AI provider status |

## Medical Records

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/medical-records` | List / upload (multipart) |
| GET/PUT/DELETE | `/medical-records/{record_id}` | Read / update / delete |

## Reports

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reports` | List reports |
| POST | `/reports/generate` | Generate a structured wellness report |
| GET | `/reports/latest` | Most recent report |
| GET | `/reports/{report_id}` | Read a report |

## Wearables

| Method | Path | Description |
|--------|------|-------------|
| GET | `/wearables/fitbit/connect` | OAuth2 authorization URL (503 if unconfigured) |
| GET | `/wearables/fitbit/callback` | OAuth2 callback (state validated) |
| POST | `/wearables/fitbit/sync` | Pull metrics from Fitbit |
| GET | `/wearables/status` | Configured providers + connection status |
| GET | `/wearables/connections` | User's connections |

## Subscriptions & Payments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/subscription/status` | Current plan + status |
| GET | `/subscription/plan` | Plan detail + entitlements |
| POST | `/subscription/downgrade` | Downgrade to FREE |
| POST | `/payments/create-order` | Create an order (Razorpay, or demo when unconfigured) |
| POST | `/payments/verify` | Verify a payment (signature) |
| POST | `/payments/webhook` | Idempotent webhook (PaymentEvent idempotency key) |
| GET | `/payments/history` | Payment history |

## Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/users` | List users (admin only, 403 otherwise) |
| GET | `/admin/subscriptions` | Subscription overview |
| GET | `/admin/payments` | Payment events |
| GET | `/admin/audit-log` | Audit log |
| GET | `/admin/health` | System + integration status |

## Error semantics

- `401` — missing/invalid credentials
- `403` — authenticated but not authorized (e.g. non-admin on admin routes)
- `404` — resource not found (or not owned by the user)
- `422` — validation error (bad input)
- `503` — provider not configured (e.g. Fitbit/Razorpay credentials missing)
