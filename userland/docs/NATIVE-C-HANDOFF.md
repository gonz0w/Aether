# Native C experiment: concrete consumer handoff


> Current scope, 2026-09-05: the [bounded native experiment](../experiments/native-c/README.md) now demonstrates startup, private TLS/FP context, partial output and cleanup. The [kernel-owned contract](../../aether/docs/NATIVE-C.md) defines its exact ABI and narrower limits. Requirements and earlier gap snapshots below remain proposals for broader support; they do not negate that witness. Shared requirements are owned by [Aether-standards](../../../Aether-standards/docs/CATALOG.md), consumed through the [Distribution adoption](DISTRIBUTION.md). Native allocation, service-owned I/O and general POSIX integration remain open.

2026-09-05. UL-003 consumer-side proposal ready for review; shared acceptance and
native mechanisms remain open. This project owns these requirements and tests,
not implementation assignments in sibling repositories.

## Proposed first integration

Launch one source-rebuilt, statically linked musl C probe in a fresh address
space on one core. It checks startup args/environment, initialized and zeroed
data, a TLS initializer/update, an invalid descriptor error, a known output
sequence and successful exit. Preserve the unmodified Linux reference as the
comparison baseline. The allocator variant follows as a separate slice.

The [host launch profile](../experiments/launch-profile/README.md) now makes ELF
limits, page mappings, RELRO, TLS template and stack bytes executable proposals.
The [startup plan](../experiments/launch-profile/startup-plan.json) describes the
actual reference image. All addresses and bounds there are proposed test values,
not a frozen kernel ABI. The reference ELF is Linux machine code, not a native
payload; the libc transport changes still need implementation and comparison.

## Responsibilities proposed for this experiment

| Component | Proposed owner / interface |
| --- | --- |
| Musl source adaptation, libc-facing error translation, C probe and cross-build | Userland |
| ELF validation/loading, initial context, memory permissions, FS and FP/SIMD context, task stop/reclaim and capability enforcement | Aether mechanism owner |
| Bootstrap grants, observation and session/service policy | sys-init; use existing lifecycle evidence where semantics match |
| Immutable executable/manifest transport with target identity and ordinary file modes | pkg-mgr; no install-to-start coupling |
| Bounded diagnostic byte sink and FD facade | Userland proposes the facade; native sink owner/grant contract must be agreed |

Do not create a global POSIX server or service catalogue to run this one program.
The first launch may use trusted boot-supplied bytes and a bounded output sink,
without a disk filesystem, package installation or general PID 1 environment.
That keeps OpenZFS evaluation and broader service policy independent.

## Native operations still required

Use symbolic operation names until the kernel owner selects a versioned entry
and ABI. No existing int 0x80 operation number is reused by this proposal.

| Operation | Contract to agree | Required negative evidence |
| --- | --- | --- |
| launch-static-c | Validated image, bounded initial data, resource owner, immutable launch identity, initial grants; publish runnable state only after setup completes | Invalid image/grant/context or exhausted quota leaves no runnable partial task or leaked backing |
| set-thread-pointer | Change only caller FS base under the agreed user-address rules; preserve it across context switch | Invalid address rejected; two contexts retain distinct TLS/CPU state |
| register-thread-exit-address | Define address validation, caller identity and write/wake/lifetime semantics corresponding to retained musl conventions | No stale pointer writes after teardown; no synthetic successful thread support |
| write-output | Per-caller descriptor-to-grant lookup; validate pointer/length; define copy/IPC lifetime and bounded chunking; no escalation through sink's own rights | Negative FD, wrong rights, stale handle, inaccessible/overflowing buffer and oversized request fail correctly |
| exit-process | Stop executing caller, retain status for authorized observer, invalidate grants/mappings and reclaim in defined order | No return to exited code; wrong observer denied; stale references cannot reach reused memory |

The Linux reference's early operations are arch_prctl, set_tid_address, write and
exit_group. This observation determines the first adapter workload, not the entire
runtime API. Direct assembly entry sites must be covered by the adaptation.

