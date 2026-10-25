# Native anonymous memory v1

Kernel-owned opt-in implementation, 2026-09-05. Select `-Dnative-memory=true`
with `-Dsmp=false` and an explicit `-Dnative-c-image=...`. AENATC01, AENSUP01 and
AENFD001 layouts are unchanged. Without the option, new memory operations return
ENOSYS and no memory grant is issued. The old profiles are not silently enabled.
This implements a bounded kernel subset of the [shared proposal](../../Aether-standards/docs/NATIVE-C-MEMORY.md).
It does not declare the entire proposal accepted by all owners or change a pinned
standards release. Userland owns its production adapter; sys-init owns admission
and supervision policy; pkg-mgr owns artifact transport.

## Grant and exact ABI

The optional initial auxv entry `0xa000` carries a caller-local memory grant (zero
when unavailable). The value binds the admitted slot and generation and cannot be
transferred or derived. The kernel checks it against the active state before any
mutation; a supplied address, PID, UID, slot number or guessed peer handle is not
authority. The native supervisor receives no such grant. Termination invalidates
it; replacement produces a new value, and a retained old value returns EACCES.

Use interrupt 0x81. RAX is the operation; RDI is the grant. Results are signed RAX:
a nonnegative address/value or negative errno. R8/R9 must be zero on input. R10
must be zero except for protect. Outputs other than the documented query values
are not an authority channel. RDX, RCX and R8 may be overwritten; callers must
account for them in inline assembly constraints.

| RAX | RSI | RDX | R10 | Successful result |
| --- | --- | --- | --- | --- |
| `0x22000` query | 0 | 0 | 0 | RAX free backing pages; RDX arena start; RCX arena end; R8 total quota (128) |
| `0x22001` map | byte length | permissions | 0 | Kernel-selected virtual address |
| `0x22002` protect | aligned address | byte length | permissions | 0 |
| `0x22003` unmap | aligned address | byte length | 0 | 0 |

Permissions: 0 NONE, 1 R, 3 RW. EXEC and write-only requests return EACCES;
unknown permission bits return EINVAL. Length must be nonzero and safely rounds
up to 4096 bytes. Addresses for protect/unmap must be page aligned. Reserved
argument fields must be zero. Missing/wrong/stale authority returns EACCES first,
then malformed reserved arguments return EINVAL. Map validates permissions and
length before resource checks. Protect/unmap validate range and pins first;
protect then validates permissions. Overflow returns EINVAL. Holes inside the
arena and resource exhaustion return ENOMEM. Mutation outside the anonymous arena
returns EACCES, including image and stack pages. Protect/unmap validate the entire
range before changing anything. Unmapping holes is deliberately stricter than
POSIX munmap.

No native operation accepts file descriptors, fixed placement, address hints,
shared memory or executable mappings. The conformance libc adapter accepts only
zero hint, MAP_PRIVATE|MAP_ANONYMOUS, fd -1 and offset zero; it rejects other mmap
classes with ENOSYS and translates negative results to errno. It retains musl's
address rounding for the mprotect facade while raw native requests require
alignment. brk and mremap remain ENOSYS; neither pretends to succeed.

## Resources, transactions and protection

The arena is `[0x10000000, 0x10080000)`, above admitted ELF image addresses and
the fixed stack, inside the existing low PD. Placement is first-fit. Each instance
still has 128 backing pages total, including ELF, stack and anonymous pages, and
32 leaf tables. One page record corresponds to each backing slot; NONE reserves
and zeros physical backing just like RW. Query reports actual remaining backing,
not the arena's nominal size. Loader occupancy is logged for this opt-in profile.

A pure validation/reservation pass selects every backing/record slot and verifies
contiguous arena capacity and leaf-table availability before effects. No allocation
or fallible step follows commit. Runtime input never calls the loader's panic-on-
exhaustion helper. Per-page records support subrange splits without allocating new
records; holes become reusable. The arena uses at most one extra leaf table, and
an empty arena releases its table slot for reuse.

