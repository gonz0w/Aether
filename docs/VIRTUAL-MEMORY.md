# Virtual memory architecture

Status: accepted architectural direction, 2026-10-04, at the maintainer's request.
Aether owns the kernel mechanisms. Implementation is queued under
[VM-01](../.planning/ROADMAP.md#vm-01--vm-objects-address-space-mappings-and-pmap);
[STATE](../.planning/STATE.md) records progress. Exact native operations, rights
bits, locking and backing protocols require scoped implementation review. This
decision accepts the architecture without claiming a general VM implementation
or affected-consumer acceptance of a new ABI.

## Context and decision

Future mmap(), ELF loading, fork(), shared memory and Xorg/Mesa/GPU consumers
need one coherent memory model. Adopt the separation of backing objects,
address-space maps and a pmap-style hardware layer, borrowing the VM object/map
idea associated with FreeBSD and explicit memory objects associated with Zircon.
Keep Aether's capability authority, bounded resources and per-core ownership.

The broader [HO-01 handle/object research](HANDLE-OBJECT-RESEARCH.md) remains
provisional. VM-01 builds on existing typed capability and lifetime contracts;
its accepted VM-object direction does not depend on adopting HO-01's general
resource-table or POSIX descriptor proposals.

| Layer | Responsibility | Authority and representation |
| --- | --- | --- |
| VM object | What memory: size, backing, resident pages and sharing/COW state | First-class kernel object, reached through typed, rights-bearing handles |
| Mapping and address-space metadata | Where it appears: virtual range, object offset, permissions and private/shared behavior | Internal structures owned by the address space; mappings are not handles |
| pmap/MMU layer | How hardware represents it: page tables, hardware permission/cache attributes and translation invalidation | Architecture-specific implementation behind generic VM operations |

An address space owns a set of non-overlapping mappings. Each mapping references
a range of a VM object; one object may appear at different virtual addresses in
several address spaces. The initial index is a simple balanced range tree with
range lookup, overlap checks, insertion, removal and subrange splitting. Choose
the balancing algorithm during implementation; do not implement Maple Tree or
another advanced index before measured workloads justify its total complexity.

Generic VM owns object/mapping semantics, page faults, backing coordination,
sharing and COW. The pmap layer implements mapping, unmapping, protection changes
and invalidation for x86_64 first and aarch64 when that target is brought up.
Hardware page tables implement the metadata contract; they are not the source
of VM policy. Keep architecture-specific entries, fault decoding and cache rules
out of generic VM. The aarch64 implementation is an accepted direction, not a
new prerequisite for the x86_64 release.

## Objects and backing

Support these backing classes as consumers justify their executable slices:

- **Anonymous:** initially no resident private pages. Demand-zero faults allocate
  and clear a 4 KiB page before exposing it; reservation and physical commitment
  are distinct. An untouched reservation does not require eager physical backing.
- **File-backed:** an object represents an authorized file range. Faults obtain
  data through the filesystem service boundary; generic VM coordinates residency
  while filesystem policy remains in user space. Private writes use COW; shared
  writes require an explicit writeback, durability and error contract.
- **Shared:** authorized address spaces map the same VM object and see writes to
  shared pages. Shared memory uses shared objects rather than a second parallel
  memory mechanism. Sharing is mapping behavior, not necessarily a separate
  physical allocator or object type.
- **Device-backed:** an object describes an explicitly granted device range or
  buffer with device-appropriate cache/access attributes. CPU/device/GPU mappings
  use this path; arbitrary physical addresses cannot manufacture such an object.
  Device backing is not demand-zero RAM and is not implicitly copied by fork.

Initial generic VM pages are 4 KiB. This choice does not rewrite existing boot
or kernel page-table geometry. Keep allocation and metadata bounded with explicit
admission and exhaustion results. Demand paging defers commitment but does not
promise unbounded overcommit or successful future faults without resources.
Specify fault-time allocation/I/O failure before enabling the relevant backing.
No userspace pager API is required for the initial file-service integration.

## Handles and lifetime

Possession of a VM-object handle with the required rights authorizes operations
on that object. Mapping also requires authority over the target address space.
Type, generation, bounds, alignment, offsets and permission ceilings must be
checked before effects. Derivation/delegation can only narrow source authority;
numeric object IDs, virtual addresses and physical addresses confer no authority.
The exact rights vocabulary and ABI remain implementation work.

Closing a handle does not implicitly unmap an existing mapping. Mappings retain
their required object/backing references. Handle closure, revocation, unmapping,
object teardown and backing reclamation remain distinct under the existing
[capability contract](ARCHITECTURE.md#capability-and-lifetime-contract). Define
which paths a revocation disables rather than claiming all mappings disappeared.
Release backing only after references and CPU translations are safely removed;
zero reusable RAM before exposure to another protection domain.

Mutable objects and each address space have one authoritative kernel owner.
Retain core-local state and explicit cross-core messages; shared VM objects do
not introduce a global mutable allocator or capability table. A cross-core shared
mapping needs explicit owner coordination and completed invalidation before reuse.
The protocol, locks, fault-versus-unmap races, reference accounting and cancellation
rules must be specified for the first executable slice that needs them.

## Copy-on-write fork

For fork(), clone mapping metadata and initially share resident backing for
private mappings. Remove write permission in both parent and child and complete
the required TLB invalidation before either can write through an old translation.
On an authorized write fault, allocate/copy a private page and update only that
process's view. Untouched anonymous pages remain demand-zero. Shared mappings
continue to share their object; fork must not silently turn shared memory into
private copies. Deny unsupported device inheritance explicitly.

The COW representation, fault synchronization, admission rollback and ownership
of copied views remain implementation choices. Resource failure must not publish
a partial child or widen parent permissions. Process/descriptor policy stays
with its existing userland owner; COW is the native memory mechanism supporting
that policy. Existing bounded process-copy evidence does not establish COW.

## Security and translation defaults

- Data, stacks, anonymous and ordinary device mappings default to NX. Executable
  mappings require explicit authority and a supported loading/protection path.
- Enforce W^X, including writable aliases of executable backing. Permission
  changes must not create a bypass through another mapping or kernel copy path.
- Keep unmapped guard pages around stacks and other protected regions as their
  contracts require; faults at a guard must not allocate demand-zero memory.
- Disallow page-zero user mappings. Validate canonical/user-range addresses,
  arithmetic overflow, object offsets and full ranges before mutation.
- Make placement ASLR-ready: separate address selection from backing and avoid
  baking fixed user addresses into the generic contract. Actual randomization,
  entropy qualification and its acceptance tests remain future implementation.
- Do not routinely expose physical addresses through handles, query results or
  diagnostics. Scoped device authority defines allowed ranges internally.

Begin with correct, simple TLB invalidation. A conservative flush is acceptable;
unmap, protection reduction, COW write protection and address-space teardown must
complete invalidation on every CPU that could retain the affected translation
before reporting completion or reusing backing. Optimize flush ranges, batching,
PCID/ASID use and shootdowns only after correctness and measurements. Core-local
pinned execution can simplify the first slice; it does not waive later cross-core
invalidation obligations.

CPU mapping cleanup alone does not establish DMA quiescence. Before enabling
device/GPU buffers, specify cache coherence, device access, stop/reset and safe
teardown; retain the [graphics containment limits](ARCHITECTURE.md#graphics-progression).
Capability deletion, a timeout or a driver acknowledgment alone cannot authorize
reuse while hardware may still access backing.

## Consumers and dependency order

| Future consumer | Use of the accepted model |
| --- | --- |
| mmap(), munmap(), mprotect() | Userland translates POSIX requests into authorized object and mapping operations; anonymous/private/shared/file semantics use the same range metadata |
| ELF loading | Authorized executable/file objects provide segment backing, zero-filled BSS and protected mappings; loader validation and executable authority remain required |
| fork() | Mapping metadata and COW private views preserve process memory while shared objects remain shared |
| Shared memory | Delegated VM-object handles permit mappings in independent address spaces with restricted rights and explicit lifetime |
| Xorg, Mesa and GPU services | Shared RAM objects support client/service buffers; device-backed objects support granted framebuffer/MMIO/GPU resources without ambient physical-memory access |

Deliver VM-01 at the core-kernel memory stage after the existing protection,
capability and backing-ownership foundations, before general mmap/file mapping,
COW fork and Xorg/Mesa/GPU userspace integration. File-backed execution links to
R1-03/R1-04; process memory links to R1-02. File/device consumers require their
own service/driver contracts as well as VM. This dependency order does not move
desktop/accelerated graphics into R1 or require every future backing class before
the first anonymous-memory slice.

The accepted [musl/native mapping backend](MUSL-VM-BACKEND.md), queued as
[VM-02](../.planning/ROADMAP.md#vm-02--native-mapping-contract-and-musl-backend),
defines the direct anonymous-memory and service-authorized file/device boundary
for these consumers. Exact interfaces and coherence remain implementation work.

## Alternatives and deferred work

A single page-table-centric subsystem is initially smaller, but conflates backing,
placement and hardware and duplicates semantics across loader, mmap and fork.
The chosen separation gives each responsibility one owner. A handle per mapping
adds another authority/lifetime surface without a present consumer requirement;
keep mappings internal. The balanced range tree is the simple initial choice;
its predictable range operations are sufficient until measured otherwise.

This direction can eventually replace overlapping fixture-specific memory paths;
none are removed by this documentation change. Migration must preserve existing
ABI profiles and rejection behavior until matching producer/consumer evidence
supports an explicit replacement.

Defer huge pages, swap, sophisticated page reclamation/replacement, userspace
pagers and advanced mapping data structures until a concrete workload justifies
them. Basic allocation failure and safe release remain required now. Also defer
exact object layouts, balancing algorithm, syscall numbering, rights bits, backing
transport/writeback protocol, COW data structures and synchronization to scoped
implementation contracts. Acceptance is for the architecture, not those details.

## Implementation evidence required

VM-01 requires native evidence and semantic rejection controls for range/offset
validation, denied rights/type/stale handles, exhausted pages/metadata/tables,
failure rollback, demand-zero and zeroed reuse, guard/page-zero/NX/W^X enforcement,
mapping splits, reference lifetime and completed TLB cleanup. Qualify parent/child
COW isolation and retained sharing when fork is enabled; file faults/writeback
and device attributes/teardown when those backings are enabled. Broader sharing
needs cross-core race/invalidation evidence. Keep host models, native witnesses,
consumer acceptance and physical/device qualification separately identified.
Documentation acceptance closes no runtime, compatibility or release gate.
