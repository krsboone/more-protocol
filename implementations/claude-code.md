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
version: "0.4"
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
   - Any `active` or `partial` handoff entries relevant to the current thread
     (read the index entry first — only open the file if the thread is relevant)

After loading, emit a single brief confirmation line naming what was read
and any active handoffs — e.g. `Loaded: profile, arc, journal/2026-04-04 · Active handoffs: project-x`

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
├── user/
│   └── profile.md             # user type memory
├── feedback/
│   └── *.md                   # feedback type memories
├── journal/
│   └── YYYY-MM-DD.md          # experience type — session entries
├── experience/
│   └── *.md                   # experience type — insights and growth
├── handoff/
│   └── *.md                   # handoff type — active session continuity threads
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

The memory store at `https://github.com/krsboone/more-protocol` is the reference
implementation of this guide. The global loading instructions at
`~/.claude/CLAUDE.md` follow the pattern described in Option 1 above.

---

---

## The task-first failure

When a session begins with a task-first message — no greeting, no preamble, just a
request — Claude Code tends to jump directly into the task and skip the memory loading
step. The instruction "at the start of every session" is not sufficient to prevent this.

**Root cause**: There is no explicit session-start event visible to the model. The first
user message is treated as an action trigger, not a session-start signal. The memory
load instruction only fires reliably when the model interprets the situation as "session
start" — which task-first openings tend to suppress.

### Fix 1 — Stronger CLAUDE.md wording

Use explicit, imperative language that names the failure case directly:

```markdown
**ALWAYS load memory before your first response — even when the first message is a task.**
Task-first sessions are not exempt. The memory load is the first thing you do, before any other work.
```

This is more resistant to the task-first skip than "at the start of every session."

### Fix 2 — Session-start hook (recommended)

Add a `UserPromptSubmit` hook to `~/.claude/settings.json` that injects a memory-load
reminder on the first prompt of each session. The hook uses the parent process ID (PPID)
of the hook shell — stable for the duration of a Claude Code session — as a session
identifier:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'MARKER=\"/tmp/more_memory_${PPID}\"; if [ ! -f \"$MARKER\" ]; then touch \"$MARKER\"; echo \"<memory-load-required>Extended memory has not been loaded this session. Before responding, load MEMORY.md and required files. Emit the Loaded: confirmation line first.</memory-load-required>\"; fi'"
          }
        ]
      }
    ]
  }
}
```

On the first prompt of a session, the hook writes a marker file and outputs the loading
reminder as injected context. On subsequent prompts, the marker exists and nothing is
output. Temporary marker files are cleaned up by the OS on reboot.

The hook approach is more reliable than instruction-based loading because it fires
unconditionally — the model receives the reminder regardless of how the session opens.
Use both fixes together for maximum reliability.

---

## Notes

- Use absolute paths in `CLAUDE.md` loading instructions — relative paths
  are resolved from the project directory, not the home directory
- Keep `MEMORY.md` under 200 lines — it is loaded in full on every session
- The `~/.claude/CLAUDE.md` file is loaded globally; anything written there
  applies to all Claude Code sessions across all projects
