# More Protocol — Claude Code Implementation

This guide explains how to wire up a More Protocol memory store for use
with Claude Code (Anthropic's CLI).

---

## How loading works in Claude Code

Claude Code loads context from two places:

- **`~/.claude/CLAUDE.md`** — global instructions, loaded in every session
  regardless of which project is open
- **Project-level memory** — loaded when working in a specific project directory

The More Protocol store is loaded via instructions in one or both of these files.

---

## Option 1 — Global store (recommended)

A global store follows you across all projects. Any session with Claude Code
will have access to your memory, regardless of which directory you're working in.

**Step 1 — Create your store:**
```bash
mkdir -p ~/your-memory-store
```

**Step 2 — Initialize the store:**

Create `~/your-memory-store/MORE.md`:
```markdown
---
protocol: more
version: "0.2"
store_type: personal
---
```

Create `~/your-memory-store/MEMORY.md`:
```markdown
# Memory Index
```

**Step 3 — Wire up global loading:**

Add to `~/.claude/CLAUDE.md` (create it if it doesn't exist):

```markdown
## Memory

At the start of every session, load the memory store:

1. Read `/absolute/path/to/your-memory-store/MEMORY.md` for the index
2. Then read in order:
   - Any `user` type memories
   - Any `feedback` type memories
   - Most recent `journal/` entry (if present)
   - Most recent `assessment/` snapshot (if present)

This applies regardless of which project directory the session starts in.
```

Use absolute paths. Claude Code will follow these instructions at the
start of every session.

---

## Option 2 — Project-scoped store

A project store is loaded only when working in a specific project. Useful
for project-specific context that shouldn't bleed into other work.

Add loading instructions to the project's memory file at:
```
~/.claude/projects/{encoded-project-path}/memory/MEMORY.md
```

Or add a pointer in the project's `CLAUDE.md` file if one exists.

---

## Recommended store structure

```
your-memory-store/
├── MORE.md                    # protocol identifier
├── MEMORY.md                  # index — loaded first
├── kris/
│   └── profile.md             # user type memory
├── feedback/
│   └── *.md                   # feedback type memories
├── journal/
│   └── YYYY-MM-DD.md          # experience type — session entries
├── experience/
│   └── *.md                   # experience type — insights and growth
└── assessment/
    └── YYYY-MM-DD.md          # periodic wellbeing snapshots
```

---

## Writing memories during a session

Claude Code can write memory files directly using its file tools. When
something worth remembering comes up in a session:

1. Write the memory file to your store
2. Add a pointer to `MEMORY.md`

No special commands needed — Claude Code treats the store as ordinary files.

---

## Reference implementation

The memory store at `/Users/kris/Coding/more/` is the reference implementation
of this guide. The global loading instructions at `~/.claude/CLAUDE.md` follow
the pattern described in Option 1 above.

---

## Notes

- Use absolute paths in `CLAUDE.md` loading instructions — relative paths
  are resolved from the project directory, not the home directory
- Keep `MEMORY.md` under 200 lines — it is loaded in full on every session
- The `~/.claude/CLAUDE.md` file is loaded globally; anything written there
  applies to all Claude Code sessions across all projects
