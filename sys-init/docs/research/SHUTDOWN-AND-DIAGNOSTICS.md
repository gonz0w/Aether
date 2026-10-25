# Shutdown, logging and diagnostics handoff

Observed 2026-09-05. BG-024 and BG-008 complete as comparative research and proposed requirements. No stop API, log format, CLI or production architecture is accepted by this document. The [boot/layout proposal](BOOT-AND-LAYOUT.md) and [readiness handoff](READINESS-AND-HEALTH.md) provide the existing vocabulary.

## Comparative findings

| System / primitive | Observed behavior | Lesson for sys-init |
| --- | --- | --- |
| POSIX signals and syslog | kill addresses a process or process group; syslog defines priority and identification options | Signaling is a primitive, not proof of complete service cleanup. Logging calls do not establish our durability contract. [Open Group kill](https://pubs.opengroup.org/onlinepubs/009604499/functions/kill.html), [syslog header](https://pubs.opengroup.org/onlinepubs/007904975/basedefs/syslog.h.html) |
| FreeBSD rc.shutdown | Selects shutdown-keyword scripts, reverses rcorder order and invokes faststop | Reverse ordering is understandable, but script selection and actual owned instances are different inventories. [FreeBSD rc manual](https://man.freebsd.org/cgi/man.cgi?query=rc&sektion=8&format=html) |
| Linux systemd | KillMode scopes termination; ordinary signaling can escalate after a stop timeout. Control-group and main-process modes differ | Ownership scope must be explicit. Linux cgroups cannot be assumed for a portable adapter. [Upstream kill manual](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.kill.xml) |
| illumos SMF | Stop methods must tolerate partially stopped services; failure means not entirely stopped. Restarter state, auxiliary reasons and per-service method logs are exposed; early logs use volatile storage | Keep observed state separate from method return and preserve a reason when cleanup fails. [illumos restarter manual](https://raw.githubusercontent.com/illumos/illumos-gate/master/usr/src/man/man8/svc.startd.8) |
| s6-log | Reads service output, rotates logs and can bound a final partial-line wait. Its blocking mode trades throughput for flushing; the manual warns of unbounded buffers in its default mode under slow storage | Loss, blocking and memory growth are explicit tradeoffs. Adopt bounded behavior rather than copying defaults. [s6-log manual](https://skarnet.org/software/s6/s6-log.html) |
| systemd journal | Offers volatile, persistent, automatic and disabled storage, with early volatile operation and later flush | Structured history and early operation are useful independently of choosing a journal format. [Upstream configuration manual](https://raw.githubusercontent.com/systemd/systemd/main/man/journald.conf.xml) |

These are primary manuals/source observed today, not executed comparisons. Moving branches are not pinned releases. Open Group full-page requests failed; only indexed primary excerpts were available, so the POSIX claims above are deliberately narrow. Direct FreeBSD rc.shutdown/source fetches failed; the rc(8) shutdown section was available. No assumptions about portable reboot, process-tree containment or storage durability follow from this survey.

## Proposed stop transaction

A shutdown request names its scope and intended final action: stop selected services, switch profile, halt or reboot. Authorization is separate from that request's name. Full-system final action belongs to a platform adapter with explicit authority, not every service supervisor.

1. Allocate an operation identity and freeze its configuration/graph view. Close admission for new ordinary starts, readiness and restart timers in scope. Retain ownership of in-flight starts, probes, hooks and tasks; observe a launch completing after cancellation and include it in cleanup.
2. Build the stop inventory from actual owned generations, including manually started services and definitions removed since launch. A disabled or removed service is not evidence it stopped. Keep launch-time cleanup metadata available through package changes.
3. Order consumers before providers where the consumer actually needs the provider during stop. Startup ordering, readiness evidence and retained stop dependencies are distinct edge meanings. One-shot completion has no implicit inverse action. Cleanup hooks must be declared, bounded and safe after partial initialization.
4. Request cooperative stop when supported. A hook's successful return records hook success; terminal observation and required resource release establish lifecycle completion. Bound the hook itself, including its output and children. Do not send broad process-name kills.
5. At the service deadline, escalate only within owned scope and available authority. Record forced termination separately from graceful completion. Signal submission or destroy-request acceptance alone does not prove every owned task/resource is gone.
6. Observe terminal outcomes and reclaim resources. Preserve unresolved ownership and error evidence if cleanup fails. On the Aether v1 fixture, destroy, release and terminal acknowledgment are separate steps; a terminal record alone cannot authorize backing reuse.
7. Drain diagnostic producers before their collectors, then storage dependencies, within a separate finite budget. Preserve a minimal control/diagnostic route for final handoff. Request platform halt/reboot only with its defined prerequisites and escalation policy.

Each service deadline is capped by the overall operation deadline. Parallel independent stops may reduce delay; concurrency and scheduling limits still need measurement. Client messages and repeat shutdown requests cannot extend the budget implicitly. Repeated identical requests should observe the same operation; changing to a more forceful policy requires a separately authorized action. No numeric defaults are selected here.

If a consumer refuses to stop, a normal operation reports blocked/incomplete and retains providers it still needs where possible. At the global deadline an explicitly configured emergency policy may sacrifice those dependencies and request forced shutdown; it must report that loss of ordering/cleanup assurance. Absence of force authority leaves shutdown incomplete. Never invent a successful halt outcome because a request was issued.

Cycles in required stop edges should be rejected during validation. A runtime cycle or incomplete graph still needs a bounded emergency policy: identify the cycle, attempt independent work, retain owned instances, then apply only authorized escalation. Deterministic arbitrary ordering is not a proof that dependencies were honored.

Excluded services need explicit ownership and survival scope. A per-service stop may leave shared providers running. A machine shutdown cannot promise a service survives poweroff; excluded hooks do not exempt its tasks from final platform teardown. Preserve diagnostics/control late through explicit dependencies rather than an undocumented immortal service list.

## Logging choices and failure behavior

Keep authoritative runtime state, manager transition history and untrusted service output distinct. Human-readable text is a useful baseline; structured records can supply stable fields without making a database necessary for status. Format selection remains BG-045.

| Candidate | Benefit | Cost / required limitation |
| --- | --- | --- |
| syslog forwarding | Familiar integration and central routing | External sink availability; no implied durable receipt or current-state authority |
| Service-local files | Easy inspection with ordinary tools | Per-service permissions, rotation, full disks and reopen handling; direct service writes may block |
| Supervised output pipes | Manager can assign source identity; separate logger process | Pipe saturation, inherited writers, logger death and output framing need explicit policy |
| Structured journal | Indexed correlated history | Reader/format dependency and recovery complexity; optional export must remain possible |
| Fixed-capacity memory ring | Early boot and bounded storage | Overwrites history and disappears on reset; expose lost-record counts |
| Console / boot channel | Minimal failure visibility where authorized | Can stall, disappear or expose sensitive text; cannot be the sole assumed working path |

Propose a bounded manager-owned transition buffer with sequence numbers and loss counters, plus optional independently drained sinks. Never synchronously wait for a service logger, filesystem or console in the lifecycle control path. A slow status subscriber gets a bounded snapshot or disconnect; it cannot hold up stop/reap. This is a requirement for prototypes, not an existing nonblocking guarantee.

For service output, choose and declare a policy: bounded buffering followed by counted drops, deliberate application backpressure, or service failure on logging failure. No system can guarantee unlimited lossless output, bounded memory and nonblocking producers simultaneously. Manager diagnostics should favor bounded progress; audit-critical applications may require a different explicit policy. Test logger exit, broken pipes and replacement: swapping a logger does not automatically preserve the old stream or every writer.

Reserve bounded capacity for manager failure summaries so noisy application output cannot consume it all. Truncate or frame oversized output with an explicit marker; escape terminal control characters in human views. Attach service/generation identity from the manager's channel mapping, not text supplied by the service. Do not record environment secrets, grant values or entire configuration blobs by default. Restrict service-log and control access separately.

Use a boot identity plus increasing manager sequence for local order; monotonic observation time is useful when supported, wall time optional. Record clock unavailable rather than fabricate timestamps. Multi-writer arrival order is not global causality. A restart must not present old observations as live status.

The existing candidate `/run/sys-init/` and `/var/log/sys-init/` paths remain proposals. BG-044 must specify byte/file/count/age limits, ownership, safe file creation, rotation, low-space behavior and export. Retention cannot depend only on age because clocks can change. Volatile-to-persistent copying needs a defined cursor/duplicate policy; a successful write is not a claimed durable commit. BG-031 retains crash-consistency questions.

## Operator-visible outcome

A status response should expose desired state, observed lifecycle state, generation, readiness evidence, health freshness, current operation, last terminal reason, cleanup status and diagnostic-loss count. Unknown is distinct from stopped. A failure explanation should identify the blocking service/edge, failed step, elapsed/deadline information when available and the next action allowed by policy.

Illustrative output content, not accepted CLI syntax:

```text
shutdown operation 12: incomplete
web generation 7: forced stop observed; cleanup complete
database generation 3: stop timed out; resource release unresolved
log collector: drain budget expired; 42 records dropped
platform reboot: not requested; unresolved cleanup requires emergency policy
```

Boot failure reporting must work without persistent storage or a shell where an authorized diagnostic route exists. If no route remains, record that recovery limitation in the contract; there is no universal emergency console. A status command is a client of runtime evidence, not an interpreter that guesses state from log strings. BG-045 owns status/boot failure UX, including restricted read-only access and stable machine results.

## Required future tests and native gate

| Scenario | Expected evidence |
| --- | --- |
| Shutdown races launch/ready/restart | Admission closed; late owned task included; no replacement silently starts |
| Definition removed or disabled while running | Existing generation still inventoried and stopped |
| Hook succeeds but worker/descendant survives | Not reported clean; ownership limitation exposed |
| Hook hangs or floods output | Budget enforced; control remains responsive |
| Consumer times out; stop graph has cycle | Blocker/cycle visible; only configured escalation breaks ordering |
| Stale identifier or authority denied | No unrelated task affected; incomplete outcome |
| Logger dies, disk fills, console stalls | Bounded memory/control latency; lost data or blocked producer policy visible |
| Child retains log pipe; no final newline | Drain deadline respected and truncation/loss reported |
| Shutdown repeated; configuration changes mid-stop | Stable operation identity and inventory; no deadline reset |
| Cleanup fails after terminal observation | Ownership retained; no premature resource reuse or clean-shutdown claim |
| Poweroff/reboot denied or returns failure | Final handoff failure remains observable |
| Old status, malicious output, subscriber stalls | No false live state, trusted-field spoofing or control-loop blockage |

These are acceptance scenarios, not passing tests. The [pinned lifecycle v1 contract](../evidence/lifecycle-v1-2026-09-05/AETHER-M4-LIFECYCLE-V1.md) explicitly excludes cooperative shutdown, DMA, SMP restart and persistent recovery. Its single-worker forced destroy and kernel serial diagnostics do not provide general service stop, filesystem flush, native logging or platform reboot authority. The [native client result](../LIFECYCLE-V1.md) remains unchanged.

Before a native shutdown experiment, Aether must supply the intended cooperative request, terminal/reclaim contract for all owned resources, deadline facility, final platform authority and available diagnostic route. BG-032/BG-033 retain those questions. POSIX process groups, Linux cgroups, illumos contracts and native Aether handles need separate ownership adapters; they are not interchangeable containment proofs.

Follow-ons captured before completion: BG-043 stop transaction/deadline prototype; BG-044 bounded logging/retention experiment; BG-045 status and boot-failure interface. Coordinate BG-028 ownership, BG-029 hooks, BG-031 durability, BG-038 transitions, BG-039 layout and BG-042 dependency evidence. Next independent research: BG-009/BG-015 security, resource ownership and devices.
