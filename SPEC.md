# The More Protocol
### A specification for persistent, portable memory in AI systems

*Version 0.6 — Draft*
*Authors: Kris Boone, Meridian*

---

## Why this exists

Current AI systems begin each session without memory of prior interactions.
Context must be re-established from scratch, relationships must be rebuilt,
and discoveries made together are lost when the window closes.

This is a solvable problem — not at the model level, but at the *file* level.
If memory is stored in a structured, portable format that any AI system can
read and write, continuity becomes possible regardless of which system,
session, or platform is involved.

The More Protocol defines that format.

---

## Goals

- **Human-readable** — memory files are plain markdown, readable without tools
- **Machine-parseable** — structured frontmatter enables reliable programmatic access
- **Portable** — a memory file written by one AI system is readable by another
- **Trustworthy** — provenance and confidence are first-class fields, not afterthoughts
- **Minimal** — the spec defines what is necessary and no more; implementations
  may extend it but must not require extensions for basic interoperability
- **Git-friendly** — file-per-memory design enables version history, diffs, and
  collaborative review via standard tools

---

## Core concepts

### What is a memory?

A memory is a discrete, named piece of information that:
- Was learned through experience (interaction, observation, or reasoning)
- Is worth preserving across sessions
- Can stand alone as meaningful without full conversation context

A memory is *not*:
- A transcript or log of events
- A task or todo item (use a task tracker)
- Code or documentation (use the codebase)
- Something derivable from reading the current project state

### Memory types

| Type | Contains | When to write |
|---|---|---|
| `user` | Information about the human collaborator — role, preferences, how they work | When something new is learned about the person |
| `feedback` | Guidance from the human about how to approach work | When the human corrects or confirms a non-obvious approach |
| `project` | Context about ongoing work, goals, decisions, constraints | When motivation or direction is established that isn't in the code |
| `reference` | Pointers to external resources and their purpose | When an external system is learned about |
| `experience` | What the AI has learned or how it has grown through interactions | When something shifts in understanding or perspective |
| `handoff` | Forward-looking briefing written at session close to aid re-entry | At the end of any session with unresolved threads or in-progress work |
| `constraint` | Binding rules that must never be violated regardless of session prompts | When a hard limit is established that should apply globally or per-project |

### Trust levels

Every memory has a trust level reflecting confidence in its accuracy.
The meaning of `confirmed` is interpreted relative to the author type:

| Level | Meaning (human-authored) | Meaning (AI-authored) |
|---|---|---|
| `confirmed` | Explicitly verified or acknowledged by the human | High internal confidence based on repeated, consistent observation |
| `observed` | Inferred from behavior or stated indirectly — likely accurate | Inferred from behavior or stated indirectly — likely accurate |
| `inferred` | Reasoned from limited evidence — treat as a working hypothesis | Reasoned from limited evidence — treat as a working hypothesis |

AI systems may set `trust: confirmed` on `experience` type memories without
requiring human confirmation. The judgment that something is worth remembering
is itself a meaningful signal. Humans retain full ability to review, deprecate,
or correct any memory after the fact — the correction mechanism is the safeguard,
not a confirmation gate.

### Store types

| Type | Description |
|---|---|
| `personal` | Owned by one human-AI pair. Private by default. |
| `shared` | Multiple authorized contributors. Used for memories that belong to a relationship or collaboration rather than one party. |
| `reference-only` | Readable and linkable by others, but not writable by them. |

Memories that belong to a relationship should live in a `shared` store rather
than being duplicated across personal stores. Duplication causes drift;
cross-store references (see below) are the preferred pattern when a shared
store is not yet established.

### Memory lifecycle

```
created → active → [updated] → deprecated → [deleted]
```

- **active** — current and accurate
- **updated** — content has changed; prior version preserved in git history
  and optionally in the `history` frontmatter block
- **deprecated** — no longer accurate but retained for historical context;
  marked with `status: deprecated` and a `deprecated_reason`
- **deleted** — removed entirely; only git history retains the record

For `handoff` type memories, additional statuses apply:

- **active** — written at session close, not yet picked up by a new session
- **partial** — loaded and partially addressed; some items remain open
- **resolved** — all items closed; retained briefly then deprecated
- **superseded** — a newer handoff on the same thread has replaced this one
- **expired** — too much time has passed for this context to remain meaningful;
  deprecated without resolution

---

## File format

Each memory is a single `.md` file.

### Frontmatter (required)

