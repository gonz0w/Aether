---
id: BG-035
title: Define inert service descriptor profile and validation fixtures
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem and scope

Specify PS-01 through PS-08 and PS-11 without coupling metadata to executable shell or an unimplemented target ABI.

Source: [BG-027 proposed package/service boundary](../../../docs/research/PACKAGE-SERVICE-CONTRACT.md). No companion implementation or API acceptance is implied.

## Acceptance criteria

- Compare bounded inert syntax candidates; define identifiers, schema versions, field cardinality, limits, unknown-field rules, and optional extension behavior.
- Bind descriptor ownership/digest to package evidence; separate structural, graph, target and policy checks and reject duplicate service IDs.
- Define target launch prerequisites, executable mode evidence, argv/environment representation and requested authority; coordinate BG-014, BG-023, BG-029 and BG-033.
- Create a parser fixture plan covering valid/malformed descriptors, inert shell-shaped values, conflicts and unsupported profiles; implement only after the relevant decision.
- Do not mutate pkg-state-v1 or expose a fictitious validator API; document the proposed consumer interface and unresolved questions.

## Result

Pending.
