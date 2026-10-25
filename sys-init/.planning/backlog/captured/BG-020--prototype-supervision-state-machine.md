---
id: BG-020
title: Prototype supervision state machine and crash-loop policy
status: captured
created: 2026-06-21
source_type: research-follow-on
source_path: docs/archive/2026-09-05-planning-reset/.planning/research/runtime-semantics/supervision-restart.md
source_title: Core service runtime semantics research
area: research
appetite_hint: medium
depends_on:
  - BG-006
external_dependencies: []
impact: high
impact_rationale: restart and failure-state semantics need executable examples before architecture selection
target_outcomes:
  - DO-01
  - DO-04
files: []
---

## Problem

The milestone research identifies restart classes, backoff/rate limiting, one-shot behavior, maintenance state, and operator clear/reset semantics as coupled design choices.

## Desired Outcome

A prototype or executable model comparing long-running, one-shot, manual, failed, degraded, maintenance, and crash-loop-limited state transitions with POSIX-oriented assumptions.

## Promotion Notes

Use this after the current milestone requirements are planned; keep it prototype/research-only until architecture is accepted.
