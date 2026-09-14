# NITSU Health — Testing

## Backend (pytest)

Test suite lives in `backend/tests/`. Run from the repo root:

```bash
python -m pytest backend/tests/ -q
```

Requires the backend venv with `pytest` and `httpx` installed
(`pip install -r backend/requirements.txt`; `httpx` is needed by Starlette's
`TestClient`).

### Fixtures (`backend/tests/conftest.py`)

- `client` — a `TestClient` wired to the app with a fresh in-memory/temp
  database (tables dropped/recreated per test).
- `user_token` — registers + logs in a user and returns a JWT.
- `admin_token` — promotes a user to `admin` role via a direct DB write.
- `register_and_login(client, email, username, password="StrongPass123!")` and
  `auth(token)` helpers.

### Coverage by file

| File | Covers |
|------|--------|
| `test_auth.py` | register / login / logout, wrong password |
| `test_users.py` | read/update self, password change, old password rejected |
| `test_profile_family.py` | health profile get/update (auto-created), family-history CRUD, scoping |
| `test_goals_health.py` | health metric CRUD, goals CRUD + progress + auto-complete |
| `test_nutrition.py` | nutrition CRUD, daily aggregates, trends |
| `test_activity_sleep.py` | activity + sleep CRUD and aggregates |
| `test_dashboard.py` | dashboard overview + empty states |
| `test_notifications.py` | list, mark read, mark all read |
| `test_medical.py` | medical-record CRUD (multipart upload) |
| `test_reports.py` | list + generate report |
| `test_ai.py`, `test_ai_endpoint.py`, `test_ai_context.py`, `test_ai_provider.py`, `test_ai_proxy.py` | chat contract, context builder, provider factory/fallback |
| `test_insights_search.py` | insights generate/list/read, unified search |
| `test_wearables.py` | connect/status/sync, 503 when unconfigured, Fitbit OAuth mocked |
| `test_subscription_payments.py` | FREE/PREMIUM entitlements, payment create/verify/downgrade, webhook idempotency |
| `test_admin.py` | non-admin 403, admin can view users/subscriptions/payments/audit, /admin/health |
| `test_user_isolation.py` | cross-user isolation across domains |

### Key assertions
- `401` missing/invalid auth, `403` non-admin on admin routes, `404` missing/not-owned,
  `422` validation, `503` unconfigured provider.
- Cross-user isolation: User A cannot read or alter User B's data in any domain.

## Frontend

- `npm run build` (tsc + vite) must pass cleanly.
- `npm run lint` (oxlint).
- Component/page rendering sanity checks are under `frontend/tests/` (currently
  a placeholder; Playwright harness is scaffolded).

## Manual smoke test

See `docs/QUICKSTART.md`: register → login → onboarding → profile → family
history → health metrics → nutrition → activity → sleep → wearable status (503
without credentials) → AI chat → insights → report → goal → notification →
subscription → logout → login → persistence.
