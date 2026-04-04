---
id: handoff-auth-refactor-v1
type: handoff
trust: confirmed
status: superseded
created: 2026-03-20
updated: 2026-03-22
author: ai
subject: "Auth middleware refactor — superseded by handoff-auth-refactor-v2 after scope changed"
tags: [auth, middleware, refactor]
expires_after: 3_sessions
deprecated_reason: "Scope expanded significantly after compliance review — replaced by handoff-auth-refactor-v2 which reflects the new requirements"
history:
  - date: 2026-03-22
    author: ai
    change: "Marked superseded — new handoff written to reflect expanded scope"
    reason: "Compliance team review identified additional session token requirements not covered by original plan"
    superseded: "more://./handoff-auth-refactor-v2"
---

## Where we are

*This handoff has been superseded by [handoff-auth-refactor-v2](handoff-active.md).*
*Read that file for current state. This file is retained for historical context only.*

---

Auth middleware refactor in progress. Plan was to replace the JWT library with a
simpler HMAC-SHA256 implementation to reduce dependency surface. Work had started
in `src/middleware/auth.py` but was paused when the compliance team asked for a
review of the session token storage approach.

## What's unsettled

All items were carried forward into the new handoff, with scope expanded.

## Resolutions

- [open → carried forward] JWT replacement implementation
- [open → carried forward] Session token storage review (compliance requirement added)
- [open → carried forward] Test coverage for new auth path
