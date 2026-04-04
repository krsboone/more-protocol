---
id: handoff-stripe-integration
type: handoff
trust: confirmed
status: active
created: 2026-04-04
author: ai
subject: "Stripe webhook integration — session ended mid-implementation, three open threads"
tags: [stripe, webhooks, payments, backend]
expires_after: 3_sessions
---

## Where we are

Building a Stripe webhook handler for subscription events. Work is in progress at
`src/billing/webhooks.py`. Not yet connected to the router — the handler function
exists but the route registration in `src/app.py` is still a TODO.

Key decisions made this session:
- Verified webhook signature using `stripe.Webhook.construct_event` (not raw HMAC)
- Event types to handle: `customer.subscription.created`, `customer.subscription.deleted`, `invoice.payment_failed`
- DB model is `Subscription` in `src/models/subscription.py` — already has `stripe_subscription_id` field
- Webhook secret stored in `.env` as `STRIPE_WEBHOOK_SECRET` — confirmed working in test

What exists and is working:
- `handle_subscription_created()` — implemented and manually tested against Stripe CLI
- `handle_subscription_deleted()` — implemented, not yet tested
- `handle_payment_failed()` — stub only, no logic yet

## What's unsettled

- Idempotency: Stripe can send the same event more than once. The `handle_subscription_created`
  function will currently create duplicate records if the event replays. Decided to defer
  idempotency key tracking until after basic flow works — but this needs to come back.
- Error handling: currently raises on any DB error, which returns a 500 to Stripe. Stripe will
  retry on 5xx — need to decide which errors should return 200 (already handled) vs 500 (retry).
- Test coverage: no automated tests exist for the webhook handlers yet. Manual CLI testing only.

## What to do next

1. Register the webhook route in `src/app.py` — the handler is ready
2. Test `handle_subscription_deleted` against Stripe CLI (`stripe trigger customer.subscription.deleted`)
3. Implement `handle_payment_failed` — send notification email + update subscription status to `past_due`
4. Add idempotency key table (`processed_webhook_events`) and check before processing
5. Write pytest fixtures using Stripe's test payloads

## What to watch for

- Stripe test mode vs live mode — `STRIPE_WEBHOOK_SECRET` in `.env` is the **test** secret.
  A separate `STRIPE_WEBHOOK_SECRET_LIVE` will be needed for production. Easy to mix up.
- The `subscription.deleted` event fires immediately on cancellation; `subscription.updated`
  fires on scheduled cancellations (at period end). Make sure the deletion handler is only
  wired to the right event — this was a source of confusion earlier.

## Resolutions

- [resolved 2026-04-04] Signature verification approach — confirmed `stripe.Webhook.construct_event` is correct; raw HMAC was a false lead
- [open] Idempotency key tracking
- [open] Error handling strategy (which errors should retry vs acknowledge)
- [open] `handle_payment_failed` implementation
- [open] Automated test coverage
- [open] Route registration in app.py
