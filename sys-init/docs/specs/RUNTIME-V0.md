# Runtime semantics v0 — model profile

2026-09-05. BG-023's specification draft, informed by BG-016 and the completed research handoffs. [Decision 0002](../decisions/0002-runtime-model-profile.md) accepts these clarified semantics for a bounded deterministic model only; they remain candidate requirements for a real runtime, not an implemented feature list. Decision 0001 remains limited to the existing Aether lifecycle fixture.

## Shared standards boundary

[Foundations](../STANDARDS.md) owns shared authority/interface/evidence rules; [Experience](../EXPERIENCE.md) owns presentation, help/version, streams and new exit conventions; [Distribution](../DISTRIBUTION.md) supplies the proposed shared descriptor/profile requirements. R-01–R-18 remain sys-init-owned model semantics with narrower experiment limits. Exact CLI work must apply those pinned rules rather than introduce competing defaults. Future shared revisions belong in Aether-standards; existing machine contracts and historical evidence remain preserved.

## Initial scope

The first useful host prototype should manage a finite, validated graph of foreground long-running services and explicit one-shots: start, readiness, bounded restart, stop, observation and explanation. Use a fixed configuration revision for a run. Keep implementation language, process layout, wire format and metadata encoding open until the experiment decision.

Defer dynamic package activation, live graph reload, arbitrary hooks, readiness protocol compatibility, automatic health recovery, socket/calendar activation, devices/mounts, isolation profiles and machine power control. These require their own accepted contracts. Health is initially unknown/reporting-only. Diagnostic loss must be visible, but a full journal is unnecessary.

| Profile | What can be demonstrated |
| --- | --- |
| Deterministic model | Transition/order rules with synthetic time and events; no OS ownership proof |
| POSIX host experiment | Real foreground child launch/observation and a selected readiness transport, with exact platform limits stated; not production PID 1 |
| Aether lifecycle v1 | Existing fixed single-worker conformance trace only; no general graph, readiness, shell or user clock |
| Future native runtime | Requires accepted loading, authority, events/deadlines and cleanup contracts before applying this draft |

## Identity and state

R-01. Keep service ID, effective definition revision, boot/manager epoch, launch generation and operation ID distinct. Adapter handles authorize operations; textual IDs do not. Generation identity must remain unambiguous across replacement. Epoch changes invalidate old runtime observations.

R-02. Expose separate dimensions: desired state (running/stopped), observed lifecycle (absent, starting, running, stopping, terminal, unknown), readiness evidence, health freshness, cleanup (not-needed, pending, complete, failed/unknown) and current operation. Blocked dependencies, restart delay and exhausted restart budget are scheduling reasons, not fake process states. A terminal generation remains inspectable after resources are reclaimed, within declared retention bounds.

R-03. Running means execution is observed under the adapter's contract, not application readiness. Absent requires known lack of owned instances/resources; uncertainty stays unknown. One-shot successful completion is recorded separately from ongoing execution.

## Graph and admission

R-04. Validate missing references, required policy support and ordering cycles before side effects. Plan against an immutable graph revision. A plan shows potential work, not a reservation or a guarantee that future starts succeed.

R-05. Initial dependency edges are `requires(provider, evidence)` and `after(provider)`. Requires includes the provider in the activation closure and gates admission on explicit evidence. After orders startup attempts only when both services are selected; it neither selects the provider nor requires its success. Its barrier opens when the provider's startup attempt reaches a success or failure outcome, not merely when a request is queued. The union of initial ordering constraints must be acyclic. A blocked/rejected attempt also has a terminal scheduling outcome, so an after-only consumer cannot wait indefinitely for a launch that will never occur. Optional/wants edges remain deferred.

R-06. Initial evidence is `started`, `notified-ready` for long-running services and `completed` for one-shots. A service declares its startup milestone; its own start operation waits for that milestone. Dependencies may deliberately request weaker started evidence, but may not silently substitute it for notified-ready. Unsupported transports reject configuration. Activation session means one fixed graph revision within a manager epoch, shared across CLI calls. Reuse completed evidence within that session; explicit stop invalidates it, permitting a deliberate later start to rerun the one-shot. New revisions/epochs invalidate it. A provider declaring started cannot supply notified-ready evidence in the initial profile. A notified-ready provider retains its startup deadline even when weaker started edges admitted consumers.

