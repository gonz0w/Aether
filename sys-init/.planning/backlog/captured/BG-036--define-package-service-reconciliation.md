---
id: BG-036
title: Define package and service publication/reconciliation protocol
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and scope

PS-09/PS-10 need an explicit protocol before package publication and lifecycle actions can be safely coordinated.

Source: [BG-027 proposed package/service boundary](../../../docs/research/PACKAGE-SERVICE-CONTRACT.md). No companion implementation or API acceptance is implied.

## Acceptance criteria

- Assign authoritative records and coordinator ownership; specify operation identities, generation preconditions, locks or single-writer assumptions, and recovery checkpoints.
- Define failures between package publication, definition selection, and runtime dispatch; recover without blindly replaying side effects or claiming exactly-once execution.
- Define old artifact retention/release, blocked live removal and restart-needed state; include libraries/helpers, not only executable pages.
- Distinguish configuration rollback, runtime compensation and application data migration; coordinate BG-031 storage and BG-032 instance observation.
- Define interruption/unknown-reply fixtures and minimal conservative unsupported outcomes; label mock results versus real cross-project integration.

## Result

Pending.