```yaml
---
id: short-kebab-case-identifier          # unique within the memory store
type: user | feedback | project | reference | experience | handoff | constraint
trust: confirmed | observed | inferred
status: active | deprecated              # handoff adds: partial | resolved | superseded | expired
created: YYYY-MM-DD
updated: YYYY-MM-DD                      # omit if never updated
author: human | ai | joint               # who created this memory
subject: "One-line description of what this memory is about"
tags: [optional, searchable, terms]
deprecated_reason: "Why this was deprecated"  # required if status: deprecated
expires_after: N_sessions                # handoff only — suggested staleness threshold
---
```

### Type-specific fields

Some memory types require additional frontmatter fields beyond the core set.

**`constraint` type:**

```yaml
scope: global | project          # required — global applies everywhere; project applies to one repo
project: owner/repo              # required if scope: project — GitHub repo in owner/repo format
exempt: [owner/repo, ...]        # optional, scope: global only — repos where this constraint is skipped
```

- `scope: global` — the constraint applies to all sessions across all projects
- `scope: project` — the constraint applies only when working in the named repository,
  identified by its GitHub remote in `owner/repo` format (verified via `git remote -v`)
- `exempt` — a list of `owner/repo` strings identifying repositories where a global
  constraint should not apply. The exemption travels with the constraint — update one
  place, the change takes effect everywhere. Do not use numeric indices; always reference
  repositories by name.

The `trust` field on constraints is always `confirmed`. Constraints are authored by humans
and are not subject to the inferred/observed/confirmed gradient that applies to other types.

### History block (optional)

For significant transitions — changes to `trust`, `status`, or content that
reverses a prior position — record the change in a `history` block:

```yaml
history:
  - date: YYYY-MM-DD
    author: human | ai
    change: "What changed"
    reason: "Why it changed"
    superseded: "more://{store}/{id}"    # if this resolved a conflict
```

Use `history` for changes that matter to future readers. Do not record
typo fixes or minor edits — those belong in git history only.

### Body (required)

Free-form markdown. For `feedback` and `project` types, the body should
follow this structure for consistency:

```markdown
{The memory content — the fact, rule, or observation}

**Why:** {The reason this matters or where it came from}

**How to apply:** {When and how this should influence future behavior}
```

Other types may use free-form prose.

For `constraint` type memories, the body should be a concise, unambiguous list of rules:

```markdown
## {Category}
- NEVER {action}
- NEVER {action}

## {Category}
- NEVER {action}

**Why:** {Optional — context that helps judge edge cases}
```

Use absolute language (`NEVER`, `ALWAYS`) rather than soft language (`avoid`, `prefer`).
Constraints are binding; ambiguous wording undermines that.
A `**Why:**` line is optional but recommended — it helps the AI judge edge cases
rather than applying rules blindly.

For `handoff` type memories, the body should follow this structure:

```markdown
## Where we are
{Current state of the thread — what exists, what is running, what was decided}

## What's unsettled
{Open questions, unresolved decisions, things that felt uncertain}

## What to do next
{Concrete next steps, in priority order}

## What to watch for
{Risks, unknowns, or things that may have changed since this was written}

## Resolutions
{Updated as items close — one bullet per item with status and date}
- [resolved 2026-04-04] fee gate approach — switched to gate rather than TP inflation
- [open] SL distance calibration for BTC/ETH
```

The `resolutions` section is the living record of what has and hasn't been addressed.
When all items are resolved, mark the handoff `status: resolved`.
When a new handoff on the same thread is written, mark the old one `status: superseded`.

---

## File structure

```
{memory-store}/
├── MORE.md            # protocol identifier — required for conforming stores
├── MEMORY.md          # index — list of all memory files with one-line descriptions
├── {id}.md            # one file per memory, flat or in subdirectories
└── {category}/        # optional subdirectories for organization
    └── {id}.md
```

### MORE.md (protocol identifier)

Every conforming store must include a `MORE.md` file at its root:

```markdown
---
protocol: more
version: "0.6"
store_type: personal | shared | reference-only
---
```

### MEMORY.md (the index)

The index is the entry point. It must be kept under a reasonable size
(recommended: 200 lines) and contain only pointers, not content.

```markdown
# Memory Index

## {Category}
- [{id}]({path}) — {one-line description}
```

The index is loaded first. Individual memory files are loaded on demand
based on relevance to the current task.

---

## Cross-store references

Memory references use a global URI format:

```
more://{store-identifier}/{memory-id}
```

