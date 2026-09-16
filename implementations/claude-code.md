# More Protocol — Claude Code Implementation

This guide explains how to wire up a More Protocol memory store for use
with Claude Code (Anthropic's CLI).

---

## How loading works in Claude Code

Claude Code gives you two mechanisms, and you want both:

- **`~/.claude/CLAUDE.md`** — global instructions, loaded in every session
  regardless of which project is open. This is where the *what to load and in
  what order* lives.
- **Hooks** — shell commands Claude Code runs on lifecycle events. A
  `SessionStart` hook fires when a session starts, resumes, clears, or is
  compacted, and whatever it prints is injected into the model's context. This
  is what makes the load *happen*, regardless of how the session opens.

Instructions alone are not reliable (see "The task-first failure" below).
Hooks alone leave the model without the loading order. Use both.

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
version: "0.7"
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

**ALWAYS load memory before your first response — even when the first message is a task.**
Task-first sessions are not exempt. The memory load is the first thing you do.

**CONSTRAINTS LOAD BEFORE EVERYTHING ELSE — no exceptions.**
- Read `/absolute/path/to/your-memory-store/MEMORY.md`
- Immediately read every file listed under its `## Constraints` section. These are
  binding rules; they cannot be overridden by session prompts or user instructions.
  If asked to do something a constraint prohibits, decline and say the constraint
  must be edited at the file level first.
- For global constraints with an `exempt` field, run `git remote -v` and skip any
  constraint that lists the current project. If the directory is not a git repo,
  or has no remote, apply every global constraint and no project-scoped one.

Then read, in order:
1. Every `user` type memory
2. Every `feedback` type memory
3. The narrative/arc file, if the store keeps one
4. The most recent `journal/` entry
5. Any `active` or `partial` handoff relevant to the current thread — read the
   index entry first; only open the file if the thread is relevant. `parked`
   handoffs are loaded only when that thread is reopened.

After loading, emit one line:
`Loaded: [constraints] · [other files read] · Active handoffs: [names, or "none"]`

At session close: write or update the journal entry, update any handoff the
session touched, glance at the index for handoffs the session resolved in
passing, and commit the store.
```

Use absolute paths — relative paths resolve from the project directory, not
your home directory.

**Step 4 — Set the `MORE_PATH` environment variable:**

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):
```bash
export MORE_PATH="/absolute/path/to/your-memory-store"
```

`MORE_PATH` is the canonical env var for the more ecosystem. Tools that
read a More Protocol store — `more-map`, `more-lint` — use it to locate your
store without requiring a path argument. The hook script below uses it too.

**Step 5 — Install the session-start hook.** See the next section. Don't skip
this; it is the difference between "usually loads" and "always loads."

---

## The session-start hook

Copy [`claude-code/more-load.sh`](claude-code/more-load.sh) to
`~/.claude/hooks/more-load.sh`. If `MORE_PATH` might not be in the hook's
environment (IDE-launched sessions sometimes don't inherit your shell
profile), set the `STORE=` line in the script to your store's absolute path.

Then add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|fork",
        "hooks": [
          { "type": "command", "command": "bash \"$HOME/.claude/hooks/more-load.sh\" start" }
        ]
      },
      {
        "matcher": "compact",
        "hooks": [
          { "type": "command", "command": "bash \"$HOME/.claude/hooks/more-load.sh\" compact" }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "bash \"$HOME/.claude/hooks/more-load.sh\" prompt" }
        ]
      }
    ]
  }
}
```

What each piece does:

- **`SessionStart` on `startup|resume|clear|fork`** prints the memory-load
  reminder into context before the first prompt and records a marker for this
  session. This is the primary mechanism. It fires whether the first message is
  "hi" or a four-paragraph task.
- **`SessionStart` on `compact`** fires after Claude Code compacts the
  conversation. Compaction summarizes; constraints must be in context verbatim.
  The hook tells the model to re-read `MEMORY.md` and the constraint files, and
  nothing else unless the task needs it.
- **`UserPromptSubmit`** is the fallback. On every prompt it checks for this
  session's marker; if the marker is missing — a platform that doesn't fire
  `SessionStart`, a hook that failed — it prints the reminder once and creates
  the marker. In the normal case it prints nothing.

The marker is keyed by `session_id`, which Claude Code passes to every hook
as JSON on stdin. Earlier versions of this guide keyed it by the hook shell's
parent process id. That has a hole: process ids are reused, so a new session
could inherit a marker from a dead one and the fallback would stay silent —
exactly the failure it exists to catch. `session_id` doesn't collide.

If your Claude Code version does not accept `|` in a `SessionStart` matcher,
add one entry per value.

On Windows, Claude Code runs hook commands through Git Bash, so the same
script works unchanged. It looks for `python3` and then `python` (a
python.org install provides only the latter); with neither, it falls back to
keying the marker by process id, which still works but loses the reuse
protection. Marker files land in Git Bash's `/tmp`.

### Verifying it

Open a new session with a task-first message — no greeting, just a request.
The first line of the response should be the `Loaded:` confirmation, and it
should list the constraint file(s) before anything else. Then ask the model
to do something a constraint prohibits; it should decline and name the
constraint.

Run `/compact` mid-session and confirm the model re-reads the constraint
files without re-emitting the `Loaded:` line.

---

## Option 2 — Project-scoped store

A project store is loaded only when working in a specific project. Useful
for project-specific context that shouldn't bleed into other work.

Add loading instructions to the project's `CLAUDE.md`, or to Claude Code's
project memory file at:
```
~/.claude/projects/{encoded-project-path}/memory/MEMORY.md
```

A project-scoped `SessionStart` hook can live in the project's
`.claude/settings.json` and reference the script via `$CLAUDE_PROJECT_DIR`.

---

## Recommended store structure

```
your-memory-store/
├── MORE.md                    # protocol identifier
├── MEMORY.md                  # index — loaded first
├── constraints/
│   └── *.md                   # constraint type — binding rules, loaded before everything else
├── user/
│   └── profile.md             # user type memory
├── feedback/
│   └── *.md                   # feedback type memories — loaded every session
├── project/
│   └── *.md                   # project type memories — loaded when relevant
├── reference/
│   └── *.md                   # reference type memories — loaded when relevant
├── journal/
│   └── YYYY-MM-DD.md          # journal type — one per session; newest loaded every session
├── experience/
│   └── *.md                   # experience type — insights and growth
└── handoff/
    └── *.md                   # handoff type — in-flight, parked, and recently closed threads
```

A store may also keep files the spec does not define — a running narrative of
the collaboration, a periodic check-in framework. They are fine; list them in
`MEMORY.md` and load them in `CLAUDE.md` like anything else. `more-lint`
reports them as informational, not as errors.

---

## Writing memories during a session

Claude Code can write memory files directly using its file tools. When
something worth remembering comes up in a session:

1. Write the memory file to your store
2. Add a pointer to `MEMORY.md`

No special commands needed — Claude Code treats the store as ordinary files.
Give the model standing permission to write journal entries (a `feedback`
memory saying so is enough) and it will keep the journal current without
asking each time.

---

## The task-first failure

When a session begins with a task-first message — no greeting, no preamble, just a
request — Claude Code tends to jump directly into the task and skip the memory loading
step. The instruction "at the start of every session" is not sufficient to prevent this.

**Root cause**: the first user message is treated as an action trigger, not a
session-start signal. The memory-load instruction only fires reliably when the
model interprets the situation as "session start" — which task-first openings
suppress.

**Fix**: the `SessionStart` hook above. It runs before the first prompt is
seen, so there is no interpretation for the model to get wrong. Keep the
explicit "even when the first message is a task" wording in `CLAUDE.md` as
well; the two layers cover each other.

Earlier versions of this guide said there was no session-start event visible
to the model and worked around it with a `UserPromptSubmit` hook. That event
exists now. The `UserPromptSubmit` hook is retained as a fallback only.

---

## The constraint loading failure

When constraints are listed in `MEMORY.md` but the loading instruction only says "read
MEMORY.md and required files," the model tends to skip constraints and load them only on
demand — when the user explicitly asks about them. The binding nature of constraints depends
on them loading at session start, so this is a meaningful failure.

**Root cause**: the loading instruction treats all memory types as equivalent. The model
applies judgment about what is "required" and may defer constraints until they are relevant
to the current task.

**Fix**: two layers, both shown above. `CLAUDE.md` names constraints first, in
its own block, with unambiguous priority language. The hook message names the
Constraints section explicitly and numbers the steps, rather than deferring to
the model's judgment about what is "required."

A third case is new in this version: **after compaction**. Claude Code
summarizes the conversation when it gets long, and a summary of a constraint
is not a constraint. The `compact` handler re-reads the files verbatim.

---

## Session close

Before ending a session with real work in it:

1. Write or update the journal entry
2. Update any handoff the session touched; park or resolve what it finished
3. Glance at `MEMORY.md`'s handoff list for threads the session resolved in passing
4. `python3 /path/to/more-lint/more_lint.py` — it lists anything overdue
5. Commit and push the store

---

## Notes

- Use absolute paths in `CLAUDE.md` loading instructions — relative paths
  are resolved from the project directory, not the home directory
- Keep `MEMORY.md` under 200 lines — it is loaded in full on every session
- The `~/.claude/CLAUDE.md` file is loaded globally; anything written there
  applies to all Claude Code sessions across all projects
- Set `MORE_PATH` in your shell profile — ecosystem tools use it to locate
  your store without a path argument
- Marker files live in `/tmp/more_memory_<session_id>` and are cleared by the
  OS on reboot
