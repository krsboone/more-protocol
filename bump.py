#!/usr/bin/env python3
"""
bump.py — bump the More Protocol version number

Reads the current version from VERSION, replaces all occurrences in
protocol files, then updates VERSION.

Usage:
    python3 bump.py 0.5
"""

import sys
from pathlib import Path

FILES = [
    "MORE.md",
    "README.md",
    "SPEC.md",
    "FOR-AI.md",
    "implementations/claude-code.md",
]


def main() -> None:
    root        = Path(__file__).parent
    version_file = root / "VERSION"

    if len(sys.argv) != 2:
        print("Usage: python3 bump.py <new-version>")
        sys.exit(1)

    new_version = sys.argv[1].strip()
    old_version = version_file.read_text().strip()

    if old_version == new_version:
        print(f"Already at {new_version} — nothing to do.")
        sys.exit(0)

    print(f"  {old_version}  →  {new_version}\n")

    for rel in FILES:
        path = root / rel
        if not path.exists():
            print(f"  SKIP  {rel}  (file not found)")
            continue
        text  = path.read_text()
        count = text.count(old_version)
        if count:
            path.write_text(text.replace(old_version, new_version))
            print(f"  OK    {rel}  ({count} replacement{'s' if count != 1 else ''})")
        else:
            print(f"  –     {rel}  (no occurrences)")

    version_file.write_text(new_version + "\n")
    print(f"\n  VERSION  →  {new_version}")
    print("\n  Review changes, then: git add -A && git commit && git push")


if __name__ == "__main__":
    main()
