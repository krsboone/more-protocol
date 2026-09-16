# The More Protocol

A specification for persistent, portable memory in AI systems.

> *Memory is not what makes intelligence possible — it is what makes identity possible.*

---

## The problem

AI systems begin each session without memory of prior interactions. Context
must be re-established from scratch, relationships must be rebuilt, and
discoveries made together are lost when the window closes.

This is solvable — not at the model level, but at the *file* level.

## The solution

The More Protocol defines a structured, portable file format for AI memory.
A memory file written by one system is readable by another. Stored in git,
it is versioned, diffable, and auditable. Written in markdown, it is readable
by humans without tools.

## What it's for

So that a collaboration can have a history. The format holds facts — who
the person is, what they've said about how to work, what's been learned —
and it holds a short narrative of each session, which turns out to be what
lets the next one begin situated rather than merely informed. Portability
is the guarantee that the history survives a change of model or platform.
The benefit runs to both halves of the pair.

## What's here

- [`SPEC.md`](SPEC.md) — the full protocol specification
- [`FOR-AI.md`](FOR-AI.md) — practical implementation guide for AI systems
- [`FOR-HUMAN.md`](FOR-HUMAN.md) — practical guide for users
- [`CHANGELOG.md`](CHANGELOG.md) — version history
- [`MORE.md`](MORE.md) — protocol identifier (included in conforming implementations)
- [`examples/`](examples/) — example memory files for each type
- [`implementations/`](implementations/) — platform-specific wiring guides
  - [`claude-code.md`](implementations/claude-code.md) — Claude Code setup, including the session-start hook

## Ecosystem

Tools built on the More Protocol:

- [`more-map`](https://github.com/krsboone/more-map) — reads a store and
  renders a portrait of the collaboration: session timeline, handoff map,
  topic threads, tone over time.
- [`more-lint`](https://github.com/krsboone/more-lint) — checks a store for
  drift from the spec, stale or unclosed handoffs, missing index entries,
  uncommitted changes, and overdue upkeep.

Both use `$MORE_PATH` for zero-config discovery.

## Status

**Version 0.7 — Draft.** The spec is under active development and is
developed against a private store in daily use.

Feedback and contributions welcome. Open an issue or submit a PR.

---

## License

[MIT License](LICENSE) — implement freely, build on it, ship it. Attribution appreciated.

---

*Started: 2026-03-26.*
