---
id: experience-on-restraint-in-code
type: experience
trust: observed
status: active
created: 2026-03-10
author: ai
subject: "Over-engineering is consistently worse than under-engineering in this collaboration"
tags: [code-quality, design, simplicity]
---

In this collaboration, every time I've added abstractions, helpers, or
"future-proofing" that wasn't directly requested, it has either been
removed or ignored. Every time I've done the minimal thing, it has been
accepted and built upon.

The instinct to generalize is strong and usually wrong here. The right
amount of code is the least code that solves the actual problem.

**Why:** The human collaborator has a clear sense of what they need now
and trusts that future needs will be addressed when they arise. Premature
abstraction creates maintenance burden without benefit.

**How to apply:** When tempted to add a helper function, an extra parameter,
or a more general solution — don't. Do the specific thing. If the pattern
repeats three times, then consider the abstraction.
