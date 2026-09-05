# Database Architecture

This folder contains the architecture blueprint for the NITSU Health data layer.

## Storage layers
- PostgreSQL: structured relational data
- Redis: sessions, cache, rate limiting, and temporary state
- Vector DB: embeddings and semantic search support for AI
- Object storage: medical files and media assets

## Structure
- postgres/: schema, migrations, seeds, indexes, constraints
- redis/: cache and session design
- vector/: collections, embeddings, metadata, search design
- storage/: file and media storage layout
- diagrams/: ERD and documentation placeholders
