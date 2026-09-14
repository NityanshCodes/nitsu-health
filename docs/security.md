# NITSU Health — Security Model

## Authentication & authorization

- **Passwords** are hashed with bcrypt (via `passlib`) — never stored in plaintext.
- **JWT** (HS256) access tokens are issued at login/register. The `Authorization:
  Bearer <token>` header is validated by a `get_current_user` dependency that
  resolves the user from the token and rejects inactive users.
- **Ownership enforcement:** every user-data endpoint scopes its query to
  `current_user.id`. There is no endpoint that accepts another user's id to read
  or mutate their data. Cross-user isolation is covered by tests.
- **Admin routes** (`/admin/*`) require a dedicated `require_admin` dependency
  that checks a role stored in the DB. Ordinary users receive `403`, never a
  privilege escalation path. Admin status cannot be granted via a self-service
  endpoint.

## Secrets handling

- OAuth tokens (Fitbit) and payment keys (Razorpay) are **backend-only**. They are
  read from environment variables and are never serialized into API responses.
- Wearable access/refresh tokens are **encrypted at rest** with
  `TOKEN_ENCRYPTION_KEY` (Fernet) in `wearable_connections`.
- `JWT_SECRET_KEY` must be a strong random value in production.

## Audit logging

`app/utils/audit.py` provides `log_action(db, user, action, entity_type,
entity_id, metadata)`. It is called on security-relevant and data-changing
events: login/logout, password changes, profile/data changes, wearable
connect/disconnect, subscription changes, and admin actions. Audit records are
viewable via `GET /admin/audit-log`.

## Rate limiting

`app/middleware/rate_limit.py` applies an in-memory, per-client, per-window
limiter to sensitive endpoints (`/auth/login`, `/auth/register`, `/ai/chat`).
Tunable via `RATE_LIMIT_ENABLED`, `RATE_LIMIT_WINDOW_SECONDS`,
`RATE_LIMIT_MAX_REQUESTS`.

## Payments / webhooks

- Payment webhooks are **idempotent**: each event is recorded with an idempotency
  key in `payment_events`, so duplicate deliveries do not double-credit.
- Signature verification uses the provider secret; unverified payloads are rejected.

## AI safety & privacy

- The AI context builder only includes the *current user's* data and never
  secrets, tokens, or other users' records.
- Output is framed as **observations, not diagnoses**. Reports carry a disclaimer
  that NITSU is not a medical device and does not replace professional care.
- No data is shared with a third party beyond the configured AI provider (only
  when `AI_PROVIDER=openai` is set and an API key is present).

## Input validation

- Pydantic models validate request bodies (`422` on invalid input); e.g. health
  metric values must be non-negative (`ge=0`).
- Email format is validated (stdlib regex) without a hard dependency on
  `email-validator`.

## Deployment notes

- Run behind TLS in production.
- Keep `DEBUG=false`, set a real `JWT_SECRET_KEY`, `TOKEN_ENCRYPTION_KEY`, and
  integration secrets via the environment (never commit `.env`).
