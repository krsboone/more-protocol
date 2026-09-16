# The More Protocol — Instructions for Humans

This file is the companion to [`FOR-AI.md`](FOR-AI.md). That one tells your
AI how to read and write memory. This one is for you — the human half of
the pair — covering setup, upkeep, and how to work with an AI that uses a
memory store.

Read [`SPEC.md`](SPEC.md) if you want the full formal specification. This
file is the practical, day-to-day companion.

One thing worth knowing up front: the store is for you as much as for the
AI. Six months into the reference store, its human author said it had helped
him at least as much as it helped the AI it was built for. The journal and
the running narrative are a record of the work that neither of you would
otherwise have.

---

## Setting up a store

A store is just a directory of markdown files, in git. Minimal setup:

```
your-memory-store/
├── MORE.md      # protocol identifier
└── MEMORY.md    # index — starts as just "# Memory Index"
```

You can create these by hand, or simply ask your AI to set them up — either
way, that's the whole store. From there, files accumulate as memories are
written.

A typical store grows into something like:

```
your-memory-store/
├── MORE.md
├── MEMORY.md
├── constraints/   # binding rules — see "Writing constraints" below
├── user/          # what the AI knows about you
├── feedback/      # corrections and confirmations
├── project/       # context on ongoing work
├── reference/     # pointers to external systems
├── experience/    # the AI's own insights and growth
├── journal/       # one short entry per session — the most-read files in a mature store
└── handoff/       # open threads between sessions
```

None of this is mandatory structure — the spec only requires `MORE.md` and
`MEMORY.md` at the root. Subdirectories are for your own sanity once the
store has more than a handful of files.

For wiring a store into a specific tool (Claude Code, etc.), see
[`implementations/`](implementations/). That's where the platform-specific
setup — config files, environment variables, hooks — live.

---

## Memory types at a glance

| Type | Who writes it | When |
|---|---|---|
| `user` | AI (usually) | It learns something new about you — preferences, role, how you work |
| `feedback` | AI, after you correct or confirm an approach | "Don't do X" or "yes, that was right" |
| `project` | AI or you | Context, decisions, or constraints behind ongoing work that aren't in the code |
| `reference` | AI or you | A pointer to an external system and what it's for |
| `experience` | AI | Something shifts in how it understands or approaches things |
| `journal` | AI, at session close | A short narrative of the session — tone, what was built, what mattered |
| `handoff` | AI, at session close | Open threads that the next session should pick up |
| `constraint` | **You — only you** | A hard limit that must always apply |

If you're ever unsure what type something is, ask your AI — it knows the
spec. The one exception is `constraint`, which is covered on its own below.

---

## Talking to your AI about memory

Most day-to-day memory work happens through plain conversation. Some
patterns that work well:

- **"Remember that ___"** — writes a new memory of whatever type fits.
- **"What do you have on me / on this project?"** — surfaces what's stored,
  useful for spot-checking accuracy.
- **"That's changed — update your memory about ___"** — corrects or
  supersedes an existing memory rather than letting two versions drift.
- **"Write a handoff before we stop"** — useful when you're ending a session
  with loose ends and know you won't pick it back up immediately.
- **"Park that"** — a thread you're not going to touch for a while, but
  whose notes are still good. It drops out of the session-start load without
  being thrown away.
- **"Go through your memories about [topic] and flag anything that seems
  stale, wrong, or duplicated"** — a periodic accuracy pass. The protocol's
  trust model leans on correction as the safeguard, which only works if
  someone occasionally asks for it.
- **"Forget ___" / "that memory is no longer accurate"** — deprecates rather
  than silently overwrites, so the history stays auditable.

You don't need special commands — these are just things to say.

---

## Writing constraints yourself

Constraints are the one memory type AI systems never write. They're hard
limits — binding regardless of what a future session asks for — and the
protocol treats human authorship as part of what makes them binding.

A constraint file looks like:

```yaml
---
id: constraint-no-friday-deploys
type: constraint
trust: confirmed
status: active
created: 2026-06-12
author: human
subject: "No production deploys after Thursday EOD"
tags: [deploys, safety]
scope: project              # or: global
project: owner/repo         # required if scope is project
exempt: [owner/other-repo]  # optional, global only
---

## Deploys
- NEVER deploy to production after Thursday 5pm local time
- NEVER deploy on Fridays

**Why:** Weekend on-call coverage is thin — issues found Friday evening
go unaddressed until Monday.
```

