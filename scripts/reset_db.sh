#!/usr/bin/env bash
# Reset the development database: drop all tables and re-apply migrations.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Removing dev SQLite database(s)..."
rm -f backend/nitsu_health.db nitsu_health.db test_auth.db backend/test_auth.db

echo "Re-applying Alembic migrations..."
(cd backend && ./.venv/bin/python -m alembic upgrade head 2>/dev/null \
  || venv/bin/python -m alembic upgrade head \
  || python -m alembic upgrade head)

echo "Database reset complete."
