# Project direction

Updated: 2026-09-07.

Build the init and service lifecycle foundation for Aether and its distribution. Keep the system small, fast, and easy to understand through inspectable primitives and familiar POSIX shell concepts. Coordinate kernel authority and runtime contracts with Aether, package lifecycle contracts with pkg-mgr, and shared standards with Aether-standards. Consume pinned offline standards; keep domain implementation rules local.

## Accepted v1 scope

[Simple Aether v1](../docs/V1-SCOPE.md) defines the current finish line and short
delivery plan. Broader goals below describe direction beyond v1, not additional
release requirements. Keep only mechanisms needed to boot useful services,
supervise them with bounded retries, explain failures and shut down cleanly.

## Design goals

- A minimal, reliable first-process responsibility set and a clear recovery path.
- Predictable start, stop, restart, dependency, readiness, and failure behavior.
- Readable service definitions and useful explanations of why a service is blocked or failed.
- Clear separation of installed files, enablement policy, and actual service activation.
- Aether-only runtime contracts, with host tools/tests kept separate from native acceptance.
- A small dependency footprint and measurable startup, memory, and failure-recovery costs.

Learn from runit, s6, daemontools, OpenRC, BSD rc, illumos SMF, systemd, launchd, and other relevant designs. Compare costs and failure behavior as well as features. The survey is input to a coherent design, not a commitment to implement every feature.

## Current constraints

Research precedes implementation architecture. Earlier findings are hypotheses and evidence to review; their labels do not select C, shell, Rust, or a process layout. Aether's current Rust service experiments are integration context, not a sys-init language decision.

POSIX is the intended authoring and compatibility direction. Aether's native first service may have capability and task semantics that differ from traditional Unix PID 1. Define that boundary before relying on fork/exec/wait, signals, a filesystem, or a shell on target.

The original PRD file is a placeholder, not a full specification. Legacy outcome IDs DO-01 through DO-05 remain traceable through the archived INTENT document.

## Evidence of success

Before production implementation: cited comparisons, explicit lifecycle examples, accepted integration assumptions, and recorded decisions for the smallest coherent design.

Before a prototype is complete: repeatable tests for child exit, restart limits, dependency failure, readiness timeout, shutdown, and recovery, with host versus target coverage stated.

Before calling the implementation small or fast: publish binary size, runtime dependencies, idle and loaded memory, boot-to-ready time on a fixed service graph, and failure-recovery latency, with environment and measurement method. Numeric budgets remain to be set during prototype design.

Before claiming distribution integration: pkg-mgr stages and validates service artifacts, an accepted Aether loader/runtime executes them, and activation/failure/recovery are demonstrated together.

## Shared experience

Adopt Aether Experience v0.1.0 and the Hearth palette for new first-party user-facing work. `docs/EXPERIENCE.md` records the pin, scope and migration status. This shared presentation contract does not change kernel authority, service lifecycle, package state or upstream interfaces. Existing surfaces migrate through separately tested implementation work.
