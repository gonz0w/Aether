# Native suspend-frame rejection and recovery

The [prospective review](../../NATIVE-SHELL-STARTUP.md#suspend-frame-failure-recovery-review--2026-09-14)
uses the existing pending-before-entry copied-child schedule. The owner observes
child72 before releasing the parent's first WNOHANG reply. No new post is generated
between failed signal entry and recovery.

The C parent fills an unused 1024-byte bottom-stack region with a position-dependent
canary. A naked wrapper saves its real stack pointer in R11, supplies base+128,
+848 and +856 as the interrupted RSP for the existing size8 suspend operation,
restores the real RSP and returns. The final position also tests alignment beyond
the minimum-size check. Each attempt must return EINVAL with zero handlers, the
original SIGCHLD/TRAP mask, and every canary byte unchanged.

Real musl sigsuspend on the normal stack must then return EINTR after exactly one
handler under the expected temporary/action/self mask, restoring the original
mask. Existing wait errors, retained child status, one-time collection and stream
cleanup complete in two generations with six reclaims. Recovery therefore proves
that the original pending occurrence survived all three rejections.

The valid-stack control omits the stack switch. Successful entry must cause the
rejection oracle to fail raw parent238/owner1950, with child72 already recorded
and zero reclaims. No timeout or fabricated errno constitutes that rejection.
All fifteen focused cases pass on the first attempt, including previous ordering,
stop/reuse and unchanged dash wait cases. Host tests and scoped C formatting pass.

All 316 connections cases and fifteen focused cases pass on the frozen 265-source
inventory. The matching command-runner attempt hit its outer 1800-second deadline
after starting 429 of 431 cases. It produced no final results.json and is recorded
as incomplete, not a passing suite. Its log, driver and all generated artifacts
are retained. No case failure was reported before the timeout. Concurrent host
work was present; this observation does not prove the timeout's cause.

No kernel code, ABI, quota, dependency, released pin or sibling repository changed.
Prior scheduler evidence is explicitly prior, not represented as freshly run.
Matching complete command-runner coverage remains the next qualification action.

This is bounded failed-frame recovery. Immutable handler mappings are not revoked
or made writable. Default termination during suspension, nested delivery, eventual
unblocking after a blocked post and independent consumer/SDK acceptance remain
open. Producer evidence does not certify full POSIX signals or an
interactive R1 image. The next handoff must retain these limits.

Compatibility: 918/918 compared pre-existing client,
owner and kernel artifacts are byte-identical; compatibility.json lists every
changed artifact. This does not imply independent consumer acceptance. All three
newly generated unpacked target directories were removed only after every file
matched its preserved archive. All target cases remain preserved in those archives. Exact paths and
sizes are recorded in duplicate-cleanup.json. No other build directory was removed.
SHA256SUMS seals all packet members.
