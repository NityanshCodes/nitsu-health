# NITSU Health

NITSU Health is a health platform project scaffolded for Phase 1 foundation work.

## Structure

- backend: FastAPI application skeleton
- frontend: React + Vite application shell
- ai-engine: isolated AI module scaffold
- docs: architecture and planning documents
- docker: container configuration placeholders
- scripts: startup and deployment helpers

## Getting started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Status

This repository currently implements the Phase 1 foundation: project structure, environment placeholders, scaffolding, docs, and starter app entrypoints.
