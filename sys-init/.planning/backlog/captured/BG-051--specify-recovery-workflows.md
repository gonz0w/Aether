---
id: BG-051
title: Specify minimal recovery workflows
status: captured
created: 2026-09-05
source_type: research-follow-on
area: specification
---

## Problem and acceptance criteria

Define inspect, diagnose and authorized retry paths for exhausted restart budget, incomplete cleanup and invalid configuration. Cover no shell, missing console/storage and supervisor failure without pretending recovery exists. Coordinate BG-033/BG-038/BG-045. Capture native prerequisites and explicit unavailable responses before introducing rescue commands.

## Evidence

[Runtime v0 draft](../../../docs/specs/RUNTIME-V0.md) and [operator comparison](../../../docs/research/OPERATOR-INTERFACE.md). Draft completion does not accept production architecture.
