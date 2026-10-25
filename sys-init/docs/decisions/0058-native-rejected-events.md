# 0058 — Native rejected-launch events and cleanup notification

Accepted 2026-09-06, BG-058/BG-057. Extend decision 0057's private route for the
already demonstrated received busy launch error (operation 0x23001, errno 16).
No shared ABI, dependency, allocation or unsafe primitive changes.

## Contract and review

RoutedAttempt::launch keeps its Result contract: success queues Launched; the
selected native EBUSY remains Err and additionally queues LaunchFailed carrying
the exact Error and logical generation. Attempt retains error and both endpoints,
with no worker. Only that exact supported error is routed, and only when retained
Attempt error agrees. Local duplicate/cancelled errors and unsupported returns
must not manufacture an event or delivery acknowledgment.

Rename terminal-delivered bookkeeping to outcome-delivered: accepted Terminal or
LaunchFailed transfer permits cleanup, but Launched does not. A pending event
still blocks cleanup. Full inbox preserves failure and Cleaned notifications.
Rejected cleanup closes both owned endpoints; there is no target to reclaim and
no terminal observation to invent. Cleaned is queued only after complete cleanup;
retirement eligibility waits for its inbox transfer. The original launch error
remains diagnostic state. Repeated launch after failure delivery returns local
busy without reissuing native launch or manufacturing a second failure event.

This is trusted in-process transfer, not journal application acknowledgment,
recovery, unknown-effect qualification or automatic retry. Existing admitted-route
behavior and its negative cases must remain valid. Shared Foundations O-04,
I-03–06/E-01–08 apply; retained evidence, pins and marker contracts remain unchanged.

## Fresh witness

Launch a blocker in slot zero. Acquire a second Attempt and route launch into the
occupied slot; require real 0x23001/16 and exact failure payload/generation. Full
inbox refuses transfer without loss. No worker exists; observation returns local
0/9 without altering pending. Cleanup before failure delivery returns local 0/16
without closing endpoints. Deliver failure; duplicate launch returns local 0/16
without a new event. Cleanup closes both endpoints and queues Cleaned while the
blocker remains owned. Full inbox retains Cleaned and eligibility stays false;
accept Cleaned, verify eligibility and retained error. Explicitly dispose blocker
and two ordinary workers to finish 100/reclaimed=3. None is a retry of the failure.

Controls: rewriting the failure errno to 13 must hit 997/reclaimed=0; bypassing
failure-delivery gating and performing early cleanup must hit 998/reclaimed=0.
Exact profile context is required, not generic panic, timeout or build failure.
Run all 38 preceding cases plus these three on pinned SI-04, Rust 1.98.0/2024,
BSP-only, 4 KiB clients; retain frozen inputs, binary comparisons and raw logs,
then all development checks. Source review covers error origin, partial effects,
success-before-clear and selected error scope.

BG-058 next gates a routed replacement on accepted Cleaned delivery and validates
fresh generation events. Other launch errors and malformed/unknown returns stay
unsupported by this route. BG-057 retains full journal/cut and operation identity;
BG-033 retains reconciliation/recovery. No full native driver or POSIX claim.

## Validation — 2026-09-06

All 41 native cases pass with 177 frozen inputs unchanged. Twenty-eight of 38
preceding clients are byte-identical; ten changed clients pass their previous
semantic oracles, individually recorded in witness/comparison.json. New clients:
rejected-events 2,512 bytes, event-wrong-error 544, event-failure-early 2,464,
all within 4 KiB. No failed native attempts occurred.

All eight development gates pass in out/checks/run-12xq_vzo: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
447 outcomes across 25 bundles and 7,785 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; no native
code changed. Retained evidence: docs/evidence/native-rejected-events-2026-09-06/.
