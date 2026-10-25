---
id: BG-047
title: Prototype bounded event broker and reconciliation
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and acceptance criteria

Define separate observation/policy/supervision authority, source epochs, snapshot/cursor semantics, overflow recovery and bounded requests. Test duplicate/reordered/lost events, reconnect enumeration, malicious payloads, storms and shutdown admission. Compare POSIX-host adapters before accepting native interfaces.

## Evidence

[BG-009/BG-015 handoff](../../../docs/research/SECURITY-RESOURCES-AND-EVENTS.md) provides alternatives and failure cases. Research completion does not accept an implementation architecture.
