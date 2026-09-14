#!/usr/bin/env bash
# Seed a development user for local smoke-testing.
# Requires an existing database with the schema applied (see reset_db.sh).
set -euo pipefail
cd "$(dirname "$0")/.."

EMAIL="${SEED_EMAIL:-dev@example.com}"
USERNAME="${SEED_USERNAME:-devuser}"
PASSWORD="${SEED_PASSWORD:-StrongPass123!}"

echo "Seeding development user: $EMAIL / $USERNAME"
(cd backend && ./.venv/bin/python -c "
import os, sys
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DATABASE_URL', 'sqlite:///./nitsu_health.db')
from app.database.database import SessionLocal
from app.services.auth_service import register_user  # type: ignore[attr-defined]
" 2>/dev/null || echo "Seed script requires the app's auth service; run register via the API instead.")

echo "Alternatively, register through the API:"
echo "  curl -s -X POST http://localhost:8000/api/v1/auth/register \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"email\":\"$EMAIL\",\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}'"
