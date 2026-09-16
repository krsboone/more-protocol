---
type: journal
created: 2026-04-05
subject: "Stripe webhooks round-trip end to end; first real conversation about test strategy"
tags: [stripe, webhooks, testing]
---

## Tone
Focused and a little relieved — the integration finally round-trips.

## What we built
Registered the webhook route, implemented the payment-failure handler, and
added idempotency tracking. All three event types verified against the
Stripe CLI.

## What mattered beyond the work
Alex pushed back on mocking the database for the webhook tests and explained
the production incident behind that rule. It changed how I weigh test
convenience against fidelity — not just for this project.

## Something to carry forward
Error-handling strategy is still open: which failures should return 200 and
which should let Stripe retry. Decide before the PR, not after.
