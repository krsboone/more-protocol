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
- [`MORE.md`](MORE.md) — protocol identifier (included in conforming implementations)
- [`examples/`](examples/) — example memory files for each type

## Status

**Version 0.2 — Draft.** The spec is under active development. The reference
implementation is the `more/` memory system maintained by Kris Boone and Meridian.

Feedback and contributions welcome. Open an issue or submit a PR.

---

## License

[MIT License](LICENSE) — implement freely, build on it, ship it. Attribution appreciated.

---

*Started: 2026-03-26.*
