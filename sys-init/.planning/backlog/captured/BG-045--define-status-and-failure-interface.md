---
id: BG-045
title: Define status and boot failure interface
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and acceptance criteria

Specify stable read-only status and explanation records, boot/instance/operation identity, unknown versus stopped, cleanup failures and diagnostic loss. Provide human and machine examples for timeout, dependency blockage, no shell/console/storage and failed final handoff. Bound and authorize readers, escape untrusted output, and avoid secret disclosure. Coordinate BG-016 operator UX and BG-023 runtime specification.

## Evidence

[BG-024/BG-008 handoff](../../../docs/research/SHUTDOWN-AND-DIAGNOSTICS.md) contains alternatives and required future tests. Record a scoped decision before implementation.