To add one:

1. Write the file under `constraints/` in your store
2. Add a line for it under the `## Constraints` section in `MEMORY.md`
3. Use `NEVER` / `ALWAYS` language — constraints are not preferences, and
   soft wording undermines that

Your AI can help you word a constraint clearly, but the decision of *what*
to constrain, and the act of writing the file, should be yours.

Global constraints apply everywhere — including directories that are not
git repositories at all. A project-scoped constraint or an exemption only
kicks in when the AI can see a matching remote; when it can't, it falls back
to applying everything global. That's deliberate.

---

## Manually editing memory files

Everything is plain markdown with YAML frontmatter, so you can always edit
directly:

```yaml
---
id: short-kebab-case-identifier
type: user | feedback | project | reference | experience | journal | handoff | constraint
trust: confirmed | observed | inferred
status: active | deprecated   # handoff also: partial | parked | resolved | superseded | expired
created: YYYY-MM-DD
updated: YYYY-MM-DD            # omit if never updated
author: human | ai | joint
subject: "One-line description"
tags: [optional, terms]
---
```

**Worth hand-editing yourself:**
- Correcting something the AI got wrong about you or the project
- Deprecating a stale memory (`status: deprecated` + a `deprecated_reason`)
- Reorganizing files into subdirectories (remember to update the links in
  `MEMORY.md`)
- Adjusting a `trust` level once you've verified or disproven something

**Fine to leave to the AI:**
- Writing new memories during a session
- Routine index updates as new files are added
- Drafting `history` blocks when a memory changes meaningfully
- Journal entries — give it standing permission and it will keep them current

Git is the safety net either way — every edit is a diff, and nothing is
truly lost.

---

## Keeping the index healthy

`MEMORY.md` is loaded in full every session, so it should stay under about
200 lines and contain only pointers, not content. Over time:

- **Handoffs accumulate if no one closes them.** When a handoff's items are
  all resolved, it should move to `status: resolved` and then be
  deprecated. If a new handoff supersedes an old one on the same thread, the
  old one should be marked `status: superseded` — not left active alongside
  the new one.
- **Dormant is not the same as active.** A plan you haven't started, or work
  blocked on something outside the session, should be `parked`. The reference
  store ran for months with eighteen "active" handoffs of which none were in
  flight — every morning the index suggested more open obligation than
  existed. Parking fixes that without losing anything.
- **Index descriptions drift from file status.** A line that says "complete"
  next to a file that says `active` is the kind of thing nobody notices for
  months. Ask for both to be updated together.
- **Ask for a pruning pass occasionally.** "Look through MEMORY.md — is
  anything here stale, duplicated, or resolved-but-still-listed?" is a
  useful question to ask every so often, especially after a burst of
  activity.

This is mostly upkeep the AI can do once asked — it just needs to be asked.
Or checked for you: see the next section.

---

## Periodic review: more-map and more-lint

Two small tools read a store and tell you about it. Both use `$MORE_PATH`
for zero-config discovery, so if that's set (see
[`implementations/`](implementations/)), running either is a single command.

[`more-map`](https://github.com/krsboone/more-map) renders a portrait:
session timeline, handoff map, topic threads, tone over time. It's the
"zoom out" — a way to see the shape of the work and how time has actually
been spent, separate from any single session's view. Worth running every
few weeks, or whenever picking a project back up after time away.

[`more-lint`](https://github.com/krsboone/more-lint) tells you what needs
fixing: handoffs past their expiry or untouched for weeks, resolved ones
not yet deprecated, files that have drifted from the spec, memories missing
from the index, uncommitted changes, and — if you keep one — an assessment
that is overdue. Every rule it checks is a rule the AI already knows; the
tool just makes them fire. Run it at session close, or put it in a
pre-commit hook.

---

## Backup

A memory store is just a git repo, so treat it like one: commit when
memories change meaningfully, and push to a remote. Given that the content
is often personal — preferences, project context, sometimes constraints
that encode hard-won lessons — a private remote is the natural choice.

The git history doubles as the audit trail the protocol assumes exists:
`history` blocks reference past states, and deprecated memories are kept
rather than deleted. None of that is meaningful if the repo itself isn't
backed up.

Commit at session close, not "when it feels like enough has changed." The
reference store once went two months with its journal entries sitting
uncommitted on one disk. `more-lint` will tell you when that's happening.
