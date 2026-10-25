# Linux reference and compiler-runtime results

2026-09-05. UL-004b/014/017/018 complete for the bounded Linux reference scope.
No native Aether execution or full libc/compiler-runtime conformance is claimed.

## Observed results

| Witness | Result |
| --- | --- |
| Startup/TLS/data/BSS/EBADF/output | Exit 0 and exact PASS line |
| Same plus 128 KiB allocate/touch/free | Exit 0 and exact PASS line |
| Bad argument, each program | Exit 10, no PASS output |
| Missing environment, each program | Exit 10, no PASS output |
| Closed stdout, each program | Exit 14, no PASS output |
| Four unsigned 128-bit quotient/remainder vectors plus one signed quotient | Exact independently calculated results, exit 0 and BUILTINS PASS |
| Same arithmetic executable without compiler-rt | Link fails on missing helpers, including __udivti3 and __divti3 |

The [runtime evidence](runtime-evidence.json) identifies each command, input build
hash, expected status and trace digest. Raw traces are retained in [traces](traces/startup-pass.trace).
The [arithmetic evidence](arithmetic-evidence.json) records its build and execution.
Source [arithmetic.c](arithmetic.c) contains precomputed constants from Python
integer division, avoiding a comparison against the same runtime helper.

## What the traces establish

For these successful inputs the startup probe uses arch_prctl (ARCH_SET_FS),
set_tid_address, write (including the deliberately invalid FD), and exit_group.
The allocator probe adds mmap, brk and munmap. Its metadata allocation exercises
brk expansion and a fixed PROT_NONE guard mapping. The input workload uses a
small TLS image, so it does not exercise startup TLS allocation through mmap.

Trace counts differ from static instruction-site counts: linked code includes
branches these inputs do not execute. In particular secure startup, allocator
fallback/exhaustion, short writes, signals, threads, and job control remain
untested. The absence of an operation in one trace is not permission to stub it.

These are **QEMU guest ABI traces** on an arm64 Linux host, not native x86-64
strace results. QEMU translates operations; it can differ from native behavior.
Guest set_tid_address and mapping details are not Aether contracts. Preserve this
reference for comparison, then require native target evidence before claiming
thread/context correctness or security boundaries.

## Linux environment and repeatability

Reused the already-running Podman VM. Created a dedicated temporary setup
container from cached Python image digest
`sha256:739e7213785e88c0f702dcdc12c0973afcbd606dbf021a589cab77d6b00b579d`.
Installed Debian arm64 qemu-user `1:10.0.11+ds-0+deb13u1` and strace `6.13+ds-1`.
Only QEMU's -strace facility was needed for the saved guest traces.

Retained the tool image locally as localhost/aether-userland-reference:20260905,
with exact image ID
`8d0dff22866c67ea5de1d66ff04a54f17e610a11e3a5c970414820663c7649a4`.
The setup container was removed. No VM was started/stopped, sibling changed or
unrelated container touched. The local image and workspace build inputs remain.

Tests run as UID 65534, with network disabled, read-only root and input mount,
all capabilities dropped and no-new-privileges. These settings constrain the
test harness; they are not evidence of Aether confinement. The VM kernel is
6.18.10-200.fc43.aarch64. QEMU executable hash and full versions are in evidence.

```sh
python3 experiments/musl-reference/run-linux.py
python3 experiments/musl-reference/check-builtins.py
```

Scripts fail if pinned build artifacts change or the local image is unavailable;
they do not pull a replacement. Container setup used live Debian package indices,
so the retained image ID pins the resulting tools, not a reproducible package
repository snapshot. Recreating the image elsewhere requires fetching the same
base/packages, recording the new image identity and rerunning the tests. This
is test tooling, not an Aether package-manager dependency or release artifact.

## Compiler-rt build

Built LLVM compiler-rt 21.1.8 with Clang 21.1.8 using its standalone builtins CMake
project and explicit x86_64-linux-musl compiler targets. Only target musl headers
and Clang resource headers are available to the C cross-build; the host config
is disabled. CMake and source extraction live in the workspace. The script
verifies input pins and re-extracts source/CMake on each build.

```sh
python3 experiments/musl-reference/build-builtins.py
```

