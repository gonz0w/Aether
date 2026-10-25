---
id: BG-030
title: Evaluate implementation language, toolchain and recovery runtime
status: captured
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem

The old tiny-C label does not select a language or prove that its binaries run in minimal Aether userspace.

## Scope and dependencies

BG-025 for target runtime constraints; BG-028 for mechanism contract; BG-017 for test/measurement plan.

Source: [BG-026 handoff](../../../docs/research/BOUNDARY-HANDOFF.md). This is captured work; prototype code waits for the relevant research and recorded decision.

## Acceptance criteria

- Compare viable C, Rust, and other justified candidates against actual host and Aether interfaces; distinguish libc/OS requirements from language requirements.
- List compiler, linker, loader, allocation, panic/error, startup, and library dependencies, including static versus dynamic linking tradeoffs.
- Define measurement workloads and numerical budgets before evaluating binary size, memory, startup and recovery costs.
- Define failure tests for missing shell, libraries, filesystem, console, and denied authority; specify the minimum usable recovery payload.
- Record an Aether requirement and dependency-cost rationale for each proposed dependency and evidence needed for a later decision; do not copy Aether's service language automatically.

## Result

Pending. Capture unresolved risks and further work before completion.