All operations run on the BSP's interrupt-gate path with interrupts disabled.
Neither timer dispatch nor user-space stop can interleave with the transaction;
there is no asynchronous user cancellation during setup. This is not an SMP
transaction model. Host tests independently restrict backing, records, arena,
table availability and precommit selection to exercise failure without mutations.
Some production bounds coincide; one quota failure is not claimed to test them all.

NONE installs an absent user PTE. R is present/readable and not writable; RW is
present/writable. All anonymous pages are NX. Page metadata and kernel buffer-copy
validation enforce the same read/write permissions; a kernel alias cannot make a
PROT_NONE buffer accessible to a syscall. Every transferred byte is validated
before partial stream-copy effects. Kernel aliases of R/NONE backing are read-only.
Protection returns only after reloading CR3; native mode has no PCID/global user
translations. Unmap removes user access, makes cleanup aliases writable and flushes
before zeroing, verifying zeroes and returning quota. Mapping reuse is zero-filled.
Ordinary dangling C pointers inside one instance cannot be detected after same-VA
reuse; no stale-pointer protection is claimed.

Protect/unmap refuse any range intersecting registered four-byte clear-TID storage,
or the active FS page and preceding page (covering the bounded initial TLS layout).
The ELF TLS cap remains 4 KiB. This conservative pin can deny a neighboring page;
it is not a general TLS allocation registry. Before releasing anonymous TID
storage, the caller must register other valid writable storage. Teardown clears
TID, invalidates the grant and preserves the existing terminal/observer protocol.
Explicit supervised reclaim detaches the root and zeros the entire pool, including
retained allocator metadata; a fresh generation reuses the same bounded state.

## Reproduction and acceptance scope

Use a retained strict native-libc build and its pinned tool lock explicitly:

```sh
python3 scripts/memory_smoke.py \
  --libc-build /absolute/Aether-userland/build/native-c-BUILD \
  --tools-lock /absolute/Aether-userland/experiments/musl-reference/tools.lock.json
zig build test
zig build smoke
```

`memory_smoke.py` creates a new `zig-out/memory-suite-*` directory, builds the
kernel-owned conformance adapter/probe, and retains maps, source/libc/envelope
hashes, commands, image hashes and per-case serial logs. It checks the supplied
libc archive against its receipt and compiler/linker executables against the tool
lock. These establish byte identity, not authenticity or full toolchain closure.
No sibling files or packages are modified; builds use already installed inputs.
Each build has a bounded subprocess timeout and each QEMU run has a 30-second
watchdog. Scripts support --help/--version, exit 0 on success, 1 on operational
failure and 64 for invalid arguments. Incomplete runs retain their evidence.

The conformance facade in `user/native-memory` overrides only the three musl
mapping functions and adapts the retained fixture's I/O hook to the original
startup output transport. It is a kernel test consumer, not a replacement for
userland's descriptor facade. The supplied libc retains its strict metadata
protection patch. Production userland adoption, descriptor integration, larger
TLS/pre-main allocation, file-backed memory, native SMP and general POSIX
conformance remain separate work.


## Results: 2026-09-05

[Retained evidence](evidence/native-memory-2026-09-05/results.json) records nine
passing target cases: positive allocation, direct NONE read fault (PF code 4),
read-only write fault (PF code 7), read after unmap (PF code 4), withheld grant,
skipped permission tightening, skipped unmap zeroing, metadata protection denial
and retry, and supervised generation reuse. Each hardware-fault case requires the
peer to complete with status 0 and the expected 24-byte output; a timeout or generic
unrelated panic is not acceptance. The negative images deliberately fail the
ordinary native-success oracle; the suite accepts only their specific outcomes.

Positive and replacement images occupy 24 backing pages at admission, leaving
104. Two instances check zero bytes, distinct patterns, subrange NONE/R/RW,
permission-respecting kernel copies including a cross-page denied buffer, immutable
image/stack denial, wrong/peer/stale grants, pinned TLS/TID, strict holes and
failure preservation, and 40 full-capacity allocation/unmap cycles. Strict musl
mallocng then executes malloc, growing realloc, calloc and a quota-failed realloc
that preserves the old contents. brk/remap stay unsupported. A separately injected
first metadata protect failure returns EACCES through malloc; retry succeeds.
The supervisor conformance sequence reclaims both first-generation workers and a
second generation of slot zero, exercising real stale-grant rejection after reuse.
Existing sys-init policy is not replaced by this test sequence.

