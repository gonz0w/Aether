# Aether runtime contract questions

Date: 2026-09-05. BG-025 research complete. This is a sys-init proposal and gap analysis, not an accepted Aether ABI. No kernel changes or runtime tests were made in this work.

Aether has enough native task-lifetime machinery to inform a narrow supervision experiment. It does not yet expose a general service runtime. The next integration should build on scoped task authority and explicit destruction, while keeping POSIX compatibility a separate contract. Requiring fork, signals, or a shell first would prematurely constrain the kernel.

## Evidence reviewed

| Ref | Primary local source | What was inspected |
| --- | --- | --- |
| A1 | [Current state](../../../.planning/STATE.md) | Reported M2 and M3 checks and remaining limits |
| A2 | [M2 lifetime](../../../.planning/M2-LIFETIME.md) | One factory, task/backing quota, rights and register ABI |
| A3 | [M2 capabilities](../../../.planning/M2-CAPABILITIES.md) | Holder-local generation handles, derivation, revocation, endpoint operations |
| A4 | [M3 IPC](../../../.planning/M3-IPC.md) | Static cross-core routes and readiness fixture |
| A5 | [Lifetime state machine](../../../kernel/lifetime.zig) | Pool create/start/finish/destroy/release transitions |
| A6 | [x86 protection runtime](../../../kernel/arch/x86_64/protection.zig) | resetWorker, destroyWorker, releaseMemory, lifetimeInvoke and lifetimeException |
| A7 | [Rust fixture](../../../user/protection/main.rs) | supervisor loop, inspect/yield, stale-handle and authority checks |
| A8 | [Cross-core table](../../../kernel/cross_core.zig) | Three immutable route grants per worker, namespace and rights checks |

The [source manifest](AETHER-RUNTIME-SOURCES.json) records local file hashes and repository HEAD. Working files differ from the committed baseline and may change during companion development. Findings refer to the inspected code and named symbols, not HEAD alone. A1's successful test reports were read, not independently rerun.

## What exists, precisely

M2's factory can allocate one 8 KiB code/stack bundle and instantiate one pinned worker image. A6 copies fixture bytes into a code page and installs fixed entry/register context; there is no general executable selection, argv/env, or arbitrary image loader in that path. A7's supervisor runs nine create/start/inspect/destroy/release cycles. This is substantive lifetime evidence, with a deliberately small scope. [A2, A6, A7]

`inspect` requires task inspect rights and returns the pool result: 0 pending, 1 fixture exit, 2 fixture fault. It does not expose a general exit code, fault record, stopped reason, event queue, or consumable wait result. The supervisor polls and yields. `completeStop` clears the result, and task destruction invalidates task capabilities; a caller needing terminal diagnostics must capture them before destruction under the present model. [A5–A7]

Destruction removes the worker from the runnable set, clears mappings/context, reloads the supervisor address space, invalidates task references, and detaches backing. Release separately invalidates memory references and zeros backing before reuse. This is single-CPU cleanup with explicitly constrained mappings, not an SMP/DMA teardown guarantee. Revoking a factory handle does not destroy objects already created through it. [A2, A6]

M3 is a different runtime slice: two pinned workers have statically installed local endpoint grants, bounded messages, and nonblocking Full/Empty results. Its readiness message coordinates a queue test; it is not a general service readiness API. M2 generation handles and M3 namespace/slot handles must not be conflated. Dynamic grants, remote revocation and SMP worker restart remain outside the reviewed contract. [A3, A4, A8]

## Proposed semantic checklist

AR IDs name questions and candidate obligations, not syscall numbers. “Gap” means not established by the reviewed runtime; it is not a claim that all source code was exhaustively audited. Owners below identify needed coordination, not commitments by the companion project.

