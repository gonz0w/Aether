---
id: BG-021
title: Prototype dependency graph validator and diagnostics
status: captured
created: 2026-06-21
source_type: research-follow-on
source_path: docs/archive/2026-09-05-planning-reset/.planning/research/runtime-semantics/dependency-ordering.md
source_title: Core service runtime semantics research
area: research
appetite_hint: medium
depends_on:
  - BG-005
external_dependencies: []
impact: high
impact_rationale: dependency semantics need validation, cycle diagnostics, and startup-wave evidence before implementation design
target_outcomes:
  - DO-01
  - DO-04
files: []
---

## Problem

The dependency research recommends explicit hard, weak, ordering-only, conflict, provider, condition, and readiness-aware edges, but these need concrete validation behavior.

## Desired Outcome

A prototype dependency graph validator that emits missing-provider errors, cycle paths, deterministic startup waves, and explainable `why blocked` diagnostics for representative boot graphs.

## Promotion Notes

Coordinate with pkg-mgr install/enablement validation questions before treating the vocabulary as accepted.