Inputs are described in [builtins-inputs.json](builtins-inputs.json). Compiler-rt
and LLVM CMake modules match GitHub release API asset digests for
[LLVM 21.1.8](https://github.com/llvm/llvm-project/releases/tag/llvmorg-21.1.8).
The host CMake 3.31.6 wheel was obtained from PyPI over HTTPS and its local hash
recorded. No independent release signature/attestation verification is claimed.
The upstream [cross-builtins guide](https://llvm.org/docs/HowToCrossCompileBuiltinsOnArm.html)
informed the approach; actual options were checked against the pinned source.

Output is a 260,164-byte libclang_rt.builtins-x86_64.a with 173 inspected x86-64
members. [Archive evidence](builtins-evidence.json) identifies it. The arithmetic
link resolves helpers from that explicit archive, has no external unresolved
symbols or relocations, and passes static ELF/NX/WX checks before execution.
No runtime archive is silently added to the original startup/allocator probes.

The builtins build alone is not its full upstream test suite; the arithmetic
witness tests only selected signed/unsigned division and remainder paths.
Floating point, CPU detection, sanitizers, unwinding, C++ and Aether CPU-context
compatibility need separate evidence when required. This closes the host C SDK
experiment, not a production Aether toolchain ABI.

The first configuration used conflicting upstream target options and was fixed;
a later assembly step required an explicit workspace TMPDIR. No runtime functions
were patched or replaced to obtain the passing result.


## Large initial-thread TLS extension (UL-021)

`python3 experiments/musl-reference/check-large-tls.py` builds a new static
fixture using the retained SDK and pinned LLVM tools, then runs the same pinned
local QEMU image without network access. [Evidence](large-tls-evidence.json)
records tool/source/SDK hashes, commands, image identity, ELF headers and traces.
The SDK file hashes are an observation of the retained build inputs, not an
independent source-signature verification or a reproducibility comparison.

All three cases pass: normal execution exits 0 with the exact test marker; bad
arguments exit 10; changing the first byte of the ELF TLS initializer exits 12
before producing output. The negative fixture retains executable permissions;
an initial harness attempt lacked those permissions and was rejected by QEMU
before execution. The corrected run proves the initializer check executes.

The ELF is 15,608 bytes. PT_TLS contains 8,192 initialized bytes and 16,384 total
bytes, aligned to 64 bytes. The witness checks every initialized/zero-filled byte,
both addresses' alignment, and independent write/read patterns over both arrays.
Every case maps 16,664 anonymous RW bytes before arch_prctl and set_tid_address.
See [successful trace](traces/large-tls-pass.trace) and
[corruption trace](traces/large-tls-corrupt-initializer.trace).

This exercises musl's initial-thread allocation path, not pthread isolation,
allocation denial, protection enforcement, short/interrupted output, or Aether
execution. The existing host-static-c-v0 model deliberately rejects TLS larger
than 4 KiB; it has not been widened. A larger native profile needs quota-charged
startup allocation and defined fatal-startup cleanup before acceptance. Linux
mmap flags/numbers in these traces do not allocate an Aether ABI.


## Allocator failure extension (UL-023)

Run `python3 experiments/musl-reference/check-allocator-failure.py` with the existing
pinned SDK and local Podman image. Before compiling, the runner verifies the full
SDK inventory against the retained large-TLS input hashes, plus the LLVM tool
pins. [Evidence](allocator-failure-evidence.json) records input identities,
commands, ELF checks and both guest traces. No source downloads are required.

The Linux host launcher sets and verifies RLIMIT_DATA before executing QEMU,
using a 16 MiB translation cache. The limit covers the emulator as well as guest
allocations: **this is not an Aether quota or physical-memory-pressure test**.
Each disposable container has no network, a read-only root/input mount, no added
capabilities, a 512 MiB memory cap and a 32-process limit. The guest makes at most
sixteen 8 MiB allocations, avoiding unbounded host exhaustion.

The 64 MiB data-limit case passes after three successful 8 MiB allocations:
subsequent mmap fails with ENOMEM. Every byte of existing allocations is verified.
Growing the first allocation to 128 MiB fails through both mremap and mmap, with
ENOMEM and its original bytes intact. Overflowing calloc(SIZE_MAX, 2) returns
NULL/ENOMEM. After freeing all blocks, a fresh 8 MiB allocation can be written,
verified and freed. The exact success marker and exit 0 are required.

The 256 MiB control completes all sixteen allocations and deliberately exits 20
without the success marker. Its trace has no failed mmap. This confirms the
oracle requires exhaustion rather than accepting any successful program exit.
See [bounded trace](traces/allocator-failure-bounded.trace) and
[larger-limit control](traces/allocator-failure-roomy-control.trace).

Setup failures were rejected, not counted as allocator evidence: QEMU `-R 64M`
could not map the x86-64 vsyscall page; guest prlimit64 reported success but a
subsequent read did not retain the requested limit; the host limit with QEMU's
default cache prevented JIT startup. Applying the limit in the host launcher and
bounding the cache produced the recorded semantic cases. No guest setrlimit
support is claimed from those failed attempts.

Native follow-on: preserve existing storage when realloc fails; map failure to
honest errno; define remap or a bounded copy fallback, including temporary memory
cost; release mappings before reuse. This experiment exercises failed remap and
failed fallback, not successful fallback copying or allocator metadata brk
exhaustion. Short/interrupted I/O and protection failures remain UL-019 work.


## Short and interrupted output (UL-024)

Run `python3 experiments/musl-reference/check-interrupted-output.py`. The runner
verifies the retained SDK inventory and LLVM hashes before building, inspects the
static ELF and executes two cases in the pinned offline Linux/QEMU image.
[Evidence](interrupted-output-evidence.json) binds sources, tools, SDK, image,
commands, binary and guest traces. No native or sibling implementation changed.

A single-thread fixture fills a nonblocking pipe with known bytes, frees one
4 KiB page, and requires an 8 KiB write to return exactly 4 KiB. Draining checks
the original and newly written byte sequences. This relies on the identified
Linux pipe behavior; the 4 KiB geometry is not a portable POSIX requirement.

It then refills the pipe and switches the writer to blocking mode. A periodic
10 ms SIGALRM with SA_RESTART unset interrupts a one-byte write. The fixture
requires -1/EINTR, handler observation, and an unchanged full original payload.
The timer is stopped; draining and an EAGAIN read prove the interrupted byte was
not copied. An explicit retry must produce exactly one byte, followed by EAGAIN.
Both descriptors close on the passing path. The `no-retry` control omits that
write and must exit 20 at the delivery oracle without a success marker; remaining
descriptors are closed by process exit. No child processes are created.

Both cases pass their expected results. Traces require the actual short-write
result, EINTR/SIGALRM, rt_sigreturn and terminal exit. See
[passing trace](traces/interrupted-output-pass.trace) and
[no-retry control](traces/interrupted-output-no-retry.trace). A missing emulator,
startup failure or timeout does not satisfy these oracles. The initial sandboxed
attempt could not access Podman and was not counted as runtime evidence.

This establishes only selected Linux-emulated write/pipe/signal behavior. It does
not test SA_RESTART, interruption after a partial blocking transfer, stdio retry
policy, every signal schedule, native signal/pipe authority or shell job control.
The periodic timer bounds expected progress without depending on a single timed
signal; it is not a latency measurement. Native transport work must handle
signal-return assembly and preserve the distinction between copied byte counts
and errors. UL-019 retains protection and successful allocation-fallback work;
UL-007/008 retain native process/pipe/signal/session acceptance.


## Memory protection extension (UL-025)

Run `python3 experiments/musl-reference/check-protection.py`. The runner verifies
the retained SDK inventory and LLVM hashes, builds/inspects a static ELF, and
runs five isolated cases in the same pinned offline QEMU/Linux image.
[Evidence](protection-evidence.json) records exact inputs, commands and traces.

The passing case verifies invalid protection flags produce EINVAL without
changing either page's bytes/access; read-only access preserves data; a syscall
reading PROT_NONE memory returns EFAULT without output; restoring RW permits
writes; and mprotect after unmapping returns ENOMEM. Separate read-only-write,
PROT_NONE-read and unmapped-read cases require SIGSEGV with the exact attempted
address and SEGV_ACCERR or SEGV_MAPERR, respectively. The signal handler exits
40 only when all fault fields match; an unrelated crash cannot pass. The
skip-protection control must allow the write and exit 20, without signal delivery.
The passing/control paths explicitly unmap; fault paths terminate and rely on
Linux process cleanup, not a measured native reclaim witness.

All five outcomes pass. [Passing trace](traces/protection-pass.trace),
[read-only fault](traces/protection-readonly-write.trace),
[inaccessible read](traces/protection-none-read.trace),
[unmapped read](traces/protection-unmapped-read.trace), and
[omitted-protection control](traces/protection-skip-protection.trace).

Pinned musl 1.2.6 `src/mman/mprotect.c` rounds the starting address down and the
end up to page boundaries before the syscall. An initial expectation that an
unaligned libc request would fail was incorrect and rejected by the test. The
final fixture exercises a one-byte unaligned request and keeps the neighboring
page writable; invalid flags provide the error case. The trace oracle also
explicitly distinguishes delivered SIGSEGV from rt_sigaction registration.
These corrections do not change musl or native behavior.

Scope: Linux ABI emulation, not Aether capability enforcement, complete W^X/NX
validation, all range-overflow cases, concurrency or physical hardware. Mapping
permissions cannot be inferred from successful mprotect alone; the fault/control
cases exercise actual accesses. UL-019 still needs successful allocator fallback
and metadata-exhaustion coverage. Any shared requirement changes belong in
Aether-standards; local findings do not rewrite the pinned profile.


## Successful allocator fallback (UL-026)

Run `python3 experiments/musl-reference/check-allocator-fallback.py`. It verifies
the retained SDK inventory and LLVM pins, builds a static fixture and runs three
cases in the pinned offline Linux/QEMU image. [Evidence](allocator-fallback-evidence.json)
binds input hashes, the explicit linker option, commands, ELF and traces.

The fixture uses `--wrap=__mremap` to return MAP_FAILED/ENOSYS at the allocator's
internal remap boundary. This is **test fault injection**, not an actual kernel
denial or a musl source patch. It accepts only the observed four-argument
MREMAP_MAYMOVE call; it is not a general replacement for the variadic API.
Wrapping public mremap initially missed the internal call; the fixture detected
zero injected failures and rejected that attempt. The corrected boundary is
explicit in the retained build command and source.

Unmodified musl realloc grows a 1 MiB allocation to 2 MiB by allocating a new
mapping, copying the full original pattern, and freeing the old region. The
fixture requires exactly one injected failure, a different address, every old
byte preserved, and writable/verifiable new capacity. Traces require the new
mapping before successful unmap of the old, and eventual unmap of both regions.
They do not establish physical page reclamation or stale-capability enforcement.

All three expected outcomes pass: the injected case exits 0 with the exact marker;
allowing the real remap succeeds there and exits 20 at the fallback-only oracle;
corrupting one copied byte exits 21 at the data oracle. See
[passing trace](traces/allocator-fallback-pass.trace),
[real-remap control](traces/allocator-fallback-real-remap.trace), and
[corruption control](traces/allocator-fallback-corrupt-copy.trace).

This supports investigating an initial native ENOSYS remap response with working
allocation/copy/free semantics. It does not decide the native ABI or guarantee
all musl allocation paths work. Fallback temporarily holds old and new allocations,
so native quotas and failed-copy/cleanup behavior need explicit accounting.
UL-023 already covers failed growth preserving old bytes. UL-019 still retains
allocator metadata/brk exhaustion and its fallback behavior; no native allocation
or complete allocator/conformance claim follows from this experiment.


## Allocator metadata fallback (UL-027)

Run `python3 experiments/musl-reference/check-allocator-metadata.py` using the
retained SDK and pinned offline tool image. [Evidence](allocator-metadata-evidence.json)
records verified SDK/tool identities, fixture source, linker injection, ELF and
three guest traces. No musl source, native ABI or shared standard was changed.

The fixture queries the current Linux break and reserves one page immediately
above it using MAP_FIXED_NOREPLACE. A successful exact-address reservation is
required; it cannot overwrite a preexisting mapping. The allocator's attempted
brk expansion then returns the unchanged break. Musl falls back to an 8 KiB
PROT_NONE metadata mapping and makes its second page writable with mprotect.
A 1 KiB allocation is filled/checked/freed, then another allocation succeeds.
The fixture checks the break remained unchanged and releases its guard page.

A second case uses `--wrap=__mmap` to inject one ENOMEM only for the allocator's
anonymous PROT_NONE metadata request. It requires NULL/ENOMEM and exactly one
injected failure, then retries allocation and checks data/reuse. The injection
has no kernel syscall trace; its counter and return checks are the oracle.
A no-guard control allows ordinary brk growth and exits 20 because the metadata
fallback was not exercised. All three expected outcomes pass. See
[normal fallback](traces/allocator-metadata-pass.trace),
[denial/recovery](traces/allocator-metadata-deny-metadata.trace), and
[no-guard control](traces/allocator-metadata-no-guard.trace).

This is bounded brk denial plus injected metadata-allocation exhaustion, not
physical memory exhaustion, all metadata pool growth schedules or native quota
proof. Musl retains its metadata mapping for allocator lifetime; the test does
not demand unmapping retained allocator state on free. Process termination is
not a measured Aether reclaim witness. Permission-change denial, ENOSYS handling
and repeated pool expansion remain additional native-design acceptance work.

## Bounded reference suite complete (UL-019)

| Required area | Evidence |
| --- | --- |
| Large initial TLS | UL-021: initializer/zero-fill/alignment, pre-main mmap and corrupted initializer |
| Allocation exhaustion | UL-023: bounded ENOMEM, realloc preservation, calloc overflow, release/reuse and roomy control |
| Short/interrupted output | UL-024: partial bytes, EINTR, explicit retry and omitted-retry control |
| Protection failures | UL-025: error codes, exact faults, restored access and omitted-protection control |
| Successful realloc fallback | UL-026: injected unsupported remap, copy/release, real-remap and corruption controls |
| Metadata/brk fallback | UL-027: blocked growth, metadata mapping, one injected ENOMEM, recovery and no-guard control |

These 18 cases close UL-019 within the stated fixtures, not a general libc test
suite. Native allocation requirements are next under UL-003/006/015; their
acceptance must include capability scope, quota accounting, rollback of failed
setup, metadata protection, temporary realloc capacity and teardown. Preserve
these reference binaries/evidence when comparing a native implementation.


## Native adapter error questions (UL-029)

Run `python3 experiments/musl-reference/check-adapter-errors.py`. The runner
verifies the musl archive, retained SDK inventory and LLVM pins, extracts fresh
source, and compiles replacement allocator objects. Both static ELF variants are
inspected and run under the pinned offline Linux/QEMU image.
[Evidence](adapter-errors-evidence.json) records the archive, source/injection,
patch, SDK/tool, ELF and trace hashes. No native libc build has been changed.

A test-only replacement of mallocng's brk macro returns raw `(uintptr_t)-ENOSYS`
for both initial query and growth request. The fixture requires exactly two
calls and successful metadata fallback; it cannot pass by using real Linux brk.
Only the allocator object uses this injection. This is a source-level simulation
of native error values, not a target entry/assembly test or a public sbrk claim.

Four cases pass their expected outcomes:

| Variant / injection | Required result |
| --- | --- |
| Baseline / brk ENOSYS only | Allocation, pattern check and free succeed |
| Baseline / metadata mprotect EACCES once | Allocation returns NULL/EACCES; retry succeeds |
| Baseline / metadata mprotect ENOSYS once | SIGSEGV at the denied metadata page with SEGV_ACCERR; handler exits 40 |
| Strict / metadata mprotect ENOSYS once | Allocation returns NULL/ENOSYS; retry succeeds |

Protection injection uses linker wrapping at mprotect. It leaves the real
PROT_NONE mapping intact and checks the expected page-sized RW transition.
The strict object removes only the `&& errno != ENOSYS` condition from metadata
protection error handling; [candidate patch](metadata-protection-strict.patch).
Both objects otherwise retain the pinned allocator logic and the same brk test
injection. Actual permission restoration on retry goes through Linux mprotect.
The expected-fault oracle verifies signal, address inside the recorded denied
page, cause and denial count; unrelated crashes cannot satisfy it.

Recommendation: carry the strict condition into a reviewed native libc patch,
retain truthful raw brk ENOSYS, and test the actual target adapter paths. Returning
ENOMEM for all errors would conceal the observed EACCES/ENOSYS distinctions;
any translation needs an explicit contract. These experiments do not test all
pool-growth schedules, every allocator entry point, native rollback or enforcement.
They resolve the reference-side questions in UL-028, not owner acceptance or
native implementation. UL-019's original 18-case scope remains unchanged.
