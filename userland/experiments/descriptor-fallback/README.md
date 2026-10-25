# Checked descriptor fallback experiment (UL-036)

Twenty Linux-emulated outcomes compare musl 1.2.6's original fcntl/pipe2 objects
with an experimental checked fallback. Under injected setter failures, the
original fallback reports success while requested flags are missing. The checked
variant returns the error, releases allocated descriptors and retries successfully.
This is evidence about adapting musl to an incomplete native transport, not a
claim of an exploitable flaw in ordinary Linux or a native implementation result.

## Reproduce and identify inputs

```sh
python3 experiments/descriptor-fallback/check.py
```

The runner verifies the existing full Linux SDK inventory, LLVM/make executable
pins and musl archive digest before extraction/compilation. It verifies
[checked.patch](checked.patch) against [patch.lock.json](patch.lock.json), checks
source before/after digests, and compiles only replacement fcntl.c and pipe2.c
objects. Both variants link those objects before the same unmodified static libc.
No installed/native libc archive is changed. The patch derives from musl source;
musl's upstream terms continue to apply. This repository's original harness code
uses BSD-2-Clause.

Target ELF inspection checks x86-64 ET_EXEC, no unresolved symbols or dynamic
loader, no writable-executable LOAD and a non-executable stack. Host configuration
and include/runtime fallback are excluded. Builds fetch nothing and use fresh
private outputs. Full host tool/shared-library hermeticity and independent source
authentication are not established by these executable/SDK pins.

Retained output: `build/descriptor-fallback-5jkwuxb0`.
[Durable evidence](../../docs/evidence/descriptor-fallback-2026-09-05/summary.json)
records commands, all injected-source identities, exact patch, both ELF hashes,
source/tool/SDK identities and twenty traces.

## Injection boundary

Identical test-only syscall macros are inserted after syscall.h in the two
replacement objects. They route one-, two- and three-argument raw calls through
`test_raw`; the rest of libc is unchanged. The hook can:

- Return raw EINVAL for F_DUPFD_CLOEXEC, including its support probe, forcing the
  F_DUPFD/F_SETFD fallback.
- Return raw ENOSYS for pipe2, forcing pipe plus flag setters.
- Deny exactly one selected F_SETFD/F_SETFL call with raw EACCES or ENOSYS.

All other hook calls use real Linux syscalls and preserve raw negative errno
conventions. The probe's flag and open-descriptor inspections bypass the modified
fcntl object. Counters require the expected atomic attempts, setter count and
single denial, so an unentered injection path cannot pass. Synthetic returns do
not appear as kernel failures in -strace; counters and source identify them.

The oracle scans descriptors 0–63, checks the original descriptor remains valid
and unchanged, and compares the live set after cleanup. For checked pipe failures,
the caller's sentinel output array must remain unchanged. Each case then disables
the setter denial, retains the selected fallback/atomic path and verifies a
successful retry with all flags present and no new retained descriptor.

## Results

Each row runs once against baseline and once against checked: twenty total.
Baseline exit 20 specifically means success was returned with missing requested
flags after the injected failure; the probe then cleaned up and verified retry.
Checked exit 0 means the expected error/rollback or successful operation passed
its assertions. Setup errors, unexpected statuses and timeout cannot pass.

| Scenario | Baseline | Checked |
| --- | --- | --- |
| F_DUPFD_CLOEXEC fallback, setters succeed | 0, CLOEXEC present | 0, CLOEXEC present |
| Dup fallback setter returns EACCES | 20, CLOEXEC missing | 0, -1/EACCES, duplicate closed |
| Dup fallback setter returns ENOSYS | 20, CLOEXEC missing | 0, -1/ENOSYS, duplicate closed |
| pipe2 fallback, all setters succeed | 0, both flags on both ends | 0, both flags on both ends |
| Pipe fallback first CLOEXEC setter denied | 20, requested flag missing | 0, -1/EACCES, both ends closed |
| Pipe fallback second CLOEXEC setter denied | 20, requested flag missing | 0, -1/EACCES, both ends closed |
| Pipe fallback first NONBLOCK setter denied | 20, requested flag missing | 0, -1/EACCES, both ends closed |
| Pipe fallback second NONBLOCK setter denied | 20, requested flag missing | 0, -1/EACCES, both ends closed |
| Real atomic duplicate succeeds; redundant setter denied | 0, CLOEXEC already present | 0, CLOEXEC already present |
| Real atomic pipe2 | 0, flags present | 0, flags present |

Every container uses the existing pinned image, no network, read-only root/input,
UID 65534, dropped capabilities, 512 MiB memory and a 32-PID ceiling. No host/VM
lifecycle change, package activation or sibling implementation occurs.

## Adaptation decision and limits

The patch checks fallback setters, saves the raw failure across cleanup, and
publishes a pipe pair only after setup succeeds. It leaves musl's already-atomic
fast paths unchanged. The atomic duplicate control demonstrates why a denied
redundant setter is different from a denied fallback setter: the former's flag
was already set by the atomic creation operation.

This patch is **experimental and not adopted into native libc**. It does not make
fallback creation plus flag-setting atomic against concurrent exec. Cleanup also
assumes raw close consumes the new descriptors; close failure/ambiguous EINTR is
not injected. Signals, threads, cancellation and FD reuse races are not tested.
Invalid flags/minimum FD, operation allocation failure and all transport errno
combinations are not exhaustively covered. The tests are explicitly bounded,
not a replacement for upstream or native conformance tests.

For a native handoff, prefer owner-provided atomic CLOEXEC/NONBLOCK creation where
required. If the transport lacks it, choose an explicitly reviewed refusal or
synchronization/adaptation policy rather than silently assuming this checked
fallback is race-safe. Signal-mask and close assumptions from
[UL-035](../../docs/research/MUSL-PROCESS-FD.md) remain open. UL-037 will consolidate
these findings and acceptance witnesses into a shared owner-review proposal in
Aether-standards; it will not invent an implemented process ABI here.
