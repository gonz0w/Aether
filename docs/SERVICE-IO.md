# Service I/O and device control

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the read/write/ioctl discussion. General implementation remains queued/partial
under [UP-03](../.planning/ROADMAP.md#up-03--service-io-completion-and-typed-device-control).
[STATE](../.planning/STATE.md) records progress. This decision accepts ownership,
authority, buffer lifetime and completion boundaries; exact interfaces and
explicitly deferred extensions require scoped contracts and consumer evidence.

## Decision and responsibility

Use capability-authorized, resource-specific service operations, exposed through
the [small musl Aether backend](MUSL-VM-BACKEND.md). A POSIX call resolves its
[process-local descriptor binding](FILE-DESCRIPTORS.md), retains the authorized
reference, and invokes the appropriate file, stream or device owner. Native
Rust/Zig clients can use the same native/service contracts directly.

| Responsibility | Owner |
| --- | --- |
| POSIX read/write/ioctl interpretation, descriptor lookup and errno translation | Aether-userland musl/runtime |
| Resource rights, file positions, stream state, device commands and operation results | One authoritative resource service, reached through authenticated bindings |
| Protected IPC, capability enforcement, mappings, scheduling/wakeup and essential hardware mechanisms | Aether kernel |
| Startup, supervision and recovery policy | sys-init |
| Artifacts, package records and installation policy | pkg-mgr |

Keep mutable resource state at its owner. Cross-core clients send messages rather
than mutate remote owner state. The kernel has no POSIX FD table or universal
read/write/ioctl policy dispatcher. Production service placement per resource
class remains affected-owner work; this direction does not move existing bounded
hardware fixtures or allocate a new service process for each open file.

Names, FD integers, client-supplied identities, request IDs and buffer addresses
are not authority. The enforcing kernel/service validates trusted holder or
connection binding, resource generation, rights, operation, bounds and valid
state before exposing effects. Musl may reject early, but callers can bypass it.
File-data, device-command and administrative rights remain distinct. A scoped
user-space service is still trusted for the resources it owns.

## File positions and stream semantics

Prefer explicit-offset operations, conceptually read_at/write_at, for native
seekable-file clients. They do not alter the shared open-file position. Each
operation still requires authorized file access, checked ranges and a defined
ordering/atomicity contract; explicit offsets do not remove write conflicts.
These are architectural operation roles, not assigned syscall or wire names.

Musl read()/write() use the owner-held shared open-file description. Coordinate
the transfer and actual-count position update as one ordered operation, including
concurrent dup()/fork() aliases. Reading a cursor, issuing independent transfers
and later incrementing it is insufficient. Independent opens remain independent.
When append is enabled, selecting end-of-file and writing require the file owner's
atomic append contract across relevant opens, not only an individual cursor lock.
Streams use stream state; they do not acquire artificial seekable-file offsets.

Return the actual transferred byte count. Preserve short transfers, drained EOF,
live-but-empty/full nonblocking EAGAIN and resource-specific errors. A zero-length
operation follows its supported POSIX/resource contract and cannot bypass access
validation. Interrupted calls with confirmed progress return that count; EINTR
must not imply that transferred data was absent when progress is known.

The musl operation must not silently become a write-all/read-all loop. Framing or
splitting needed by a transport must preserve the enabled operation's observable
ordering and atomicity. In particular, qualify PIPE_BUF/append semantics and
scatter/gather behavior before advertising them; independently submitted chunks
or vectors cannot claim the atomicity of one request. Signals, terminal job
control and broader vector/flag behavior require their own enabled contracts.

## Acceptance, completion and durability

Distinguish request admission from completed I/O and storage durability.

| Observation | Meaning |
| --- | --- |
| Accepted | The owner admitted the request with required references and bounded outcome capacity |
| Completed | The operation has a known result and actual transferred byte count, and its declared buffer-access obligations are resolved |
| Durable | The applicable synchronization/flush and ordering contract has been satisfied |

An ordinary successful write need not be durable. Explicit synchronization and
the selected storage contract define that boundary. A transport acknowledgment
does not establish either I/O completion or device quiescence.

Correlate results using connection/instance generation and operation identity;
those fields do not confer authority or guarantee exactly-once execution. Retain
outcomes and cleanup obligations until their declared consumption/reconciliation
boundary. A lost reply can leave the operation unknown to its client. Do not
blindly replay side effects or guess the shared cursor; the affected open instance
must remain uncertain/unusable where required until its owner resolves the state.
The first profile may fail closed rather than provide transparent recovery.
Restart creates a fresh binding and accounts for outstanding I/O before replacement
access. Exact retention, acknowledgment and recovery protocols remain future work.

Design completion explicitly even for an initially synchronous implementation.
Blocking musl calls wait through native blocking/wakeup mechanisms; a yield loop
is not the general blocking contract. Begin with bounded requests and simple
ordering, allowing one outstanding operation per selected connection/resource
where sufficient. Multiple outstanding requests, batching and a general submission/
completion ring are deferred until an actual consumer justifies them. No request
needs a new kernel handle merely to correlate its result.

## Copied messages and bulk buffers

Begin with bounded copied control messages and small copied payloads. Declare
admission bounds and explicit backpressure; select production sizes from real
workloads and measurements. Existing tiny fixture limits remain fixed until an
explicit qualified profile change, not a permanent general-I/O sizing decision.
Application pointers are meaningful only in the caller's protection domain. Do
not send them as dereferenceable pointers to another service.

For justified bulk traffic, use an authorized [VM object](VIRTUAL-MEMORY.md) with
checked offset, length and access direction. Read data requires service write
access to the destination; write data requires service read access to the source.
Bounds checks do not themselves narrow a whole-object mapping grant: enforce the
actual permitted memory scope through the available grant/mapping mechanism, or
use a dedicated buffer/copy where finer isolation is required. Endpoint rights
cannot exceed their source. Retain backing and mappings for the declared lifetime.

Copy and validate critical control metadata from a stable snapshot before effects.
A writable shared alias permits later payload changes; a read-only service mapping
does not freeze the caller's aliases. If immutable input is required, use a stable
copy or an enforced ownership handoff. A cooperative reuse handshake is not
enforcement against an untrusted peer. Exact buffer registration, synchronization,
grant transfer and reuse protocol remain scoped work, not a new generic framework.

Buffer reuse requires completed access and cleanup, including CPU mapping/TLB
obligations where applicable. Device DMA additionally needs pinning, address
translation/isolation appropriate to the device, and confirmed completion or
quiescence. Close, timeout or cancellation request alone cannot authorize reuse.
Current CPU fixtures do not establish DMA isolation or general IOMMU support.

Measure IPC latency, copies, throughput, cache behavior and backpressure with the
consumer before choosing shared buffers or batching. Shared memory can reduce
copies but introduces mapping, synchronization and failure-accounting costs; this
decision makes no zero-copy or superior-performance claim.

The accepted [device-service and scoped /dev direction](DEVICE-SERVICES.md),
tracked by [UP-08](../.planning/ROADMAP.md#up-08--device-services-and-scoped-dev),
uses these owner-held I/O/control contracts behind authorized provider acquisition.
Enumeration and compatibility naming cannot grant command/mapping/admin access;
publication withdrawal and driver replacement preserve unknown effects and cleanup
obligations rather than retargeting existing open instances.

## Typed native device control and ioctl adaptation

Native device services expose explicit, versioned operations with defined input/
output schemas, bounds, rights, state transitions, effects and errors. Examples
are querying supported capabilities, setting terminal attributes, creating an
authorized GPU buffer and submitting a validated device command. Enable only the
operations required by the selected consumer.

Musl translates supported ioctl() commands to those operations. The resource owner
validates them independently. Unknown or unsupported commands fail with the
appropriate error, including ENOTTY where applicable; never report fabricated
success. Caller-selected command size/direction bits are not a trusted schema or
permission. Decode bounded nested data safely; do not tunnel arbitrary pointers
or unrestricted raw commands into a driver. Support discovery cannot grant access.

Mesa/Xorg ports must identify their actual device, mapping, synchronization and
compatibility requirements. Device-backed VM objects and typed commands supply
foundations; they do not establish Linux DRM ABI compatibility, accelerated GPU
support or NVIDIA enablement. GPU command and DMA validation need device-specific
authority and lifetime contracts before exposure.

The accepted [TTY/session/seat direction](TTY-SEATS.md), tracked by
[UP-07](../.planning/ROADMAP.md#up-07--native-tty-sessions-and-seat-boundaries),
applies these typed controls to authoritative terminal state. Input/output/mode/
foreground/recovery permissions are distinct; drain/flush and generation-bound
restoration require actual effects and cleanup, not successful termios stubs.

## Cancellation, closure and resource bounds

An admitted operation retains its original resource reference across descriptor
closure/reuse. An internal generation prevents late work from targeting a new
binding; public FD integers remain reusable. Process death must leave an owned
cleanup obligation for admitted work rather than drop references prematurely.

Cancellation requested, cancellation confirmed and completed effects are distinct.
Define which stages can be cancelled, what progress is reported and when all
buffer/device access ends. Reserve bounded request, buffer-reference and retained
outcome capacity before admission/effects. A full completion path cannot silently
lose the only result. Outcome consumption and final resource release need a
declared order; no unbounded history is implied.

Keep table locks out of blocking service IPC, preserve fair progress for unrelated
clients, and validate malformed/incomplete frames without consuming unauthorized
effects. Exact scheduling, locking, numeric quotas and cancellation representation
remain implementation choices with matching witnesses.

## Existing foundations and design tradeoffs

[Native byte streams](NATIVE-IO.md), [channels](NATIVE-CHANNEL.md),
[shared-position file I/O](NATIVE-FILE-IO.md),
[command adapters](NATIVE-COMMAND-IO.md), and
[scoped block I/O](NATIVE-BLOCK.md) establish bounded authority, counts, owner
positions and cleanup/error behavior. Preserve their ABIs, pins, limits and
receipts. They do not prove the general concurrency, blocking, bulk-buffer or
recovery contracts accepted here. Shared normative changes still belong to
Aether-standards; this local direction records no companion implementation sign-off.

The simpler alternative is the existing copied, synchronous owner-bound path;
choose it for the first slice. General consumers additionally require explicit
completion/lifetime rules and shared-position ordering. A universal POSIX broker
or kernel dispatcher adds topology and policy these requirements do not need.
The decision removes no code now. Later consolidation may remove overlapping
adapter paths only after consumer compatibility and cleanup are established.

Borrow the separation of messages and authorized shared-memory transport studied
in [seL4's driver framework](https://trustworthy.systems/projects/drivers/), and
explicit shared-buffer rights/lifetime illustrated by
[Fuchsia IOBuffer](https://fuchsia.dev/fuchsia-src/reference/kernel_objects/io_buffer).
These are design references, not adopted components or Aether benchmarks. Reuse
our existing IPC and VM foundations; do not import their whole frameworks.
POSIX [read](https://pubs.opengroup.org/onlinepubs/9799919799/functions/read.html)
and [write](https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html)
define supported compatibility behavior, not the native architecture.

The accepted [readiness/native waiting](READINESS-WAITS.md) and
[Unix-socket/descriptor-passing](UNIX-SOCKETS.md) directions are tracked separately
under UP-04/UP-05. They build on these references and outcomes; exact subscriptions,
wait ordering and attachment admission/delivery still need scoped implementation
contracts. Their general features are not blanket prerequisites for copied I/O.

The accepted [signal/interruption direction](SIGNALS.md), tracked under existing
[UP-02](../.planning/ROADMAP.md#up-02--native-shell-process-semantics-and-first-executable-workload),
builds on these retained outcomes. Handler reentry/nonlocal escape cannot abandon
reply/reference/buffer ownership; SA_RESTART requires supported-operation semantics
rather than blind request replay. Exact enabling contracts remain implementation work.

## Dependencies and implementation sequence

[UP-03](../.planning/ROADMAP.md#up-03--service-io-completion-and-typed-device-control)
coordinates this direction with UP-01 descriptor/reference ownership and UP-02
shell/process consumers. Preserve the current backing/storage implementation order.
Basic copied file/pipe I/O uses existing capability, IPC and lifecycle mechanisms;
it does not wait for every VM feature or HO-01 research. Bulk VM buffers depend on
the relevant VM-01 enforcing slice; POSIX mapping consumers coordinate with VM-02.

First qualify file/pipe read/write through the musl backend: byte counts, shared
positions, blocking/nonblocking results, authority, admission bounds and cleanup.
Reuse existing progress for those slices rather than reopen completed fixtures.
Then enable a concrete typed control consumer, such as required terminal attributes.
These slices support R1-01 console, R1-02 shell, R1-03 filesystem and R1-04 runner/
loading. Add bulk buffers and deeper asynchronous execution only for measured
filesystem/device needs. General Xorg/Mesa/GPU work remains later than R1.

Readiness means an operation can be attempted; completion means a specific
operation has finished. Poll/select/native waitsets and Unix-socket descriptor
passing need separate scoped contracts. Defer exact wire ABI, service placement,
sizes, vector/append expansions, recovery protocols, buffer registration, batching,
out-of-order execution and general rings until their implementing consumers.
Before each enabled slice, require matched native and userland positive witnesses
and semantic rejection controls for its authority, concurrency, partial progress,
resource exhaustion, cancellation/closure and peer-failure boundaries. Runtime,
independent consumer and release acceptance remain separate gates.
