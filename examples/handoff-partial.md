---
id: handoff-stripe-integration
type: handoff
trust: confirmed
status: partial
created: 2026-04-04
updated: 2026-04-05
author: ai
subject: "Stripe webhook integration — route registered, payment failure handler done, idempotency still open"
tags: [stripe, webhooks, payments, backend]
expires_after: 3_sessions
---

## Where we are

Webhook handler is now live in the application. Route registered in `src/app.py` at
`POST /webhooks/stripe`. Manually verified end-to-end with Stripe CLI for all three
event types. The `handle_payment_failed` function sends a notification email via
`src/notifications/email.py` and updates the subscription status to `past_due`.

What's working:
- All three handlers implemented and manually tested
- Route registered and reachable
- Stripe CLI round-trips successful for all event types
- Email notification on payment failure confirmed delivered (Mailpit in dev)

What was resolved this session:
- Idempotency key tracking — implemented `processed_webhook_events` table, checked
  on every inbound event before processing. Duplicate events now silently 200.
- Route registration — done.

## What's unsettled

- Error handling: still unresolved. Current behavior raises on DB errors (returns 500,
  triggers Stripe retry). Need a decision on which errors should be swallowed vs retried.
  The risk of retrying on a transient DB error is safe. The risk of retrying on a logic
  error that partially succeeded is not — could corrupt subscription state.
- Test coverage: no pytest tests yet. Manual CLI testing has caught issues but leaves
  the happy path unverifiable in CI.

## What to do next

1. Decide error handling strategy — suggest: catch `IntegrityError` and return 200
   (idempotency already guards this); re-raise everything else so Stripe retries
2. Write pytest tests using Stripe's fixture payloads from `tests/fixtures/stripe/`
3. Review with the team before merging — this is billing code

## What to watch for

- The `processed_webhook_events` table uses `event_id` as a unique key. Make sure
  migrations are applied before deploying — the handler will crash on first event
  if the table doesn't exist.
- Stripe test vs live webhook secrets — see original handoff note. Not yet addressed.

## Resolutions

- [resolved 2026-04-04] Signature verification approach — `stripe.Webhook.construct_event` confirmed correct
- [resolved 2026-04-05] Route registration in app.py — done
- [resolved 2026-04-05] `handle_payment_failed` implementation — implemented with email notification
- [resolved 2026-04-05] Idempotency key tracking — `processed_webhook_events` table added and working
- [open] Error handling strategy (which errors should retry vs acknowledge)
- [open] Automated test coverage
- [open] Team review before merge
