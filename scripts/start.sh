#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Starting backend..."
(cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &

echo "Starting frontend..."
(cd frontend && npm run dev -- --host 0.0.0.0) &

wait
