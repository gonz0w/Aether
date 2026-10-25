# Signals and interruption

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the signal review. Broader implementation remains queued/partial under existing
[UP-02](../.planning/ROADMAP.md#up-02--native-shell-process-semantics-and-first-executable-workload).
[STATE](../.planning/STATE.md) records progress. Acceptance covers ownership,
authority, delivery, return and interruption boundaries. Exact interfaces and
explicitly deferred wider features require scoped contracts and consumer evidence.

## Decision and responsibility

Prefer explicit native events and retained lifecycle outcomes for Aether services.
Provide a scoped POSIX signal runtime for musl applications needing signal handlers,
masks, child notification and interrupted waits. Native services can handle shutdown,
child completion and cancellation in their ordinary event loops; those protocols
do not require every service to adopt asynchronous POSIX handlers.

| Responsibility | Owner |
| --- | --- |
| POSIX calls, signal-number/record adaptation, errno and supported restart interpretation | Aether-userland musl/runtime |
| Authoritative native signal records, pending/mask coordination, checked delivery, park/wakeup and context restoration | Aether native execution owner |
| Authorized process targeting, group membership and lifecycle relationships | The applicable authoritative process/lifecycle owner |
| Service supervision and recovery policy | sys-init |
| Artifacts and installation policy | pkg-mgr |

Preserve the existing authoritative native records. Public/internal musl calls
must agree with those records rather than maintain a second successful libc action
or mask table. This direction selects no global signal broker, new service or
global mutable process table. General process/thread routing and production state
placement remain affected-owner work; existing bounded native ownership is not
silently relocated into a service. The kernel supplies mechanisms and enforcement;
the runtime and resource owners preserve the supported compatibility contract.

## State scope and delivery selection

| State | Scope |
| --- | --- |
| Signal disposition: default, ignored or handler | Process-wide shared state |
| Blocked signal mask | Per thread |
| Process-directed pending signals | Process |
| Thread-directed pending signals | Target thread |
| Handler return context | Interrupted execution |

The broader runtime must preserve these scopes even if an initial profile has one
context per domain. Process-directed delivery selects an eligible thread; it does
not invoke every thread's handler. Thread-directed occurrences remain associated
with that thread. Before enabling multiple execution owners, define how selection,
mask changes and occurrence consumption are serialized at the enforcing boundary.
Each mutable state has one authoritative owner; cross-core coordination uses
authenticated messages rather than independently copied authoritative masks.

Start with an explicitly supported ordinary-signal set and bounded coalescing
pending bits. Define selection, default actions, ignored-signal discard, supported
flags and exhaustion. Real-time queuing, ordering, payloads and capacity semantics
are separate future work. A private numbered signal/bitset witness is not proof of
the POSIX real-time signal contract. Unknown signal numbers and unsupported flags
fail explicitly under the selected profile.

## Targeting and lifecycle authority

Names, PIDs, thread IDs, signal numbers and claimed sender fields are not authority.
kill(pid, signal) resolves an authorized target through the applicable process-owner
contract. Self-directed operations use established caller identity. Remote delivery
requires delegated target/operation scope and exact instance generation. Foreign,
stale or excessive rights reject below libc before effects; PID reuse cannot redirect
an admitted request. A parent relation does not grant every process-control operation.

SIGCHLD originates from a trusted parent-child lifecycle relationship. Terminal-
generated SIGINT requires authorized foreground-group targeting and the terminal/
process-owner policy. Supervisor stop/termination uses its distinct lifecycle grants;
supervision and package installation do not imply arbitrary signal authority.

When enabled, SIGKILL and SIGSTOP remain uncatchable and unblockable. Sending them
still requires authority. Stop, continue and terminate are separate state transitions
with scheduling/resource outcomes; a successful no-op cannot satisfy them. Groups,
sessions, foreground selection and job control require their own consumer-qualified
contracts. No ambient system-wide PID targeting is introduced.

The accepted [TTY/session/seat direction](TTY-SEATS.md), under
[UP-07](../.planning/ROADMAP.md#up-07--native-tty-sessions-and-seat-boundaries),
coordinates controlling terminals, foreground groups and enabled background-access
policy with these signal mechanisms. Ctrl-C/Z, fg/bg and terminal restoration need
actual group/stop/continue and generation-bound owner evidence before exposure.

## Checked handler entry and return

A handler runs in the interrupted thread's user context. General asynchronous
delivery eventually needs checked transitions including return to user execution
and preemption, so a CPU-bound program can receive signals without voluntary libc
calls. Existing selected delivery points remain limited until those wider paths
are implemented and qualified. Handler injection cannot occur in kernel execution
or silently treat another worker thread as the interrupted thread.

Use the documented user-stack return-frame direction with the matching musl
restorer. Validate handler/restorer executable mappings and the complete writable
stack span at delivery; preserve architectural register, FP/SIMD and mask state,
including x86_64 alignment/red-zone requirements. Exact layout and architecture
code remain owned by the qualified native profile, not allocated by this document.

On return, snapshot and validate user-controlled context before changing live
execution. Enforce permitted user selectors/flags and FP control state; preserve
kernel ownership of TLS/execution authority, page tables and capabilities. Mapping
or protection changes require revalidation. A forged/replayed frame cannot restore
kernel state or another domain's authority. User-controlled resumption within the
same domain needs the declared profile policy. Invalid return must not partially
install an unsafe context; frame-preparation failure has a defined retained-pending,
error or terminal outcome, never an unexplained consumed signal or permanent sleep.

Dash can leave a handler through longjmp. Preserve supported sigsetjmp/siglongjmp,
ordinary nesting and mask-restoration behavior. Do not hold a permanent kernel
active-handler slot that can only be cleared by sigreturn; a nonlocal escape would
leave it occupied. Do not infer handler completion from stack pointer comparisons.
Nested delivery consumes user-stack capacity and still requires checked bounds;
removing a kernel slot does not remove exhaustion obligations.

Alternate stacks and advanced action flags remain deferred until a consumer needs
them and their frame/lifetime behavior is qualified. In particular, general stack-
fault handling cannot be promised using an already unusable ordinary stack. No
default core-dump or debugger interface is implied by signal termination.

## Interruption of service I/O

Apply the [accepted service I/O contract](SERVICE-IO.md). Signals may arrive during
partial request framing, reply observation, descriptor publication or shared-buffer
access. Interrupted waits do not prove underlying cancellation. Confirmed progress
remains progress; a lost reply remains unknown. Do not convert uncertain effects to
a false zero-progress EINTR or replay a side effect to make an operation look complete.

Handler reentry must not interleave incompatible requests on a connection. A nonlocal
exit must not abandon an unowned reply, reference, descriptor reservation or buffer
access obligation. Define what is retained, completed/cancelled, reconciled or poisoned
before returning control. Shared-buffer/DMA access still needs its own completion or
quiescence; signal delivery cannot authorize reuse of memory still in use.

Short publication-critical sections may temporarily block catchable signals using
the authoritative mask, with nested-mask and errno preservation. Existing bounded
transaction-wide guards keep their documented scope. Indefinite reads/waits cannot
mask signals for their entire duration while claiming interactive interruption.
Do not infer adapter reentrancy from one handler that only records a flag.

SA_RESTART requires an explicit supported-operation contract. It may resume waiting
for an already admitted request where appropriate, rather than submit another write.
Partial progress, unknown outcomes, non-restartable operations and deadline behavior
remain explicit. Preserve existing rejection of unsupported custom-handler restart
semantics. Storage of an inert flag for default/ignored dispositions is not proof of
interrupted-operation restart. Use the actual pinned musl wrapper/restorer behavior
when qualifying the adapter; do not advertise a Linux signal ABI from that seam.

## Signal observation and atomic waiting

Provide sigwait-style synchronous acceptance when a POSIX consumer needs it, using
the same authoritative pending state. Define competition with asynchronous delivery
and other waiters before enabling that mode. A native event-loop interface remains
available independently. Qualify supported async-signal-safe operations through the
actual musl backend; ordinary locks, allocation and a nonreentrant RPC connection
cannot be assumed safe from a handler merely because they are user-space code.

Coordinate [readiness/native waiting](READINESS-WAITS.md). sigsuspend, pselect and
ppoll combine temporary mask changes, pending inspection and parking atomically,
with defined return/restoration outcomes. Separate libc unblocking followed by
sleep leaves a lost-wakeup window. Ignored/blocked occurrences do not fabricate
handler delivery, successful I/O or EOF. Timeout, handler delivery, termination
and cancellation remain distinct; spurious wakes require recheck without resetting
the original deadline. General multithreaded/cross-core atomicity needs its own
proof and cannot be inferred from local interrupt exclusion.

## Child status, fork and exec

SIGCHLD is a hint to inspect retained child status. Several transitions can coalesce
while each child's status remains collectible through its authorized wait owner.
Generation-checked parent provenance must survive applicable child exec and reject
reclaimed/reused parents. Notification is not reaping or status acknowledgment.
Explicit ignore, default-ignore and SA_NOCLDWAIT/automatic-reaping effects require
their own enabled contract; discarding a notification alone does not prove that
child status may be discarded.

Fork inherits dispositions and the calling thread's mask, initializes child pending
state empty at the fork boundary, and preserves parent state. Define concurrent
posting versus process publication so new occurrences are not lost or misclassified
as inherited pending state. The copied user stack can include a handler frame;
the existing copied-handler return/escape contract must remain valid in that slice.

Successful exec resets caught handlers according to the supported contract and
preserves applicable masks, ignored dispositions and pending state; any permitted
special SIGCHLD behavior is explicit. Old handler addresses cannot be invoked in
the new image. Commit replacement alongside process/descriptor lifetime, including
signal posts at the transition. Failed preparation preserves the old usable state.
Discard obsolete suspension/delivery bookkeeping under its declared lifecycle rule,
not pending occurrences simply because an image changed. General multithreaded
exec and alternate-stack reset require their own implementation evidence.

## Hardware faults and native exceptions

Keep requested asynchronous signals distinguishable from faults of the affected
thread. Generic [VM](VIRTUAL-MEMORY.md) first handles legitimate demand-zero/COW
faults where supported. An unresolved fault remains a native exception outcome;
a qualified POSIX runtime may translate appropriate faults to SIGSEGV, SIGBUS or
SIGILL. A fault in one thread is not a request to invoke an unrelated thread's handler.

Native services can expose retained exception outcomes to an authorized owner.
Resumption requires checked execution mechanisms and a valid repair/termination
contract; notification alone cannot make execution safe. Preserve exception origin,
generation and reason, distinguish signal death from ordinary exit, and release
resources through the existing lifecycle path. Fault handlers, alternate stacks,
debugging and broader recovery are enabled only with concrete consumer evidence.

## Existing foundations and simplicity

The [shell signal-frame direction](NATIVE-SHELL-STARTUP.md#findings-and-selected-direction),
[public routing review](NATIVE-SHELL-STARTUP.md#public-signal-routing-review--2026-09-08),
[signal-copy experiment](NATIVE-CONNECTIONS.md#explicit-native-signal-copy-experiment--2026-09-10)
and [ABI24 wait/SIGCHLD evidence](NATIVE-CONNECTIONS.md#asynchronous-child-notification-during-wait)
retain their bounded qualification. Consume completed frame, nonlocal-return,
mask/disposition, copy, child-notification and suspension progress rather than
reopen it or promote it to general signal support. Exact ABIs, limits, SDK pins,
fixtures and historical review statements remain intact.

The simpler alternative is explicit native events with no asynchronous POSIX
handlers; choose it for services where sufficient. Actual musl/dash consumers need
handlers and interruption, so reuse the current checked native frame/record seam.
A new global signal service or kernel unwinding protocol adds lifecycle complexity
the first consumer does not require. No code is removed now; qualified replacement
can retire duplicate facade state or polling paths while preserving consumers.

References: [signal concepts](https://man7.org/linux/man-pages/man7/signal.7.html),
[POSIX sigaction](https://pubs.opengroup.org/onlinepubs/9799919799/functions/sigaction.html),
[fork](https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html) and
[exec](https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html) guide
supported compatibility semantics, not native authority or Linux-binary compatibility.
[seL4 fault handling](https://docs.sel4.systems/Tutorials/fault-handlers.html)
illustrates explicit exception-owner boundaries; no external runtime/framework is
adopted and no Aether performance/fault-recovery claim follows from that reference.

## Dependencies and implementation sequence

Use existing UP-02 process/shell work and coordinate UP-03 I/O completion and UP-04
waiting. Prioritize the actual musl/dash signal path and interruption of blocking
I/O, preserving current backing/storage implementation order and all completed
bounded evidence. General signals are not a blanket prerequisite for every R1
consumer; required R1-02 shell and R1-01 terminal slices have explicit semantics.
VM-01 supplies relevant fault/frame backing work where needed; basic signal work
does not wait for every VM feature, general socket passing or HO-01 research.

Then qualify broader delivery points and authorized targeting. Process-group job
control, general multithreaded/cross-core routing, alternate-stack fault handling,
real-time queues and advanced flags follow concrete consumers. Exact ABI, state
placement, routing, restart/cancellation and recovery protocols remain scoped work.
Require native and independent userland witnesses plus semantic rejection controls
for each enabled slice. Documentation acceptance does not close native, companion,
shared-standard adoption or release gates.
