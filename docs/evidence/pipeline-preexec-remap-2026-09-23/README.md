# Pre-exec stdin/stdout remapping — 2026-09-23

The private pipeline helpers now support inheriting their final standard-descriptor
layout across exec. Before replacement, both source helpers duplicate their pipe
reader onto fd0. The relay also duplicates its pipe writer onto fd1, closing its
inherited capture through scoped pre-exec dispatch. The final reader keeps capture
fd1. fd2 remains its inherited diagnostic stream. Old pipe descriptor aliases are
marked CLOEXEC, and a reader alias at fd10 is added with F_DUPFD_CLOEXEC.

Denied exec must preserve every descriptor flag. The owner validates the complete
snapshot against the expected layout and commits it through the existing shared
CLOEXEC/holder transaction. The replacement validates the filtered table, requires
fd0/1/2 present without CLOEXEC, and requires every fd3..15 absent. It performs no
post-exec redirection: its normal libc read/write path uses inherited fd0/1 directly.
The existing scoped duplicate/close, stream-rights and denial probes remain active.

Descriptor numbers confer no authority. The bound channel/slot/generation and
existing object holdings authorize operations. Closing the relay's old capture
updates the same ledger subsequently checked by exec commit; no alternate ledger,
ambient grant or special successful close is introduced. All snapshot/report traffic
retains the existing exclusive channel ownership after exec intake.

## Controls and bounds

The positive requires exact ten-byte data through both pipes/capture, input EOF,
all diagnostics, eight parent wait replies,12 admissions and15 reclaims over three
generations. Existing first-writer/partial-exec overlap remains required.

Two source mutations exercise the same owner and replacement bytes: incorrectly
mark fd0 CLOEXEC, or create fd10 without CLOEXEC. Each must reject2733 at snapshot
validation before replacement admission and before reclaim. Generic failure or
watchdog timeout is not acceptance. Existing descriptor-filtering and lifetime
regressions remain in the full suite.

All98 previous ELF/raw images remain identical. Three new source variants and one
replacement variant are added; all three new owner images are identical17496-byte
programs within the unchanged24-KiB bound. Kernel, shared pipe core, SDK, dependencies,
siblings, released pins and public protocols remain unchanged.281 runtime inputs
are frozen. No new unsafe boundary, allocation, stack page, participant or channel.

The positive ELF's extracted text exactly matches the tested raw owner. Reviewed
start/replacement-poll/commit/descriptor-prepare/memory-leaf depth remains3968 bytes
of4088 usable, leaving120. Layout validation is shallower. This scoped linked-binary
review is not a general stack proof; renew it on code/compiler/caller growth.

## Reproduce and retain

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The preimplementation requirement, forbidden outcomes, security/resource review
and shared-path choice are in NATIVE-SHELL-STARTUP. finalize.py verifies frozen
snapshots and generated archive/live bytes before removing only the duplicate
suite directory. SHA256SUMS seals the packet; earlier evidence remains immutable.
Final qualification is recorded below after the complete run.

This qualifies the descriptor shape needed by the shell's pipeline helpers. It does
not execute actual dash main/eval or the unchanged pipeline script. Next connect
consumer helper path/argv, followed by dash-driven creation and wait orchestration;
reuse scoped startup facilities instead of successful compatibility stubs.
Independent consumer/full-suite acceptance and serial-shell assembly remain open.
Persistence/OpenZFS, packages and sys-init remain separate R1 requirements.

Native attempt1 passes all83 cases in237.747 recorded case seconds. Host checks pass105 Python tests plus Zig/Rust checks. Both incorrect-flag controls reject2733 with no slot3/4 replacement admissions and zero reclaims; the positive completes all streams/waits/reclaims. All98 prior images remain identical. One native attempt; no failed cases in this slice.
