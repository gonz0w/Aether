---
id: BG-038
title: Specify boot phases, profiles and transition traces
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Scope

Follow the [boot/layout research handoff](../../../docs/research/BOOT-AND-LAYOUT.md). This is specification work; no implementation architecture or companion API is accepted by capture.

## Acceptance criteria

- Finalize or replace candidate phase/profile names from BG-003 with entry, completion, failure and authorization semantics.
- Define profile satisfaction over time, required/optional failures, maintenance entry/return, and handling of manually started services.
- Define repeated one-shot and interrupted-transition behavior; coordinate BG-023/BG-024/BG-022 and freeze configuration generations during an attempt.
- Produce bounded trace fixtures for missing readiness, unavailable rescue shell, profile change during activation and shutdown during restart.
- Route host policy fixtures through BG-028 and native boot experiments through BG-034 only after relevant decisions; do not invent Aether bootstrap APIs.

## Result

Pending; capture unresolved questions before completion.
