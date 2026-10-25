# Readiness and native waiting

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the readiness/waitsets discussion. General implementation remains queued/partial
under [UP-04](../.planning/ROADMAP.md#up-04--readiness-and-native-wait-many).
[STATE](../.planning/STATE.md) records progress. Acceptance covers ownership,
observation, registration and lifetime rules; exact ABI, production topology and
cross-core/multithreaded behavior require scoped contracts and executable evidence.

## Decision and responsibility

Use a small capability-based waiting mechanism beneath the musl poll/select
adapters. Begin with a bounded native wait-many list and straightforward scanning.
Persistent registrations, queued event interfaces, edge triggering and specialized
indexes follow actual consumers and measurements. This direction does not require
a new first-class kernel waitset object or a separate global event service.

| Responsibility | Owner |
| --- | --- |
| File, terminal, socket and device readiness semantics and subscriptions | Authoritative resource service |
| Authorized endpoint/notification observation, atomic local park and thread wakeup | Aether kernel |
| Descriptor resolution, POSIX event masks, results and errors | Aether-userland musl/runtime |
| Service startup readiness, deadlines and supervision policy | sys-init |

Native callers use authorized sources directly. The kernel does not interpret
POSIX FD integers. [Descriptor bindings](FILE-DESCRIPTORS.md) retain resource
references; [service I/O](SERVICE-IO.md) defines their operation outcomes. Each
mutable source has one authoritative owner. Cross-core subscriptions and wakeups
use authenticated messages, not remote mutation of another core's private state.
Event keys, descriptor numbers and claimed sender identities cannot confer access.

## Readiness and completion are different observations

| Observation | Meaning |
| --- | --- |
| Readable | At the observation, a supported read can return data, EOF or an applicable error without waiting |
| Writable | At the observation, some supported write progress or an applicable error is possible |
| Peer closed | The peer closed; buffered data may remain to drain |
| Completed | A particular admitted operation has a known result |
| Lifecycle changed | The watched instance changed state |

A readiness result does not reserve data or space. Another thread can consume it
before the caller attempts I/O. The caller must handle a changed condition and
EAGAIN for nonblocking operations. Writable does not promise an arbitrary-size
write will complete. EOF is established by the resource operation's contract;
a wakeup or timeout does not fabricate EOF or a transferred byte count.

Start with level-triggered readiness: while a supported condition remains true,
checking it continues to report ready. Keep resource readiness, peer closure,
errors, operation completion and lifecycle changes distinguishable, even if a
wakeup causes them all to be rescanned. Reading some buffered data must not erase
readability of the remainder. A closure indication must not discard unread data.

Musl preserves the enabled POSIX poll/select distinctions, including invalid-FD
results, ignored poll entries, duplicate entries, return counts and select set
bounds. Regular-file readiness follows the POSIX adapter contract; it is not a
claim that storage data is resident or an asynchronous operation has completed.
Unsupported event classes fail honestly rather than appear ready indefinitely.

The accepted [TTY/session/seat direction](TTY-SEATS.md) defines terminal readiness
from its supported canonical/raw read-completion and buffer contract. An incomplete
canonical line, EOF control character, timed raw completion and actual hangup have
distinct effects; generic byte availability or lifecycle notification alone cannot
stand in for those semantics. Required timing coordinates SI-01.

## Registration and lost wakeups

Observe the relevant state/revision, establish authorized subscriptions, recheck,
and sleep only when no required condition is ready and the observations still
permit parking. This is a required ordering property, not an assigned wire API.
The enforcing boundary validates source rights, holder, generation, interest mask
and bounds while binding the registration. A subscription cannot remain silently
attached to a replacement instance after source closure or authority loss.

For local kernel sources, comparison and scheduler exclusion must be atomic with
the state transitions that can wake the thread. For service-owned state, define
how the owner's observation/subscription acknowledgment and retained notifications
bridge the gap before the client's final kernel park. An event during any of those
steps must be found by recheck or cause an observable wake. Independent service
observations need no fabricated globally simultaneous snapshot.

Local interrupt exclusion does not establish cross-core ordering. Before exposing
remote sources, specify source publication, transport visibility, subscription
acknowledgment, wake delivery and unregister/replacement ordering. Qualify those
paths on their actual architecture and scheduler. Old BSP-only evidence stays
BSP-only; shared ready bits alone cannot establish a general wait contract.

Notifications may coalesce when they mean rescan authoritative state. Retain the
condition/revision or pending observation until the declared consumption boundary;
do not clear it in a way that loses a concurrent update. Wakeups are hints, not
event counts. Per-operation results and lifecycle records remain retained under
their own contracts; coalescing cannot discard the only completion outcome.
Declare registration/notification bounds and explicit backpressure or a qualified
rescan mechanism. No silent queue overflow and no unbounded event history.

## Lifetime, cancellation and deadlines

Registrations retain the exact native/resource reference they watch. Close, transfer,
authority loss, cancellation and process teardown have explicit observation and
cleanup outcomes. Validate generation and registration identity on delivery and
before reuse; a late event cannot redirect through a reused FD or source slot.
Public FD integers remain reusable. Coordinate concurrent descriptor closure with
the runtime's declared profile; do not invent universal POSIX close-race semantics.

Bound registrations, retained observations and waiting contexts. Keep descriptor
locks out of blocking IPC. Specify multiple-waiter selection and fair progress
before enabling multithreaded use; one waiter draining data does not entitle another
to assume a transfer succeeded. Preserve in-flight cleanup until subscriptions
are removed and delayed deliveries are safely identified or retired.

Use documented monotonic absolute deadlines at the native boundary, with explicit
units, range/exhaustion, timer precision, suspend assumptions and event/deadline
tie ordering. Musl translates its supported timeout forms without extending a
deadline on every spurious wake. Immediate checks and indefinite waits remain
distinct. Current delivered-interrupt clocks are not evidence of calibrated
elapsed time or suspend-aware nanosecond behavior. Coordinate needed clock work
with [SI-01](../.planning/ROADMAP.md#si-01--native-wait-and-service-deadline-contract).

The accepted [clock/timer direction](CLOCKS-TIMERS.md) supplies calibrated source/
local event separation and a coherent timeline before general elapsed-time or
cross-core exposure. UTC adjustments cannot change monotonic waits; musl still
preserves API-specific realtime semantics where supported. Exact providers, timer
objects and broader power/SMP work remain scoped implementation dependencies.

Cancellation requested and a retained final wait outcome are different. Timeout,
signal interruption and cancellation must not consume underlying stream data or
replay partially transferred I/O. pselect()/ppoll() require atomic temporary
signal-mask-and-wait semantics plus mask restoration on return; a libc mask update
followed by separate sleep has a race. Their general support depends on the scoped
signal/runtime contract, not this architectural acceptance alone.

The accepted [signal/interruption direction](SIGNALS.md), under existing
[UP-02](../.planning/ROADMAP.md#up-02--native-shell-process-semantics-and-first-executable-workload),
coordinates these atomic waits with authoritative masks/pending state and checked
handler entry/return. Broader signals and wait combinations remain scoped future
work; signal delivery cannot substitute for underlying I/O completion.

## Existing evidence and design tradeoffs

The [ABI24 endpoint-wait review](evidence/session-channel-wait-2026-10-03/README.md)
defines the bounded single-endpoint, single-context AENMX009 foundation: ownership/
generation checks, bytes/space/peer-close readiness, atomic local registration,
signal interruption and scheduler idle. It has no wait set, timeout or general
cross-core/multithreaded guarantee. [Init observation](NATIVE-INIT.md) and the
[sustained init direction](NATIVE-INIT-COMMAND.md) retain separate revision/deadline
and supervisor scopes. Preserve their profiles, pins, quotas and recorded results.

The simpler alternative is the existing single-source wait; use it when sufficient.
A caller needing several independent sources requires coordinated observation and
parking. A bounded scan is the first extension; a persistent queued interface adds
registration/overflow/lifetime costs before measurements justify it. No code is
removed now; qualified use can replace polling loops for the selected consumers.

Borrow coalesced wake-and-rescan ideas illustrated by
[seL4 notifications](https://docs.sel4.systems/Tutorials/notifications.html).
[Fuchsia asynchronous waits](https://fuchsia.dev/reference/syscalls/object_wait_async)
illustrate explicit source subscriptions and edge-registration obligations.
These are references, not adopted frameworks or Aether performance evidence.
[POSIX poll](https://pubs.opengroup.org/onlinepubs/9799919799/functions/poll.html)
defines adapter semantics rather than Aether's native architecture.

## Dependencies and acceptance

UP-04 builds on existing capability, IPC, scheduler and endpoint-wait mechanisms,
with UP-01 descriptor/reference ownership and UP-03 service I/O. Coordinate SI-01
clock/wait needs and SI-02 delegated service readiness without replacing their
existing work or claiming companion sign-off. Basic waiting does not depend on
all VM features, general socket passing or provisional HO-01 research.

Keep current backing/storage and boot-to-shell priorities. First select a real
consumer needing more than one source and specify its bounded local wait-many
contract. Qualify event-before-registration, event-during-registration, immediate
level readiness, repeated wake/rescan, peer close with buffered data, stale/foreign
denial, capacity exhaustion, cancellation/teardown and late delivery. Add deadline,
signal-mask, multiple-waiter and cross-core cases only as those slices are enabled.
Required consumers support R1 console/shell/service composition; later local
sockets and Xorg/Mesa use the same foundation. The whole design does not become
a blanket R1 prerequisite. Native, independent consumer and release gates remain
separate from documentation acceptance.
