# Native allocation implementation plan

2026-09-05. UL-028 completes the proposal/plan, not UL-003 owner acceptance or
UL-006/015 implementation. The canonical shared draft is
[Aether-standards: native memory](../../../Aether-standards/docs/NATIVE-C-MEMORY.md).
It is outside immutable v0.1.0 releases, is not a new consumer dependency and
must not be read automatically by a build. No native code changes in this turn.

## Current implementation assessment

The inspected `kernel/arch/x86_64/native_c.zig` uses 128 backing pages and 32
page tables per instance. `addPage` appends to a page array and panics on violated
loader assumptions. Runtime allocation needs a transactional, recoverable path
and reusable slots; it cannot call that loader helper unchanged on user input.
`byte` looks up page records and checks the write bit for writable copies. Adding
PROT_NONE requires explicit readable/present/ownership validation too. This is a
new-feature prerequisite, not evidence of a current reachable PROT_NONE bypass.

The current source also contains supervised-instance state/control work beyond
the older NATIVE-C.md summary. Preserve it; this read is not an integration test
or authority to replace companion changes. The memory extension needs rebasing
against current owner contracts before implementation. No claim is made about
that supervised path's readiness from source inspection alone.

## Ordered implementation work

| Local work | Producer / consumer and concrete outcome | Acceptance gate |
| --- | --- | --- |
| UL-003 agreement | Aether defines runtime arena, exact authority/result ABI, critical section and resource accounting; userland reviews libc expectations; sys-init reviews admission/lifetime boundary | Review the central draft; record actual owner acceptance and exclusions before changing the shared ABI |
| UL-015 translation | Userland retains pinned native libc build and explicit unsupported semantics; test first brk query, internal remap and metadata protection handling | No successful stubs; evaluate removal of musl's metadata mprotect ENOSYS exception; hash patch and audit linked paths |
| UL-006 mechanism slice | Aether adds anonymous mapping/protection/unmap with atomic errors, reusable bookkeeping and full cleanup | Implement owner tests for quotas, ranges, permissions, pinned TLS/clear-TID, peer isolation and rollback |
| UL-006 consumer | Userland adds bounded native allocation probe using the accepted exact ABI | Choose small payloads from recorded remaining capacity; prove malloc/realloc/calloc, metadata fallback, failure preservation and terminal cleanup |
| UL-003 integration | Aether/sys-init bind tested instance generation, authority and observer lifecycle | Preserve supervised work and existing success/negative contracts; fixture sink remains a separate limitation |

Do not copy the Linux reference's 1–128 MiB requests into a 512 KiB native pool.
First record image/stack/metadata occupancy, then derive payload and negative
sizes. Keep the 4 KiB TLS cap until pre-main allocation/teardown has its own
accepted extension. Full allocator source coverage, mmap/POSIX certification and
production entropy/login remain outside this implementation plan.

## Review issues requiring evidence

- Raw brk ENOSYS is not the same result as the reference's unchanged break on
  growth denial. Exercise the exact adapter behavior before claiming fallback.
- Musl tolerates metadata mprotect ENOSYS; a native protection requirement must
  not be bypassed by this exception. Protection denial must not publish metadata
  or accidentally crash the peer/kernel. Capture actual failure and retry state.
- Realloc copy fallback temporarily retains both allocations. Avoid releasing
  quota before the old mapping is actually removed, and preserve it on failure.
- Guard reservations consume resources; PROT_NONE cannot become a zero-cost way
  to exhaust page tables or bookkeeping. Unmap subranges and mapping splits need
  bounded accounting. Retained allocator metadata is not a leak merely because
  free does not unmap it; teardown must inventory it.
- Reject freeing/protecting active FS/TLS or registered clear-TID storage until
  its lifetime protocol supports invalidation. An address lookup through kernel
  backing aliases must respect current user access permissions.

## Evidence retention

[Review manifest](research/NATIVE-MEMORY-SOURCES.json) hashes the inspected kernel,
libc/reference and standards inputs. Existing reference runtime reports remain
unchanged. This turn validates local links, JSON and unchanged standards pins;
it does not rerun or claim native allocation support. The central draft's
acceptance cases become executable owner tests only after the exact contract is
selected. No new operation numbers, reviewed signer identities or release claims
are inferred from writing this plan.


## Reference-side adapter results (UL-029)

The [four-case experiment](../experiments/musl-reference/RUNTIME.md#native-adapter-error-questions-ul-029)
now demonstrates allocator fallback with raw brk ENOSYS from the first query.
Baseline metadata protection ENOSYS produces a fault; EACCES returns failure and
permits retry. The candidate strict patch makes ENOSYS return failure and permits
retry too. This closes the reference-side uncertainty above. Native entry/error
translation, patch adoption and enforcement still require UL-003/006/015 work;
no accepted ABI or full native allocator follows from the replacement-object test.


## Native build adoption (UL-030)

The native build now applies the strict metadata condition to each fresh musl
source tree and records exact source/patch/archive identity. A rebuilt descriptor
fixture passes its four existing target outcomes in an isolated Aether snapshot.
[Evidence](evidence/strict-native-libc-2026-09-05/summary.json). No native memory
operation was implemented; descriptor regression does not execute mallocng's
protection branch. UL-006 retains target allocation/protection-denial acceptance.


## Delivered owner ABI and consumer adoption (UL-032)

Aether delivered native-memory v1 and the user resumed integration. The
[userland adoption](NATIVE-MEMORY.md) now passes nine combined target cases plus
four ordinary descriptor regressions. This supersedes earlier waiting statements
for the bounded memory mechanism and consumer; general proposal acceptance and
remaining profile scope are still separate.
