---
id: BG-029
title: Define POSIX shell hook and repair conventions
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem

Readable hooks need a concrete argument, environment, failure, and authority contract.

## Scope and dependencies

Use BG-026 findings; coordinate BG-016 operator UX, BG-022 readiness, and BG-027 metadata.

Source: [BG-026 handoff](../../../docs/research/BOUNDARY-HANDOFF.md). This is captured work; prototype code waits for the relevant research and recorded decision.

## Acceptance criteria

- Define allowed hook inputs and argument encoding, environment/PATH/locale, cwd, umask, and inherited descriptors.
- Compare quoted argv forwarding with command-string interpretation; data must not require eval. Define unsupported names, bytes, sizes, and environment forms.
- Specify exit meanings, timeout/cancellation, and when retries are safe; distinguish hook completion from service readiness.
- Design fixtures for spaces, empty values, globs, newlines, malformed input and helper failure; identify supported POSIX shell implementations.
- Define a repair interface that requests lifecycle operations without inventing process identity; document behavior if no target shell exists.

## Result

Pending. Capture unresolved risks and further work before completion.
