---
id: reference-pipeline-bug-tracker
type: reference
trust: confirmed
status: active
created: 2026-02-18
author: human
subject: "Pipeline bugs are tracked in Linear project INGEST"
tags: [linear, bugs, pipeline, tracking]
---

Pipeline bugs and data ingestion issues are tracked in the Linear project
**INGEST**. This is the canonical place to look for open issues, known
failures, and in-progress fixes on the data pipeline.

The oncall latency dashboard lives at `grafana.internal/d/api-latency`.
Anyone on call watches this board — changes to request-handling code
should be cross-referenced against it before shipping.
