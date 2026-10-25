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