R-07. Before dispatch, recheck the current generation's required evidence. Known terminal, stop or timeout wins over pending readiness. A dependency failing before admission blocks consumers. If it fails after a consumer starts, report dependency loss and block new admissions; do not automatically stop/restart already-running consumers in the initial profile. Consumers must handle provider loss. Recovery of the provider may unblock waiting work within its original operation deadline.

## Launch, readiness and restart

R-08. Resolve the effective policy and prepare resources before executing the service. Failure of a required restriction rejects launch. Roll back acquired resources or retain an explicit cleanup failure. Every child/helper belongs to a declared ownership scope; unsupported descendant containment must be visible in the profile.

R-09. A notified-ready launch receives fresh authority bound by the manager to its generation. Late/stale notifications cannot satisfy a replacement. Accepted notification is idempotent; EOF without a valid frame is not readiness. The transport decision must define framing, authorized helper delegation, bounded parser work and the setup race. Startup has a finite manager-owned monotonic deadline. At its boundary timeout wins; no implicit client extension.

R-10. Initial restart modes: `never` and `on-failure` for long-running services. One-shots never retry automatically. Failure includes nonzero exit, fault, startup timeout and an adapter-reported launch failure after admission; invalid configuration/denied required authority is a permanent rejection. Successful exit does not restart under on-failure. Operator stop, shutdown and dependency-loss reporting do not count as a crash and cannot trigger restart.

R-11. Require explicit finite retry count N and fixed retry delay D for on-failure in the experiment profile; N counts automatic replacement launches after the initial launch. Cleanup must complete before consuming the next retry and launching. No retry-budget reset on readiness or brief survival. Budget exhaustion remains visible until a new explicit activation after the previous operation finishes. A repeated start while running/starting joins or observes existing work; it does not reset N. After successful activation, retry policy belongs to desired-running service state rather than the completed start operation. Automatic replacements continue only while desired state is running. Stop cancels pending delay. Numerical defaults and adaptive backoff are deferred.

R-12. Startup-operation failure is final when its budget/deadline is exhausted. Partial graph success remains running and is reported; there is no automatic graph-wide rollback. On operation deadline, cancel queued starts and automatic retries owned solely by that operation; stop/reclaim its still-starting generations using a separate bounded cleanup budget. Suppress retries for unfinished participants until a later explicit start. Already successfully activated services remain running. Still-initializing providers are cancelled even if a weaker started edge already admitted a consumer; that consumer remains running with dependency loss. Cleanup exceeding its budget produces an incomplete result with retained ownership, not a successful cancellation.

## Stop and operations

R-13. Validate stop scope before any state change; rejection preserves desired state and timers. Accepted stop changes current desired state to stopped, closes readiness/restart admission and inventories actual generations plus in-flight starts. It does not change persistent enablement. Initial stop order is consumer-before-provider for live requires edges, a conservative profile choice; after-only startup edges imply no stop requirement. Reject a provider-only stop when a desired-running required consumer is starting, running or retry-pending outside scope; expose the expanded plan for a separately requested closure stop. Queued consumers in the same operation must be cancelled or included; unrelated overlapping operations conflict. Force/cascade convenience flags are deferred.

R-14. Cooperative request, forced termination, terminal observation and cleanup are separate steps. Stop success requires cleanup completion for the declared ownership scope. A hook exit or accepted kill request alone is insufficient. Bound stop and cleanup independently, preserve failures and never reuse unresolved backing. Restart is successful stop/reclaim followed by fresh launch; failed cleanup prevents replacement. In the initial profile, restart accepts only an owned live long-running generation; one-shots and absent services reject it without side effects.

R-15. A state-changing request returns an operation ID and whether it was accepted. Completion distinguishes success, failure, incomplete cleanup, cancellation and unknown. Serialize conflicting mutations in the initial profile: reject a conflict with the active operation ID, except a stop may supersede a pending start/retry using the defined cancellation path. A late launch completion after supersession remains owned and is stopped/reclaimed before any replacement. Joining identical requests must not extend deadlines. Client disconnect or client wait timeout does not cancel manager work. Request replay after an ambiguous connection result needs deduplication; exact transport/storage scope is BG-050.

R-16. Shutdown closes activation admission for its entire scope, resolves in-flight work and uses actual ownership, not only enabled definitions. The host prototype stops only its owned experiment services; it must not invoke system-wide kill, reboot or halt. Full-machine shutdown and emergency bypass wait for native authority/cleanup decisions.

