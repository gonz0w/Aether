# Native service musl storage qualification

Before-code scope, 2026-10-05. Requirement: replace the bare-cookie capacity
witness with real source-rebuilt musl 1.2.6 pthread creation, TLS/errno, guard,
join/unmap and allocator behavior under the existing private 82-worker owner.
Aether owns this conformance fixture; Aether-userland still owns the production
musl port. No kernel, public SDK, ABI, quota, sibling or released pin changes.

Reviewed the accepted VM-01/VM-02, UP-01 through UP-08 and SI-01 designs in
VIRTUAL-MEMORY, MUSL-VM-BACKEND, FILE-DESCRIPTORS, SERVICE-IO, READINESS-WAITS,
UNIX-SOCKETS, SIGNALS, IDENTITY-PERMISSIONS, CLOCKS-TIMERS, TTY-SEATS and
DEVICE-SERVICES. ARCHITECTURE/PROJECT/ROADMAP preserve bounded storage priority.
HO-01 remains provisional after R1; it is not an implementation dependency.
This fixture uses the existing eager anonymous v1 grant, not VM objects/demand
paging. No new FD owner, device namespace, wait-many or calibrated clock is added.

Allowed result: one 32 MiB owner simultaneously holds 82 real joinable pthreads
with 256 KiB requested stacks and 4 KiB PROT_NONE guards. The small peer retains
two default-size threads. Checked native identity, actual musl TLS list and
parent state remain isolated; joins use saved IDs after upstream unmapping.
Record exact thread mapping/TLS geometry and observed grant accounting, plus
allocation/free and failed realloc preservation with all workers live. Repeat
lifetimes through the existing separately compiled supervisor, including stop
while parked. Keep requested stack size distinct from used stack and engine peak.

Forbidden: ambient authority, widened grants, fake successful unsupported calls,
freeing live stacks/TLS, parent/thread TLS aliasing, stale-ID reuse, false success
on exhaustion, abandoning upstream references or guessing completion. Application
pointers and auxv values convey no authority outside enforcing native checks.

Native adapters borrow only the currently selected musl create/join/wait/mapping
seam. Startup records are static owner-local fixture state; one primary admits and
joins. No callback may outlive its slot. Native admission pins the actual musl
mapping; unmap follows confirmed exit. IF-clear kernel checks remain unchanged.
All pthreads share one process/domain; cross-core pthreads, cancellation, detached
cleanup and general signal/thread semantics remain unsupported. Heap tests must
preserve the old allocation on failed realloc and report retained allocator pages
separately from stack reclamation.

Tests: positive capacity/TLS/guard metadata/park/wake/join/allocation, stop and
replacement, actual corrupted self-pointer rejection, actual guard #PF; full host
suite, formatter/pin/workflow checks. Matching old native behavior is unchanged;
reuse previous frozen runtime evidence only after exact source hash comparison.
No broad runtime regressions are substituted for missing consumer/engine evidence.
Freeze inputs per attempt, retain failures and commands/artifacts, seal/read all
archive members before cleaning only this run's duplicate output.

Simplicity: the simpler bare-cookie test already qualifies native record capacity
but cannot qualify musl TCB/list/allocator behavior. Reuse actual pinned upstream
functions and the existing narrow adapter instead of a new threading runtime.
No paths are removed now; this adds one bounded experiment needed for startup.
Its measurements may identify the next actual engine prerequisite. Broader VM,
provider/UTC and production port work stay explicitly open.
