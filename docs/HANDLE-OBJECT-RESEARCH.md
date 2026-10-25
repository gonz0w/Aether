# Handle/object model and POSIX compatibility research

Status: research / provisional. Date: 2026-10-04. Owner: Aether maintainer.
Review: deferred under [HO-01](../.planning/ROADMAP.md#ho-01--handleobject-model-and-posix-compatibility-review).

This records the handle/object discussion in [Aether Compatibility Research](https://chatgpt.com/c/6ac2c69c-6fb4-83ea-af35-3762060ab434)
for later review. It is not a final architectural decision, an accepted general
ABI, an implementation plan for the current milestone, or evidence of Xorg support.
The conversation supplies candidate ideas, not independently verified contracts.
The [current architecture](ARCHITECTURE.md) and bounded native profiles remain
authoritative. [STATE](../.planning/STATE.md) owns implementation progress.

## Purpose, scope and review gate

Investigate whether one thin resource-reference mechanism can support native
Aether programs and future POSIX/Xorg consumers without making Unix conventions
the kernel's internal architecture. Preserve capability enforcement, small native
mechanisms, explicit per-core ownership, bounded resources and user-space policy.

The proposed direction is **POSIX compatibility as an ABI/personality over native
Aether objects**. Libc and agreed user-space services translate process, file,
device and event semantics; native enforcement remains at the kernel or resource
owner that an untrusted caller cannot bypass. A translation wrapper alone cannot
enforce a rights restriction. This is source/ABI adaptation research, not a promise
to run unmodified Linux binaries or adopt Linux syscall/DRM interfaces.

HO-01 is lower priority than every R1 workstream. Revisit only after the core
protection/capability, per-core IPC and stop/reclaim mechanisms in M2–M4 are
qualified, R1-01–07 acceptance is complete, and a concrete post-R1 consumer needs
a broader resource contract. In particular, current backing/metadata/alias work,
process/FD runtime, grant-bound persistent storage/loading and sys-init assembly
must proceed first. Component receipts do not satisfy assembled R1 acceptance.
M5 physical framebuffer and M6 NVIDIA display are not prerequisites for this
review. This research never becomes a new dependency of M1–M4 or R1.

Record the deferred proposal now; allocate no new syscall, rights bit, magic,
wire format, table quota or companion acceptance. Aether owns native mechanisms;
Aether-userland owns libc/SDK evaluation; sys-init owns supervision/activation;
pkg-mgr owns package state. General POSIX process/FD/VFS/TTY service ownership
remains subject to affected-owner agreement, as required by
[Foundations O-01–O-05](vendor/aether-foundations/v0.1.0/OWNERSHIP.md).

## Existing foundation and proposed extension

The [capability/lifetime contract](ARCHITECTURE.md#capability-and-lifetime-contract)
already requires holder-local references, monotonically limited delegation,
stale-reference rejection and generation exhaustion retirement. The bounded
[capability implementation](../kernel/capability.zig) already encodes a u64
generation/slot reference, checks holder, object type and rights, and implements
local derivation and descendant revocation. [M2 capabilities](../.planning/M2-CAPABILITIES.md),
[M2 lifetime](../.planning/M2-LIFETIME.md) and
[M3 IPC](../.planning/M3-IPC.md) define the executable limits.

Those facts do not establish a general process resource table, arbitrary object
transfer, generalized reference-counted lifetime management, or Xorg semantics.
Review reuse of the existing mechanisms before introducing a second authority
system. The following layout and rights names describe candidates only.

## Objects, handles and the resource table

An **object** is the protected resource; a **handle** is a holder's authorized
reference to it. Several handles may reference one object with different rights.
Kernel references, pending operations, mappings and in-transit references can
also keep the resource alive. Object identity is distinct from a handle value,
PID, pathname, device name or diagnostic ID; none of those names grants authority.

Handles are process-local. Resolve a supplied number only in the authenticated
caller's table. The same bits in another process may name an unrelated entry or
nothing at all. Copying a number through IPC cannot install authority. Processes
and resource objects retain one authoritative local kernel owner; remote requests
use authenticated messages, never a global mutable table or remote state writes.

Conceptual view:

```text
native API: generation + slot ----+
                                 +--> process resource entry --> object
POSIX libc: small fd --> fd view -+
```

| Candidate resource-entry field | Purpose and constraint |
| --- | --- |
| Object reference | Owner-controlled reference to a kernel resource or scoped service binding; no exposed raw kernel pointer |
| Object type | Validate the expected operation/type before interpreting resource state; check consistency with the referenced object |
| Rights | Per-handle operation mask; constrained by the source and the object type's allowed rights |
| Flags | Explicit local lifecycle/inheritance semantics; distinguish these from shared object state and POSIX open-file-description flags |
| Slot generation and occupancy | Reject stale or vacant references before object use; retired slots cannot be allocated again |
| Optional delegation/revocation binding | Only where the concrete contract requires lineage or a revocable session; not mandatory metadata for every resource |

Investigate a **generation-tagged native handle**. The discussion's illustrative
64-bit layout is 32 bits of slot plus 32 bits of generation; it matches the basic
shape of the bounded capability fixture, but freezes no future ABI. Resolve with
one bounded slot lookup, generation/occupancy checks, type check and rights mask.
Closing/replacing an entry invalidates its old generation. Retire a slot on
generation exhaustion rather than wrap. Table destruction/recreation, process
replacement and saved/in-transit references need their own incarnation rules so
resetting a table cannot resurrect stale authority.

Generation tags prevent slot-reuse aliasing; they do not protect a pointer after
lookup. Lookup and acquisition of a stable operation reference must synchronize
with close, rights reduction, revocation and teardown. Document the operation's
authorization/commit point and treatment of already-running work.

Use handles for userspace-visible protected resources: tasks/processes, exposed
threads, IPC endpoints, scoped device resources, memory objects and future file,
directory, socket, pipe, timer or waitset resources when a consumer needs them.
Files and other service-owned resources need not become kernel implementations.
Do not make every internal page frame, page-table entry, spinlock, scheduler queue,
cache entry, packet or interrupt bookkeeping structure a handle.

## Rights, acquisition and delegation

Candidate operation rights include READ, WRITE, MAP, WAIT, SIGNAL, DUP/DERIVE and
TRANSFER. Device control needs operation-specific authority: a generic IOCTL or
CONTROL bit must not accidentally grant administrative commands. Resolve actual
right sets, valid type combinations and unsupported-command errors with the first
consumer; do not allocate these candidate names as executable bits now.

Rights decrease monotonically for a given handle and its descendants:
`new_rights & ~source_rights == 0`. Resource scope cannot widen either. Reject an
attempt to add rights before any effect; never recover removed rights by duplicate,
transfer, inheritance, remapping or POSIX translation. An independently authorized
new acquisition can issue a new grant; it does not upgrade the reduced handle.
Unrelated pre-existing stronger handles are not automatically reduced.

Separate **acquisition authorization** from **use authorization**:

- Acquisition: trusted bootstrap, directory-relative lookup, UID/GID/ACL policy
  or a scoped seat/device service decides whether to issue a particular grant.
  Paths and UID 0 cannot bypass native authority or widen directory/device scope.
- Use: validate caller table, generation, type, rights, live resource state and
  any applicable revocation binding at the enforcing owner before effects. Avoid
  repeated namespace lookup and a second blanket ACL evaluation on every object
  operation. A broker still authorizes each client request within its own grants.

**TRANSFER is an explicit right**, separate from use and local duplication.
A send requires source TRANSFER, authorized channel access, a valid destination
and an explicit requested-rights subset. A recipient gets a fresh local handle;
source bits are never meaningful in the destination table. Strip TRANSFER for a
consumer that must not delegate through the handle-transfer API. This does not
stop that consumer from sharing data or acting as a proxy for another program.

Prefer rights-reducing delegation: a device broker can issue MAP/RENDER/WAIT
without device administration; a buffer producer can transfer READ/MAP while
dropping further TRANSFER. These are examples, not a selected graphics ABI.
Do not silently send full authority as a default. Distinguish the sender's
permission to transfer from the rights installed for the receiver; the receiver's
new handle need not retain TRANSFER.

Before implementation, specify copy versus move, source invalidation, in-transit
ownership, receiver table/queue exhaustion, peer death, interruption, cancellation
and rollback. Partial installation cannot leak references or amplify authority.
Duplication, fork inheritance and exec preservation must not provide a transfer
bypass; their exact authority checks need explicit compatibility review. General
cross-core transfer remains deferred under M3 rather than assumed from local IPC.

## Lifetime management and selective revocation

Investigate centralized object lifetime/refcount management through one small,
hardened get/put mechanism with checked overflow/underflow, explicit owned versus
borrowed references and defined destruction. Centralized means common invariants
and code, **not one global manager, lock, registry or mutable refcount database**.
Mutation and destruction remain with each resource's authoritative owner.
Subsystems can supply narrow teardown hooks instead of independent ad hoc lifetime
rules; service-owned resources still need an explicit service-binding contract.

Initially prefer simple correctness-first refcounting under the existing owner
serialization or a clearly scoped lock. Count handles, kernel operations,
queued transfers and other retaining paths. Publish/transfer only after acquiring
the reference; release once on close, delivery failure, cancellation or teardown.
Specify how cycles are prevented or broken; a refcount cannot collect them.

Closing one handle does not destroy an object retained elsewhere. Final reference
release is not automatically safe backing reuse: stop execution, settle pending
I/O and transfers, remove effective mappings/translations and device access,
then clear memory before exposing it to another domain. Refcount zero alone is
not evidence of CPU/DMA quiescence. Preserve
[M4 remote lifetime](../.planning/M4-REMOTE-LIFETIME.md) and the existing cleanup
barriers; no driver-specific refcount shortcut can replace them.

Investigate **selective revocation** for seat/session device access, GPU control,
input, camera/microphone or temporary grants where withdrawal is required. A
revocation binding/epoch could invalidate a selected session's descendants while
leaving unrelated sessions usable. This is distinct from the slot generation:
slot generations track handle reuse; a session epoch tracks authority withdrawal.
The existing bounded descendant revocation remains authoritative for its scope.

Do not impose a revocation tree or epoch on every ordinary file, pipe or shared
memory object without a workload that needs it. Closing the grantor's handle is
not revoking recipients. Revocation must identify affected descendants and queued
transfers, wake blocked operations, and define completion/error outcomes. Existing
maps and submitted device work require explicit unmap/stop/quiescence. An epoch
check only on future syscalls cannot revoke already-mapped memory or cancel DMA.

## POSIX small-integer fd view

Expose POSIX's small nonnegative integers, including stdin/stdout/stderr, through
a compatibility fd table mapping to native resource references. Keep the native
generation-tagged API distinct. Both views refer to the same protected resource
and preserve its type/rights; fd creation/remapping cannot manufacture authority.
Keep fd-specific CLOEXEC separate from shared open-file-description offset and
status flags. Review lowest-available-fd allocation, dup/dup2 replacement, shared
offsets, fork sharing, exec preservation, close/error/interruption and descriptor
passing against actual libc and consumer requirements.

POSIX fd numbers can be reused. A correct internal generation check cannot make
an application's stale `fd=7` unambiguously refer to its old resource after 7 has
been reopened. Application synchronization remains necessary for close/use races.
Once an operation resolves a live fd, however, it must retain the selected resource
safely while another thread closes/replaces the fd. Do not claim generation-safe
native handles eliminate POSIX fd ABA races.

Future SCM_RIGHTS translation must install authorized local references, with
explicit transfer/inheritance policy and complete failure cleanup. Decide how
extended no-transfer restrictions affect ordinary POSIX programs; fail honestly
when a restriction blocks required behavior. Read/write, device control, mmap and
poll/select can translate to narrow native/service operations without committing
this document to a universal operation dispatcher or a waitset implementation.

## Security risks and required future evidence

| Risk | Design direction and review evidence needed |
| --- | --- |
| Stale handle reuse / type confusion | Caller-local lookup, generations, type checks, exhausted-slot retirement and table-incarnation tests; stale native handles reject after close/reuse |
| Confused deputy | Authenticate caller/request and authorize target, operation and scope; reject clients asking a privileged broker to exercise unrelated authority |
| Over-delegation / ambient authority | Explicit TRANSFER and requested subset; reject enlarged masks, device-admin commands, numeric-ID copying and scope expansion through lookup/dup/fork/exec/SCM_RIGHTS |
| Incomplete revocation | Define descendant/session scope, queued transfer and in-flight behavior; verify unrelated grants survive and old maps/device work cannot access reused backing |
| UAF, double put, leaks, overflow and teardown races | Stable lookup references, checked get/put, one destructor owner, cycle policy; test close/use, sender/receiver death, cancellation and failed installation |
| Resource exhaustion / denial of service | Bound entries, objects, queued references, metadata and revocation work; reject full tables/queues without partial effects or unbounded kernel-stack allocations |

Kernel enforcement protects delegated resource access; it does not establish
whole-kernel compromise containment, driver correctness, physical DMA isolation,
side-channel resistance or trusted-service policy correctness. Future unsafe
pointer/FFI obligations belong in the concrete implementation review, not inferred
from the handle abstraction or a Rust wrapper.

## Performance implications and mitigations

Target **O(1) handle-table lookup** with a bounded dense array, or a bounded-depth
indexed table if measured sparse capacity needs it. Bounds, generation, type and
rights checks precede narrow typed operations. Handle allocation and revocation
may have different complexity; do not label the entire resource system O(1).
Avoid a Windows-style heavyweight Object Manager design: no mandatory global
object namespace, ACL stack, universal execute opcode or repeated name resolution
in the hot path. This is an Aether scope choice, not a Windows benchmark claim.

Acquire entries when acquiring resources, then reuse them for ordinary operations;
avoid temporary object/handle allocation per read/write/wait. Keep entry metadata
compact and separate optional revocation state. Bound table/object memory, queue
references and metadata placement; large tables must not consume exception stacks.
Use process-local tables and owner-local serialization instead of a global lock.
The fd view adds lookup, bookkeeping and synchronization costs worth measuring.

Rights checks are small integer operations, but their total cost is not measured
here and must not be described as free. Shared atomic get/put can contend on cache
lines across CPUs. Owner messaging also has latency and backpressure costs.
Retain simple safe references initially; do not skip a stable reference merely to
avoid an increment. Compare baseline lookup/check/retain latency, memory per live
entry, table exhaustion, transfer throughput and shared-object contention under
declared workloads, bounds, toolchain and target before changing the design.

RCU/epochs, per-CPU references, hazard pointers or lock-free tables are later
options only after measured contention justifies their reclamation, ordering and
recovery complexity. Preserve all authority checks. No throughput, latency,
security or scalability advantage over Unix kernels is established by this paper.

## Alternatives and simplicity review

1. **Simpler alternative:** keep current bounded typed capabilities and extend only
   the next real consumer's existing process/FD contracts. This remains the current
   implementation choice; a universal table is unnecessary for today's milestone.
2. **Why investigate more:** a later consumer may need consistent references across
   process, memory, file, IPC and device resources. Compare a thin shared lifetime
   and lookup mechanism against separate subsystem-specific tables, including the
   cost of adapters, transfer, revocation, cleanup and contributor understanding.
   Borrow Zircon's process-local rights-bearing references and Capsicum's rights
   reduction deliberately; neither commits Aether to their whole architecture.
3. **Complexity removable:** potentially duplicated lifetime/validation/delegation
   rules in a future coherent resource boundary. None is removed now. Preserve
   consumed native profiles and fixtures until a qualified replacement exists.

Before promotion, resolve entry layout/handle representation, resource ownership,
lookup/close synchronization, authority checks for duplication/inheritance,
reference cycles, selective revocation and the POSIX compatibility restrictions.
Specify rights, states, errors, resource bounds, commit/rollback and cleanup using
[Foundations I-01–I-08](vendor/aether-foundations/v0.1.0/INTERFACES.md).
Review alternatives and an actual workload with affected owners; define host,
native denial/lifetime/concurrency and matching consumer witnesses. Record a
separate architectural decision only after that review. This document stays
provisional unless explicitly superseded; it does not allocate an ADR number.

## Research sources and evidence limits

Official documents checked 2026-10-04:

- [Zircon handles](https://fuchsia.dev/fuchsia-src/concepts/kernel/handles)
  describe process-local references carrying rights, rights-reducing duplication,
  in-transit ownership and reference-counted object retention. They also warn that
  closed integer handle values can be reused. Borrow the narrow reference model;
  Aether's generation/slot candidate follows its own existing capability contract.
- [FreeBSD cap_rights_limit(2)](https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit&sektion=2)
  documents reducing descriptor rights without subsequent expansion. Borrow that
  monotonic constraint, not an assumption that ordinary acquisition grants every
  native Aether right.

These are research references, not dependency pins, executed upstream experiments
or performance evidence. Native enforcement and cleanup requirements come from
the current Aether contracts. [Foundations evidence rules](vendor/aether-foundations/v0.1.0/EVIDENCE.md)
separate this research record from future implementation and consumer acceptance.