`zig build test` passes kernel host tests (including three new memory-planning
tests), 44 Python tests and all three standards checks. Default two-core smoke and
framebuffer, the retained legacy native startup envelope, and userland's four
existing descriptor-regression cases pass with memory disabled. No pinned standard
or sibling source file changed. Descriptor-facing allocation adoption remains
userland work; the memory test uses the legacy bounded output sink.

## Live-allocation stop and replacement

The kernel-owned `STOP_LIVE` conformance variant uses the existing supervision
ABI; it adds no kernel operation or production restart policy. Slot zero's first
worker maps every remaining backing page, checks zeroes, fills distinct data,
checks exhaustion, leaves one page R and another NONE, and registers clear-TID
storage in a retained RW page. Only then does it report readiness and yield.
The supervisor rejects live reclaim, starts the peer, stops the ready worker,
checks retained detail 143/kind 3/readiness and idempotent stop, and confirms the
peer is still running below its required 64 yields. Peer completion must follow.

Reclaim must invalidate observation, stop and reclaim through the old handle.
The replacement runs in the same slot with a new grant and checks every available
page for zeroes before writing, then runs the ordinary range/allocator checks.
The runner requires equal initial/replacement admission occupancy and quota.
Existing stale memory-grant checks run in the replacement. This exercises retained
anonymous pages and permission metadata, including clear-TID cleanup; it does not
prove interruption inside a memory syscall, native SMP teardown or sys-init's
production adapter acceptance.

`memory_smoke.py` now runs eleven cases with the same command above. In addition
to the original nine, `stop-live` requires successful peer and replacement exits
and three reclaims. `bad-stop` deliberately expects exit kind 1 after verified
stop kind 3; only supervisor result 304 with zero reclaims followed by the exact
native-profile panic satisfies this negative. Timeout, early worker failure or
another supervisor assertion cannot pass it. The negative tests the consumer's
terminal-kind expectation, not an injected failure of kernel zeroing (the
existing runtime-unmap zeroing negative remains separately covered).

[Retained eleven-case evidence](evidence/native-memory-stop-2026-09-05/results.json)
passes, together with kernel host tests, 44 Python tests and all three standards
checks. Kernel runtime source and companion repositories were unchanged.

## Page-table reservation contract — 2026-09-06

Before implementation: replace the native memory path's single-leaf assumption
with bounded precommit reservation of every leaf table touched by a request.
The measured x86_64 OpenZFS image alone exceeds one 2-MiB leaf span; this prepares
the transaction boundary for a separately scoped capacity extension. Current
128-page quota, arena, loader limits, grant ABI and single-thread/BSP scope remain
unchanged. No native OpenZFS support follows from this prerequisite.

Aether owns the planner and enforcement; userland remains the memory consumer,
sys-init owns admission policy and pkg-mgr transports artifacts. No shared standard
or consumer pin changes. The planner borrows immutable table-slot metadata and
returns a fixed bounded plan on the kernel stack; no heap, FFI, retained pointer,
external authority or fallible allocation is introduced. New tables consume only
this domain's existing 32-slot pool. Reuse vacant slots before extending its high
water mark. Resolve all slots before publishing any directory entry or zeroing
backing. Failure must preserve all caller mappings, table ownership and quotas.
Protect/unmap require every touched table to exist. Unmap releases each table only
when no anonymous record remains in that table, including PROT_NONE records.

Test synthetic ranges crossing 2-MiB boundaries, mixed existing/vacant/new slots,
late table exhaustion, missing-table protect/unmap, malformed/overflowing ranges
and bounded slot identity. These are host planner tests, not enlarged-arena target
evidence. Run all eleven current native memory cases, host/standards/workflow and
default boot regression; retain source snapshots, commands and all attempts.
No user-facing output changes or new script/profile entry points are planned.

## Page-table reservation result — 2026-09-06

