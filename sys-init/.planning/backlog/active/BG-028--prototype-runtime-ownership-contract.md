---
id: BG-028
title: Prototype runtime ownership and launch contract
status: active
created: 2026-09-05
source_type: research-follow-on
area: research
---

## Problem

Precise child ownership and event accounting need evidence before choosing helper boundaries.

## Scope and dependencies

BG-025 defines target limits; BG-030 evaluates runtime feasibility. Coordinate with BG-020, which owns restart policy, and BG-022, which owns readiness semantics.

Source: [BG-026 handoff](../../../docs/research/BOUNDARY-HANDOFF.md). Active bounded slices follow decisions 0003 and 0005; broader prototypes still require a recorded contract.

## Acceptance criteria

- Write the candidate contract before code: launch inputs, child/instance identity, owner lifetime, events, control authority, and error results.
- Compare a persistent owner with executable helper chains; do not propose an independent waiter for another process's children.
- Define and run bounded host fixtures for immediate exit, exec failure, coalesced wakeups, signal versus normal exit, descriptor inheritance, stop races, and parent death when implementation is authorized by the research/decision stage.
- Explain descendant containment limits and what requires Aether or platform-specific facilities; measure process count, memory, size, and responsiveness.
- Record findings and follow-ons without treating a host supervisor as target PID 1 proof.

## Result

Partial. Trusted readiness/direct-parent and emergency cleanup slices are tested; broader ownership, containment and measurements remain open; parent-death survival is now witnessed on macOS.

## Readiness/ownership follow-up

[Decision 0003](../../../docs/decisions/0003-host-readiness-fixture.md) and the [host follow-up](../../../docs/HOST-RUNTIME.md) establish the trusted first-frame/direct-parent subset. Twenty macOS host cases pass, including six new framing/descriptor/exit-order cases; an isolated old-parser negative control detects both corrected bugs. This story remains open for its wider cross-host, parent-death, helper/native ownership and contract acceptance scope.

## Emergency lifetime result

[Decision 0005](../../../docs/decisions/0005-host-emergency-close.md) records closure/admission and retained cleanup ownership. Six new macOS tests cover finally cleanup, closed-state rejection, repeated close, injected wait/kill failures, cleanup retry and unrelated-child isolation. All 30 host cases pass. Guard removal causes seven assertion failures including subtests. This does not close parent-death, helper-chain, exclusive-wait enforcement, measurement or native-recovery questions; those remain in this story and BG-033.

## Parent-death witness

[Decision 0006](../../../docs/decisions/0006-host-parent-death-witness.md) records the bounded fixture. Two cases pass: abrupt original-owner death leaves the child running under a changed parent, while normal owner exit executes finally cleanup and records child wait. External orphan reaping is unobserved; cooperative fixture exit is not containment. The combined run passes 32 host tests; a forged unchanged-parent receipt fails. Remaining scope includes launch/exec failure, coalesced terminal accounting, helper chains/exclusive wait, measurements and a separately accepted parent-death enforcement strategy (native recovery remains BG-033).

## Accounting and launch-failure slice

[Retained evidence](../../../docs/evidence/host-accounting-2026-09-05/README.md): three new methods test eight accumulated terminal children, exact signal/normal outcome and cleanup accounting, real exec-error descriptor cleanup/dependency blocking, and post-construction executable changes. All 35 host cases and the combined runner pass. Signal-as-exit and leaked-writer negative controls fail assertions. Runtime/model/shared pins are unchanged. Remaining ownership/helper/exclusive-wait, measurement and cross-host scope stays open.

## Exclusive-wait/helper slice

[Decision 0007](../../../docs/decisions/0007-host-exclusive-wait.md) records the local Python ECHILD false-zero finding and direct-wait fix. Lost status now produces incomplete/unknown and no signalling/reclamation of that identity. Real sibling-helper wait rejection and explicitly delegated helper readiness are tested. All 38 host cases pass; restoring poll fallback fails one assertion. Scope remains trusted and single-threaded; measurements, concurrent/exclusive-wait enforcement, broader helper containment and native recovery remain unresolved.

## Exploratory measurement slice

[Host measurements](../../../docs/HOST-MEASUREMENTS.md) add retained start/readiness, stop/reap, CPU, traced manager allocation and live process inventory baselines for one/eight children. Two warmups and ten measured repetitions per workload pass; a deliberate readiness timeout is recorded as censored failure. Three summary tests bring harness evidence coverage to 13. Full-process RSS/child memory, exact CPU model, production binary footprint, cross-host measurements and ownership enforcement remain open. These exploratory host values do not close BG-028 or establish native performance.

## Consolidation checkpoint

[Ownership/native review](../../../docs/OWNERSHIP-REVIEW.md) consolidates the host slices without closing this wider story. BG-055 captures a fresh native integration witness because current kernel/build inputs differ from retained receipts. Stronger ownership, cross-host and production gates stay with their existing owners.