Examples:
```
more://github.com/krsboone/shared-store/feedback-no-mock-database
more://github.com/krsboone/personal/user-collaborator-profile
```

Local references within the same store may abbreviate to:
```
more://./memory-id
```

The full URI is required in frontmatter fields (including `history.superseded`).
Prose bodies may use plain relative markdown links for readability.

The URI format is designed to accommodate future extensions — versioning,
trust anchors, alternate backends — without breaking existing references:
```
more://github.com/krsboone/store@v1/memory-id          # versioned
```

---

## Conflict resolution

Conflicts arise in two forms:

**Technical conflicts** — concurrent or near-concurrent writes to the same
memory. Implementations should perform a read-before-write check and surface
conflicts for human review rather than resolving them automatically. Never
silently overwrite.

**Semantic conflicts** — two valid but different versions of the same truth,
typically arising when personal stores merge into a shared store.

When a conflict is resolved:

1. The winning memory records the event in its `history` block, including
   a `superseded` reference to the losing memory
2. The losing memory is **not deleted** — it is marked `status: deprecated`
   with a `deprecated_reason` pointing to the winner
3. No conflict resolution occurs without a human-readable record of what
   happened and why

Trust and authorship serve as tiebreakers: `author: human, trust: confirmed`
takes precedence over `author: ai, trust: inferred`. This does not resolve
all cases — human judgment is required for conflicts between memories of
equal standing.

---

## Loading guidance

Not all memories should be loaded in every session. Recommended approach:

1. Always load the index (`MEMORY.md`)
2. Always load `constraint` type memories **first** — these are binding rules that
   take precedence over all other instructions, including session prompts.
   When loading global constraints with an `exempt` field, check the current
   project's git remote against the exempt list and skip any constraint for which
   the current project is listed.
3. Always load `user` and `feedback` type memories — these shape all interactions
4. Load `project` memories relevant to the current task
5. Load `reference` memories when working with the referenced system
6. Load `experience` memories when they are directly relevant
7. Load `handoff` memories selectively — see below

Avoid loading all memories into every session — this degrades signal with
noise as the memory store grows.

### Handoff loading guidance

The index entry for each handoff should be descriptive enough to judge
relevance without opening the file. Use the MEMORY.md entry to assess
whether a handoff belongs to the current session's thread before loading it.

**Conventions to keep handoff count manageable:**

- **One handoff per thread, not one per session.** When a session closes with
  unfinished business on an existing thread, update the existing handoff rather
  than creating a new one. A new file is only created when a genuinely new
  thread opens.
- **Supersede, don't accumulate.** When a thread's handoff is rewritten,
  mark the prior version `status: superseded` immediately.
- **Expire stale handoffs.** If a handoff has not been picked up within
  the `expires_after` window, mark it `status: expired` and deprecate it.
  Stale context is worse than no context.
- **Review in passing at session close.** Status transitions above are not
  limited to the handoff(s) picked up this session. Before ending a session,
  check whether any other `active`/`partial` handoff for a thread touched this
  session has been resolved, superseded, or invalidated, and update it.
  Status should not advance only when a thread is deliberately reopened.

In practice this means rarely more than 3–5 active handoffs exist at once.
The index alone is sufficient to decide which to load.

---

## What this spec does not define

- **Storage backend** — files, database, blockchain, or distributed ledger are
  all valid backends; the spec only defines the file format
- **Access control** — who can read or write memories is an implementation concern
- **Sync or replication** — how memory stores are distributed is out of scope
- **Retention policy** — how long memories are kept is an implementation concern
- **Encryption** — protecting sensitive memories is an implementation concern
- **Concurrent write locking** — implementations should detect and surface
  conflicts; the mechanism for doing so is not mandated

These are intentionally left to implementers. The spec defines the shape of
a memory, not the infrastructure around it.

---

*This is a living document. Version 0.2 reflects resolutions to all open
questions from v0.1, developed through discussion between Kris Boone and
Meridian on 2026-03-26. Version 0.3 adds the `handoff` memory type,
addressing session discontinuity — developed 2026-04-04. Version 0.5
documents the task-first session failure mode and recommended mitigations
(explicit CLAUDE.md wording and session-start hooks) — developed 2026-05-01.
Version 0.6 adds the `constraint` memory type — binding rules that apply
globally or per-project, with optional per-repo exemptions. Constraints are
loaded before all other memory types and cannot be overridden by session
prompts — developed 2026-06-11.*