The memory path now resolves all touched directory-to-leaf slots through a pure
bounded planner before creating mappings. It reuses vacant slots before extending
the local high water mark, retains existing table ownership and rejects a request
whose final table cannot be reserved without changing any metadata. Protect and
unmap resolve their entire existing-table set before effects. Unmap releases each
touched table only if no page record remains in that directory, including NONE
and any non-anonymous record; CR3 reload still completes invalidation before return.
All work remains BSP-local with interrupts disabled. No new allocator or shared
mutable pool was introduced. The plan has at most 32 entries on the kernel stack;
stack high-water measurement and optimized-mode qualification remain open.

[Retained evidence](evidence/native-memory-tables-2026-09-06/README.md) passes:
three new host tests covering cross-leaf placement, late exhaustion and invalid
geometry/bounds; all eleven native-memory positive/fault/denial/reuse controls;
all host checks including 85 Python cases and standards/workflow; Zig 0.16.0
formatting; and default two-core boot with framebuffer verification. An initial
format check rejected one test literal's spacing. The first memory suite passed,
but default QEMU could not bind its control socket in the sandbox. Both attempts
are retained; the final frozen run passes with the required local socket access.

The runtime arena and 128-page quota are unchanged, so actual multi-leaf anonymous
transactions are host-planner coverage only. No larger native filesystem workload,
new thread primitive, consumer adoption or shared-profile compliance is claimed.
Next: a bounded capacity/loader extension with real cross-leaf target allocation,
protection, partial table release and teardown/reuse. Widen backing-slot indices,
account for kernel backing aliases and preserve explicit per-domain admission
before increasing limits; this change alone cannot host the OpenZFS artifact.

## Extended backing experiment contract — 2026-09-06

Before implementation: explicit native-memory-large build option and --large
memory-suite mode select 2048 eager private backing pages (8 MiB) per native slot,
with an 8-MiB arena at the existing base. Default remains 128 pages. This is a
four-leaf transaction experiment justified by the measured 1287-page engine ELF,
not a selected OpenZFS service/cache budget or larger executable admission.
The loader file/image/TLS limits remain unchanged. Opt-in requires native memory.

Keep owner-local grants, errors, zeroing, NX, TLS/TID pins and stop/reclaim semantics.
Use quota-specific planner types and 16-bit backing indices for the large profile;
no global pool or implicit growth. Four fixed slots reserve 32 MiB of backing in
the opt-in kernel image. Expand only that profile's kernel alias coverage to 64 MiB
and reject image overflow before entry. Query reports actual profile quota/end.
Sys-init/userland policies and package pins remain owned by their companions;
this kernel conformance profile is not consumer acceptance. No new dependency/FFI.

Run all eleven existing memory outcomes in both profiles; the large probe also
checks every backing page, cross-leaf protection, full middle-leaf release/reuse
and retained neighbors. A single bad boundary expectation must reject specifically.
Use three large saturation rounds instead of forty small rounds to bound fixture
cost; neither is a performance/soak claim. Host planner tests cover the widened
slot range and exact quota failure. Freeze inputs and retain all attempts; run
host/standards/workflow, scoped formatting and default boot checks. Kernel stack
high-water and native service budget remain unmeasured. Update this reference
and workflow inventory; preserve machine markers and existing adapter ABI.

The large profile also reserves a 64-KiB BSP interrupt stack (default 16 KiB),
accounting for bounded 2048-slot reservation plans and Debug call frames. This
is a fixed experimental bound, not a measured maximum. Its extra negative flips
the middle-leaf reuse expectation and must fail at worker result 129; skipped
protection must fail at the earlier cross-leaf buffer-denial check (123).

## Extended backing result — 2026-09-06

`-Dnative-memory-large=true` now selects 2048 private backing/record pages per
native slot and arena `[0x10000000,0x10800000)`. It requires native-memory=true;
query returns total 2048 and actual remaining backing. The tested image occupies
24 pages, leaving 2024. The default remains total 128 with 104 remaining for that
image. Admission diagnostics now report the selected quota; the suite rejects
missing or inconsistent counts. Default marker/schema bytes are preserved.