Buffer design remains a real decision: current register-only IPC cannot simply
carry an arbitrary user pointer into another address space. Prefer an initially
bounded copy into service-owned/request-owned storage with explicit lifetimes;
compare actual native mechanisms before selecting a byte limit or shared mapping.
The receiver must know which caller/grant authorized the request. Never treat a
host-side preflight check as the enforcement boundary: applications can bypass libc.

For clear-TID registration, either implement the supported semantics or explicitly
adapt musl's initial-thread handling and document/test the narrower profile.
Returning a made-up ID while ignoring required behavior is not acceptable.
Thread creation, cancellation and signal delivery remain separate gates.

## Launch and failure sequence

1. Validate image and configuration without exposing a runnable task.
2. Reserve bounded backing and authority; zero/load pages and initial stack.
3. Establish read-only/executable protections and remove loader write aliases;
   initialize required CPU context and grant only the declared output access.
4. Start the instance. Its native libc adapter must use the accepted entry.
5. Observe exact output and terminal status. Preserve status through cleanup;
   successful stop request alone does not prove reclaim completion.
6. Exercise a second instance to check zeroing, stale references and TLS/CPU
   isolation. Inject launch failure at each allocation/publication boundary.

General x86-64 C may use vector registers and red-zone storage. The image build
profile and interrupt/context implementation must agree before running it. This
is not resolved by a single integer-only fixture or by the host ELF checker.
Real entropy is required for the hardened startup profile; predictable host test
bytes must not be copied into a production image builder.

## Current companion facts and remaining gate

Aether now reports bounded remote stop/reclaim/replacement, live display and
lifecycle v1. Its general executable/C/FD interfaces are still absent. Sys-init
has independently consumed lifecycle v1 successfully; its blanket wait is lifted
for that fixture only. pkg-mgr now preserves ordinary file modes and supports
private-root binary transport/replacement. These are useful mechanisms, not an
accepted C runtime or permission to change sibling policy.

No sibling code or tests were changed/run for this handoff. Reviewed working-file
hashes are in [handoff sources](research/NATIVE-C-SOURCES.json). Next native work
needs concrete agreement on the five operations above and implementation owners;
UL-003 remains active and UL-015 remains waiting. Independent UL-019 reference
failure/large-TLS coverage can proceed while those mechanisms are developed.


## Additional reference evidence: large initial TLS

UL-021 demonstrates 16 KiB initial-thread TLS with initialized and zero-filled
regions and 64-byte alignment. Musl maps 16,664 anonymous RW bytes before setting
FS and entering main, even though the application does not call malloc.
[Results and limitations](../experiments/musl-reference/RUNTIME.md#large-initial-thread-tls-extension-ul-021).
This does not widen the first host model's 4 KiB TLS cap. Before accepting larger
TLS, define allocation authority/quota before libc initialization and teardown
when startup allocation or thread-pointer setup fails. The first small probe's
observed call set must not be treated as sufficient for all static C programs.


## Allocator failure evidence (UL-023)

The [bounded Linux reference](../experiments/musl-reference/RUNTIME.md#allocator-failure-extension-ul-023)
now exercises ENOMEM and original-buffer preservation when both realloc remap
and allocation fallback fail, calloc multiplication overflow, and allocation
following release. A larger-limit control rejects the exhaustion oracle. These
are consumer evidence for a future native allocation proposal; they neither
allocate native operation numbers nor revise the pinned Distribution profile.
A native remap/copy decision must account for temporary quota, old-buffer lifetime
and cleanup on failure. Successful fallback and native enforcement remain open.


## Next native slice

UL-019 reference coverage is complete in its bounded scope. The canonical
[native-memory proposal](../../../Aether-standards/docs/NATIVE-C-MEMORY.md) and
[local implementation plan](NATIVE-MEMORY-PLAN.md) supersede older statements
above that reference testing is still the next step. UL-003 agreement and
UL-006/015 implementation remain open.
