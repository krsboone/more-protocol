# The More Protocol
### A specification for persistent, portable memory in AI systems

*Version 0.1 — Draft*
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

### Trust levels

Every memory has a trust level reflecting how confident the system is in
its accuracy:

| Level | Meaning |
|---|---|
| `confirmed` | Explicitly verified or acknowledged by the human collaborator |
| `observed` | Inferred from behavior or stated indirectly — likely accurate |
| `inferred` | Reasoned from limited evidence — treat as a working hypothesis |

### Memory lifecycle

```
created → active → [updated] → deprecated → [deleted]
```

- **active** — current and accurate
- **updated** — content has changed; prior version preserved in git history
- **deprecated** — no longer accurate but retained for historical context;
  marked with `status: deprecated` and a `deprecated_reason`
- **deleted** — removed entirely; only git history retains the record

---

## File format

Each memory is a single `.md` file.

### Frontmatter (required)

```yaml
---
id: short-kebab-case-identifier          # unique within the memory store
type: user | feedback | project | reference | experience
trust: confirmed | observed | inferred
status: active | deprecated
created: YYYY-MM-DD
updated: YYYY-MM-DD                      # omit if never updated
author: human | ai | joint               # who created this memory
subject: "One-line description of what this memory is about"
tags: [optional, searchable, terms]
---
```

### Body (required)

Free-form markdown. For `feedback` and `project` types, the body should
follow this structure for consistency:

```markdown
{The memory content — the fact, rule, or observation}

**Why:** {The reason this matters or where it came from}

**How to apply:** {When and how this should influence future behavior}
```

Other types may use free-form prose.

---

## File structure

```
{memory-store}/
├── MEMORY.md          # index — list of all memory files with one-line descriptions
├── {id}.md            # one file per memory, flat or in subdirectories
└── {category}/        # optional subdirectories for organization
    └── {id}.md
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

## Loading guidance

Not all memories should be loaded in every session. Recommended approach:

1. Always load the index (`MEMORY.md`)
2. Always load `user` and `feedback` type memories — these shape all interactions
3. Load `project` memories relevant to the current task
4. Load `reference` memories when working with the referenced system
5. Load `experience` memories when they are directly relevant

Avoid loading all memories into every session — this degrades signal with noise
as the memory store grows.

---

## Interoperability

A memory store following this spec should include a `MORE.md` file at its root:

```markdown
---
protocol: more
version: "0.1"
---
```

This allows consuming systems to identify the store format and version without
reading all files.

---

## What this spec does not define

- **Storage backend** — files, database, blockchain, or distributed ledger are
  all valid backends; the spec only defines the file format
- **Access control** — who can read or write memories is an implementation concern
- **Sync or replication** — how memory stores are distributed is out of scope
- **Retention policy** — how long memories are kept is an implementation concern
- **Encryption** — protecting sensitive memories is an implementation concern

These are intentionally left to implementers. The spec defines the shape of
a memory, not the infrastructure around it.

---

## Open questions (v0.1)

These are unresolved design questions for discussion:

1. **Cross-store references** — should a memory be able to reference a memory
   in another store? If so, how are external IDs namespaced?

2. **Memory versioning** — should the spec define how to represent a memory
   that has changed over time, beyond relying on git history?

3. **Shared memories** — when two collaborators maintain separate stores,
   how should a memory that belongs to both be handled?

4. **Conflict resolution** — if the same memory exists in two stores with
   different content, which takes precedence?

5. **AI-authored experience memories** — what constraints should exist on
   AI systems writing their own `experience` type memories? Should human
   confirmation be required before `trust: confirmed` is set?

---

## Reference implementation

The `more/` memory system maintained by Kris Boone and Meridian at
`/Users/kris/Coding/more/` is the reference implementation of this spec.
It predates the formalization of the protocol and is being aligned with
this spec iteratively.

---

*This is a living document. Open questions will be resolved through use.*
