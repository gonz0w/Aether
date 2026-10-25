---
id: BG-042
title: Define dependency evidence and invalidation
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and acceptance criteria

Define how edges consume started, completed, notified-ready, probed-ready and activation-available evidence. Specify one-shot evidence lifetime by configuration revision, admission rechecks and provider-loss behavior for new versus running dependents. Coordinate BG-021/BG-023/BG-035; include negative validation examples preventing silent strength downgrades.

## Evidence

[BG-007/BG-022 readiness handoff](../../../docs/research/READINESS-AND-HEALTH.md) supplies alternatives and the required scenario matrix. Research completion does not select a production architecture.

Bounded implementation input, 2026-09-06: [decision 0025](../../../docs/decisions/0025-native-dependency-loss.md)
demonstrates R-07 provider loss with an admitted dependent kept running, new
admission blocked and explicit later cleanup. This does not complete evidence
strength comparison, one-shot lifetime, arbitrary graphs or queued consumer
recovery. Preserve those acceptance criteria and use the exact retained target
profile when citing this input.
