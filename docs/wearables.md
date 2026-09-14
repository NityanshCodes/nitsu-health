# NITSU Health — Wearables / Fitbit

## Provider architecture

`backend/app/providers/wearables/` defines a `WearableProvider` ABC with:

- `auth_url(state)` — build the OAuth2 authorization URL
- `exchange_code(code)` — trade the callback code for tokens
- `refresh_token(token)` — refresh an expired token
- `fetch_metrics(access_token, period_days)` — pull steps/activity/sleep
- `is_configured()` — whether credentials are present

Implementations:

- **`FitbitProvider`** — real Fitbit Web API (OAuth2). **`REQUIRES USER
  CONFIGURATION`:** set `FITBIT_CLIENT_ID` and `FITBIT_CLIENT_SECRET`.
- **`DemoProvider`** — safe, clearly-labeled dev data used when Fitbit is
  unconfigured, so the integration is exercisable locally.

## Fitbit setup

1. Create a Fitbit developer app at https://dev.fitbit.com.
2. Register the redirect URI (matches `FITBIT_REDIRECT_URI`).
3. Set `FITBIT_CLIENT_ID`, `FITBIT_CLIENT_SECRET`, and the redirect URI.
4. Optionally set `TOKEN_ENCRYPTION_KEY` so returned tokens are encrypted at rest.

> OAuth secrets are **backend-only** — they are never sent to the frontend.
> Set `ENVIRONMENT=production` and `DEBUG=false` in production.

## API flow

1. `GET /wearables/fitbit/connect` → returns the Fitbit authorization URL
   (with a state token). Returns **503** with a clear config error if
   credentials are missing.
2. User authorizes on Fitbit; Fitbit redirects to `GET /wearables/fitbit/callback`
   with a `code` and `state` (validated).
3. `POST /wearables/fitbit/sync` → exchanges/pulls metrics and stores them as
   `wearable_data` (`source=WEARABLE`).
4. `GET /wearables/status` → configured providers + the user's connection status.
5. `GET /wearables/connections` → the user's stored connections.

Tokens (access/refresh) are stored encrypted in `wearable_connections` and
rotated on refresh. Synced metrics feed the normal health/analytics surfaces.

## Extending

To add another provider (e.g. Google Fit, Garmin), implement the
`WearableProvider` ABC and register it in the factory. (Listed as future work.)
