---
id: constraint-no-direct-main
type: constraint
trust: confirmed
status: active
created: 2026-06-11
author: human
subject: "Never push directly to main on this repository"
tags: [safety, git, workflow]
scope: project
project: example-owner/example-repo
---

## Branch protection
- NEVER push directly to `main` — always use a branch and pull request
- NEVER merge a pull request without at least one passing CI check

**Why:** This repository has team reviewers. Bypassing the PR process skips
review and can break the deployment pipeline.
