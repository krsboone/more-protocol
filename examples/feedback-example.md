---
id: feedback-no-mock-database
type: feedback
trust: confirmed
status: active
created: 2026-02-03
author: human
subject: "Integration tests must use a real database, never mocks"
tags: [testing, database, integration]
---

Do not mock the database in integration tests. Use a real database instance.

**Why:** Last quarter, mocked tests passed while the production migration
failed — the mock didn't reflect actual database behavior closely enough
to catch the problem. This caused a production incident.

**How to apply:** Any test touching database logic gets a real connection.
If setting up a real database for tests is inconvenient, that inconvenience
is acceptable. The alternative is worse.
