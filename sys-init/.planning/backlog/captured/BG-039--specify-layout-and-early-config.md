---
id: BG-039
title: Specify layout, early configuration and migration
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Scope

Follow the [boot/layout research handoff](../../../docs/research/BOOT-AND-LAYOUT.md). This is specification work; no implementation architecture or companion API is accepted by capture.

## Acceptance criteria

- Compare proposed POSIX paths with actual image/runtime prerequisites; define early bootstrap/recovery configuration availability without relying on an unavailable /usr mount.
- Define ownership, versioning, path grammar, permissions, links and read-only versus writable storage; coordinate BG-035 and pkg-mgr file metadata limits.
- Select an enablement representation with BG-037 and distinguish vendor suggestions from administrator policy and runtime state.
- Define migrations preserving local overrides, disable intent and application data, with publication/recovery constraints from BG-031/BG-036.
- Design missing /usr-/var, stale boot state, read-only root, traversal/link, conflicting override and failed-migration fixtures; native paths remain gated on Aether contracts.

## Result

Pending; capture unresolved questions before completion.
