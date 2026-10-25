 — 2026-09-06

Before implementation: musl's ordinary join and internal __wait issue futex waits
with a null timeout. Provide that missing mechanism without retrying arbitrary
native deadlines or adding signal no-ops. Aether owns wait registration, wake and
teardown; userland retains libc locking/join/cancellation policy. This is an opt-in
AENATC01/AENSUP01 thread-grant extension, not pthread or consumer acceptance.

Opcode 0x28008: RDI=thread grant, RSI=aligned writable four-byte word, RDX=expected
u32; R10/R8/R9 must be zero. Authority, pointer and comparison rules match 0x28003.
Mismatch returns -11 without registration, malformed fields -22, invalid backing
-14 and foreign/stale authority -13. Equal words register atomically under the
existing BSP IF=0 gate and block with no deadline. Wake 0x28004 or clear-TID wakes
a matching waiter with RAX=0 and RDX=elapsed native ticks. Domain stop cancels the
registration without resuming the context before reclaim. The registered word
stays pinned throughout. IDs/addresses confer no authority across domains.

The existing one-registration-per-context bound and idle context remain. An
all-blocked domain has no wait deadline; external supervisor stop still works.
The existing native experiment 3000-tick global budget and external QEMU watchdog
remain in force; this is not an unbounded system-uptime qualification. There is no implicit timeout, signal interruption, cancellation API, new
allocation, clock guarantee or child-slot reuse. Existing 1–100 tick wait and wake
contracts remain unchanged. Represent the absent deadline explicitly in wait state;
timer completion must not make it runnable, including at the maximum tick value.

Select host no-deadline/mismatch/wake/reset tests and a native optional --indefinite
suite: hold a child blocked across two 100-tick parent timeouts, then matching wake
and clear-TID join; reject malformed and stale calls; retain pins, parent exit and
supervisor stop/replacement. Reuse exact compare/pin negative controls and idle/FP
checks. Run both memory profiles, older thread suites, memory/image/M4 and host/
format checks on frozen inputs. Preserve every attempt. No sibling, dependency,
standard or pin changes; document the ABI, command and result separately. Existing
ASCII markers and progress format remain. No new unsafe pointer lifetime is added.
