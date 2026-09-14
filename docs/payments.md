# NITSU Health — Payments & Subscriptions

## Entitlements

`backend/app/services/entitlement_service.py` centralizes feature gating. A
single `check(user, feature)` reads the plan from `subscriptions` (FREE /
PREMIUM) and a `FEATURE_MAP`. Limits for the FREE tier are configurable via env
(`FREE_REPORT_LIMIT`, `FREE_INSIGHT_LIMIT`, `FREE_AI_QUESTIONS_PER_DAY`). This
keeps gating in one place instead of scattered `if premium` checks.

## Provider abstraction

`backend/app/providers/payments/` defines a payment provider ABC:

- `create_order(amount, currency, receipt)`
- `verify_payment(order_id, payment_id, signature)`

Implementations:

- **`RazorpayProvider`** — real Razorpay Orders API. **`REQUIRES USER
  CONFIGURATION`:** set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`.
- **`DemoProvider`** — deterministic dev flow used when Razorpay is
  unconfigured (exercises create/verify without external calls).

Secrets are **backend-only**; they are read from the environment and never
returned to the frontend.

## API flow

1. `POST /payments/create-order` → returns an order (Razorpay `provider_order_id`,
   or a demo order). The client renders the payment UI.
2. `POST /payments/verify` → verifies the signature (`order_id|payment_id` HMAC).
   On success the user's subscription is upgraded to PREMIUM and a `Payment` row
   is recorded.
3. `POST /payments/webhook` → idempotent server-to-server notification. Each
   event is recorded in `payment_events` keyed by an idempotency key, so
   duplicate deliveries never double-credit.
4. `GET /payments/history` → the user's payment history.
5. `GET /subscription/status` → current plan + status.
6. `GET /subscription/plan` → plan detail + entitlements (drives the frontend).
7. `POST /subscription/downgrade` → return to FREE.

## Testing

`test_subscription_payments.py` covers: default FREE plan, feature flags,
create-order + demo verify → PREMIUM, payment history, downgrade, and webhook
idempotency.
