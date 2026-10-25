# Clocks and timers

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the clock/timer review. Broader implementation remains queued/partial under existing
[SI-01](../.planning/ROADMAP.md#si-01--native-wait-and-service-deadline-contract),
coordinated with [UP-04](../.planning/ROADMAP.md#up-04--readiness-and-native-wait-many).
[STATE](../.planning/STATE.md) records progress. Acceptance covers time domains,
hardware separation, local ownership, deadlines and compatibility boundaries.
Exact providers, ABI and explicitly deferred features remain implementation work.

## Decision and responsibility

Separate measuring time, delivering deadlines and maintaining calendar-time policy.
The generic native layer exposes supported clock observations and authorized waits;
architecture-specific code reads counters and programs hardware events. Each core
owns its deadline state and timer interrupt handling. User space owns UTC source
selection/synchronization, calendar conversion and service retry/deadline policy.

| Responsibility | Owner |
| --- | --- |
| Counter reading, calibration, conversion, local hardware interrupts and scheduler wakeup | Aether native time/execution owner and architecture implementation |
| Pending deadlines, wait outcomes and reusable timer state | One authoritative native owner for each supported resource, local to its core |
| POSIX clock IDs, timespec/errno adaptation, sleep and timed-thread semantics | Aether-userland musl/runtime |
| UTC establishment, adjustments and synchronization policy | Aether-userland shared runtime policy; trusted capability-scoped user-space implementation |
| Startup timeout, retry, shutdown and supervision policy | sys-init within its existing contracts |
| Persistent timestamp and storage-engine time consumers | Applicable filesystem/resource owner, using the supported clock contract |

This selects no global mutable timer queue, new universal time service, replicated
authority table or service round trip for every read. Sys-init retains supervision
policy; pkg-mgr retains artifact/install policy. Future shared normative changes
belong in Aether-standards; no released pin or companion ownership changes here.

## Clock domains and truthful observations

| Clock domain | Meaning and use | Sequence |
| --- | --- | --- |
| Monotonic | Nondecreasing elapsed timeline within one boot, unaffected by calendar-time adjustments; sleeps, retries and ordinary service/I/O deadlines | First calibrated provider |
| Realtime / UTC | Established calendar-time estimate for persistent timestamps, logs, date and absolute calendar deadlines; can change with adjustments | Add truthful provider for required consumers |
| Suspend-aware elapsed time | Elapsed timeline including suspension when that behavior is required | Defer until suspend support is qualified |
| Process/thread CPU time | Execution consumed by the selected process/thread, distinct from elapsed time | Defer until scheduler accounting is reliable |

Declare epoch, units, range, resolution, suspend behavior and source availability.
Monotonic values are not portable persistent dates across reboot. UTC may be
unavailable or not yet established; fail explicitly under the selected compatibility
profile rather than return zero or relabel uptime. Time-zone/calendar conversion
belongs in libc/user space and does not redefine the underlying UTC clock.

Use checked 64-bit time values and explicit clock identity at the generic boundary.
Nanosecond representation does not promise nanosecond hardware resolution, accuracy
or wakeup latency. Validate timespec fields, sign/range, conversion arithmetic and
deadline addition; reject unsupported IDs and exhaustion without silent wrapping.
Immediate checks, expired deadlines and indefinite waits remain distinguishable;
no wire sentinel, syscall number or new ABI field is allocated by this direction.

## Clock sources and clock-event devices

A clock source reads the timeline. A clock-event device requests an interrupt at
a future point on that timeline. The hardware can be shared, but these are separate
contracts: a counter need not generate interrupts and an interrupt counter is not
automatically a reliable elapsed-time source.

For x86_64, evaluate calibrated TSC observation and local APIC event facilities,
with a specified fallback for the supported QEMU profile. This direction does not
select an unqualified TSC, deadline mode or HPET dependency. Qualify frequency,
stability, cross-core agreement, read ordering, counter wrap, delayed interrupts
and virtualization behavior before exposing the selected provider. Feature bits
alone are insufficient evidence of a common calibrated timeline. Unsupported
platform/source combinations reject or use their explicitly qualified fallback.

The first [private BSP q35 source and absolute word wait](NATIVE-CLOCKS.md)
uses the HPET's validated reported period and checked elapsed conversion, with
interrupt-independent progress, repeated QEMU CPU-profile witnesses and semantic
controls. This is a scoped reference fallback, not a universal HPET dependency,
empirical physical/TSC calibration, certified effective resolution or coherent SMP
timeline. Existing interrupt-count interfaces retain their old meaning. Actual
libc timed conditions, truthful UTC and production provider adoption remain open.

The architecture-independent interface hides source registers and event programming.
A later aarch64 implementation supplies its own counter and timer backend under
the same observation/deadline contract. Source replacement and calibration updates
must preserve the declared continuity/order with checked conversion state; exact
publication protocol remains scoped work. Begin with a syscall for clock reads.
Consider a validated read-only fast path only when measurements justify its update,
consistency, permissions and architecture-access obligations.

## Per-core ownership and a coherent timeline

Each kernel instance owns its pending deadlines and hardware timer programming.
Remote requests coordinate with that owner through explicit authorized messages;
they do not mutate another core's queue or timer registers. Keep tasks pinned
within the current profile; migration and core-offline behavior need future contracts.

Applications still need a coherent system-wide monotonic meaning. Unrelated local
interrupt counts cannot masquerade as one clock. Qualify a common reference timeline
or explicit conversion from local counters, including ordered observations across
cores and any published conversion revisions. An absolute deadline transferred
between cores must preserve its meaning. BSP-local evidence does not establish
this cross-core property; keep unsupported routes unavailable until qualified.

Begin with a small bounded ordered deadline collection sufficient for the selected
consumer. Bound admission, retained outcomes and timer processing; expiration bursts
must not monopolize interrupt handling or lose pending work. A heap can follow
measured capacity needs. Timer wheels and elaborate distributed structures remain
deferred. Periodic hardware interrupts can remain the initial qualified mechanism;
one-shot programming/tickless idle follows consumer and efficiency evidence.

## Absolute deadlines and waiting

Prefer an authorized native wait for an event until an absolute monotonic deadline.
Translate relative compatibility timeouts once and retain that deadline across
spurious wakeups/rechecks. Do not restart a duration at every retry. A blocked
thread parks through the scheduler; user-space yield loops do not implement sleep.

Under the [readiness contract](READINESS-WAITS.md), combine event observation,
expiration checking and registration/park without a lost wakeup. Define the
event-versus-timeout decision at the owner, including simultaneous eligibility,
before/during registration, already expired deadlines and delayed servicing.
Round hardware scheduling conservatively for contracts forbidding early expiration.
Expiration makes the thread eligible to run; scheduler latency can delay execution.
No hard real-time guarantee or numerical latency budget follows from this design.

Timeout, [signal interruption](SIGNALS.md), cancellation and operation completion
remain distinct outcomes. A timeout does not prove an I/O request was cancelled,
a worker stopped or device/DMA activity quiesced. Retain cleanup obligations and
supported remaining-duration/restart semantics; signals cannot extend an absolute
deadline or justify blind replay of effects. Timed condition waits must preserve
their atomic release/wait and mutex reacquisition behavior, not merely add sleep.

## Reusable timer objects and expiration delivery

Start with one-shot deadlines internal to sleeps and waits. When a real service
needs an independently observable timer, provide a capability-scoped timer object
that can be armed, observed, cancelled or rearmed within its supported rights.
It composes with native level readiness and wait-many; every short-lived timeout
need not allocate a public handle. No exact rights bits or object ABI are selected.

Define owner/caller authority, object generation, arm identity, capacity and the
expiration observation contract. Rearm/cancel races and delayed notifications
must not expire a new arm using an old event. Cancellation request, confirmed
disarming, draining retained outcomes and reclamation remain distinct. Owner death,
teardown and slot reuse retain references until delivery/cleanup obligations are
settled. Foreign timer control and clock adjustment must fail below libc.

Keep kernel expiration handling bounded: record eligibility and wake/notify the
authorized owner. Application callbacks run in user space. Periodic timers follow
a real consumer and preserve their original schedule with checked arithmetic;
report missed expirations or apply a declared bounded policy instead of accumulating
drift or an uncontrolled callback backlog. Timer FD/POSIX timer and signal-delivery
adapters require their own enabled semantics, not arbitrary Linux-binary compatibility.

## Calendar-time authority and adjustment

A trusted user-space maintainer establishes UTC using an available RTC, explicit
configuration and eventually network synchronization. Kernel mechanisms provide
supported observations and validated updates; policy decides which sources to trust.
The maintainer assigned shared UTC establishment/policy to Aether-userland on
2026-10-06. Exact implementation placement and source trust remain affected-owner
work; this assignment does not require a separate time daemon or enable UTC in the
current SDK. Aether supplies bounded raw source observations, not calendar policy.
Reading time and arming an ordinary timer do not confer clock-adjustment authority.
UID zero and source labels cannot manufacture that authority.

UTC adjustments do not change ordinary monotonic deadlines. Preserve the declared
clock mapping and update consistency without calling a service on every observation.
Absolute realtime deadlines require defined behavior when UTC steps or its rate
changes; converting them once to an immutable monotonic deadline loses those
semantics. Qualify reevaluation and expiration/cancellation behavior for supported
realtime waits. Suspend/resume, RTC validity and recovered wall time require their
own evidence before claims about those modes or persisted dates.

## Musl and storage consumers

Implement clock_gettime/clock_getres, sleeps, timed readiness and the timed-thread
operations the actual consumers require through the native backend. Preserve each
API's clock semantics, outputs on failure, errno/return conventions and signal or
thread-cancellation behavior. Do not silently make every POSIX timeout monotonic:
pthread_cond_timedwait defaults to realtime unless its clock attribute selects
another supported clock. Explicit clock-selection APIs can use monotonic time.
Unsupported clocks/options fail truthfully; retain existing disabled-profile errors.

The [OpenZFS provider review](OPENZFS-FEASIBILITY.md#granted-providers-and-checked-time-helper-consumers--2026-10-04)
distinguishes checked virtual time from calibrated elapsed/UTC and notes upstream
helpers that ignore clock errors. Preserve guarded SDK and bounded helper evidence.
Real providers need rebuilt actual consumers, error handling and independent intake;
a corrected libc alone does not repair unchanged inline engine bodies. Persistent
filesystem timestamps require a truthful supported wall-clock policy. This acceptance
does not close engine startup, filesystem, SDK or assembled R1 gates.

## Existing foundations and simplicity

[SI-01](../.planning/ROADMAP.md#si-01--native-wait-and-service-deadline-contract),
[init observe/park](NATIVE-INIT-COMMAND.md) and UP-04 retain their bounded contracts.
Current periodic PIT/APIC interrupt counts, virtual-clock witnesses and public SDK
errors are not calibrated elapsed-time or general wall-clock evidence. Preserve
their ABIs, ticks, grants, limits, receipts and qualification rather than reinterpret
old fields as nanoseconds or promote bounded acceptance to system-wide time.

The simpler alternative is periodic interrupts with the existing small local wait
state. Keep it where adequate. Counting delivered interrupts is insufficient for
accurate elapsed time under delayed delivery; add a calibrated source and checked
conversion before consumers depend on durations. Local ordered deadlines and a
syscall read avoid unnecessary queues, services and fast-path publication now.
No code is removed by this documentation change; qualified replacements can later
retire fixture-only conversions or polling with explicit migration and recovery.

Borrow source/event separation and local event ownership from
[Linux timekeeping](https://docs.kernel.org/timers/timekeeping.html), and explicit
time-domain separation from
[Fuchsia time](https://fuchsia.dev/fuchsia-src/concepts/kernel/time/overview).
[POSIX condition waits](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_cond_clockwait.html)
guide supported clock selection and wait semantics. These are design references,
not adopted frameworks, implementation evidence or performance guarantees.

## Dependencies and implementation sequence

Use existing SI-01 with UP-04 waiting, UP-02 signals and the native scheduler/IPC
foundation. Preserve current backing/storage implementation order. First qualify
a calibrated monotonic source on the supported QEMU profile, then real elapsed-time
deadline/park semantics and required musl/storage consumers. Add truthful realtime
support for persistent timestamps and calendar consumers. Reusable timer handles,
one-shot hardware programming and broader SMP support follow justified workloads.
Required R1-02 runtime, R1-03 filesystem/engine and R1-06 startup slices select their
scope; every future clock/timer feature is not a blanket first-release prerequisite.

Defer timer coalescing/slack, suspend-aware clocks, CPU accounting, timer wheels,
fast mapped reads, broad POSIX timer/signal modes, network synchronization and
hard real-time scheduling until justified. Exact ABI, platform fallback, calibration,
conversion publication, quotas, recovery and cross-core protocols remain scoped
implementation work. Require native positive/semantic rejection evidence and
independent affected-owner consumption before claiming each enabled slice.
