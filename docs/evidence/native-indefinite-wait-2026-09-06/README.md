# Native wait without a deadline — 2026-09-06

Opcode 0x28008 adds compare-and-block without a per-wait deadline under the
existing thread grant. Matching wake or clear-TID completes the registration;
domain stop cancels it before reclaim. Timer progress alone cannot release it.
The registered word remains pinned. The existing timed wait and its timeout/wake
precedence remain unchanged. No new allocation, authority or child-slot reuse
is introduced. The [contract](../../NATIVE-C.md#native-wait-without-a-deadline-contract--2026-09-06)
specifies registers, errors, resource limits, ownership and selected verification.

This supplies a mechanism needed by musl's ordinary join and internal __wait,
which pass a null timeout. It does not implement futex translation, pthread
creation/join, signals or cancellation. The global native 3000-tick experiment
budget and QEMU watchdog remain; this is not unlimited system-uptime evidence.

## Verification

[Final results](final/results.json) retain exact commands, UTC boundaries and
hashes for [frozen inputs](final/sources.tar.gz). All selected checks pass:

- Six no-deadline cases per memory profile: positive, supervised replacement,
  parent exit with a blocked child, supervisor stop/replacement, deliberate
  comparison bypass at assertion 215 and wait-pin bypass at assertion 218.
- Fourteen actual-musl TLS, twelve storage, twelve stack, twelve timed-wait,
  fourteen older thread, 25 memory, nine image and seven M4 cases: 117 target
  cases total.
- 97 Python tests plus Zig kernel and offline standards/workflow checks. A new
  Zig test verifies no-deadline comparison, occupancy, nonmatching wake, timer
  noncompletion even at maximum tick value, matching wake and reset cancellation.
  Zig and pinned C formatting pass.

The native child registers without a deadline. Its parent then completes two
separate 100-tick waits on another word and checks that the child remains blocked
without error after each. Only the matching wake releases it. Clear-TID also
wakes the parent's no-deadline join. Both use the existing per-context CPU/TLS/FP
save state. The inherited idle witness checks real timer progress and FP state.
Malformed, foreign/stale and mismatched calls reject without registration.
Parent exit and supervised stop discard blocked continuations before replacement.
The native negative controls require exact terminal reasons, not generic timeouts.

## Attempts and limits

The first unsupervised positive passed, but its supervised case ended with result
302: the conformance supervisor exhausted 100,000 observation iterations. This
new suite deliberately holds workers for 200 timer ticks. Its long_wait build now
allows at most 1,000,000 observation iterations; other suites retain 100,000.
Global and external watchdogs are unchanged. The second six-case suite passed,
followed by full final qualification. Existing compact Rust style was retained
for this small fixture constant change; no broad formatting migration is claimed.

The failed attempt, passing retry and all final suites are retained in
`target-attempts.tar.gz`; `target-directories.json` inventories eighteen directories.
`before.tar.gz`, `contract.md` and raw logs preserve the earlier work. Reviewed
musl construction/join/wait sources and COPYRIGHT are archived in
`consumer-source-review.tar.gz` with hashes in `review-inputs.json`.
`formatter.json` records post-format identity. No sources changed during final
qualification; hashes were checked again before archival. SHA256SUMS covers this
packet. No sibling source, immutable standard or consumer pin changed.

Next work is actual libc creation/join adaptation, including signal and lifecycle
requirements. Main TLS extent registration, repeated thread creation and measured
filesystem-engine resource budgets remain open. There is no native filesystem
service or assembled shell/package release yet. Independent reader/consumer review,
optimized modes, stack high-water and extended stress remain missing. Top-level
timestamps do not cover every internal libc-builder command. These checks do not
establish companion acceptance or release readiness.
