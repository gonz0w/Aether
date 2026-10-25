# Worker-driven native service cleanup

Status: private producer qualification passes,2026-10-05.
[Before-code scope](contract.md) and [reference](../../NATIVE-SERVICE-REAPER.md)
retain existing authority and owner-local storage. No kernel, maintained user
source, public ABI/SDK, sibling or released standard/pin changes. Production musl
remains userland-owned and the full native storage engine has not run.

Eight final native cases run fresh in attempt4: joinable TSD and primary-driven
detached regressions, worker-driven cleanup, descending worker-driven completion,
parked stop/replacement, actual wrong-grant observation355, premature unmap352 and
removed primary join-park356. All three controls require their exact terminal,
supervisor401/reclaimed0 and named rejection panic; unrelated failure or timeout
cannot pass. The final controls retain the valid origin-enabled build profile.

One ordinary joinable musl worker owns detached-peer cleanup while the primary
blocks in actual source-rebuilt pthread_join. It occupies one of the existing82
service/two small-peer slots, leaving81/one detached peers. Primary admission and
publication finish before release; cleanup mutations belong to that worker, and
main reads them only after real join. The primary's actual native compare-and-park
must return zero and complete after every detached peer is retired. The negative
nonblocking-yield adapter leaves completed-park count zero and rejects356.

The cleanup worker selects any pending request, checks that native observation
still says running and unmap rejects EACCES, permits native exit, observes that
exact ID stopped, then unmaps/retires through its held domain grants. It never
reads the unmapped TCB. Descending completion forces81/one peers to retire in
reverse order. Saved metadata survives upstream list removal; requests are not
stop evidence. Worker yields do not alter the primary yield-count oracle.

On a rejected witness the cleanup worker permits remaining published peers to
exit, synchronizes musl's list lock and leaves their mappings/records allocated.
This lets actual join report the exact rejection without deadlocking on an exiting
peer's retained list lock. It does not authorize cleanup after a denied operation.
Normal cleanup restores exact records/list/quota; the parent finally joins,
unmaps and retires the cleanup worker. Parked stop/replacement preserves stale
handles, confirmed (144,3) supervisor observations and three reclaims.

All82/two workers retain actual1024-byte TSD, independent TLS/errno, two/four
callback invocations, deleted/recreated key isolation and parent state. Complete
stack/TLS/guard mappings still cost66/34 eager-backed pages. Synthetic240 KiB/
4 KiB touches, counted82/two park/wake, bounded malloc, failed64 MiB realloc byte/
grant preservation and two retained allocator pages pass. The fixture image
admits30 pages/120 KiB; these are not engine ARC/heap/stack high-water measurements.
A dedicated cleanup worker reduces useful workload slots and must be included in
the eventual engine budget; this trial does not claim82 detached engine workers.

All attempts are preserved. Attempt1's five positives pass; its proposed disabled-
origin control fails the existing build guard before a guest runs. That is a
configuration failure, not a passed semantic control. Attempt2 uses an actual
wrong held grant instead, adds the omitted-park control and passes all eight.
The inherited runner hashes the rustup dispatcher. Attempt3 resolves/hashes the
actual pinned1.98.0 rustc but direct invocation fails linking before any guest:
macOS rust-lld needs rustup's library search environment. Attempt4 restores the
same rustc+1.98.0 entry and additionally freezes the resolved actual compiler,
rust-lld and LLVM library, then passes all eight fresh. Runtime/C bytes do not
change between attempts2/4. Both infrastructure/configuration failures remain;
no guard is weakened and no installed toolchain or host environment is changed.
The first receipt-check attempt mistakenly selected historical workers target4
instead of target2; it fails before host checks. Its recipe/receipt and triage
remain in checks-attempt-1. The corrected checker retains the historical path and
verifies it independently. Full137 Python/Zig/Rust/pin/workflow, scoped formatting, simplicity snapshot, links and frozen review/source checks pass.
Historical runtime suites bind identical executable sources and are not fresh runs.

Offline reproduction from a fresh owned root:

```sh
python3 docs/evidence/native-service-reaper-2026-10-05/sdk-setup.py
python3 docs/evidence/native-service-reaper-2026-10-05/qualify.py 1
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Setup verifies sealed musl/SDK/upstream inputs without mutable sibling builds.
`checks.py` validates the original receipts and failure, exact controls and source/
tool/SDK bindings. `archive.py` reads back every owned artifact before removing
only its verified duplicate tree. Commands, bounds, logs, artifacts and all four
attempts' source/recipe snapshots remain with upstream notices.

Next real musl worker-origin creation and required concurrent admission/progress,
then actual engine providers/identity/configuration, calibrated monotonic/UTC,
feature/runtime closure and measured startup/fini/restart before grant-bound
volume/Rust filesystem/packages. Production reaper placement and repeated dynamic
lifetime schedules, consumer/SDK/reader acceptance and assembled R1 remain open.
No wider companion SESSION contract or completed engine port is delivered here.
