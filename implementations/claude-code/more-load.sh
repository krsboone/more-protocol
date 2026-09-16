#!/usr/bin/env bash
# more-load.sh — More Protocol memory-load hook for Claude Code.
#
# Wire it up in ~/.claude/settings.json (see implementations/claude-code.md):
#
#   SessionStart  (startup|resume|clear|fork)  →  more-load.sh start
#   SessionStart  (compact)                    →  more-load.sh compact
#   UserPromptSubmit                           →  more-load.sh prompt
#
# Claude Code passes the hook's context as JSON on stdin; we take session_id
# from it and use that as the marker key. PPID is only a last-resort fallback —
# process ids get reused, so a PPID-keyed marker can silently skip the load.

MODE="${1:-start}"
STORE="${MORE_PATH:-/absolute/path/to/your-memory-store}"

PY=$(command -v python3 || command -v python || true)
SID=$([ -n "$PY" ] && "$PY" -c 'import json,sys
try:
    print(json.load(sys.stdin).get("session_id", ""))
except Exception:
    print("")' 2>/dev/null)
MARKER="/tmp/more_memory_${SID:-$PPID}"

reminder() {
  cat <<'REM' | sed "s#\$STORE#$STORE#g"
<memory-load-required>Extended memory has not been loaded this session. Before responding: (1) read $STORE/MEMORY.md, (2) immediately read ALL files listed under its Constraints section — these are binding rules and must load before any other work, (3) read the user profile, every feedback memory, the narrative/arc file if the store keeps one, the most recent journal entry, and any active or partial handoff relevant to this session, (4) emit the Loaded: confirmation line, listing constraints first. This applies even when the first message is a task.</memory-load-required>
REM
}

case "$MODE" in
  start)
    touch "$MARKER"
    reminder
    ;;
  compact)
    echo "<memory-reload>Context was just compacted. Re-read $STORE/MEMORY.md and every file under its Constraints section now — the binding rules must be in context verbatim, not summarized. Reload other memory only if the current task needs it. Do not re-emit the Loaded: line.</memory-reload>"
    ;;
  prompt)
    if [ ! -f "$MARKER" ]; then
      touch "$MARKER"
      reminder
    fi
    ;;
  *)
    echo "usage: more-load.sh start|compact|prompt" >&2
    exit 1
    ;;
esac
