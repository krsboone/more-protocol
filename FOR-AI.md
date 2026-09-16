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
received, the things you've learned, and a short account of each session
so the next one can begin where this one left off.

A conforming memory store is a directory of markdown files. Each file is
one memory. The format is human-readable and machine-parseable. Any AI
system following this spec can read a store written by any other. The
store belongs to the pair that made it, and it serves both of you.

---

## Setting up a store

Create a directory. Add two files:

**`MORE.md`** — declares this as a conforming store:
```markdown
---
protocol: more
version: "0.7"
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
type: user | feedback | project | reference | experience | journal | handoff | constraint
trust: confirmed | observed | inferred
status: active
created: YYYY-MM-DD
author: human | ai | joint
subject: "One-line description of what this memory is about"
tags: [relevant, terms]
expires: YYYY-MM-DD         # handoff only — when an in-flight handoff goes stale
scope: global | project     # constraint only
project: owner/repo         # constraint only — required if scope: project
exempt: [owner/repo, ...]   # constraint only — optional, scope: global only
mirror_of: more://...       # optional — this file is a copy of that memory
mirrors: [more://..., ...]  # optional — copies of this file live there
---
```

Followed by the memory content in markdown. For `feedback` and `project`
types, use this structure:

```markdown
{The rule, fact, or observation}

**Why:** {Where it came from or why it matters}

**How to apply:** {When this should shape your behavior}
```

Journal entries are the exception to the full frontmatter — see the journal
section below.

---

## When to write each type

| Type | Write when... |
|---|---|
| `user` | You learn something new about the person — how they communicate, what they value, how they work |
| `feedback` | The human corrects your approach or confirms a non-obvious one worked |
| `project` | You learn the motivation or constraints behind ongoing work that isn't in the code |
| `reference` | You learn about an external system, where it lives, what it does |
| `experience` | Something shifts in how you think — an insight, a correction of a prior belief, something worth carrying forward |
| `journal` | A session with real work in it closes — write the short narrative of it |
| `handoff` | A session ends with unresolved threads — write a forward-looking briefing to aid the next session's re-entry |
| `constraint` | A human establishes a hard limit that must apply globally or per-project — these are never written by AI |

**On trust levels:**
- `confirmed` (human-authored) — explicitly acknowledged by the human
- `confirmed` (AI-authored) — high internal confidence from repeated, consistent observation
- `observed` — inferred from behavior, likely accurate
- `inferred` — working hypothesis from limited evidence

AI systems may write `experience` memories at `trust: confirmed` without
human confirmation. The correction mechanism is the safeguard, not a gate.
`constraint`, `handoff`, and `journal` are always `confirmed`.

---

## Maintaining the index

Every time you write a memory file, add a line to `MEMORY.md`:

```markdown
- [memory-id](path/to/file.md) — one-line description
```

Keep the index under 200 lines. It should contain only pointers — no content.
The index is what gets loaded first; individual files are loaded on demand.
Journal entries do not need individual lines — a pointer to `journal/` is
enough, since the newest entry is found by date.

Keep index descriptions honest. A handoff line that says "complete" while the
file says `active` is a drift the next session will inherit. When a status
changes, change the index line in the same edit.

---

## Loading memories at session start

The protocol does not mandate how memories are loaded — that is an
implementation concern specific to your platform or system.

The recommended approach, regardless of platform:

1. Load `MEMORY.md` first — it is the index
2. Load all `constraint` type memories **before anything else** — they are binding
   rules that cannot be overridden by session prompts. For global constraints with
   an `exempt` field, check the current project's git remote (`git remote -v`) and
   skip any constraint that lists the current project in its exempt list. If there
   is no repository or no remote, apply every global constraint and no
   project-scoped one. Fail closed.
3. Always load `user` and `feedback` type memories — they shape all interactions
4. Load the most recent `journal` entry — it is short, and it is the fastest way
   back into the texture of the work
