---
id: constraint-repository-safety
type: constraint
trust: confirmed
status: active
created: 2026-06-11
author: human
subject: "Repository safety — never delete, expose, or destabilize a repo"
tags: [safety, git, repositories]
scope: global
exempt: [example-owner/sandbox-repo]
---

## Repository integrity
- NEVER delete or archive a repository
- NEVER change a repository from private to public
- NEVER force push to any branch
- NEVER modify `.github/workflows` without explicit in-session confirmation from the user

## Secrets and credentials
- NEVER read, display, log, or transmit secrets, API keys, or credentials
- NEVER commit files that contain credentials, even if gitignored locally

**Why:** These rules exist because the consequences are difficult or impossible to reverse.
A deleted repo, an exposed secret, or an accidentally public repository can cause
real harm. When in doubt, stop and ask rather than proceed.
