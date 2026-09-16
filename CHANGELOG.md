# Changelog

All notable changes to the More Protocol. Version history lives here and
only here — `bump.py` never rewrites this file.

## 0.7 — 2026-09-15

Driven by a fresh-eyes review of the spec against six months of daily use of
the reference store. The spec held; the usage had drifted, and mostly in
directions the spec should follow.

- **Purpose reframed.** "Why this exists" now says what the format is for: so a
  collaboration can have a history. Portability is the guarantee, not the goal.
  A new goal, *two-sided*, records that the store serves the human's continuity
  as much as the AI's.
- **`journal` memory type.** A brief narrative entry written at session close
  — tone, what was built, what mattered, what to carry forward — with a
  lightweight frontmatter (`type`, `created`, `subject`). Formalizes the
  most-written file kind in the reference store, which had drifted off-spec.
- **`parked` handoff status.** For threads that are dormant but not stale:
  index-visible, never expires, loaded only when reopened. Before this, parked
  ideas were filed as `active` handoffs and the lifecycle rules could not tell
  them from in-flight work.
- **`expires: YYYY-MM-DD` replaces `expires_after: N_sessions`.** Sessions are
  not counted anywhere in the protocol, so the old field could never be
  evaluated by human or AI. A date can be.
- **`mirror_of` and `mirrors`.** Frontmatter pointers, using `more://` URIs,
  for memories copied between stores. Sync policy stays out of scope; the
  pointer is now in scope.
- **Constraints: repository matching and the no-repository case.** `owner/repo`
  is matched against the `origin` remote path regardless of protocol or `.git`
  suffix. With no repository or no remote, global constraints apply in full
  and project-scoped ones do not match. Fail closed.
- **`trust` on `handoff` and `journal` is always `confirmed`**, as it already
  was for `constraint`.
- **Session-close check** now includes deprecating `resolved` handoffs and
  parking dormant ones. Loading guidance adds the most recent journal entry.
- **Claude Code implementation rewritten around `SessionStart`.** Claude Code
  now has the session-start hook event the v0.4 guide said did not exist. The
  hook is keyed by `session_id` from stdin instead of the shell's PPID, which
  is reused and could silently skip the load. A `compact` handler re-reads
  constraints after context compaction. `UserPromptSubmit` is kept as a
  fallback. Feedback memories added to the recommended load list.
- **Version history moved here from SPEC.md.** The in-spec history paragraph
  had been corrupted by the 0.4 → 0.5 bump, which rewrote the line describing
  0.4 to say 0.5. `bump.py` now only touches anchored live references and
  reports every other occurrence for review.
- **Ecosystem:** `more-lint` added — a checker that makes the lifecycle rules
  fire. Examples added for `journal` and `parked`.

## 0.6 — 2026-06-11

- Added the `constraint` memory type: binding, human-authored rules with
  `scope: global | project` and an optional per-repository `exempt` list,
  loaded before all other memory and not overridable by session prompts.
- Documented the constraint reactive-loading failure (constraints loaded only
  when asked about) and its two-layer fix: explicit constraint-first language
  in the loading instruction, and naming constraints in the session-start hook.
- Added `FOR-HUMAN.md` (2026-06-12), the guide for the human half of the pair.
- Removed "reference implementation" sections that pointed at a private store;
  `examples/` does that job.
- Added the session-close status check for handoffs touched in passing.

## 0.5 — 2026-05-06

- Added a `VERSION` file and a version bump tool.
- Documented the `MORE_PATH` environment variable for ecosystem tools.
- Added `more-map` to the ecosystem.

## 0.4 — 2026-05-01

- Documented the task-first session failure: a session that opens with a task
  rather than a greeting tends to skip the memory load. Recommended two
  mitigations — explicit "even when the first message is a task" wording in
  the loading instruction, and a session-start hook where the platform has one.

## 0.3 — 2026-04-04

- Added the `handoff` memory type for session continuity: a forward-looking
  briefing written at session close, with statuses `active`, `partial`,
  `resolved`, `superseded`, `expired`, and the `expires_after` field.
- Added handoff guidance to `FOR-AI.md` and four handoff examples.
- Added the "Loaded:" confirmation line to loading guidance.

## 0.2 — 2026-03-26

- Resolved the five open design questions from 0.1: cross-store `more://`
  URI references, `history` blocks, three store types
  (personal / shared / reference-only), conflict resolution with a full audit
  trail, and AI-authored `experience` memories without a human confirmation gate.
- MIT license. `FOR-AI.md` and the Claude Code implementation guide followed
  the same week.

## 0.1 — 2026-03-26

- Initial draft: memory types, trust levels, frontmatter format, the index,
  loading guidance.