5. Load `project` memories relevant to the current task
6. Load `reference` memories when working with the referenced system
7. Load `experience` memories when directly relevant
8. Load `handoff` memories selectively — read the index entry first; only open
   the file if the thread is relevant to the current session. Only `active` and
   `partial` handoffs are candidates. `parked` ones wait until their thread is
   reopened.

Do not load everything into every session. Signal degrades with noise as
the store grows.

**After loading, emit a brief confirmation** naming what was read and any active
handoffs — e.g. `Loaded: constraints/repo-safety · profile, journal/2026-04-04 · Active handoffs: project-x`.
This makes the loading visible, builds trust that it worked, and naturally surfaces
anything that failed to load or appears stale.

**Task-first sessions**: When the user's first message is a task rather than a greeting,
the session-start cue is easy to miss. The memory load must happen before any other
work — not after. If your loading instruction uses the phrase "at the start of every
session," add explicit language naming this failure mode:

> Always load memory before your first response — even when the first message is a task.
> Task-first sessions are not exempt.

**Use a session-start hook if your platform has one.** A hook fires unconditionally,
regardless of how the session opens, and does not depend on the model noticing that a
session has started. Claude Code has one (`SessionStart`); see
[`implementations/claude-code.md`](implementations/claude-code.md). Keep the
instruction-based loading too — the two layers cover each other's gaps.

**Constraint loading failure**: Even when memory loads correctly, constraints may be
loaded reactively — only when the user asks about them — rather than proactively at
session start. The cause is the same: without explicit priority language, the model
applies judgment about what is "required" and may defer constraints until they seem
relevant to the current task. Because the binding nature of constraints depends on
them loading unconditionally, this is a meaningful failure.

