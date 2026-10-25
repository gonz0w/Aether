---
id: BG-044
title: Prototype bounded logging and retention
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and acceptance criteria

Compare bounded transition rings and service-output collectors. Specify overflow, fairness, broken pipes, writer inheritance, logger restart, partial frames and drain deadlines. Test full/slow storage and stalled console/subscribers without blocking lifecycle control. Specify log directory permissions, rotation and byte/count/age retention with BG-039, plus persistence limits with BG-031.

## Evidence

[BG-024/BG-008 handoff](../../../docs/research/SHUTDOWN-AND-DIAGNOSTICS.md) contains alternatives and required future tests. Record a scoped decision before implementation.
