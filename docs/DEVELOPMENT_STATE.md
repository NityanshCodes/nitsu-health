# NITSU Health — Development State

**Last updated:** 2026-09-14
**Current branch:** `rebuild/full-platform-checkpoint`
**Pending commit:** dead-code cleanup (91 files deleted, 1 modified) — commit `92ce8b7` → pending

---

## What Was Completed This Session

### Dead-code cleanup (91 files removed)

Removed all genuinely dead code across backend, frontend, and root — superseded modules, empty stubs, stale configs, and test artifacts that no longer tested live code.

**Backend — 42 files deleted (8 dead subpackages + 20 individual files):**
- `app/ai/` (10 files) — superseded by `app/services/ai_*`
- `app/analytics/` (5 files) — superseded by `app/services/analytics_service.py`
- `app/notifications/` (4 files) — superseded by `app/services/notification_service.py`
- `app/nutrition/` (4 files) — superseded by `app/services/nutrition_service.py`
- `app/reports/` (4 files) — superseded by `app/services/report_service.py`
- `app/auth/` (6 files) — superseded by `app/utils/auth.py`
- `app/wearables/` (4 files) — superseded by `app/providers/wearables/`
- `app/middleware/` (6 files) — all empty (0 bytes), no imports anywhere
- 8 dead model files (not in `models/__init__.py`): `ai_chat`, `allergy`, `analytics`, `appointment`, `doctor`, `meal`, `medication`, `prediction`
- 5 dead schema files: `allergy`, `appointment`, `doctor`, `meal`, `medication`
- 2 dead API files: `appointments.py`, `medications.py` (empty, not registered in `main.py`)
- 5 dead services: `doctor`, `medical`, `storage`, `appointment`, `medication`
- 1 dead test: `test_ai_proxy.py` (tested removed ai-engine proxy route)

**Frontend — 43 files deleted:**
- `src/app/` directory (9 `.tsx` + 9 `.gitkeep`) — old Next.js-style re-exports; pages import from `src/pages/`
- `src/pages/Appointments.tsx`, `Medications.tsx` — placeholders not in `App.tsx` routes
- `src/hooks/` (6 files + `.gitkeep`) — all empty stubs; auth hook is in `context/AuthContext.tsx`
- `src/store/` (4 files + `.gitkeep`) — 0 references; all state in page-local useState
- `src/services/` (7 files) — 0 references; all pages import from `services/api.ts`
- `src/types/` (5 files) — 0 references; types live in `services/api.ts`
- `src/utils/` (4 files) — 0 references
- `src/styles/` (3 files) — 0 references; only `index.css` + `tokens.css` are live
- `src/middleware/auth.ts` — placeholder, 0 imports
- `src/components/ui/Textarea.tsx` — 0 references
- `frontend/next.config.ts` — duplicate of `vite.config.ts`
- `frontend/tailwind.config.ts` — Tailwind not used in project
- `frontend/test-results/.last-run.json` — stale Playwright artifact

**Root — 6 files deleted:**
- `ARCHITECTURE.md` — stale pre-rebuild doc; superseded by `docs/architecture.md`
- `PROMPT_5_COMPLETION.md` — stale historical snapshot
- `STATUS.md` — superseded by `docs/DEVELOPMENT_STATE.md`
- `setup_project.sh` — 0 bytes empty file
- `scripts/backup.sh`, `scripts/deploy.sh` — placeholder stubs, 0 references

**1 file modified:**
- `frontend/src/components/ui/index.ts` — removed `export { default as Textarea } from "./Textarea"` line

### Post-cleanup verification

| Check | Before cleanup | After cleanup | Explanation |
|-------|---------------|--------------|-------------|
| Backend tests | 89 passed, 2 skipped | 88 passed, 2 skipped | `test_ai_proxy.py` deleted (tested removed ai-engine proxy route) |
| Frontend build | ✅ | ✅ | No change |
| Backend import | ✅ | ✅ | No change |
| OpenAPI schema | ✅ | 96 endpoints (86 API + 10 system) | No change |
| SQLAlchemy tables | 20 | 20 | No models deleted from `__init__.py` |
| Routers | 19 | 19 | No routers deleted from `main.py` |

**No registered endpoints were removed.** The 2 deleted API files (`appointments.py`, `medications.py`) were empty and never imported in `main.py`. The test count decreased by exactly 1 due to deleting the ai-engine proxy test.

---

## What Remains

1. **GitHub push** — sandbox blocks `git push` and `gh` (network: `github.com:443` denied)
   - Run locally: `git push -u origin rebuild/full-platform-checkpoint && gh pr create --base main --title "Rebuild: full-platform checkpoint" --body "..."`

2. **OpenAI provider test coverage** — skipped due to missing `httpx` in `backend/.venv` (installed in `.venv` but not `backend/.venv`). Install `httpx` in `backend/.venv` when network available.

3. **Alembic live migration** — not executed (alembic not installed in either venv; sandbox blocks `pip install`). Schema validated via compile + `create_all` parity check.

---

## Known Blockers

| Blocker | Impact | Workaround |
|---------|--------|------------|
| Sandbox network egress blocked (`github.com`, `pypi.org`) | Can't push, can't install packages | Run push/commands locally |
| `httpx` missing in `backend/.venv` | 2 OpenAI provider tests skipped | `pip install httpx` in `backend/.venv` when network available |
| `alembic` not in `backend/.venv` | Can't run live migration test | Install `alembic` in `backend/.venv` or use root `.venv` |

---

## Next Exact Task (when resuming)

```bash
# Local terminal (outside sandbox):
cd /Users/nityansh/Documents/nitsu-health
git push -u origin rebuild/full-platform-checkpoint
gh pr create --base main --title "Rebuild: full-platform checkpoint" --body "Full-platform rebuild: backend domains, providers, frontend UI kit, tests, docs. Post-cleanup: 91 dead files removed, 88 tests passing."
```

Then verify PR CI passes.

---

## Quick Status Summary

| Area | Status |
|------|--------|
| Backend tests | 88 passed, 2 skipped |
| Frontend build | ✅ |
| Backend import/compile | ✅ |
| OpenAPI endpoints | 96 (86 API + 10 system) |
| SQLAlchemy tables | 20 |
| Routers | 19 |
| Docs | ✅ Complete |
| Dead code cleanup | ✅ 91 files removed |
| Git state | Unstaged cleanup ready to commit |

**Safe to sleep.** Nothing broken. All verification green.
