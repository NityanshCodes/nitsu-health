# NITSU Health — Database Schema

Schema is owned by **Alembic migrations** in `backend/alembic/versions/`. In
development SQLite is used; production uses PostgreSQL. Run `alembic upgrade
head` from `backend/` to apply. (In non-production environments the app may also
auto-create tables via `Base.metadata.create_all` for convenience; production
never does.)

All user-owned tables carry a `user_id` foreign key with an index, and every
query path in the API scopes reads/writes to the authenticated user's id.

## Tables (20)

| Table | Purpose | Key fields |
|-------|---------|-----------|
| `users` | Accounts & auth | `email` (unique), `username`, `password_hash`, `role`, `is_active` |
| `health_profiles` | User health profile | `user_id`, height/weight, blood type, lifestyle, notes |
| `family_history` | Family medical history | `user_id`, `category`, `relation`, `notes` |
| `health_metrics` | Longitudinal vitals/metrics | `user_id`, `metric_type`, `value`, `unit`, `recorded_at`, `source` |
| `nutrition_entries` | Food log | `user_id`, food name, calories, macros, `recorded_at`, `source` |
| `activity_entries` | Exercise log | `user_id`, `activity_type`, steps, active_minutes, distance, calories, `source` |
| `sleep_entries` | Sleep log | `user_id`, `start_time`, `end_time`, `duration_minutes`, `sleep_stages` (JSON), `source` |
| `wearable_connections` | OAuth connections | `user_id`, `provider`, status, encrypted tokens, scopes, `last_synced_at` |
| `wearable_data` | Synced wearable metrics | `user_id`, provider, metric type, value, `source=WEARABLE` |
| `medical_records` | Uploaded records | `user_id`, category, title, `file_path`, `mime_type`, `recorded_at` |
| `health_goals` | Goals | `user_id`, `goal_type`, title, target/unit, start/target date, progress, status |
| `health_reports` | Generated reports | `user_id`, title, `report_data` (JSON), `generated_at` |
| `ai_conversations` | Chat sessions | `user_id`, title, created_at |
| `ai_messages` | Chat turns | `user_id`, `session_id`, role, content, `context_used` (JSON) |
| `ai_insights` | Derived insights | `user_id`, `insight_type`, title, body, `source_data` (JSON), confidence, read state |
| `notifications` | In-app notifications | `user_id`, type, title, body, `is_read`, `created_at` |
| `subscriptions` | Plan/status | `user_id`, `plan` (FREE/PREMIUM), status, provider, start/expiry |
| `payments` | Orders | `user_id`, amount, currency, status, provider, `provider_order_id` |
| `payment_events` | Webhook/event log (idempotency) | `user_id`, `event_id` (idempotency key), event, payload, `created_at` |
| `audit_logs` | Audit trail | `user_id` (nullable for admin), action, entity_type/id, metadata, `created_at` |

## Conventions

- Primary keys: integer autoincrement (`id`).
- Timestamps: `created_at`/`updated_at` (UTC) where relevant.
- JSON columns (Postgres `JSONB`, SQLite `JSON`) for flexible payloads:
  `sleep_stages`, `report_data`, `context_used`, `source_data`, audit `metadata`.
- `source` enums on tracked data: `MANUAL` / `WEARABLE` / `IMPORTED` /
  `CALCULATED` / `AI_GENERATED`.
- OAuth access/refresh tokens are stored **encrypted** in `wearable_connections`
  using `TOKEN_ENCRYPTION_KEY` (Fernet).

## Migrations

```
backend/alembic/
  env.py              # wires DATABASE_URL + models
  versions/0001_initial_schema.py
  versions/0002_add_report_type.py
```

Revisions are applied in order. To add a new column/table after changing a model:

```bash
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
