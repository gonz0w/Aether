# Readiness and health handoff

Observed 2026-09-05. BG-007 and BG-022 are completed together as research; both IDs remain traceable. This proposal supersedes the readiness candidates in the archived touchpoints report. It does not accept a wire protocol or implement readiness on Aether.

## Findings from prior art

| Evidence | What it establishes | Consequence for this proposal |
| --- | --- | --- |
| POSIX pipe/read primitives | A pipe has read/write descriptors; a read returns EOF when no writer remains | A private inherited channel is a plausible portable transport. EOF is not a readiness assertion. [POSIX pipe](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pipe.html), [read](https://pubs.opengroup.org/onlinepubs/9799919799/functions/read.html) |
| s6 notification descriptor | Daemon writes a newline; supervisor publishes ready state separately from spawned state. A check-command adapter exists | Direct notification is a small candidate, with a fallback for unmodified programs. [s6 manual](https://skarnet.org/software/s6/notifywhenup.html) |
| systemd notification | READY=1 reports completion; NotifyAccess controls acceptance. Short-lived helper attribution can race; barriers address reception. WATCHDOG=1 is a separate keepalive field | Transport success and authorized manager acceptance differ. Compatibility requires more than parsing READY=1. [Upstream manual source](https://raw.githubusercontent.com/systemd/systemd/main/man/sd_notify.xml) |
| FreeBSD rc.subr | PID-file/process checks establish a matching running process; default status reports process status | Preserve these useful legacy observations without calling them application readiness. Custom status commands must state their stronger contract explicitly. [FreeBSD manual](https://man.freebsd.org/cgi/man.cgi?query=rc.subr&sektion=8&format=html) |
| illumos SMF methods | Start methods must delay return until functional; methods have timeouts and categorized exit statuses | A method can represent readiness when its author fulfills that contract. Arbitrary successful script return is weaker. [illumos source manual](https://raw.githubusercontent.com/illumos/illumos-gate/master/usr/src/man/man7/smf_method.7) |
| systemd socket activation | Manager-created sockets can activate services; connected sockets or listeners are passed according to the activation mode | Endpoint admission can precede application initialization. Label activation availability separately. [Upstream socket manual](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.socket.xml) |

Source access limitations: rendered systemd manuals returned 403, so upstream XML was reviewed. The illumos rendered page failed; its upstream manual source was reviewed. Open Group full-page fetches failed; only indexed primary-source excerpts for pipe/read were available, so no detailed clock or descriptor-inheritance guarantees are inferred from them here. Upstream main-branch references describe the observed manuals, not pinned deployed releases. No surveyed init was executed during this research.

## Proposed evidence vocabulary

Avoid a single strength number: successful work completion and an accepting endpoint prove different properties. Use explicit evidence kinds, selected by the service declaration and consumed by the dependency requirement. These names are conceptual, not descriptor syntax.

| Kind | Evidence | Does not prove |
| --- | --- | --- |
| started | Runtime accepted launch (with exact adapter definition, such as successful exec) | Initialization, usable API or sustained liveness |
| completed | Declared one-shot invocation exited successfully | A persistent service remains available; produced state remains valid forever |
| notified-ready | Authorized participant asserts the declared application boundary | Truthfulness, future availability or every possible operation |
| probed-ready | A bounded check exercised a declared predicate against the current instance | More than that predicate; identity if the endpoint cannot identify its owner |
| activation-available | Manager owns the declared usable admission endpoint | Worker initialization, database migrations, successful request completion |
| legacy-running | PID/process/status evidence under an explicit compatibility mode | Application readiness or stable instance ownership |

A service requiring application readiness must not silently accept started or legacy-running evidence. A legacy package may explicitly choose weaker startup ordering, with that choice visible in status. Missing adapter support is a validation error rather than an automatic downgrade. BG-035 should eventually validate these declarations; no package schema is selected here.

## Candidate transport and author experience

A fresh inherited write descriptor per launch is the leading POSIX-host candidate for notified-ready. A daemon can optionally receive its descriptor number and write one short readiness frame after initialization; shell wrappers can pass the descriptor through an exec. A wrapper must not announce readiness merely because it backgrounded a daemon. Direct notification needs no service-specific library.

Prototype two alternatives before selection: exact newline (s6-shaped simplicity) and a bounded versioned message. Define frame length, malformed input, duplicates, partial reads and close behavior. Do not settle these by implementing a permissive parser first. Separate readiness from logs and arbitrary status text.

Descriptor possession is delegated authority, not a proof of writer PID. A forked helper inheriting the channel can signal; use a new channel for every generation and restrict inheritance to the intended participants. A leaked writer can delay EOF and can lie about readiness. A timeout bounds the wait but does not fix authority leakage. Main-process-only authentication would require another mechanism or platform-specific credentials. This is a design risk for BG-040.

A notify-socket compatibility adapter is secondary. It must specify sender attribution, helper lifetime, supported fields and ignored/rejected fields; do not advertise full sd_notify compatibility after implementing READY=1 alone. Linux credential/cgroup machinery must not enter the portable core by assumption. BSD and illumos adapters need their own authority evidence. Native Aether would use an explicitly granted endpoint or equivalent kernel facility rather than pretend handles are POSIX descriptors.

PID files, endpoint-path existence and generic process status remain compatibility observations. A TCP connect alone can reach a queued listener before the worker serves anything. A probe should exercise the minimum useful application operation, be side-effect-free where possible, and explain how it targets this generation. An unbound external endpoint probe must be labeled as external availability, not credited to a replacement service instance.

## Proposed lifecycle rules

The manager owns a launch identity, readiness evidence, a startup deadline and an independently tracked health observation. Service ID plus fresh generation identifies a launch; PID or a client-supplied generation number alone does not authorize a message.

1. Before launch, create fresh readiness authority and initialize state to starting/health unknown. Map the authority to the generation in manager-owned state.
2. Accept evidence only for the current starting generation, from its authorized channel/participant, while the startup deadline is open and stop/terminal state is not already known. Repeated accepted evidence is idempotent.
3. On timeout, stop request or terminal observation, close readiness admission for that generation before processing further readiness messages. In a batch where terminal and ready are both known, terminal wins. At the deadline boundary, timeout wins. These are proposed deterministic manager rules, not claims about kernel event ordering.
4. A running service's terminal event invalidates its active readiness. A one-shot's successful completion is separate recorded evidence whose lifetime and invalidation must be specified with the graph/configuration revision.
5. Replacement gets fresh authority and no inherited readiness. Late messages and probe results from the old generation cannot release dependencies of the new one.
6. Dependency admission rechecks current evidence before dispatch. There is still a race between observation and future provider failure; consumers need error handling. Readiness cannot promise a provider stays alive after admission.

Startup timing should use a manager-owned monotonic deadline and bounded input/probe work. Client timestamps must not extend it implicitly. Numeric defaults, suspend behavior, extension limits and native clock semantics remain unresolved. Aether's fixture watchdog is not that contract.

Once readiness was accepted, health observations may become healthy, degraded, unhealthy or unknown without rewriting the historical readiness event. Current availability and admission policy can change, but restarting a provider, stopping existing dependents and blocking new dependents are separate explicit policies. Health success must not reset crash-loop accounting automatically. Start with reporting-only health as a candidate; recovery actions require BG-041 and supervision research.

A health probe needs an interval, timeout, bounded output, one-in-flight limit, generation association and cancellation on stop/replacement. Record observation time, freshness, failure reason and consecutive outcomes; stale data becomes unknown. A heartbeat shows that its sender ran, not that the application served a request. Thresholds and recovery hysteresis must be explicit, not invented in the transport adapter.

## Race and failure acceptance matrix

These are required future tests, not tests run in this handoff. BG-040 owns transport cases; BG-041 owns health cases; BG-042 owns graph cases.

| Scenario | Required outcome |
| --- | --- |
| Spawn succeeds, initialization is delayed | A notified-ready dependent remains blocked |
| Notification arrives before launch registration finishes | Manager preserves or rejects it deterministically; never loses a valid registered launch through an unexamined setup race |
| EOF with no complete frame | Startup is not marked ready; report closed channel |
| Partial, oversized or malformed frame; sustained junk | Bounded parser/resource use and a diagnostic; no readiness from malformed input |
| Duplicate valid frame | At most one readiness transition |
| Child inherits writer; main exits | Known terminal state prevents child notification from reviving readiness; inheritance policy is tested |
| Ready and terminal are observed together | Terminal wins; no dependent admitted from stale evidence |
| Ready arrives at/after deadline | Timeout wins; late input cannot revive generation |
| Stop races ready | Closed admission remains closed |
| Generation N probe/notification arrives during N+1 | Rejected for N+1 even if PID/descriptor numbers were reused |
| Probe connects to an old/external endpoint | Cannot assert readiness of the new instance without binding evidence |
| Activation listener exists while worker initializes | Only activation-available requirement is satisfied |
| One-shot succeeds, then configuration is replaced | Completed evidence is invalidated according to graph revision policy |
| Health probe hangs, floods output or outlives replacement | Bounded resources; cancellation/reaping; old result ignored |
| Health toggles or provider fails after dependent admission | Explicit hysteresis/failure policy; no accidental restart cascade |
| Wall clock jumps or supervisor resumes late | Deadline uses specified monotonic semantics; overdue work does not become successful |

## Aether boundary and next work

The [consumed lifecycle v1 contract](../evidence/lifecycle-v1-2026-09-05/AETHER-M4-LIFECYCLE-V1.md) supplies identity, termination and reclaim/acknowledgment. It explicitly excludes readiness and a user deadline API. The [passing native experiment](../LIFECYCLE-V1.md) therefore remains a lifecycle proof. Yield, task start and successful reclaim are not readiness messages.

A next readiness fixture would need: a service-accessible scoped send authority bound to the launch; defined receive/terminal ordering and queue limits; cancellation/revocation; bounded wait with specified clock semantics; a worker that delays, notifies, faults and sends stale messages under controlled cases. BG-032 owns the kernel contract questions. A host experiment can test policy and POSIX descriptors now, but cannot validate native transport or time semantics.

Follow-ons captured before completion: BG-040 (transport/authority prototype), BG-041 (health observation and recovery policy), BG-042 (dependency evidence and invalidation contract). Coordinate BG-029 shell hooks, BG-035 descriptors, BG-020 supervision and BG-021 graph work. Next independent research remains BG-024/BG-008 shutdown, logging and diagnostics; production readiness architecture is still undecided.
