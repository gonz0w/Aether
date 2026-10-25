# Shell and systems-language boundary handoff

Date: 2026-09-05. Story: BG-026, continuing BG-013. Status: research synthesis complete; architecture and language decisions remain open.

The defensible boundary is between inspectable policy and precise runtime mechanisms. The evidence supports investigating a small runtime component for supervision and authority-sensitive operations. It does not require every helper to be written in C or every policy to execute as shell.

## Corrections to earlier findings

1. **Shell can preserve arguments.** In ordinary command arguments, quoted positional parameters preserve argument boundaries, including empty arguments; an `exec "$@"` wrapper need not reconstruct a command string. Avoiding `eval`, accidental splitting, and command-string serialization is a data/interface design issue. Arbitrary binary data, arbitrary environment names, and descriptor/credential setup need separate contracts. The old blanket claim that exact argv requires C is withdrawn. [POSIX shell language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html)
2. **Shell can wait for children.** POSIX shell `wait` operates on known process IDs in its execution environment. That supports bounded scripts, not a portable interface for arbitrary adopted children and a multiplexed supervisor loop. POSIX `waitpid` exposes nonblocking collection and separate normal-exit/signal status interpretation; an independent helper cannot simply wait for its caller's children. The ownership of the long-lived parent matters more than the number of small executables. [Shell wait, Issue 7](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/wait.html), [system wait, Issue 7](https://pubs.opengroup.org/onlinepubs/9699919799/functions/wait.html)
3. **A signal is a wakeup, not an exit ledger.** POSIX's signal guidance describes draining available child statuses with nonblocking wait calls. Candidate runtime tests must check multiple exits per wakeup. This supports precise event/status ownership without selecting C or requiring work to happen inside a signal handler. [POSIX sigaction](https://pubs.opengroup.org/onlinepubs/9799919799/functions/sigaction.html)
4. **Atomic replacement is not a language choice or a complete persistence protocol.** `rename` provides atomic name replacement; `renameat` provides directory-relative addressing. POSIX separately discusses directory durability and synchronization. Whether sys-init needs persistent runtime records at all is unresolved. A compiled helper does not, by itself, establish crash safety, safe path traversal, locking, or rollback. [POSIX rename](https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html), [durability rationale](https://pubs.opengroup.org/onlinepubs/9799919799/xrat/V4_xbd_chap01.html)
5. **Readiness depends on a semantic contract.** A successful setup job, successful program launch, service-reported readiness, and ongoing health answer different questions. A pipe notification does not independently verify the service's assertion. A method can establish readiness if its specified success condition requires availability. Neither transport nor implementation language supplies that meaning automatically. The revised model must reject a required-readiness timeout instead of silently upgrading it to success. [s6 notifications](https://skarnet.org/software/s6/notifywhenup.html), [illumos restarter](https://raw.githubusercontent.com/illumos/illumos-gate/master/usr/src/man/man8/svc.startd.8)

These corrections supersede categorical `tiny-C-required` and automatic `weak-ready` fallback recommendations in the archived matrix. They do not invalidate the earlier failure scenarios or select final state names.

## Prior-art comparison

| Evidence | Useful observation | Design inference and cost to investigate |
| --- | --- | --- |
| [runit runsv](https://smarden.org/runit/runsv.8) | A supervisor launches run/finish programs, delays immediate restarts, and can connect a separate logger through a pipe. | Small composable programs are a credible experiment; process count, log backpressure, and supervisor failure still need measurement. |
| [s6 notification contract](https://skarnet.org/software/s6/notifywhenup.html) | Spawn and ready are distinct events; a daemon can signal initialization by writing a newline to an inherited descriptor. | Try instance-bound notifications with a timeout; define who may write and invalidate stale readiness on restart. |
| [FreeBSD rcorder](https://man.freebsd.org/cgi/man.cgi?query=rcorder&sektion=8&format=html) | Comment metadata permits ordering and cycle/missing-provider diagnostics; REQUIRE does not establish a running daemon. | Keep offline graph validation distinct from runtime dependency satisfaction. A standalone tool is plausible; no required language follows. |
| [OpenRC script guide](https://github.com/OpenRC/openrc/blob/master/service-script-guide.md) | Scripts use a POSIX shell subset through openrc-run; default lifecycle functions delegate to tooling. The guide also supports PID-file/daemonizing patterns. | Borrow readable conventions and helper boundaries, but do not claim all prior art endorses one supervision model. |
| [illumos svc.startd](https://raw.githubusercontent.com/illumos/illumos-gate/master/usr/src/man/man8/svc.startd.8) | Restarter state, methods, failure handling, and process contracts cooperate. Start-method success requires availability to consumers. | Separate state meaning from transport; process contracts are platform facilities, not POSIX guarantees. |
| [systemd service manual source](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.service.xml) | Simple, exec, and notify services have different startup milestones. The manual discourages PID files for new services. | Record exactly what startup success proves. Keep Linux containment separate from portable lifecycle semantics. |

This is a bounded boundary review, not a fresh exhaustive survey of every init. Earlier daemontools, launchd, boot-stage, and service-format notes remain historical leads until their claims are needed and rechecked.

## Responsibility matrix

“Runtime” below means a component with the necessary OS interfaces and ownership, not an accepted process layout or language. “Policy” means a suitable place to investigate scripts or inert data, not a promise that a target shell exists. Each row is a recommendation derived from the evidence above and the companion constraints below.

| Responsibility | Research recommendation | Open choice / tracking |
| --- | --- | --- |
| Boot and shutdown stages | Policy jobs; bounded execution and explicit failure outcomes | Root/console prerequisites and shutdown authority: BG-003, BG-024, BG-025 |
| Service hooks and repair commands | Small policy programs; lifecycle requests use owned service identity | Hook inputs, retries, timeouts, authority: BG-029, BG-016 |
| argv and environment | Structured inputs or disciplined quoted wrappers; never require re-parsing data as code | Accepted character/size/environment rules: BG-029, BG-028 |
| Spawn, child identity, status collection | One clearly identified runtime owner per child; helper chains preserve that ownership | Supervisor topology and parent failure: BG-028, BG-020 |
| First-process adoption/reaping | Platform contract first; portable shell alone does not expose a general init interface | Unix PID 1 versus Aether service bootstrap: BG-025 |
| Signals, sessions, groups and stop escalation | Runtime-owned targeting, event handling, and deadlines | Descendant escape and stale identity: BG-028, BG-024 |
| Descriptors, log pipes and readiness channels | Simple shell redirection can be useful; lifetime/inheritance and event coordination belong to runtime contract | Leaks, blocked logger, readiness sender identity: BG-028, BG-008, BG-022 |
| Credentials and resource authority | Enforce before exposing a runnable service; platform adapter | No ambient-root assumption for Aether: BG-009, BG-025 |
| Metadata and graph validation | Inert data plus deterministic validation is a candidate; graph complexity does not require C | Schema, cycles, missing/ambiguous providers: BG-021, BG-027 |
| Readiness and health | Distinct launch/completion/ready/health facts; release dependencies only on specified evidence | Protocol and timeout policy: BG-007, BG-022, BG-023 |
| Restart limits | Runtime observes exact exit events and time; policy chooses restart rules | One-shot side effects, bounded counters and reset behavior: BG-020 |
| Status storage and locking | Queryable status; separate volatile observation from durable configuration | Single writer versus locks; replacement versus persistence: BG-031 |
| Diagnostics and logger policy | Human-readable explanations and bounded failure behavior | Blocking, loss, rotation, and recovery surface: BG-008 |
| Emergency recovery | Minimal authorized recovery payload; keep required runtime control responsive | Shell unavailable or broken, authority recovery: BG-029, BG-030, BG-025 |
| Halt, device and package integration | Explicit adapters with unsupported/failure results | BG-024, BG-015, BG-027 |
| Language, build and helper packaging | Compare viable runtimes after contracts; measure cost | BG-030; no dependency added by this report |

## Portability and companion constraints

| Environment | What the evidence supports | What it does not establish |
| --- | --- | --- |
| POSIX | Shell policy and system-level process/file mechanisms with specified interfaces | A complete init, hotplug, containment, or recovery architecture |
| BSD | rcorder provides useful offline ordering evidence | Readiness, whole-service containment, or a uniform API across all BSDs |
| illumos | SMF methods and process-contract-based restarters demonstrate richer lifecycle semantics | Process contracts on other platforms |
| Linux | systemd demonstrates distinct service types and Linux-specific management facilities | cgroups, procfs, signalfd, or other Linux interfaces as sys-init baseline |
| Aether | Native task/capability ownership, scoped user-space supervision, and bounded POC fixtures | A general POSIX process/service ABI or a target shell |
| pkg-mgr | Host staging/metadata work and a proposed separation of artifacts from activation | An implemented service installation/enablement protocol |

Local evidence: [Aether architecture](../../../docs/ARCHITECTURE.md), [pkg-mgr architecture](../../../pkg-mgr/docs/ARCHITECTURE.md), and [integration questions](../INTEGRATION.md). Aether documents scoped capabilities, task teardown, and fresh worker instances; its fixed factory fixtures explicitly do not define a general service ABI. POSIX remains outside its POC dependency chain. Therefore a Unix-oriented host experiment can explore lifecycle policy, but cannot establish target process adoption, stop authority, or recovery. BG-025 must identify native and compatibility boundaries without requiring Aether to adopt fork merely to suit an experiment.

pkg-mgr proposes inert descriptor validation and a separate activation decision. BG-027 must specify the actual artifact, owner, failure, and rollback contract before sys-init relies on package state. Neither companion repository was modified or tested here.

## Verification and recovery plan

Carry forward the [archived scenario catalog](../archive/2026-09-05-planning-reset/.planning/phases/phase-2-layer-classification-testing-and-recovery/specs/scenarios/layer-testing-and-recovery-scenarios.md) with these revised expectations. These are future acceptance tests, not results.

| Experiment | Required observation | Recovery expectation | Tracking |
| --- | --- | --- | --- |
| Quoted hook inputs, empty args, globs, newlines, hostile command text | Exact allowed arguments arrive; data never executes as syntax; rejected inputs have reasons | Failed hook leaves explicit state; retries only under declared idempotency | BG-029 |
| Rapid child exits, simultaneous exits, exec failure, normal versus signal termination | Every owned child has one terminal record; startup failure is distinguishable under the chosen contract | No unbounded restart churn; control remains responsive | BG-028, BG-020 |
| Supervisor death, orphaned descendants, stale control request | No unrelated process is signaled; unknown ownership is exposed | Recovery/reconciliation is explicit, not guessed from a PID file | BG-028, BG-025 |
| Missing/inherited descriptors, dead or stalled logger, readiness writer from an old instance | Inheritance is bounded; stale readiness cannot release dependents; log blockage policy is observable | Report failure/loss/backpressure according to policy | BG-028, BG-008, BG-022 |
| Cycle, missing provider, deterministic graph output | Invalid candidate graph cannot silently replace a valid active definition | Preserve prior accepted configuration; explain path to failure | BG-021, BG-027 |
| Partial writes, concurrent changes, crash at publication boundaries | Atomic visibility and durability are measured separately on declared filesystems | Defined old/new/repair outcomes; never infer power-loss safety from process termination tests | BG-031 |
| Missing shell/library/rootfs/console and denied authority | Minimum recovery dependencies are enumerated and exercised in the relevant environment | Retain authorized diagnostics/control when possible; report unrecoverable cases honestly | BG-030, BG-025 |
| Stop timeout, teardown failure, failed final halt | Distinguish request accepted from task/service actually stopped | Do not report shutdown complete while required work remains | BG-024, BG-025 |

POSIX host runs must name OS, shell, runtime, and filesystem. BSD/illumos/Linux behavior requires actual platform runs; a mock only tests policy. Aether target checks require an agreed ABI and executable environment. Record size, memory, process count, startup and recovery measurements with fixed workloads before selecting the smallest viable arrangement.

## Requirement and follow-on handoff

| Earlier requirement | Documentary disposition in this handoff |
| --- | --- |
| REQ-SCB-001 | Satisfied with corrections: policy/argv capabilities and limits are explicit |
| REQ-SCB-002 | Satisfied as a semantics-based boundary; unsupported blanket C requirements withdrawn |
| REQ-SCB-003 | Satisfied: POSIX, BSD, illumos, Linux, Aether and package boundaries remain distinct |
| REQ-SCB-004 | Satisfied: scenario carry-forward, corrected recovery expectations, and host/target limits recorded |
| REQ-SCB-005 | Satisfied: primary-source comparison and access limitations recorded |
| REQ-SCB-006 | Satisfied: BG-028 through BG-031 capture newly scoped work; existing IDs cover readiness, graph, supervision, shutdown, logging, security, devices and companions |

New follow-ons: BG-028 runtime ownership/launch experiment, BG-029 shell hook conventions, BG-030 language/toolchain/minimal recovery runtime evaluation, BG-031 state publication and durability research. Open questions OQ-004 through OQ-006 remain open with clarified wording and routing; OQ-007 remains the cross-project boundary question.

BG-026 completes the unfinished documentary handoff of BG-013. It does not retroactively edit the archived workflow or claim a historical milestone audit. Next work is BG-025, then BG-027; implementation follows research-backed decisions as specified in the roadmap.

## Source audit and confidence

External sources were consulted on 2026-09-05. Open Group full-page requests returned 403; the citations above were checked through indexed primary-source passages. Shell quoting, signal guidance, rename and durability passages are Issue 8; shell/system wait details use explicitly identified Issue 7 passages. Do not read this as a full Issue 8 conformance audit. Moving branch documentation for OpenRC, illumos and systemd was read as observed, without asserting release-specific behavior. FreeBSD's returned rcorder page identifies its June 10, 2023 manual text. The runit and s6 pages were readable directly.

Local revision context at review: Aether HEAD `0ea1d0b83a43247874be2b306f68bbbc2f5a6cdd`; pkg-mgr HEAD `f9f5b16f890d7aa9d2f7f1594360cdf82116dc13`. Working files can differ from HEAD. Observed architecture-file SHA-256 values: Aether `29a4ccf15f08915939e3054d8bf38e1d4ba84a8df98e6e1cd8d1340b28496b40`; pkg-mgr `f8ff393d4ab0a208ad9ac22e57555bd09aee0e6c8b45972e153eda88103eef04`.

Confidence is sufficient for the corrected research handoff and experiment scope, not for a final language/process-layout choice. No runtime experiment, cross-OS result, performance result, or target integration is claimed.
