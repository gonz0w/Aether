# Unix sockets and authorized descriptor passing

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the Unix-socket/descriptor-passing discussion. General implementation remains
queued under [UP-05](../.planning/ROADMAP.md#up-05--unix-sockets-and-authorized-descriptor-passing).
[STATE](../.planning/STATE.md) records progress. Exact service placement, ABI,
resource types and failure/recovery protocols remain scoped implementation work.

## Decision and responsibility

Provide Unix sockets as a compatibility interface over Aether's native IPC and
capability-enforcing resource services. Native Rust/Zig services can keep using
explicit native protocols. Begin with connected local stream pairs; add named
listeners, datagrams or sequenced packets only for consumers needing their
connection, message-boundary and error semantics. Reuse existing endpoints where
sufficient rather than add a parallel kernel networking framework.

Musl owns socket/descriptor adaptation. A resource owner holds authoritative
connection state, buffers, peer relationships and outcomes. Aether supplies native
authority, IPC, scheduling and lifetime mechanisms. A service-owned reference is
delegated through that owner's enforcing boundary; a kernel-object reference uses
the kernel's applicable authority mechanism. Exact production topology is open.
Sys-init owns startup/supervision policy and pkg-mgr owns artifacts/install policy.

The [descriptor model](FILE-DESCRIPTORS.md), [service I/O contract](SERVICE-IO.md)
and [readiness direction](READINESS-WAITS.md) apply. Socket aliases retain real
references; duplicate/inherited aliases share their supported open-instance state.
The kernel does not acquire a POSIX FD table. Mutable connection/reference state
has one owner; remote clients coordinate through authenticated messages.

## Connection and namespace authority

Specify connection admission, bounded queue sizes, ordering, backpressure,
half-close, final closure, EOF, errors and peer failure for each enabled type.
Connected streams preserve byte order without exposing native message boundaries
as application records. Datagrams and sequenced packets require their own message
preservation/truncation contract; stream fragmentation is not an implementation
of those semantics. Buffered data drains according to the supported shutdown/EOF
contract. Readiness remains advisory and distinct from operation completion.

Named sockets require an authorized namespace owner. Resolve names through a
delegated namespace/directory and enforce lookup, bind/listen/connect policy.
Paths, package names, service labels and claimed PIDs do not themselves grant
native access. A successful authorized lookup/admission may yield the scoped
connection reference. Backlogs and accepted connections consume explicit capacity.
Unlink/rebind and replacement-generation semantics need a contract before exposure.

Where peer credentials are required, derive them from trusted connection/lifecycle
state under an explicit observation contract, not caller-supplied message fields.
Identity can inform owner policy; it does not substitute for delegated capability
authority. Global/abstract namespaces, broad credential compatibility and general
networking remain deferred until needed by a qualified consumer.

The accepted [identity/permission direction](IDENTITY-PERMISSIONS.md), under
[UP-06](../.planning/ROADMAP.md#up-06--identity-and-permissions-over-capabilities),
keeps advisory UID/GID labels distinct from authenticated principals and capabilities.
Peer observation/credential revisions require their actual connection contract;
passing an existing authorized reference does not reopen a pathname under the
recipient's credentials or widen the source access.

## Descriptor passing delegates a resource reference

SCM_RIGHTS sends an authorized reference to an open instance, not the sender's
integer FD. The recipient obtains its own descriptor binding, possibly at another
number, to that same instance. Applicable shared position and file-status state
remain shared. Passing a descriptor does not reopen a path or copy its position.

Conceptually, resolve and retain the sender's reference, admit the attachment with
its associated data, hold it while queued, deliver an authorized recipient binding,
then publish the receiver's descriptor. The transport/owner must enforce each
reference transition. Copying capability-shaped bytes or service tokens is not
delegation; a caller-bound service alias must be authorized for the new holder.

Permit only resource types whose enforcement contract supports delegation. Check
sender authority, generation, transferable scope and rights before admission.
Ordinary supported SCM_RIGHTS preserves descriptor access and never widens it;
explicit native delegation may narrow rights. Native move and reference duplication
are distinct operations with declared failure effects. POSIX passing retains the
sender's descriptor. Do not expose raw backend access that bypasses alias rights
or authoritative shared-position enforcement.

## Admission, delivery and cleanup

Declare sender, queue and receiver ownership at every stage. Reserve bounded
attachment/reference and message capacity before admission, with rollback of
unpublished reservations. Successful queue admission retains the transferred
reference even if the sender closes its descriptor. Queue discard, peer death and
final teardown release queued references through the authoritative cleanup path.

Before publishing received descriptors, account for native/service-reference and
process-local FD capacity. Define delivery commit, acknowledgment and any partial
failure across the involved owners; a userland table lock does not create an atomic
multi-service transaction. Unknown delivery must not justify retry that installs
duplicate descriptors or repeats delegated access. Exact reconciliation may be
fail-closed in the first profile rather than transparently recoverable.

Attachments must remain associated with the correct stream data. A short send or
partial transport frame must not send the same attachment twice when the remaining
bytes are retried. Receive fragmentation, ordinary reads, ancillary truncation and
discard need explicit behavior before sendmsg()/recvmsg() support. Preserve the
selected compatibility profile's control-truncation indication, including
MSG_CTRUNC where applicable, and release undelivered/discarded references without
leaks or silent successful delivery. Define descriptor-exhaustion behavior rather
than guess it from the native transport.

Descriptor flags remain local entries. Qualify ordinary received-FD flag behavior
and atomic close-on-exec receipt where that extension is supported; do not publish
an inheritable FD and fix its flag later during concurrent exec. Resource rights
remain enforced below libc even if the receiving application edits its table.

Passing transport endpoints can create cycles of queued references. Before enabling
that class, either qualify reclamation of unreachable cycles or declare and enforce
a restriction that excludes them. A byte/attachment quota bounds growth but does
not reclaim an unreachable cycle. Start with a needed, narrower resource set such
as files or buffers; general socket/channel passing is not implied. No generic
garbage collector is required by this documentation decision.

## Existing foundations and design tradeoffs

[Native channels](NATIVE-CHANNEL.md), [file/channel launch transfer](NATIVE-FILES.md)
and [inherited-file admission](NATIVE-INHERITED-LAUNCH.md) provide bounded ownership,
stream closure and delegation foundations. They do not establish arbitrary socket
creation, named listeners, ancillary attachments or general SCM_RIGHTS. Preserve
all exact ABIs, quotas, source/pin identities, fixtures and earlier receipts.

The simpler alternative is a connected pair using existing native endpoints; choose
it for the first consumer. Named connections and attachment passing add namespace,
reference coordination and failure states and need concrete consumers. A universal
POSIX broker or full kernel socket stack is not required for that first local pair.
No code is removed now; consolidate overlapping adapters only after compatibility
and lifetime evidence supports the change.

The [Linux Unix-socket documentation](https://man7.org/linux/man-pages/man7/unix.7.html)
illustrates open-instance sharing and ancillary-data/truncation requirements for a
Linux-oriented compatibility profile. It does not select Linux's native architecture
or every extension for Aether. [Fuchsia channels](https://fuchsia.dev/fuchsia-src/reference/kernel_objects/channel)
illustrate explicit queued-handle ownership. Their consuming-move failure semantics
are not automatically Aether's chosen semantics. Reuse Aether's enforcement paths;
do not adopt an entire external framework from these design references.

## Dependencies and acceptance

UP-05 follows the required UP-01 descriptor/reference and UP-03 I/O slices; socket
readiness uses UP-04 as needed. Named listeners depend on the applicable namespace/
filesystem owner contract. VM-object attachments require the relevant VM-01 slice;
POSIX mapped-buffer consumers coordinate with VM-02. Basic connected pairs do not
wait for every VM feature, arbitrary capability transfer or HO-01 research.
SI-02's bounded delegated service-readiness work remains separate and can reuse
existing launch transfer without general SCM_RIGHTS.

Keep current backing/storage/boot-to-shell priorities. First qualify one actual
connected stream-pair consumer, then a real file/buffer passing workload, adding
named listeners when required. No socket feature is a blanket R1 requirement;
enable the concrete R1 consumer subset if needed. Later Xorg/Mesa/service protocols
may require connections and buffer/device-reference passing, but this direction
does not establish graphics or DRM compatibility.

For enabled slices, require matching native and independent userland witnesses for
byte ordering, short progress, backpressure, half-close/drain/EOF, readiness,
foreign/stale/rights denial, reference and descriptor exhaustion, rollback,
sender-close-after-send, receiver death, queued-message discard, shared positions,
attachment association and late/unknown delivery. Qualify flags, truncation,
namespaces and cycle restrictions as those features are enabled. Keep exact ABI,
service placement, general recovery, extra socket types/options, credential modes,
cross-core transfer and unrestricted endpoint passing as scoped future work.
Documentation acceptance closes no native, companion or release gate; shared
normative changes remain owned by Aether-standards.
