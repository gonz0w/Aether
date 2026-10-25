# Musl backend and native memory mapping

Status: accepted architectural direction, 2026-10-04, by the maintainer after
the mmap discussion. Implementation is queued under
[VM-02](../.planning/ROADMAP.md#vm-02--native-mapping-contract-and-musl-backend).
Aether owns native enforcement; Aether-userland owns the production musl port
and POSIX adapters. Exact interfaces and affected-consumer acceptance remain
implementation work. [STATE](../.planning/STATE.md) records progress.

## Decision and scope

Keep musl as the C/POSIX library with a small, maintained Aether-specific OS
backend. That backend translates supported operations into native capability
calls and scoped service requests. Build on the accepted
[VM object/map/pmap architecture](VIRTUAL-MEMORY.md), existing typed capabilities
and the source-rebuilt musl experiment rather than adding a second object manager.

The kernel's public contract is native: VM objects, address-space mappings,
rights, bounded resources and lifetime. Musl's Linux-shaped internal arguments
and errors may remain a private porting convention where they reduce patch
burden. This does not commit Aether to a Linux kernel syscall ABI or arbitrary
Linux-binary compatibility. Native Rust/Zig programs can use the same native
operations and service protocols directly without routing through musl.

| Responsibility | Owner and boundary |
| --- | --- |
| C/POSIX interpretation and errno translation | Aether-userland's musl backend, including descriptor resolution through its existing owner |
| Anonymous VM creation, mapping, protection, unmapping and demand-zero faults | Aether kernel, with caller-scoped resource/address-space authority |
| File/device backing authorization and policy | The relevant capability-scoped filesystem/device service |
| Hardware mappings, permissions, reference lifetime and TLB cleanup | Aether generic VM plus architecture-specific pmap |
| Admission/supervision policy and package artifacts | Existing sys-init and pkg-mgr owners respectively |

This is an accepted ownership boundary, not a new service topology or a generic
RPC framework. It assigns no new syscall number, rights bit, handle layout,
protocol version, production SDK pin or quota.

The accepted [descriptor ownership design](FILE-DESCRIPTORS.md), tracked under
[UP-01](../.planning/ROADMAP.md#up-01--inherited-file-ownership-and-composable-processfile-capacity),
separates process-local FD bindings from owner-held shared open instances and
native authority. File/device mapping resolves through that boundary; basic
descriptor work does not wait for every VM feature.

## Anonymous mappings use the native VM path

For anonymous private mmap(), the backend obtains an anonymous VM object under
the caller's resource grant, maps it into the caller's address space and returns
the virtual address. Creation and mapping are conceptual steps; exact operation
names and whether a bounded combined operation is needed remain contract work.

Ordinary application mapping acts on its own address space. Mapping another
process requires separately delegated address-space authority. The kernel checks
object type, rights, generation, bounds, offset and permission ceilings before
effects. The backend cannot widen the caller's grant or use ambient supervisor
authority. A mapping retains the object references it needs; closing a temporary
object handle does not unmap it.

Demand-zero faults stay in generic VM. An ordinary heap allocation does not
require a filesystem request or a separate memory-service round trip per page.
Allocation policy/admission can remain outside the kernel without moving CPU
fault handling out of the accepted initial VM design. Preserve the existing
core-local owner and explicit cross-core coordination rules.

## File and device mappings use authorized service backing

For a file mapping, resolve the process-local descriptor through its descriptor
owner, request an authorized mapping resource from the filesystem service, then
invoke native mapping operations. The equivalent device-service path supplies
an authorized device-backed object and its access/cache constraints. Numeric
descriptors, paths and physical addresses alone are not mapping authority.

The service controls access to its backing. The kernel enforces placement,
permissions and safe mapping/backing lifetime. All checks must also hold for
applications that bypass musl and invoke native operations directly. The backend
and service must not become confused deputies for callers with narrower grants.

Define service failure, cancellation, partial admission, object-handle transfer
and cleanup before enabling each backing class. Acquire backing and mapping
resources without publishing a partial mapping or leaking grants on failure.
These rules require explicit protocols, not an assumption that existing IPC
can already transfer arbitrary VM-object authority.

File-backed coherence remains implementation work: define mapped versus ordinary
file I/O, file size/truncation, private COW, shared writes, writeback failures and
msync() completion/durability. A copied file buffer is not a substitute for
coherent writable MAP_SHARED. Begin with a narrower explicitly supported file
mapping class when needed; do not claim unsupported shared/writeback semantics.
The initial route must not require a general userspace pager. Device/GPU mappings
retain their separate cache/coherence, DMA quiescence and teardown requirements.

## Use musl's actual memory requirements

The first useful mapping slice must support anonymous zero-filled memory, real
unmapping, PROT_NONE reservations and protection changes for allocator metadata
and thread guards. Preserve NX, W^X including aliases, guard pages, page-zero
exclusion, ASLR-ready placement and no routine physical-address disclosure.
Correct TLB invalidation precedes completion and backing reuse.

Validate length/alignment/offset arithmetic and actual supported flags. Address
hints and fixed placement/replacement need explicit semantics, conflict handling
and rollback before support is advertised. Do not translate all failures into
ENOMEM or return success for unsupported protection, unmapping or synchronization.
Mapping support alone does not establish complete POSIX or pthread support.

Use the tested allocation/copy fallback while brk and remapping are unavailable
in the bounded port. Qualify every newly enabled realloc path, preserving the
original buffer on failure. Keep protection denial meaningful; the current
strict metadata-protection adaptation must not be weakened to hide missing VM.
Additional native brk/remap operations are deferred until consumer needs justify
them. Exact fault-time resource failure and its process outcome also need a
contract: demand-zero is not an unlimited commitment guarantee.

Port coverage includes musl's internal symbols and direct assembly paths, not
only public mmap() or one syscall header. Review startup/TLS, thread creation,
cancellation, signal restoration and thread teardown as those paths are enabled.
Keep patches small, pinned, recorded and reproducible, with matching native
behavioral evidence and explicit unsupported branches.

## Existing evidence and migration

Userland's [decision 002](../userland/docs/decisions/002-native-musl-experiment.md)
selected the narrow native-transport experiment. Its
[source-rebuilt musl fixture](../userland/experiments/native-c/README.md)
and [bounded memory adapter](../userland/docs/NATIVE-MEMORY.md) are
existing foundations. Aether's [native memory v1](NATIVE-MEMORY.md) remains the
authoritative bounded ABI; its eager anonymous arena is not general object-based,
file-backed or demand-paged VM.

This acceptance records the broader design boundary without relabeling old
fixtures, changing sibling documents or closing SDK/consumer/release gates.
Preserve existing profiles and rejection behavior until an explicitly versioned
replacement has matching producer/consumer qualification.

## Alternatives and consequences

An unchanged Linux syscall entry minimizes some musl changes but broadens the
machine-level compatibility commitment. A deep rewrite of musl's OS-sensitive
internals increases recurring upstream maintenance. The chosen small native
backend retains useful internal conventions while keeping enforcing contracts
native. A separate memory-service round trip for ordinary anonymous faults adds
protocol/recovery work that the accepted kernel VM can already own.

Borrow the small backend idea from [seL4's musl support](https://docs.sel4.systems/projects/user_libs/)
and the libc/service-I/O separation illustrated by [Fuchsia's libc](https://fuchsia.dev/fuchsia-src/development/languages/c-cpp/libc).
seL4 documents these libraries as prototyping tools; Fuchsia's documented libc
omits fork, exec and Unix signals. Neither is a complete compatibility template
for Aether. [Upstream musl mmap](https://git.musl-libc.org/cgit/musl/tree/src/mman/mmap.c)
shows the OS-facing boundary being adapted.

This split can consolidate overlapping memory adapters as consumer contracts
mature; none are removed now. Retaining a port costs upstream merge review and
native testing. Shared-file coherence and service failure remain real complexity
to resolve, not behavior that can be hidden inside a wrapper.

## Dependency and acceptance

VM-02 follows the required VM-01 enforcing slice, before broader musl mmap and
file/device consumers. It supports R1-02 allocator/process memory and R1-03/R1-04
file-backed execution, with later Xorg/Mesa/GPU work retaining its own device
gates. Current bounded shell/storage/backing work keeps its priority; initial
anonymous support does not wait for filesystem completion or every VM-01 class.

Before enabling a slice, require native positive/semantic rejection witnesses
and a matching userland consumer for rights/type/stale references, malformed
ranges, unsupported flags, resource exhaustion, rollback, zero-fill/reuse,
PROT_NONE/guard/NX/W^X and completed TLB cleanup. Exercise real musl allocator
metadata protection, allocation/free, failed realloc preservation and enabled
thread guard/teardown paths. File/device slices additionally require backing
authorization, service failure, lifetime and coherent shared/writeback or device
teardown evidence. Host models alone establish none of those native outcomes.

Exact ABI, descriptor-to-backing/transfer protocol, file-cache/writeback design,
placement semantics and wider musl thread/process coverage remain implementation
work. Huge pages, sophisticated reclamation/swap and general userspace pagers
retain VM-01's deferral. Architectural acceptance closes no runtime milestone.
