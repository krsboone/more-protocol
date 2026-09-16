#!/usr/bin/env python3
"""
bump.py — bump the More Protocol version number

Rewrites the *live* version references (frontmatter `version:` lines, the
"Version X — Draft" title/status lines, and "More Protocol vX" phrases)
across every markdown file in the repo, then updates VERSION and adds a
stub entry to CHANGELOG.md.

It deliberately does NOT do a blind search-and-replace:

  * CHANGELOG.md is never touched — version history lives there.
  * Any other occurrence of the old version string is left alone and
    listed at the end for human review. Historical prose ("v0.3 added
    the handoff type") must survive a bump; a live reference the
    patterns missed should be added to LIVE_PATTERNS, not hand-edited.

Why: the 0.4 → 0.5 bump once rewrote SPEC.md's own history paragraph,
turning "Version 0.4 documents the task-first failure" into "Version 0.5
documents ...". A hardcoded file list also let new files fall through.
Files are discovered by walking the tree; only the exclusions are listed.

Usage:
    python3 bump.py 0.7             # apply
    python3 bump.py 0.7 --dry-run   # report only
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT         = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "VERSION"
CHANGELOG    = ROOT / "CHANGELOG.md"

EXCLUDE_FILES = {"CHANGELOG.md"}
EXCLUDE_DIRS  = {".git", "node_modules", ".github"}

# Each pattern has exactly three groups: (prefix)(version)(suffix).
# {v} is replaced with the escaped old version before compiling.
LIVE_PATTERNS = [
    r'^(version: ")({v})(")\s*$',            # YAML frontmatter
    r'(\*Version )({v})( — Draft\*)',        # SPEC.md title line
    r'(\*\*Version )({v})( — Draft\.\*\*)',  # README.md status line
    r'(Protocol v)({v})(\b)',                # "More Protocol v0.6"
]


def markdown_files():
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if p.name in EXCLUDE_FILES:
            continue
        yield p


def bump_text(text, old, new):
    total = 0
    for pat in LIVE_PATTERNS:
        rx = re.compile(pat.format(v=re.escape(old)), re.M)
        text, n = rx.subn(lambda m: m.group(1) + new + m.group(3), text)
        total += n
    return text, total


def leftovers(text, old):
    rx = re.compile(r'(?<![\d.])' + re.escape(old) + r'(?![\d.])')
    return [(i, line.strip()) for i, line in enumerate(text.splitlines(), 1) if rx.search(line)]


def add_changelog_stub(new, dry):
    if not CHANGELOG.exists():
        print("  –     CHANGELOG.md not found; no stub added")
        return
    text = CHANGELOG.read_text()
    if re.search(rf'^## {re.escape(new)}\b', text, re.M):
        print(f"  –     CHANGELOG.md already has a {new} entry")
        return
    stub = f"## {new} — {date.today().isoformat()}\n\n- (describe the changes in this version)\n\n"
    m = re.search(r'^## ', text, re.M)
    text = text[:m.start()] + stub + text[m.start():] if m else text.rstrip() + "\n\n" + stub
    if not dry:
        CHANGELOG.write_text(text)
    print(f"  OK    CHANGELOG.md  (stub entry for {new} added — fill it in)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry  = "--dry-run" in sys.argv
    if len(args) != 1:
        print("Usage: python3 bump.py <new-version> [--dry-run]")
        sys.exit(1)
    new = args[0].strip()
    old = VERSION_FILE.read_text().strip()
    if old == new:
        print(f"Already at {new} — nothing to do.")
        sys.exit(0)

    print(f"  {old}  →  {new}{'   (dry run)' if dry else ''}\n")
    review = []
    for path in markdown_files():
        rel = path.relative_to(ROOT)
        text = path.read_text()
        bumped, n = bump_text(text, old, new)
        left = leftovers(bumped, old)
        if n:
            if not dry:
                path.write_text(bumped)
            print(f"  OK    {rel}  ({n} live reference{'s' if n != 1 else ''})")
        else:
            print(f"  –     {rel}")
        review += [(rel, i, line) for i, line in left]

    add_changelog_stub(new, dry)
    if not dry:
        VERSION_FILE.write_text(new + "\n")
    print(f"\n  VERSION  →  {new}")

    if review:
        print(f"\n  Remaining '{old}' references — left untouched, review by hand:")
        for rel, i, line in review:
            print(f"    {rel}:{i}: {line}")
        print("  Historical mention → leave it. Live reference → add a LIVE_PATTERNS entry and re-run.")
    if not dry:
        print("\n  Next: fill in the CHANGELOG entry, review the diff, then commit.")


if __name__ == "__main__":
    main()
