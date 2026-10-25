---
id: BG-037
title: Define enablement, defaults and local override semantics
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and scope

The separation of install, enablement and live state needs precise policy and conflict rules.

Source: [BG-027 proposed package/service boundary](../../../docs/research/PACKAGE-SERVICE-CONTRACT.md). No companion implementation or API acceptance is implied.

## Acceptance criteria

- Define explicit enable/disable, defaults and any stronger activation prohibition; settle dependency-triggered and explicit-start behavior.
- Specify precedence and provenance for distribution policy, vendor suggestions and local overrides; preserve administrator decisions across upgrade and reinstall.
- Define effective-definition validation, conflicting overrides, renamed services and owner transfer, coordinating BG-035 and BG-014.
- Provide install/upgrade/remove/purge examples and fixtures with selected/running revisions and pending actions visible independently.
- Coordinate BG-023 and BG-016 for lifecycle/operator semantics; capture unresolved policy questions before completion.

## Result

Pending.
