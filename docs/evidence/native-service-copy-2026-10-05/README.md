# Checked native input copies — 2026-10-05

Bounded correctness qualification; **repeated-service stress remains blocked**.
The [before-code contract](contract.md) scopes one kernel-local page-fragment input
copy helper for8-byte masks and64/96-byte thread descriptors. Writable first/last
mask-output bytes are validated before any output or mask effect. No new ABI,
SDK authority, quota, allocator or sibling/pin change.

Final attempt5 passes eleven fresh native cases: origin regression, dynamic reuse,
capacity stop/replacement, denied clone360, early unmap352, omitted overlap365,
omitted primary park356, cross-page alias/permissions/wrap and actual musl clone,
inaccessible descriptor370, suppressed mask fault371, and actual missing native
inheritance362. Both cross-page mask and descriptor traps enter with DF=1; existing
vector entry clears DF before trusted copies. The trampoline tests initial native
inheritance before musl restores its saved application mask. Failed operations
preserve outputs, admission/mapping budget and mask state.

The twelfth case completes its first service but times out within the unchanged
30-second budget after replacement admission. Its status is `blocked-deadline`,
the attempt/check record is `partial`, and no passing stress/engine claim follows.
Do not enlarge the deadline, infer an external blocker or declare native-engine
startup from this witness. Native operation/progress cost and production resource
sizing still require work. Four-round and281-lifetime engine coverage remain open.

Selected maintained regressions are190 fresh targets: embedded/external memory
(default/large), thread pairs, pthread lifecycle, stack/storage and signal masks.
Their actual QEMU commands and original suite roots are recorded. Full137 host
checks, pins/workflow, scoped formats, simplicity digest, AST, links, reviewed
design/source/tool/SDK hashes are required by [checks.py](checks.py). This packet
changes only native_c input/output validation plus workflow inventory relative to
the previous sealed dynamic packet; its original body and exact patch are retained.
No historical runtime-suite count is reused as fresh evidence.

Five attempts are preserved. Attempt1 has nine passes then unrelated strict ELF
rejection from optimized-away initialized TLS. Attempt2 has ten passes but musl
restoration hides initial inheritance loss. Attempt3 has eleven passes then stress
timeout. Attempt4 has nine passes then unused DF-helper compile failure. Attempt5
uses an actual DF mask call, eleven passes and explicitly blocked stress. Loader,
mask authority and guest budgets were never weakened to accept those failures.

Reproduce current targets in a fresh owned output root with `sdk-setup.py`,
`qualify.py 1`, `regressions.py` and `zig build test`. Attempt directories must be
new. `checks.py` validates this original five-attempt evidence tree, including
historical failures; it cannot validate a fresh one-attempt tree. Inspect the sealed
snapshots/receipts for that audit rather than regenerating historical failures.
Sources freeze during each qualified run;180/30/3-second build/
guest/forced-teardown budgets remain. `archive.py` collects only recipe-tracked
fresh suite directories, verifies before/after move inventories, then reads back
all archive members before deleting the owned duplicate tree. `archive-check.json`
and `manifest.json` seal exact contents including every failed attempt.

Private Debug QEMU evidence is not calibrated latency/WCET, public process-mask
consumer qualification, production musl SDK/reader sign-off,82 detached engine
workers, actual native heap/ARC peak or assembled bootable-shell/R1 acceptance.