A quota-specific planner widens indices to u16 and preserves atomic reservation,
permissions and pins. Only the opt-in kernel reserves four 8-MiB backing bundles,
64-MiB kernel alias coverage and a 64-KiB BSP interrupt stack. Default backing,
16-MiB alias coverage and 16-KiB interrupt stack remain unchanged. Backing is eager
and fixed at boot, not overcommit, a global allocator or a service-selected quota.
This 8-MiB experiment is not a chosen OpenZFS cache/runtime budget. The static ELF
file, mapped-image and TLS limits remain unchanged; Linux PIE support is not added.

Run both modes with the same explicit strict-libc and tool pins:

```sh
python3 scripts/memory_smoke.py --large \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json
python3 scripts/memory_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json
```

[Retained qualification](evidence/native-memory-capacity-2026-09-06/README.md)
passes twelve large and eleven default target cases. The large probe checks every
available byte, changes protection across a 2-MiB boundary, frees/reuses an entire
middle leaf and verifies retained neighboring data and zeroed new backing. Its
CPU read/write/unmap fault probes access the second leaf and require exact page
fault codes plus peer completion. Stop/replacement repeats full allocation and
zero checks across generations. A deliberately inverted middle-leaf reuse check
rejects at result 129; skipped protection rejects at cross-leaf denial result 123.
Other existing denial/zeroing/retry/stale-grant controls remain passing.

Host checks include widened slot 2047/quota tests and three admission-oracle
regressions (88 Python cases total), with standards/workflow, Zig formatting and
default two-core boot/framebuffer passing. Invalid large-without-memory selection
rejects explicitly. Initial workflow inventory misclassification and the misleading
old large-profile diagnostic are retained and corrected; the new checker rejects
the old log. Existing compact C fixture style remains a scoped migration item;
no whole-file reformat, C engine change, dependency update or companion edit.

Next: larger static executable admission with quota-aware preflight and retained
rejection cases, then native threads/waits and engine platform integration. Native
OpenZFS, full filesystem paths and assembled shell/package boot remain open.
No independent consumer acceptance, stack high-water/optimized-mode qualification
or release readiness is inferred from these Debug-kernel QEMU cases.

## Opt-in native child-context storage

With the [bounded thread extension](NATIVE-C.md#bounded-shared-address-space-thread-contract--2026-09-06),
protect/unmap additionally checks every live child FS/TID range and its designated
stack page, regardless of which context invokes the memory grant. Child exit ends
its pins only after execution stops and TID clears. Domain stop quiesces both
contexts before backing reuse. The existing main-context pins, mapping ABI and
quotas remain unchanged. This does not supply a general pthread stack allocator.

The [explicit stack-range extension](NATIVE-C.md#native-child-stack-range-contract--2026-09-06)
pins every page of the declared child stack through running and blocked states.
It requires existing anonymous RW/NX backing and grants no additional quota.
Caller-created PROT_NONE guard pages retain their existing access behavior.
Legacy child creation still designates one page.

The [child TLS/TID storage extension](NATIVE-C.md#native-child-tls-and-tid-storage-contract--2026-09-06)
also pins every page of its declared anonymous RW/NX TLS span, even when FS moves
within that span. Creation's parent-TID output is a one-time write and gains no
lifetime pin. The independent clear-TID word retains the existing pin and wake
semantics. This opt-in mode does not register a full main-context TLS extent.

## Blocked native wait words

The [native wait extension](NATIVE-C.md#native-compare-and-wait-contract--2026-09-06)
pins each registered four-byte word against protect/unmap until wake, timeout or
stop cancellation. This check covers both contexts regardless of the caller and
is additional to stack/TLS/TID pins. Registration and mapping mutation are serialized
by the BSP interrupt gate. Stop cancels registrations before TID/backing cleanup;
replacement cannot inherit old wait state. Mapping and quota ABIs are unchanged.

The [wait without a deadline](NATIVE-C.md#native-wait-without-a-deadline-contract--2026-09-06)
uses the same registration and word pin. Only matching wake, clear-TID wake or
domain-stop cancellation removes that registration; timer progress alone cannot
release its pin. The existing experiment-wide watchdogs remain in force.
