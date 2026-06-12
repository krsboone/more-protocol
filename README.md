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

## What's here

- [`SPEC.md`](SPEC.md) — the full protocol specification
- [`FOR-AI.md`](FOR-AI.md) — practical implementation guide for AI systems
- [`FOR-HUMAN.md`](FOR-HUMAN.md) — practical guide for users
- [`MORE.md`](MORE.md) — protocol identifier (included in conforming implementations)
- [`examples/`](examples/) — example memory files for each type
- [`implementations/`](implementations/) — platform-specific wiring guides
  - [`claude-code.md`](implementations/claude-code.md) — Claude Code setup

## Ecosystem

Tools built on the More Protocol:

- [`more-map`](https://github.com/krsboone/more-map) — reads a More Protocol
  store and renders a portrait of the collaboration: session timeline, handoff
  map, topic threads, tone over time. Uses `$MORE_PATH` for zero-config discovery.

## Status

**Version 0.6 — Draft.** The spec is under active development.

Feedback and contributions welcome. Open an issue or submit a PR.

---

## License

[MIT License](LICENSE) — implement freely, build on it, ship it. Attribution appreciated.

---

*Started: 2026-03-26.*