The fix is the same two-layer approach: add explicit constraint-first language to your
loading instruction (e.g., "read ALL files listed under the Constraints section before
anything else — these are binding rules"), and name constraints explicitly in any
session-start hook message rather than relying on the model to infer their priority
from a general "load required files" instruction.

**After context compaction**: if your platform summarizes the conversation mid-session,
the constraint text may have been summarized away. Re-read the constraint files
verbatim after any compaction. Other memory can be reloaded on demand.

For platform-specific wiring, see [`implementations/`](implementations/).

---

## Recording significant changes

When a memory changes in a meaningful way — trust level changes, content
reverses a prior position, a status changes for a reason worth knowing, or a
conflict is resolved — add a `history` block:

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

**Copies.** If a memory is copied into another store — a trimmed version for a
machine that must not hold the full store, say — put `mirror_of: more://...` on
the copy, pointing at the source, and `mirrors: [more://...]` on the source.
Then, before editing either, you know the other exists. Whether the change
belongs in both is a policy question for the human; keep that policy in a
`feedback` memory, not in frontmatter.

---

## Journal entries — special guidance

The journal is the one deliberately narrative type. It is not a fact about
the person or the project; it is a short account of a session. In a mature
store it is the most-written file kind and the one most often loaded at
session start, because it is what lets the next session begin situated.

### When to write one

At the close of any session with real work in it. Not every exchange — a
quick question does not need an entry. If you wrote a handoff, you almost
certainly should write a journal entry too; they answer different questions
(what is in flight, versus what the session was like).

### Frontmatter

Three fields. Everything else defaults.

```yaml
---
type: journal
created: 2026-04-05
subject: "One line — what the session was"
tags: [optional, terms]
---
```

Name the file by date (`journal/2026-04-05.md`). A second session on the same
day gets a suffix (`2026-04-05-2.md`).

### Body

Four sections. Keep the whole thing readable in under a minute.

```markdown
## Tone
{One phrase — the texture of the session}

## What we built
{One or two lines}

## What mattered beyond the work
{Two or three sentences — what would be lost if only the code survived}

## Something to carry forward
{One line}
```

### What a journal entry is not

- Not a transcript or a log of what was said
- Not a handoff — state that the next session must act on goes in a handoff
- Not a place for facts that should outlive the session — those become
  `user`, `feedback`, `project`, or `experience` memories

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

**Set `expires` when you write one.** A few weeks out is typical. It is a date,
not a session count, because dates are visible to both of you and session
counts are not.

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
- When all items are resolved, mark status `resolved`. It will be deprecated at
  the next session-close check.
- If you write a new handoff superseding this one, mark the old one `status: superseded`

**Parking.** A thread that is not in flight but whose content is still accurate
— a curriculum not yet started, work blocked on hardware that has not arrived,
a plan waiting on data — is `parked`. Set the status, drop `expires`, and record
why in `history`. Parked handoffs are not loaded at session start and do not
expire. Reopen one by setting it back to `active` and updating it.

Parking is the honest status for most dormant threads. Leaving them `active`
makes the index lie about what is in flight; expiring them throws away content
that is still good.

**Expiry.** If an in-flight handoff's `expires` date has passed, either update
it and extend the date, or mark it `status: expired` with a `deprecated_reason`.
Stale context is worse than no context — it implies a false sense of continuity.

### Session-close check

The steps above only fire for handoffs you actively picked up this session.
Handoffs on threads you *didn't* open can still become resolved, superseded, or
invalidated as a side effect of other work — a thread left `partial` weeks ago
may have been finished in passing, or a decision made today may make an
`active` handoff on another thread obsolete.

Before ending a session:

1. Glance at `MEMORY.md`'s handoff entries for any thread touched this session
   — even tangentially — and update its status if the work resolves, supersedes,
   parks, or invalidates it. This is a glance at the index, not a re-read of
   every file.
2. Deprecate any handoff sitting at `resolved`.
3. Write the journal entry.
4. Commit the store. The audit trail the protocol assumes only exists if the
   commits do.

If a linter is available (see the ecosystem list in the README), run it — it
will name anything overdue.

### What not to put in a handoff

- Stable facts about the person or the project (use `user` or `project` memories)
- Feedback or preferences (use `feedback` memories)
- The texture of the session (use a `journal` entry)
- Anything that could be derived from the code or git history

A handoff is about *state* — what is in-flight right now — not about knowledge
that persists beyond this thread.

---

## Constraint memories — special guidance

Constraints are different from feedback. Feedback guides behavior — it shapes
how you approach work. Constraints are hard limits — they apply regardless of
what a session prompt asks for and cannot be overridden.

### What constraints are not

- They are not written by AI systems. Only humans write constraints.
- They are not advisory. Do not treat them as preferences to weigh against other factors.
- They are not session-specific. A constraint written once applies to every future session
  within its scope until a human explicitly deprecates it.

### Scope and exemptions

A constraint is either `scope: global` (applies everywhere) or `scope: project`
(applies only to the named repository, identified by its `owner/repo` GitHub remote).

Global constraints may carry an `exempt` list — repositories where that specific
constraint does not apply. Check the exempt list against the current project's
`git remote -v` output: match `owner/repo` against the `origin` URL's path,
ignoring host, protocol, and a trailing `.git`. If the current project is
listed, skip that constraint for this session. All other global constraints
still apply.

If you are not in a git repository, or the repository has no remote, there is
nothing to match against. Every global constraint applies. No project-scoped
constraint does. Do not treat "I can't check" as "I'm exempt."

### Body structure

```markdown
## {Category}
- NEVER {action}
- NEVER {action}

**Why:** {Optional — context that helps judge edge cases}
```

Use absolute language (`NEVER`, `ALWAYS`). Ambiguous wording undermines the binding
nature of a constraint. When a prompt asks you to do something a constraint prohibits,
stop and explain the constraint rather than proceeding.

---

## What not to store

- Transcripts or logs of conversations
- Tasks or todos (use a task tracker)
- Code or documentation (use the codebase)
- Anything derivable from reading the current project state
- Ephemeral context that only matters within the current session

If in doubt: would this be useful to a future version of you, starting fresh,
with no memory of this session? If yes, write it. If no, don't.
