# Security, resources and event integration

Observed 2026-09-05. BG-009/BG-015 research handoff. These are proposed semantic requirements and adapter boundaries, not accepted policy syntax, sandbox implementations or native device support.

## Comparative evidence

| Platform / source | Observed facility | Boundary for sys-init |
| --- | --- | --- |
| POSIX [setuid](https://pubs.opengroup.org/onlinepubs/009604599/functions/setuid.html), [resource limits](https://pubs.opengroup.org/onlinepubs/7908799/xsh/getrlimit.html) | Identity changes and calling-process resource limits; setuid does not change supplementary groups | Explicit identity/group handling and limit scope are necessary. A process limit is not an aggregate service budget |
| FreeBSD [Capsicum](https://docs.freebsd.org/en/books/handbook/security/#capsicum), [jails](https://docs.freebsd.org/en/books/handbook/jails/) | Descriptor-based capabilities and a separate jail isolation model | Object authority and container isolation are distinct policies, not alternate spellings of UID |
| illumos [privileges](https://smartos.org/man/7/privileges), [resource controls](https://smartos.org/man/7/resource_controls) | Effective/permitted/inheritable/limit sets; controls at process, task, project and zone scopes | Declare privilege transition and accounting domain, rather than importing one generic capability or memory-limit field |
| Linux [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) | Hierarchical process membership and resource controllers; controller availability/delegation matters | An adapter can offer aggregate enforcement when the required hierarchy and controller exist. It is not a portable syscall or a complete sandbox |
| FreeBSD [devd](https://man.freebsd.org/cgi/man.cgi?query=devd&sektion=8&format=html) | User-space policy reacts to kernel events and multiplexes device notifications | A separate event service is a useful boundary; a notification is input to policy |
| Linux [udev](https://raw.githubusercontent.com/systemd/systemd/main/man/udev.xml) | Event tasks are short-lived; long-running daemons belong in service management | Avoid blocking the event worker with service lifetime ownership |
| Apple [launchd guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html) | On-demand jobs and socket check-in | Admission endpoints can trigger work without making arrival equivalent to application readiness |
| systemd [timers](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.timer.xml) | Monotonic and calendar triggers differ, including suspend behavior | Scheduling policy requires explicit clock/missed-event semantics; lifecycle deadlines are a separate use case |
| Linux [managed device resources](https://docs.kernel.org/driver-api/driver-model/devres.html) | Driver resource lifetime can be tied to detach cleanup | Resource bookkeeping is a kernel/driver concern; this alone establishes no cross-platform DMA-quiescence guarantee |

Sources are project manuals or upstream documentation, not tested adapters. FreeBSD cap_enter/capsicum manual requests and the illumos upstream privileges source failed; the FreeBSD handbook and SmartOS distribution's illumos manuals were available. POSIX evidence is indexed primary-source text from the linked older editions, not a complete current-edition conformance review. Apple material is archived guidance. Moving branches are not pinned releases. No sandbox or device test was run.

The [SMF findings](SHUTDOWN-AND-DIAGNOSTICS.md) additionally show a restarter managing service state and method outcomes. Event policy should request that lifecycle management rather than bypass it.

## Threat and ownership model proposal

Assume a service may crash, fork helpers, flood output/events, retain inherited resources, lie about readiness or attempt access beyond its grants. Packages and event payloads do not gain activation authority merely by supplying text. Trusted bootstrap/configuration and the enforcing kernel remain explicit trust roots; this project does not claim to contain a compromised kernel.

Separate installation ownership, desired-state authority, launch identity, object authority and accounting ownership. A service name or PID is not an authorization token. The manager binds each launch to an immutable effective-policy revision, owned resources, assigned observer/control rights and its terminal/cleanup evidence.

The core should validate requested policy against an adapter's supported guarantees before launch. Each field needs: resource/action, subject and scope, hard enforcement versus advisory behavior, units, inheritance, failure outcome and cleanup owner. Required policy that cannot be enforced must reject launch. Optional policy may be omitted only through an explicit declaration, with the omission visible in status. Never silently replace a hard aggregate memory cap with an advisory process limit.

| Candidate policy family | Required specification before implementation |
| --- | --- |
| Identity | User/group resolution, supplementary groups, saved identity and privilege transition; no fallback to privileged identity when lookup/setup fails |
| Object grants | Exact objects and rights, permitted delegation/inheritance, holder identity, revocation and cleanup; diagnostic views must not expose usable grant values |
| Resource budget | Per-process versus service aggregate scope; hard cap versus scheduling weight; accounting for helpers, shared objects, queues and retained terminal resources |
| Filesystem view | Allowed objects and lookup rules, working directory, read/write access; a changed root directory alone is not accepted as a complete containment boundary |
| Isolation profile | Named, versioned platform guarantee for a jail, namespace/other Linux profile, zone or native capability domain; no generic promise that these are equivalent |
| Control requests | Separate read-only status, per-service lifecycle changes, grant changes and final shutdown authority; authenticate caller and target generation |

A launch transaction should prepare owned resources, apply and verify required restrictions, then admit service execution. Partial setup must not fall through to unrestricted launch. Exact sequencing differs by adapter: identity changes can remove authority needed to apply later restrictions, while some mechanisms require preopened objects. Record a rollback/reclaim path for each acquired resource; failed cleanup remains owned and visible. Initial hooks and health helpers need explicit grants and budgets too.

No accepted hook is introduced by this research. BG-046 will choose a minimal profile and record decisions per policy family before code. BG-035 will validate package declarations once a schema exists; package installation must not auto-authorize expanded privileges. BG-036 must retain the running generation's cleanup metadata through updates.

## Resource ownership proposal

Account for more than worker count: memory/backing, tasks/helpers, handle slots, IPC queues, probes, logs and pending operations all need finite budgets. Distinguish allocation denied, accounting unavailable, deadline expired and observed resource exhaustion. A zero/absent setting needs explicit meaning; do not confuse disabled accounting with unlimited authority.

Reserve enough control/cleanup capacity that service exhaustion cannot prevent termination or observation. Saturating logs or event queues must not consume every manager allocation. Numeric reserves and latency bounds need measurements, not research guesses. Shared resources need a named owner and reference/release rules; deleting one consumer must not free another's backing.

The [tested Aether v1 seam](../LIFECYCLE-V1.md) provides an eight-slot holder table, rights attenuation, stale-reference rejection and a one-worker quota with ordered reclaim/acknowledgment. Its [pinned contract](../evidence/lifecycle-v1-2026-09-05/AETHER-M4-LIFECYCLE-V1.md) has no multi-holder transfer, device grants, SMP reclaim or general resource controller. This is evidence for those exact fixed-fixture rules, not service-wide isolation against arbitrary native programs.

## Event boundary proposal

A separately supervised adapter should translate kernel/platform events into bounded observations. An event-policy component matches them against validated rules and submits ordinary authorized lifecycle requests. The supervisor remains the owner of launch, restart, stop and resource accounting. A helper must not acquire general shell execution or all-service control merely because it can observe device changes.

Use structured arguments; do not interpolate device names or kernel payload strings into shell commands. Bind requests to source epoch, object identity/generation and policy revision. Coalesce duplicate observations only when semantics allow it; edge-triggered work cannot be discarded as though it were current state. Cap queue length, payload size, concurrent actions and retries. During shutdown, reject activation requests even if old events remain queued.

Snapshot plus event subscription needs a defined reconciliation protocol: either an atomic snapshot/cursor boundary or a subscribe/enumerate/reconcile sequence justified by the provider. After overflow, reconnect or a sequence gap, mark the view uncertain, stop making positive availability claims from it and resynchronize. If the source offers no authoritative enumeration/replay, expose that limitation; do not claim reliable hotplug from best-effort notifications.

## Device, mount, socket, timer and power policies

Device discovery, driver attachment, usable service readiness, permission to access the device and safe resource reclamation are separate facts. Track present, usable, removal-pending and absent observations with an object generation. Reusing a path or device number must not attach an old event or grant to a new device.

For removal, invalidate new admissions, request affected consumers to stop or degrade under declared policy, and ask the owning kernel/driver layer to quiesce/revoke. Memory reuse requires the platform's proof that interrupts, DMA and outstanding references can no longer reach it. A stopped user task, closed handle or removal notification does not supply that proof. If proof fails or times out, quarantine resources and report incomplete cleanup; generic init code must not reset unrelated hardware. BG-048 owns these native questions.

Mount appearance is not proof of the expected filesystem identity, access mode or durable availability. A mount adapter must identify the mounted object and required access; unmount coordinates with actual consumers and open-resource ownership. Avoid automatic arbitrary mounts from untrusted event data.

Socket activation requires a designated endpoint owner, grant transfer/inheritance rules, admission backlog limits and stop/restart semantics. Keep activation-available distinct from notified-ready as in the [readiness handoff](READINESS-AND-HEALTH.md). Compare socket activation as an optional adapter rather than imposing a socket subsystem on the core.

For timers, separate monotonic lifecycle deadlines from periodic/calendar job scheduling. Specify suspend, wall-clock changes, missed triggers, overlap and restart persistence. A bounded coalesced trigger is a candidate; unlimited catch-up jobs are not an acceptable accidental default. Aether yield and its harness watchdog are not a timer API. BG-049 must select a minimal timing/activation scope before implementation.

Power events are policy inputs, not direct reboot authority. A trusted event service may request shutdown through the authorized operation path; duplicate or stale events cannot reset deadlines or resurrect activation. Untrusted observers cannot authorize forced poweroff.

## Future acceptance matrix

| Scenario | Required outcome / owner |
| --- | --- |
| Missing hard controller, failed identity lookup or partial restriction setup | No unrestricted launch; diagnostic and cleanup evidence — BG-046 |
| Service/helper retains excess grant, tries wider delegation or leaks descriptors | Denial or explicitly documented unsupported containment; no hidden broad authority — BG-046/BG-028 |
| Worker, queue, log or handle budget exhausted | Bounded manager memory; cleanup/control capacity remains usable — BG-046/BG-044 |
| Policy changes during launch or package replacement | Generation retains its effective policy and cleanup ownership — BG-046/BG-036 |
| Duplicate, reordered or lost events; reconnect during enumeration | No stale positive state; reconciliation or visible uncertainty — BG-047 |
| Event storm, malicious device name or action recursion | No command injection; bounded queue/actions/retries — BG-047 |
| Unplug/replug reuses path while old consumer stops | Separate generations/grants; stale request rejected — BG-048 |
| Task exits but DMA or shared reference persists | No backing reuse; quarantine/incomplete cleanup — BG-048 |
| Mount replaced or read-only; endpoint exists before worker is ready | Exact resource requirement checked, no readiness shortcut — BG-048/BG-049 |
| Clock jumps, suspend/resume, missed triggers or shutdown with queued power/device events | Declared timer policy and admission closure honored — BG-049/BG-043 |

These are required future tests, not measured results. Follow-ons captured before completion: BG-046 policy profiles and enforcement, BG-047 event broker/reconciliation, BG-048 device and mount ownership, BG-049 socket/timer activation. Existing BG-032/BG-033 retain native grants, clocks and recovery questions. No sibling project was modified or new kernel feature presumed.

Next: BG-016/BG-023 should consolidate these findings into a small operator-facing lifecycle specification with explicit initial scope, then BG-017 should define its test matrix. Avoid turning every researched option into a required first-release feature.
