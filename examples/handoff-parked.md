---
id: handoff-search-relevance-tuning
type: handoff
trust: confirmed
status: parked
created: 2026-02-10
updated: 2026-03-30
author: ai
subject: "Search relevance tuning — parked until click-through data exists"
tags: [search, relevance, ranking]
history:
  - date: 2026-03-30
    author: ai
    change: "Marked parked"
    reason: "Blocked on click-through data from the new analytics pipeline (ETA next quarter). Everything here is still accurate; there is simply nothing to do until the data exists."
---

## Where we are

A relevance-tuning harness exists at `tools/relevance/` — it replays saved
queries against the search index and scores results with NDCG. Baseline
scores are recorded in `tools/relevance/baseline.json`. No tuning has been
attempted yet because there is no click-through data to tune against.

## Why it's parked

The analytics pipeline that will produce click-through data is a separate
project, not yet shipped. Tuning against synthetic relevance judgments was
tried and rejected — it optimized for the judgments, not for users.

A parked handoff does not expire. Its content is believed accurate; it is
simply not in flight. Reopen it by setting `status: active` and updating
this file.

## What to do when reopened

1. Confirm the pipeline is writing `click_events` with query and result position
2. Build the relevance judgments from a month of click data
3. Re-run the harness against the new judgments to get a real baseline
4. Only then start tuning

## What to watch for

- The baseline in `baseline.json` was captured against the index as of
  2026-02-10. If the index schema changes before this reopens, recapture it.

## Resolutions

- [resolved 2026-02-20] Synthetic judgments approach — tried, rejected
- [open] Real click-through baseline
- [open] Tuning pass
