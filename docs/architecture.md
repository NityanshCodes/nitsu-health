# Architecture

## Backend
- FastAPI application entrypoint in backend/app/main.py
- Core configuration in backend/app/core/config.py
- Database connection placeholders in backend/app/database
- API modules under backend/app/api

## Frontend
- React + Vite app in frontend
- Page placeholders under frontend/src/pages
- Future routing and state management will be added here

## AI Engine
- Separate module scaffold under ai-engine
- Intended for future embeddings, prompts, and pipelines

## Database
- PostgreSQL is configured as the target database
- Connection URL is supplied via environment variables