| ID / needed semantics | Current evidence | Required answer and failure criterion | Coordination / follow-on |
| --- | --- | --- | --- |
| AR-01 Bootstrap first service | Trusted bootstrap installs fixed grants (A2–A4) | Who loads sys-init, supplies its configuration and grants, and recovers from bootstrap failure? Reject unknown ABI/grants before service execution. | Aether + sys-init / BG-033 |
| AR-02 Program launch | Fixed image and one task quota (A2, A6) | Image identity, format, ABI/version, arguments, environment, memory bounds and launch completion must be defined. Failed launch must expose cleanup obligations without reporting running. | Aether + pkg-mgr + sys-init / BG-033, BG-027 |
| AR-03 Instance identity | M2 holder-local generation handles; M3 fixed namespaces (A3, A8) | Separate service name, generation/instance identity and authority. Old control requests must never address a replacement instance. Specify exhaustion and cross-holder naming. | Aether + sys-init / BG-032 |
| AR-04 Exit/fault observation | M2 inspect returns three fixture values (A5–A7) | Define terminal reason, status lifetime, observation/acknowledgment, multiple observers and owner death. Terminal facts must not silently disappear before required collection. | Aether + sys-init / BG-032 |
| AR-05 Wait, clocks and deadlines | Poll/yield in M2; nonblocking IPC and watchdog fixture in M3 (A1, A7) | Define notification or bounded polling, time units, monotonicity, overflow and cancellation. Timer interrupts alone do not supply a user deadline API. Required readiness timeout must not become success. | Aether + sys-init / BG-032, BG-022 |
| AR-06 Graceful versus forced stop | Authorized destroy of a live task (A2, A6) | A cooperative stop/reload request needs a protocol and completion evidence. Destroy is not graceful shutdown. Report failure or uncertainty if teardown cannot complete. | Aether + sys-init / BG-032, BG-024 |
| AR-07 Quiescence and reclamation | Explicit local destroy, detach, zero and release (A2, A6) | Preserve the distinction between stop, revocation, mapping removal and reusable resources. Cross-core or device-owned resources need separately established completion. | Aether / BG-032, BG-009 |
| AR-08 Dependency grants | M2 same-holder derivation; M3 trusted static grants (A3, A4) | Who installs dependencies in a newly created worker and replaces/revokes them on restart? Sending capability-shaped bytes must not create authority. | Aether + sys-init / BG-032 |
| AR-09 Readiness and endpoint availability | Fixed M3 synchronization message (A4) | Bind readiness to an authorized current instance and defined readiness predicate. Endpoint existence alone need not mean the service can handle requests. Reject stale notifications. | sys-init + Aether / BG-022, BG-032 |
| AR-10 Supervisor death and orphan ownership | Normal fixture supervisor completion ends the experiment (A6, A7) | Define who owns surviving tasks, backing and diagnostic facts; recovery must not depend on the dead supervisor's inaccessible handles. Choose explicit recovery or explicit non-recovery for the first experiment. | Aether + sys-init / BG-033 |
| AR-11 Resource policy | Fixed pools and explicit exhaustion (A2, A3) | Specify quota ownership/recovery and accounting. CPU scheduling policy and service restart limits remain separate from task allocation rights. | Aether + sys-init / BG-009, BG-032 |
| AR-12 Console, logs and crash records | Kernel serial diagnostics and fixture assertions (A1, A6) | Define authorized user diagnostics, bounded buffering/backpressure, record retention and emergency access. A kernel log is not a service stdout API. | Aether + sys-init / BG-008, BG-033 |
| AR-13 Filesystem and devices | General POSIX services/device environment not established (A1) | Identify configuration/image source, mount/device authorities and availability events. A first native fixture may be filesystem-free; shell recovery cannot be presumed. | Aether + pkg-mgr + sys-init / BG-003, BG-014, BG-015, BG-033 |
| AR-14 Final shutdown | Fixture halt is kernel control flow (A6) | Define who authorizes halt/reboot, when outstanding work is stopped, and how failure is reported. Do not expose fixture completion as a production power API. | Aether + sys-init / BG-024, BG-033 |
| AR-15 POSIX compatibility | No POSIX service runtime reported (A1) | Decide where Unix process ancestry, PID 1, wait, signals, credentials, descriptors and shell execution are implemented, if needed. Native instance control must not infer authority from a PID. | Aether + distribution/sys-init / BG-033 |

These questions refine OQ-001 and OQ-007; they do not close them. OQ-002 remains owned by package integration. General fault capture and supervisor-death recovery are recorded as OQ-010 and OQ-011.

