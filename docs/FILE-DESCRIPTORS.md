# File descriptors and shared open-file ownership

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the descriptor discussion. Broader implementation remains queued/partial under
the existing [UP-01](../.planning/ROADMAP.md#up-01--inherited-file-ownership-and-composable-processfile-capacity)
backlog. [STATE](../.planning/STATE.md) records progress. Acceptance is for the
ownership and lifetime model; exact native interfaces and production placement
of shared descriptions remain scoped implementation/affected-owner work.

## Decision and responsibility

Musl and its Aether backend provide the POSIX descriptor view. Each process has
its own descriptor table in the userland runtime. Native capabilities and
capability-enforcing resource services authorize access; the kernel has no POSIX
descriptor table. Separate descriptor entries, shared open-file descriptions and
native references rather than treating them as one resource table.

| Concept | State and responsibility | Owner |
| --- | --- | --- |
| Descriptor entry | Process-local integer index, descriptor flags and a binding to an authorized resource reference | Per-process userland runtime |
| Open-file description | One open instance with shared position, access mode and file status flags where applicable | One authoritative user-space resource owner |
| Native capability/reference | Holder/caller binding, resource identity, enforceable rights and lifetime | Kernel or capability-enforcing service |

Threads in one process use its descriptor table; a forked child has a separate
table referencing the inherited open instances. Two independent opens create
independent descriptions. dup() and inherited descriptors refer to the same
description; they do not copy mutable positions into separate clients.

Conceptually, a parent descriptor and a child descriptor each hold an authorized
reference to the same owner-held open-file description, which refers to the
backing file, stream or device. Shared state has one owner even across cores;
coordination uses the existing authenticated message/capability boundaries.

Aether-userland owns musl/POSIX adaptation and its assigned bounded runtime.
Aether owns native enforcement and conformance fixtures; resource owners enforce
their backing contracts. Sys-init retains supervision policy and pkg-mgr retains
artifact/package policy. Which production service hosts each resource class's
shared description remains open. This decision chooses no new global POSIX
broker, service process per open file, generic VFS or system-wide mutable table.

## Descriptor flags, shared state and rights

FD_CLOEXEC belongs to a descriptor entry. File position and file status flags,
such as O_NONBLOCK, belong to the shared open instance. Access mode and native
rights are distinct from mutable status flags; a flag update cannot widen access.
Other supported POSIX flag semantics require their own consumer contract.

Plain POSIX duplication preserves the source's access. Narrower native delegation
is an explicit operation, enforced by the resource owner rather than a writable
client-side rights mask. The shared description remains the same when a restricted
alias is delegated; shared mutable position/status effects must be explicit.

FD numbers, paths, PIDs and caller-supplied session IDs are not authority. Resolve
requests using a trusted connection or holder binding and validate the referenced
alias, generation, operation and rights at the enforcing boundary. An application
can bypass musl or edit its own table, so the service/kernel must still reject
foreign references and excessive access. Keep raw backend handles private where
they would bypass alias restrictions or shared-position enforcement.

The accepted [identity/permission direction](IDENTITY-PERMISSIONS.md) applies
credential policy when acquiring new access within delegated scope. Ordinary chmod
does not implicitly revoke existing authorized open references; a UID change does
not close descriptors or establish that native authority was dropped. Strong
revocation and authority-drop operations require separate enabled contracts.

## Duplication and inheritance

- dup() chooses the lowest available descriptor and references the same open
  instance, following the supported POSIX flag behavior. Descriptor exhaustion
  returns a real error without leaking references.
- dup2() validates the source and destination before effects, handles the valid
  same-descriptor case without closing it, and atomically replaces the destination
  binding. An invalid source leaves the destination intact. Reserve/retain the
  source before dropping a destination that may already alias it.
- Support close-on-exec creation/duplication atomically when the relevant API is
  enabled. Creating an inheritable entry and setting its flag afterward introduces
  a window in which concurrent launch can inherit unintended access.
- fork() gives the child its own descriptor bindings to the same inherited open
  instances. Acquire actual child references and commit their bindings alongside
  process admission; copying FD integers or client-local counters is insufficient.
- Native spawn delegates an explicit authorized set of bindings. Validate and
  reserve the whole selected set before publication; rejected admission rolls
  back reservations without changing the parent's positions or references.

Define synchronization, backend-close failure and publication boundaries before
implementing replacement. A local lock alone cannot make a multi-service launch
or close transaction atomic. If admission succeeded but its reply was lost, retain
the owned child/references and report uncertainty instead of replaying launch.
Existing bounded native inheritance remains a foundation, not proof of all these
concurrent or general POSIX paths.

## Exec commit and failure

On successful exec replacement, preserve descriptors without FD_CLOEXEC and
consume those marked for closure. Treat that transition as part of the existing
process/descriptor commit boundary. Rejected preparation/replacement preserves
the old process's usable descriptor state; do not close entries while merely
preparing a prospective image.

Specify retained references, endpoint rebind, matching instance generations and
post-commit cleanup with the existing process owner. Exact rollback, cancellation
and ambiguous-completion outcomes remain contract work, not a promise that a
simple libc wrapper can recover every interrupted replacement.

## Close, process death and stale requests

Closing one descriptor consumes one reference. Other aliases and admitted
operations may retain the resource. Distinguish local descriptor retirement,
last-reference removal and confirmed backend cleanup. Final release requires
one owned cleanup obligation, not a successful local counter decrement alone.
Mappings can retain their own backing references after descriptor closure under
the [accepted VM lifetime contract](VIRTUAL-MEMORY.md#handles-and-lifetime).

Observe process death through the trusted lifecycle path and release its owned
references even when the application never calls close(). Preserve surviving
process aliases. Internal descriptor/session generations prevent queued requests
from attaching to reused slots or replacement instances. Public POSIX FD integers
remain reusable; generation protection does not make a stale application integer
safe after that index is reused.

In-flight operations retain and validate the reference they were admitted under;
closing/reusing the public index cannot redirect them to a new resource. Specify
the exact close-versus-operation ordering for the supported profile. An uncertain
remote consuming close cannot be blindly replayed, and an uncertain backend I/O
result cannot justify an assumed shared position. Preserve outstanding cleanup
and ambiguity until the owner can resolve them under its declared failure model.

## Small implementation and mapping integration

Begin with a bounded indexed descriptor table and straightforward synchronization.
Bind operations to the appropriate resource owner. Do not introduce a system-wide
broker solely to allocate POSIX integers. Hold references across service calls;
keep table locks out of blocking IPC while preventing slot reuse from changing
an admitted operation's identity. Exact locking and pending-state representation
remain implementation choices.

The [accepted musl backend](MUSL-VM-BACKEND.md) resolves mmap(fd, ...) through the
descriptor binding to obtain authorized VM backing, then invokes the kernel's
mapping path. A future poll/select adapter resolves supported readiness through
the same resource binding. Neither requires the kernel to interpret POSIX FD
numbers. Readiness, Unix-socket descriptor passing and general handle transfer
need separate scoped contracts before enablement; they are not implemented by
this descriptor decision.

The accepted [service I/O and device-control direction](SERVICE-IO.md), tracked
under [UP-03](../.planning/ROADMAP.md#up-03--service-io-completion-and-typed-device-control),
uses these authorized references for read/write/control. It specifies shared-
position ordering, operation completion and buffer lifetime; typed native control
sits below musl ioctl translation. Readiness and descriptor passing still require
their own contracts.

Accepted [readiness/waiting](READINESS-WAITS.md) under
[UP-04](../.planning/ROADMAP.md#up-04--readiness-and-native-wait-many) and
[Unix sockets/descriptor passing](UNIX-SOCKETS.md) under
[UP-05](../.planning/ROADMAP.md#up-05--unix-sockets-and-authorized-descriptor-passing)
extend these bindings with owner-defined observations and authorized queued
reference delegation. Exact enabling contracts and wider implementation remain
future work; general waiting/passing is not established by descriptor acceptance.

## Existing foundations and deferred choices

The [inheritance ownership review](NATIVE-INHERITANCE-REVIEW.md) already specifies
owner-held shared positions/references, alias restrictions, caller binding and
admission cleanup. The [shared-file witness](NATIVE-SHARED-FILES.md) exercises
both alias exit orders and actual final backend close. Userland's
[descriptor facade](../userland/docs/NATIVE-DESCRIPTORS.md) and
[bounded runtime responsibility](../userland/docs/SESSION-SDK-BOUNDARY.md)
remain separate evidence with their documented profile limits.

The new acceptance extends those foundations into an architectural direction;
it neither rewrites old receipts nor relabels them as complete POSIX support.
Preserve profile ABIs, SDK pins, quotas, smoke markers and rejection behavior
until matching producer/consumer evidence supports an explicit replacement.
HO-01's provisional general object-table research is not a prerequisite.

A client-local table with copied offsets/refcounts is simpler for one process
but fails shared-position/lifetime requirements across independent clients. One
user-space owner for each shared description avoids those copies. A kernel POSIX
file table or new universal broker adds policy/topology the requirement does not
need. This model can consolidate overlapping fixture ownership later; no existing
code is removed now. The real cost is reference coordination, concurrency and
failure accounting, which cannot be eliminated by moving them into libc.

Defer exact table/reference layouts, numeric limits, rights vocabulary, service
placement per resource class, locking, transfer wire formats and recovery protocol
to the first implementing consumer. Broader fcntl/append/locking semantics,
readiness and SCM_RIGHTS are later scoped work. Preserve the core distinction of
descriptor flags, shared state and enforceable rights when extending support.

## Dependencies and acceptance

UP-01 builds on existing capability, lifecycle and owner-bound I/O mechanisms;
basic descriptors do not wait for all VM-01/VM-02 work. Coordinate descriptor-to-VM
backing with the required VM-02 slice, and fork/exec with UP-02/R1-02 process work.
R1-04 loading and later Xorg/Mesa mapping/readiness/descriptor-passing consumers
use these contracts as their concrete requirements arise. Current implementation
priority remains unchanged; general graphics stays outside R1.

Before enabling a slice, require matching native/userland positive witnesses and
semantic rejection controls for independent opens versus shared duplicates,
alternating shared positions, alias flag scope, denied rights widening, foreign/
stale references, descriptor/reference exhaustion and rollback. Qualify atomic
replacement, both alias exit orders, process-death cleanup, exactly owned final
close, in-flight reference lifetime, FD reuse, failed exec preservation and enabled
close-on-exec creation/commit paths. Keep host models, native results, affected-
consumer acceptance and recovery claims separate. Documentation closes no runtime
milestone or release gate.

POSIX semantic references: [open](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html),
[dup](https://pubs.opengroup.org/onlinepubs/9799919799/functions/dup.html),
[fork](https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html),
and [exec](https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html).
They define compatibility requirements, not Aether's native internal architecture.
