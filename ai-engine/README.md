# AI Engine Architecture

This directory contains the Phase 4 AI engine scaffold for NITSU Health.

## Purpose
Build a modular, scalable AI system that supports:

- Medical chatbot
- Nutrition recommendations
- Health risk prediction
- Medical report analysis
- Wearable data interpretation
- Vector search / RAG

## Architecture

### models/
Contains model adapters and wrappers for:

- LLMs
- Embeddings
- Classifiers
- Recommendation engines
- Prediction models

### prompts/
Stores prompt templates and prompt engineering assets for each AI feature.

### rag/
Contains the RAG pipeline structure:

- ingestion
- chunking
- embedding generation
- vector store
- retrieval
- ranking

### pipelines/
Defines workflows for each AI feature:

- chatbot
- nutrition
- report analysis
- prediction
- wearable analysis

### agents/
Specialized AI agents and a coordinator agent that routes requests.

### tools/
Deterministic utilities the AI can use for calculations and validation.

### memory/
Conversation, session, and summary memory helpers.

### evaluation/
Benchmarking and dataset structure for AI quality measurement.

### configs/
Central configuration for models, prompts, and runtime settings.

### data/
Stores knowledge files, embeddings, uploads, and cache artifacts.

### tests/
AI architecture and integration test stubs.

### logs/
AI request and behavior logging.

## Workflow

A request enters the backend and is forwarded to the coordinator agent. The coordinator determines which specialized agent should handle it, optionally uses the RAG components to load relevant knowledge, and then delegates execution to the selected agent.

## Phase 4 status

This scaffold contains the complete architecture, placeholder modules, and config files needed to begin AI implementation without requiring any further structural changes.
