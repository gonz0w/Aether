# Larger-owner bounded scans (before code)

Requirement: remove the observed quadratic metadata scans from the private
8192-capacity service's map/range/protect/unmap path before expanding live workers.
The three-full-budget-generation timeout is retained in the preceding memory
packet. Keep all caller authority, error ordering, actual owner endpoints, whole
preflight, thread/TLS/wait pins, table capacity, stop/flush/zero/reuse and generation
rules. No new ABI, flags, quotas, general VM interface or sibling/pin change.

Use a temporary 8192-bit occupancy/coverage set (1024 bytes) only in the sliced
8192-capacity arena. Scan metadata once, then arena/range bits once; default typed
128/2048 implementations retain their existing algorithm. Only checked aligned
in-arena addresses can index the set. Map occupancy includes all mapped records;
range coverage requires anonymous records. No heap, persistent mutable index,
invalid caller pointer or metadata cache is added. Constant-size plans remain.
Native larger-profile commits visit matching anonymous records in backing order
once, while IF-clear keeps owner metadata stable. Existing unique-address ownership
is a constructor invariant. Advancing cursors permits flags/publication/clearing
of already visited records. Unmap still clears PTEs, restores kernel-only write
permission, flushes CR3, then zeros/returns quota before user dispatch. Do not claim
separate flush-before-kernel-write restoration. Legacy commits stay unchanged.

Tests: pure fragmented/permuted/hole/immutable/pin/actual-small-owner/atomic-failure
cases plus whole8192 range and constant workspace/cursor sizes. Compare sliced
small views against legacy planner on deterministic layouts/errors. An actual
removed coverage bound must fail a hole witness. Full host/pins/workflow; fresh
larger-owner ten-case matrix and two storage cases; restore three full-budget
big-image generations under the unchanged 30-second watchdog, with tool/source/
SDK receipts. Select maintained default/large memory and seven M4 regressions for
shared source integration. Previous full pair/origin/reuse/entropy evidence is
historical only where unchanged bodies/profile paths are verified. Preserve failed
attempts; no independent reader or production latency/scheduling assurance claim.

Simplicity/security: a persistent index introduces cache invalidation across every
loader/reset path. A general allocator adds unrelated mechanisms. A bounded local
bitmap and record cursor remove repeated scans without new ownership/state.
1024 temporary bytes fit the existing required 64 KiB exception stack; fresh
native targets test that compiled boundary, not a complete stack high-water proof.
Work is O(owner records + requested arena pages), with table selection bounded by
32; zeroing and verification remain proportional to requested payload. No wall-clock
WCET claim, preemption change, thread-capacity expansion or untrusted broad access.
