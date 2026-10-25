# Worker-origin creation under a domain grant (before code)

Requirement: actual retained OpenZFS txg_sync_thread calls spa_sync; its final
spa_async_dispatch can call thread_create/zk_thread_create/pthread_create. Routing
creation through a parked primary would change the algorithm and risk deadlock.
Source-backed call path is not a claim that native engine execution has occurred.

Add native-thread-origin, requiring the bounded native-thread-reuse profile.
Only that profile permits child contexts to create, observe by exact ID and retire
other children through their existing domain thread grant. The authoritative
State remains the sole owner; no grant is added or widened beyond this domain.
Legacy parent-only behavior remains unchanged. Preserve512 lifetime/two-live-slot
limits, quota-before-publication, stack/TLS separation, stop/clear-TID/retirement,
mapping pinning, monotonic IDs and whole-domain failure. IDs alone never authorize.

Child signal mask inherits the actual creating execution context, never the primary
by assumption. Save creator state before publishing the candidate. Child caller
cannot retire itself or another running context; those requests reject-16 without
mutation. A stopped target may be retired by a different live context with the
same valid domain grant; the retired record never supplies authority. Legacy
slot-zero query stays parent-only; worker code uses exact-ID query.

Tests: real parent→A→B creation with both slots occupied; parent parked while A
creates/waits/retires B. A sets a mask distinct from primary; B must inherit A,
then changes its own mask without changing A/primary. Self/running retirement,
foreign/old grants, stale IDs, invalid mappings, stop/reap/unmap and unchanged
quotas/legacy parent denial must pass. Actual omitted-mask inheritance mutant
must fail254. Repeat nested lifetimes and supervised fresh admissions; retain old
memory/TLS/output/exact64-yield oracles. Run older pair/pthread lifecycles, entropy,
block/M4, host/pins/workflow/format/simplicity. Preserve failures/frozen sources and
read archive members before only verified owned duplicate cleanup.

Security/simplicity: reuse existing domain-owned records/grant and exact-ID
operations; no RPC scheduler, global task table, implicit delegation or kernel
policy service. A simpler primary-only bridge cannot satisfy the real caller path.
Extra branch/profile cost preserves established consumer rejection contracts.
Bare stack/FS-cookie children do not qualify production musl TCB/adoption. Full
engine backing/live-slot/identity/configuration/feature/lifecycle remain open.
