---
id: BG-019
title: Capture Research Intake v0 follow-on work
status: captured
created: 2026-06-21
source_type: research
source_path: docs/archive/2026-09-05-planning-reset/.planning/research/SUMMARY.md
source_title: Research Intake v0
area: research
appetite_hint: large
depends_on:
  - BG-001
  - BG-002
  - BG-004
  - BG-010
  - BG-011
  - BG-012
  - BG-018
external_dependencies:
  - ~/DEV/Aether
  - ~/DEV/pkg-mgr
impact: high
impact_rationale: prevents unresolved research findings from disappearing after the research milestone closes
target_outcomes:
  - DO-01
  - DO-02
  - DO-03
  - DO-04
  - DO-05
files:
  - docs/archive/2026-09-05-planning-reset/.planning/research/SUMMARY.md
---

## Problem

Research Intake v0 identified unresolved questions, risks, and prototype needs that should become schedulable backlog work before the selected research is treated as closed.

## Why Now

The repository requires follow-on backlog stories for unresolved questions, newly discovered risks, or prototype work before research backlog work is marked complete. The research summary records candidate work, but follow-on planning needs an explicit captured backlog entry.

## Desired Outcome

Split the follow-on candidates from `docs/archive/2026-09-05-planning-reset/.planning/research/SUMMARY.md` into deduplicated backlog stories with clear dependencies, appetite, and traceability.

## Candidate Work to Split

- Prototype and compare three minimal service authoring surfaces: service directory, `rc.d`-style script header, declarative envelope plus POSIX hook.
- Produce an explicit “features not copied from systemd” decision log with Aether scope rationale.
- Research rescue/recovery UX across runit, BSD single-user mode, SMF maintenance, and systemd emergency/rescue targets.
- Draft a formal PID 1 state machine and failure-mode table for boot, runtime, degraded mode, emergency, shutdown, and reboot.
- Coordinate with Aether to specify initial-process ABI, orphan reaping, shutdown events, console capabilities, and reboot/halt authority.
- Build a non-production PID 1 semantics test harness after architecture approval.
- Write example service definitions for getty, syslog/log collector, network daemon, one-shot mount, and socket-activated local service in each candidate format.
- Research safe shell hook conventions, quoting rules, and environment sanitization for POSIX sh service metadata.
- Define validation levels: parse-only, package-install validation, boot-graph validation, and runtime readiness validation.
- Create an Aether/sys-init interface checklist and open-question issue list in both repos.
- Research microkernel init/service-manager prior art: seL4/CAmkES, Zircon component manager, Hurd translators, QNX proc/service models.
- Define capability handoff examples for device manager, filesystem, logger, network stack, and package-triggered service restart.
- Draft `pkg-mgr <-> sys-init` command/API contract for validate, install-definition, preset, enable, disable, reload, restart, rollback, and remove.
- Research package-manager service scripts in Debian maintainer scripts, RPM scriptlets/systemd presets, FreeBSD `rc.d`/pkg messages, and OpenRC Gentoo ebuilds.
- Define rollback cases for service definition schema migration and failed post-upgrade restart.
- Define Aether-native ownership for events, resource controls, credentials, and service logs.
- Research event/wait prior art only where an Aether supervisor requirement needs it.
- Write an explicit non-POSIX primitive adoption template requiring Aether authority, failure behavior, and rationale.
- Reconstruct the 15-item PRD agenda as explicit backlog candidates with duplicate detection against existing captured backlog.
- Research implementation substrate options: POSIX sh, tiny C, Rust/Zig helper binaries, and mixed architecture for init/supervisor/CLI.
- Define YAGNI guardrails and “do not build yet” examples for service manager scope control.
- Research security model for service definitions: trusted packages, admin overrides, signature/manifest validation, capability drops, and unsafe hook review.

## Source Notes

- This is a consolidation backlog item. It should be split before promotion into execution work.
- Source: `docs/archive/2026-09-05-planning-reset/.planning/research/SUMMARY.md` follow-on backlog candidate lists.

## Promotion Notes

Before promotion, split this consolidation item into focused backlog stories or explicitly deduplicate it against already captured items.