## Diagnostics and operator surface

R-17. Current status comes from manager state, never by scraping service logs. Include revision/epoch/generation, desired and observed states, readiness/health, operation, last terminal reason, cleanup result and loss count. Explain missing prerequisites and failed steps with stable reason identifiers plus readable context. Untrusted output cannot populate trusted identity fields.

R-18. Bound logs, control queues, subscribers and parsing. Preserve lifecycle progress if an optional sink stalls; report drops. No secrets or usable grant values in default output. Status-read authority and mutation authority are separate. Missing runtime means unavailable/unknown, not all services stopped.

Candidate commands below use `initctl` as a placeholder name only:

| Command | Completion meaning |
| --- | --- |
| check / plan | Offline validation or proposed work; no activation |
| list / status / explain | Snapshot or reason retrieval; command success does not imply service health |
| start SERVICE | Include required closure and wait for declared milestones unless explicitly asynchronous |
| stop SERVICE | Current desired state stopped and owned cleanup complete; report scope conflict |
| restart SERVICE | Stop/reclaim then fresh launch; no implicit reset of persistent policy |
| operation ID / wait ID | Inspect or wait for manager operation; timeout reports ID and continuing/unknown state |

Default mutation calls should wait for a finite client budget; an explicit asynchronous form returns accepted status only. Exact options, exit codes and machine schema remain BG-050/BG-045. Enable/disable belong to the later profile-persistence contract and must not implicitly start/stop. Reload and rescue are unavailable until their contracts exist, not aliases that silently restart or launch a privileged shell.

## Worked conformance examples

| Trace | Required result |
| --- | --- |
| setup one-shot exits 0; database notifies; web requires both | setup completed, database ready, then web admitted; web's milestone determines start completion |
| database launched but remains silent until startup deadline | no ready evidence; web blocked; database stopped/reclaimed; operation fails or retries within explicit budget |
| database generation 1 faults; late ready arrives while generation 2 starts | old message rejected; web remains blocked until current generation's evidence |
| N=2, D=10 synthetic time units; initial launch and two replacements fail | exactly three launches, two delays, exhausted budget; readiness does not grant more retries |
| web running when database dies | report dependency loss; web remains owned/running; new dependents blocked; database policy may retry |
| operator stops database while web requires it | scope conflict with explanation; no hidden consumer stop |
| closure stop includes web and database; database cleanup fails | web stops first; database reported terminal with incomplete cleanup; no successful restart |
| CLI times out after receiving operation 12 | show operation 12 and client wait timeout; manager still owns work |
| graph activation deadline expires after setup completed but database still starting | keep setup evidence for this session; cancel queued web, stop/reclaim database, report failed/incomplete operation |
| log sink fails during stop | bounded loss count, lifecycle observation continues; no claim logs were durable |

The [BG-053 result](../RUNTIME-MODEL.md) now records bounded model tests against these rules; real process/transport cases remain unimplemented. BG-017 must translate R-01–R-18 into model, real-process and target checks, including invariants under event permutations. BG-052 owns contradictions and unresolved semantic decisions discovered during that work.

## Evidence and remaining decisions

This draft synthesizes [operator research](../research/OPERATOR-INTERFACE.md), [readiness](../research/READINESS-AND-HEALTH.md), [shutdown/diagnostics](../research/SHUTDOWN-AND-DIAGNOSTICS.md), [security/events](../research/SECURITY-RESOURCES-AND-EVENTS.md), [boot/layout](../research/BOOT-AND-LAYOUT.md) and [package boundaries](../research/PACKAGE-SERVICE-CONTRACT.md). It narrows alternatives for an experiment without replacing their recorded risks.

BG-050 command/request contract; BG-051 recovery workflow; BG-052 semantic review/acceptance were captured before closing BG-016/BG-023. Coordinate existing BG-040 readiness transport, BG-042 graph evidence, BG-043 stops, BG-045 status and BG-046 enforcement. Decision 0002 and the [test strategy](TEST-STRATEGY.md) now define the next bounded deterministic experiment (BG-053). Real process/transport decisions and production acceptance remain open. General Aether loading, deadlines, readiness and supervisor recovery remain BG-032/BG-033; pkg-mgr activation/enablement remains BG-035–BG-037.
