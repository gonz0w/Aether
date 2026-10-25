# Bounded virtual clock and timed condition witness

Pair-only native 0x2800e observes the BSP delivered-timer counter under the current
thread grant. RDI exact grant; RSI/RDX/R10/R8/R9 zero. Return RAX=counter*10,000,000
nanoseconds; -13 authority, -38 pair mode disabled, -22 reserved input. No pointer,
allocation, mutation or yield beyond ordinary dispatch. Observation includes idle
and sibling time, is boot-local and does not reset on worker replacement. Native
watchdog bounds counter below 3000. It is an experimental virtual monotonic clock,
not calibrated elapsed physical time, UTC/realtime, suspend accounting or POSIX
clock conformance. Existing 0x25000 supervisor contract is unchanged.

New fixture alone adapts CLOCK_MONOTONIC to this clock; realtime rejects. Actual
musl condition attributes select monotonic. Native relative waits round positive
nanoseconds up to 10-ms quanta (1..100 ticks); existing compare-before-park and
timeout-before-wake rules remain. Fixture restricts relative waits to <=1 second;
this is not a general futex/time facade. No absolute deadline syscall is added.

Two child conditions use separate mutexes: one times out after 30 virtual ms and
must observe deadline elapsed, the other is signaled before a 500-ms deadline.
Both return owning their mutex; parent holds signaled mutex across wake to prove
reacquisition blocks. Exercise expired deadline, malformed nanoseconds, unsupported
clock, denied grant/reserved query, cleanup and supervised replacement. Frozen
adapter clock must fail exact elapsed-time status 271, not hang. Pair-disabled
clock operation must reject -38 before child creation.

Run full lifecycle suites in both profiles, raw pair/memory/M4 regressions plus
host/format/workflow. Preserve every attempt and freeze sources. No sibling/pin,
quota, task-placement or production userland changes. Time conversion lives in
user-space; only granted counter observation enters the kernel.
