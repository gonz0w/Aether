# Private worker-origin thread profile

Status: experimental producer extension,2026-10-04; not public SDK adoption.
`-Dnative-thread-origin=true` requires the
[lifetime reuse profile](NATIVE-THREAD-REUSE.md). The same domain thread grant
permits any live execution context to create a child and observe/retire an exact
child ID. Legacy parent-only creation/ID query/retirement remain unchanged without
this flag; legacy slot-zero observation remains parent-only in every profile.

The current creator's mask is inherited; primary and peer masks remain private.
Two live slots,512 monotonic lifetime admissions and existing memory/stack/TLS
bounds are unchanged. Bad/foreign/stale grants, failed mapping preflight, occupied
slots and exhaustion cannot publish execution or spend the admission ordinal.
Running/self retirement rejects-16. Clear-TID completion, confirmed stop and
retirement precede backing release; IDs alone never authorize any operation.
There is no implicit delegation, global table or primary-thread RPC dispatcher.

This is required by the retained OpenZFS worker path txg_sync_thread→spa_sync→
spa_async_dispatch→thread_create. Source reachability is separate from native
engine execution. A parent→A→B fixture checks parked-parent progress, worker masks,
self/running/stale/foreign rejection and cleanup. It uses bare4KiB stack/FS-cookie
pairs, not production musl TCB. Whole-engine capacity and SDK adoption remain open.
Before-code scope/recipes/receipts belong to the
[origin packet](evidence/native-thread-origin-2026-10-04/README.md).

With pinned offline tools run its `setup.py`, then `native.py`; builds180seconds,
VM30seconds and owned teardown3seconds. Force-kill fails. Required older pair/
pthread/kernel regressions, host/pins/workflow and independent review remain
separate qualification coverage. No released pins or sibling sources change.
