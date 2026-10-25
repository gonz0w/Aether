---
id: BG-048
title: Define device and mount ownership and native teardown requirements
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and acceptance criteria

Specify object generations, access grants, usable-state evidence, consumer stop dependencies and mount identity. Record concrete Aether requirements for quiescence, interrupt/DMA revocation, shared references and quarantine when reclaim fails. Test unplug/replug and stale grants only against a supported fixture; coordinate BG-032/BG-033/BG-043.

## Evidence

[BG-009/BG-015 handoff](../../../docs/research/SECURITY-RESOURCES-AND-EVENTS.md) provides alternatives and failure cases. Research completion does not accept an implementation architecture.