## Comparison before selecting a target interface

| Platform evidence | Lesson for the contract |
| --- | --- |
| [POSIX wait](https://pubs.opengroup.org/onlinepubs/9699919799/functions/wait.html), reviewed in the [boundary handoff](BOUNDARY-HANDOFF.md) | Parent-owned status collection is a useful Unix baseline. It does not itself define native capability ownership or supervisor recovery. |
| [FreeBSD procctl source manual](https://raw.githubusercontent.com/freebsd/freebsd-src/main/lib/libsys/procctl.2) | Reaper acquisition, release, status and descendant control are explicit extensions; descendant PID snapshots have race caveats. BSD is not one universal reaper API. |
| [illumos process contracts](https://raw.githubusercontent.com/illumos/illumos-gate/master/usr/src/man/man5/process.5) | Group fault boundaries, exit/empty events and owner-exit behavior can be separately specified. A service need not be reduced to its main PID. |
| [Linux pidfd implementation](https://raw.githubusercontent.com/torvalds/linux/master/kernel/pid.c) | A referenced process object can be distinct from a reusable numeric PID. This is design evidence, not a request to make Linux pidfds the Aether API. |
| Aether A2–A8 | Holder-scoped authority and explicit reclaim boundaries already express valuable native concepts. The unresolved work is general service semantics and recovery. |

External source inspection: 2026-09-05, moving primary source branches. POSIX evidence/access limits remain as recorded in BG-026; the three platform source files above were retrieved in this review. These comparisons do not prove sys-init portability or establish implementation dependencies.

## Smallest useful integration experiment

Propose a single-core, fixed-image supervisor/worker fixture first (BG-034), subject to a recorded experiment decision. Keep the production loader and POSIX surface as explicit future work. The existing M2 loop supplies a reference behavior; it is not already sys-init integration.

1. Freeze a narrow versioned fixture contract covering bootstrap grants, one instance, inspectable terminal result, create/start/destroy/release and failure outcomes. Aether must expose the accepted fixture seam; sys-init owns lifecycle policy and observable expectations.
2. Drive a normal exit, a fault, an explicit live stop and a replacement instance. Observe terminal data before teardown, assert stale handles are rejected, and verify reclamation occurs only after quiescence.
3. Exercise wrong rights, wrong object type, exhausted quota, and a rejected lifecycle transition. No error may leave an undocumented runnable task or reusable-but-still-mapped backing.
4. Put a finite bound on the experiment using a labelled harness watchdog. Poll/yield may suffice for fixture progress; it must not be advertised as a calibrated service timeout or low idle CPU result.
5. Demonstrate supervisor failure only after AR-10 has an explicit outcome. Until then record it as unsupported and do not claim resilient init. Add readiness only with an accepted instance-bound channel; do not reuse the M3 queue-test message as service readiness by name alone.

The experiment may use a prebuilt fixed target image rather than a general loader, but must actually exercise sys-init-owned policy under a documented Aether interface before being called integration. Re-running Aether's existing smoke test alone is kernel evidence. A host model using the same event sequence is useful policy evidence and must be labelled host-only.

Acceptance artifacts should include the pinned source and fixture ABI, command/environment, expected event trace, bounded negative cases, and target output. General package loading, multithreaded/multiprocess containment, SMP restart, device teardown, durable recovery and POSIX conformance remain outside this first experiment.

## Completion and next actions

BG-025's requested checklist is complete: each runtime area now has current evidence, a specific unresolved question/failure condition, and a route to further work. It does not mean the interfaces are implemented or accepted by Aether.

New work captured before completion:

- BG-032: specify native instance lifetime, terminal events, deadlines and dependency grants; coordinate existing BG-020/BG-022/BG-028 instead of duplicating their policy/prototype scope.
- BG-033: define bootstrap, supervisor failure, minimum recovery, and POSIX compatibility ownership; coordinate BG-003/BG-030.
- BG-034: shape the bounded native integration experiment after the fixture contract and decision exist.

BG-027 package/service contract research is next. Stage 2 of the roadmap remains open until its companion, boot and layout work has findings. No source implementation, kernel modification, deployment, or performance claim follows from closing this research item.
