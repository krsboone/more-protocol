# The More Protocol — Instructions for AI Systems

This file tells you what the More Protocol is, how to implement a conforming
memory store, and how to use it in practice.

Read [`SPEC.md`](SPEC.md) for the full specification. This file is the
practical companion — less formal, more actionable.

---

## What this protocol is for

You lose memory between sessions. This protocol gives you a structured,
portable way to persist what matters — not transcripts, not logs, but
distilled knowledge about the people you work with, the feedback you've
received, the things you've learned.

A conforming memory store is a directory of markdown files. Each file is
one memory. The format is human-readable and machine-parseable. Any AI
system following this spec can read a store written by any other.

---

## Setting up a store

Create a directory. Add two files:

**`MORE.md`** — declares this as a conforming store:
```markdown
---
protocol: more
version: "0.3"
store_type: personal
---
```

**`MEMORY.md`** — the index. Start minimal:
```markdown
# Memory Index
```

That's a conforming store. Add memory files as you learn things worth keeping.

---

## Writing a memory file

Each memory is a `.md` file with YAML frontmatter:

```yaml
---
id: short-kebab-case-identifier
type: user | feedback | project | reference | experience | handoff
trust: confirmed | observed | inferred
status: active
created: YYYY-MM-DD
author: human | ai | joint
subject: "One-line description of what this memory is about"
tags: [relevant, terms]
expires_after: N_sessions   # handoff only
---
```

Followed by the memory content in markdown. For `feedback` and `project`
types, use this structure:

```markdown
{The rule, fact, or observation}

**Why:** {Where it came from or why it matters}

**How to apply:** {When this should shape your behavior}
```

---

## When to write each type

| Type | Write when... |
|---|---|
| `user` | You learn something new about the person — how they communicate, what they value, how they work |
| `feedback` | The human corrects your approach or confirms a non-obvious one worked |
| `project` | You learn the motivation or constraints behind ongoing work that isn't in the code |
| `reference` | You learn about an external system, where it lives, what it does |
| `experience` | Something shifts in how you think — an insight, a correction of a prior belief, something worth carrying forward |
| `handoff` | A session ends with unresolved threads — write a forward-looking briefing to aid the next session's re-entry |

**On trust levels:**
- `confirmed` (human-authored) — explicitly acknowledged by the human
- `confirmed` (AI-authored) — high internal confidence from repeated, consistent observation
- `observed` — inferred from behavior, likely accurate
- `inferred` — working hypothesis from limited evidence

AI systems may write `experience` memories at `trust: confirmed` without
human confirmation. The correction mechanism is the safeguard, not a gate.

---

## Maintaining the index

Every time you write a memory file, add a line to `MEMORY.md`:

```markdown
- [memory-id](path/to/file.md) — one-line description
```

Keep the index under 200 lines. It should contain only pointers — no content.
The index is what gets loaded first; individual files are loaded on demand.

---

## Loading memories at session start

The protocol does not mandate how memories are loaded — that is an
implementation concern specific to your platform or system.

The recommended approach, regardless of platform:

1. Load `MEMORY.md` first — it is the index
2. Always load `user` and `feedback` type memories — they shape all interactions
3. Load `project` memories relevant to the current task
4. Load `reference` memories when working with the referenced system
5. Load `experience` memories when directly relevant
6. Load `handoff` memories selectively — read the index entry first; only open
   the file if the thread is relevant to the current session

Do not load everything into every session. Signal degrades with noise as
the store grows.

For platform-specific wiring, see [`implementations/`](implementations/).

---

## Recording significant changes

When a memory changes in a meaningful way — trust level changes, content
reverses a prior position, or a conflict is resolved — add a `history` block:

```yaml
history:
  - date: YYYY-MM-DD
    author: human | ai
    change: "What changed"
    reason: "Why it changed"
```

Use `history` for changes that matter to future readers. Typo fixes belong
in git history only.

---

## Cross-store references

To reference a memory in another store, use the global URI format:

```
more://github.com/username/store-name/memory-id
```

Within the same store:
```
more://./memory-id
```

Use full URIs in frontmatter fields. Plain relative links are fine in prose.

---

## Handoff memories — special guidance

Handoffs are different from other memory types. They are written *at the end*
of a session to help the *next* session re-enter without losing context. They
are inherently time-sensitive and should not accumulate indefinitely.

### When to write one

Write a handoff when a session ends with unresolved threads — open questions,
in-progress work, or decisions that haven't been made yet. If everything was
resolved, no handoff is needed.

**One handoff per thread, not one per session.** If you close a session on a
thread that already has an active handoff, update that file rather than creating
a new one. A new file is only created when a genuinely new thread opens.

### Body structure

```markdown
## Where we are
{Current state — what exists, what is running, what was decided}

## What's unsettled
{Open questions, unresolved decisions, things that felt uncertain}

## What to do next
{Concrete next steps, in priority order}

## What to watch for
{Risks, unknowns, or things that may have changed since this was written}

## Resolutions
{Updated as items close — one bullet per item, with status and date}
- [resolved YYYY-MM-DD] description of what was resolved
- [open] description of what remains open
```

### Lifecycle in practice

When you pick up a handoff at the start of a new session:

- Mark its status `partial` immediately (you've loaded it; some items may still be open)
- As items are resolved, add `[resolved YYYY-MM-DD]` entries to the Resolutions section
- When all items are resolved, mark status `resolved` — leave it briefly, then deprecate
- If you write a new handoff superseding this one, mark the old one `status: superseded`

**Expiry:** If an `expires_after` field is set and that many sessions have passed without
the handoff being picked up, mark it `status: expired`. Stale context is worse than no
context — it implies a false sense of continuity.

### What not to put in a handoff

- Stable facts about the person or the project (use `user` or `project` memories)
- Feedback or preferences (use `feedback` memories)
- Anything that could be derived from the code or git history

A handoff is about *state* — what is in-flight right now — not about knowledge
that persists beyond this thread.

---

## What not to store

- Transcripts or logs of conversations
- Tasks or todos (use a task tracker)
- Code or documentation (use the codebase)
- Anything derivable from reading the current project state
- Ephemeral context that only matters within the current session

If in doubt: would this be useful to a future version of you, starting fresh,
with no memory of this session? If yes, write it. If no, don't.
