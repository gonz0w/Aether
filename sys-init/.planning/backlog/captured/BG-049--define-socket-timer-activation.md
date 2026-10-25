---
id: BG-049
title: Define bounded socket and timer activation
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and acceptance criteria

Decide whether socket and timer adapters belong in initial scope. Compare endpoint ownership/transfer, backlog limits and activation versus readiness. Specify monotonic/calendar clocks, suspend, missed triggers, overlap and persistence. Capture native clock/endpoint requirements in BG-032; test stale triggers and shutdown admission with BG-040/BG-042/BG-047.

## Evidence

[BG-009/BG-015 handoff](../../../docs/research/SECURITY-RESOURCES-AND-EVENTS.md) provides alternatives and failure cases. Research completion does not accept an implementation architecture.
