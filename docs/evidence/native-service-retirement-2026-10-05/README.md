# Native musl TSD and service retirement

Status: private producer qualification passes, 2026-10-05.
[Before-code scope](contract.md) and [reference](../../NATIVE-SERVICE-RETIREMENT.md)
retain existing authority, owner-local quotas, published ABI/SDK and release pins.
No kernel, maintained user source or sibling changes. Production musl remains
userland-owned; the native engine has not run.

Six final native cases run fresh in attempt2: joinable TSD, detached TSD,
reverse-order detached completion, parked detached stop/replacement, actual
removed upstream destructor traversal and premature unmap. Both controls reject
exactly: terminal351 for missing destructors,352 for unmapping a still-running
requester; supervisor401/reclaimed0 and the named rejection panic. No timeout or
unrelated failure is accepted. Stop uses the compiled supervisor's (144,3) checks,
exact stale authority, replacement and three confirmed reclaims.

Actual pinned musl1.2.6 key/create/set/get/delete and destructor traversal execute
with82 simultaneous service pthreads and two small-peer pthreads. TSD is1024 bytes
per thread. Each worker's first destructor reassigns its value and runs exactly
twice; another runs the full four PTHREAD_DESTRUCTOR_ITERATIONS. Deleting and
recreating a key clears old values; its old destructor never runs. Parent TSD stays
independent. Real joinable exit/join behavior remains covered.

Detached workers complete upstream destructors/list removal, publish saved native
ID/mapping metadata and wait for permission to exit. The primary selects any pending
request, checks that unmap still rejects EACCES, permits exit, observes that exact
ID stopped, then unmaps and retires. It never reads an unmapped TCB. Requests must
be processed individually because musl holds its list lock until native clear-TID.
The reverse-order gate forces every82/two worker to finish in descending order.
Pending is not stopped and no user-local request authorizes backing reuse.

Each complete service stack/TLS/guard mapping still costs66 eager-backed pages;
small-peer mappings cost34. Synthetic240 KiB/4 KiB touches, counted82/two park/wake,
512 KiB/4 KiB malloc, failed64 MiB realloc byte/grant preservation and two retained
allocator pages pass. The test image now admits29 pages/116 KiB. These are fixture
reservations, not engine stack high-water, ARC demand or a measured engine peak.

Both attempts are retained. Attempt1 passes all five original cases; source review
then found its ascending-slot reaper depended on the completion schedule. Attempt2
selects any pending request and adds the reverse-order case; all six pass. There
are no failed native attempts in this packet. Full137 Python/Zig/Rust/pin/workflow,
scoped formatter, simplicity snapshot and documentation checks pass. Older runtime
regressions bind identical maintained source bytes as historical coverage only.

Offline reproduction from a fresh owned root:

```sh
python3 docs/evidence/native-service-retirement-2026-10-05/sdk-setup.py
python3 docs/evidence/native-service-retirement-2026-10-05/qualify.py 1
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Setup reads verified sealed SDK/upstream inputs, not mutable sibling outputs.
`checks.py` verifies the original two-attempt receipts, source/tool/SDK identities,
actual control mutation and final exact observations. `archive.py` seals and reads
back every owned member before removing only verified duplicate output. Sources,
recipes, commands, bounds, raw logs, images and upstream notices remain preserved.

This primary-driven reaper does not establish progress while the creator blocks,
worker-origin concurrent creation, cancellation or pthread_detach transitions.
Provider identity/configuration, actual engine feature/runtime closure including
those required progress paths, calibrated monotonic/UTC and native startup/fini/
restart still precede grant-bound volume/Rust filesystem/packages. Independent
consumer/SDK/reader acceptance and assembled R1 remain open. Wider SESSION for
companion continued-shell work is separate and is not delivered here.
