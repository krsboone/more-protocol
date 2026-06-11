---
id: project-auth-middleware-rewrite
type: project
trust: confirmed
status: active
created: 2026-03-05
author: human
subject: "Auth middleware rewrite is driven by legal compliance, not tech debt"
tags: [auth, compliance, middleware, legal]
---

The old auth middleware is being replaced because legal flagged it for storing
session tokens in a way that does not meet the new compliance requirements.
This is not a tech-debt cleanup — the scope and approach should favor
compliance over ergonomics.

**Why:** The compliance requirement came from a legal review of how session
tokens are persisted. The old approach stored full tokens in a manner that
violates the new policy. Timeline is driven by a regulatory deadline, not
an engineering preference.

**How to apply:** When making scope decisions on the auth rewrite, err toward
full compliance even when it adds friction. Backwards-compatibility shims and
gradual rollouts are acceptable only if they still meet the compliance
requirement by the deadline.
