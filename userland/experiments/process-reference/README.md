# Process and descriptor reference witness (UL-035)

Nine bounded outcomes pass with the pinned Clang/LLD 21.1.8 and unmodified musl
1.2.6 Linux SDK. This witness narrows dash's process/descriptor requirements; it
implements no Aether process service or new shared ABI.

Run from the repository root after the existing SDK and container setup:

```sh
python3 experiments/process-reference/check.py
```

The script verifies LLVM/make executable hashes, the complete retained SDK file
inventory and musl archive digest before compiling/extracting. It uses explicit
static target startup/libc inputs, excludes host headers/configuration, inspects
ELF architecture/dependencies/permissions, and creates a fresh private build root.
No upstream patch or fault injection is applied. Builds do not fetch dependencies.
Host tool/shared-library closure and source authentication retain the limitations
of the [musl reference](../musl-reference/README.md).

Retained run: `build/process-reference-d5slesr6`.
[Durable evidence](../../docs/evidence/process-reference-2026-09-05/summary.json)
contains the full input identities, audited source hashes, commands, headers,
expected statuses and guest traces.

| Case | Expected exit | Oracle |
| --- | --- | --- |
| fork | 0 | Child changes global/TLS/heap state without changing parent state; FD_CLOEXEC is descriptor-local; O_APPEND and offsets are shared; child closure leaves parent handle open; status 7 is reaped once, then ECHILD |
| reopen-control | 20 | A separately opened file fails the same shared-offset oracle |
| exec | 0 | FD 40 closes, FD 41 survives with shared offset; quoted argument/environment arrive; child reads c, advancing parent's offset; child is reaped |
| cloexec-control | 21 | Omitting FD 40's close-on-exec flag makes the replacement image reject the inherited descriptor |
| failed-exec | 0 | ENOENT and EACCES leave PID, cwd, global/TLS state, descriptor flags and file offset intact; no child exists |
| pipe | 0 | Child byte arrives; retained writer alias keeps empty read at EAGAIN; closing it produces EOF; closed reader produces EPIPE with SIGPIPE ignored |
| writer-control | 22 | Keeping the writer alias open fails the same EOF oracle; explicit cleanup follows |
| fd-exhaustion | 0 | Real 32-FD limit reaches EMFILE; a pipe with only one free slot fails without consuming it; freeing a second slot permits a pipe; handles close successfully |
| vfork-exit | 0 | Assembly vfork entry returns a child whose _exit(17) status is reaped, followed by ECHILD |

Each run uses the pinned image from the earlier Linux reference, UID 65534,
network disabled, dropped capabilities, a read-only root and input mount,
16 MiB noexec scratch, 512 MiB container memory and a 32-PID limit. Timeout or
container failure cannot count as a semantic pass. The FD limit is set by the
guest and its EMFILE behavior is exercised, not inferred from a successful setter.

Successful exec explicitly replaces the child with the container's native
`/usr/bin/qemu-x86_64 -strace /inputs/probe exec-child ...`. This tests inheritance
across a real exec boundary without assuming x86 binfmt registration. It is not
direct Aether or native x86-64 ELF replacement. Both pre/post-exec guest traces
are retained; concurrent lines may interleave.

The vfork case intentionally performs only _exit in the child. It does not prove
shared-address-space or parent-suspension semantics under emulation. The suite
is single-threaded; it does not cover pthread-atfork, cancellation, fork failure,
interrupted waits, signal-frame correctness, descriptor races, all possible FD
leaks, TTY/session cleanup or cross-process native capability enforcement.
Negative controls differ in deliberate application actions; no kernel/library
failure is injected. Return codes 20–22 are oracle rejections, not setup failures.

See the [exact musl path audit](../../docs/research/MUSL-PROCESS-FD.md). UL-036
tracks unchecked fallback-setter failures before native descriptor adoption;
UL-003/007/015 continue to own the broader implementation/coordination gaps.
