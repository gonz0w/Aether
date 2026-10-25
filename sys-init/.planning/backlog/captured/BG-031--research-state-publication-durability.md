---
id: BG-031
title: Research state publication, ownership and durability
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem

Atomic name replacement, concurrent writer safety, and durable configuration are separate requirements.

## Scope and dependencies

Coordinate BG-027 package ownership/rollback, BG-023 state semantics, and BG-014 layout.

Source: [BG-026 handoff](../../../docs/research/BOUNDARY-HANDOFF.md). This is captured work; prototype code waits for the relevant research and recorded decision.

## Acceptance criteria

- Classify configuration, enablement, observed runtime state and counters as durable, reconstructible, or deliberately volatile; justify persistence.
- Compare a single writer, locking, and replacement protocols using POSIX/BSD/illumos/Linux documentation; record Aether filesystem gaps.
- Define trusted-directory/path handling, permission and symlink behavior, error outcomes and recovery from interrupted publication.
- Distinguish atomic visibility from durability and process-kill tests from power-loss tests; specify filesystem-specific experiments and unsupported cases.
- Choose follow-on scope for a commit helper only if the required guarantees need it; do not infer rollback of service side effects from file rollback.

## Result

Pending. Capture unresolved risks and further work before completion.
