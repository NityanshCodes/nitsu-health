# NITSU Health — AI Layer

The AI layer is consolidated in the main backend as part of the modular
monolith (there is no separate `ai-engine` runtime service).

## Provider abstraction

`backend/app/services/ai_provider.py` defines an `AIProvider` interface with
two implementations:

- **`OpenAIProvider`** — real chat-completions calls when `OPENAI_API_KEY` is set
  (model configurable via `OPENAI_MODEL`).
- **`DevelopmentProvider`** — a keyless, deterministic fallback used when no API
  key is present. It returns structured development responses that demonstrate
  context awareness. This keeps the entire platform runnable locally with zero
  configuration.

`AIProviderFactory.get_provider()` returns OpenAI when configured, otherwise the
development provider.

## Capabilities

### Chat (`POST /ai/chat`)
A data-aware assistant. The request includes the user's `question` (and
optionally a `conversation_id` for multi-turn). Before answering, the service
builds an **AI context summary** from the current user's real data:

- recent health metrics (last N days)
- today's nutrition summary
- active goals and progress
- recent activity / sleep
- medical-record metadata and family history (metadata only, no file contents)

Conversations and messages are persisted (`ai_conversations`, `ai_messages`) and
are user-scoped (`GET /ai/conversations`, `GET /ai/conversations/{id}`).

### Insights (`POST /ai/insights/generate`, `GET /ai/insights`)
Derives insights **from actual recorded data**, never fabricated:
- trend detection over a window (e.g. declining sleep duration),
- goal progress milestones,
- missing-data nudges (e.g. no nutrition logged in 3 days).

Each insight carries `insight_type`, `title`, `body`, `source_data` (the
supporting records), a `confidence`, and a suggested next step. Insights are
observations — e.g. *"recorded sleep duration decreased over the last 2 weeks"* —
not diagnoses.

### Reports (`POST /reports/generate`, `GET /reports`)
Builds a structured wellness report from real data + AI observations: summary
statistics, trends, goal status, and a plain-language AI narrative. Reports are
stored (`health_reports`) and include a disclaimer noting NITSU is not a medical
device. Report generation is an entitlement-gated feature (PREMIUM by default).

## Safety rules (enforced in code)

1. Context only includes the **current user's** data.
2. Never include secrets, tokens, or other users' data.
3. Observation vs interpretation framing — no diagnostic language.
4. Provider is chosen by factory; development mode works keyless.

## Health status

`GET /ai/health` reports the active provider and whether it is configured.
