# 0060 — Cancellation intent through the native route

Accepted 2026-09-06, BG-058/BG-057. Add private RoutedAttempt::cancel_service,
delegating to Attempt's existing intent-before-stop operation. Preserve its exact
Result, pending event, resource inventory and outcome-delivery state. Cancellation
is desired intent, not a fabricated terminal, failure or cleanup event.

## Contract and scope

Receiving or delivering Cleaned does not clear cancellation. Eligibility describes
resource/event retirement only, not permission to retry: after delivery a cancelled
route still returns local 0/13 from Attempt::retry. Before delivery the existing
route gate returns 0/16. Both deny acquisition and leave the retry allowance unused.
Cancellation must not discard queued failure or cleanup evidence. Repeated calls
are harmless in the rejected/no-worker case. No new Cancelled event or service
control transport is introduced. Launch remains denied after cancellation.

Test the selected received native busy rejection at three independent activation
points: pending LaunchFailed; pending Cleaned; and after Cleaned transfer. Each
activation owns a fresh blocker and a generation-one rejected route. For every
point, cancel twice, preserve exact pending/outcome state, finish required failure
and cleanup delivery, then deny retry with 0/13 and preserve error/retried=false.
Pending Cleaned additionally denies retry with 0/16 and survives a full inbox.
Explicitly dispose the blocker; three activations consume each channel's three
generations and yield actual 100/reclaimed=3. No rejected route acquires a retry.

Controls: discarding pending during cancellation must hit 1005/reclaimed=0;
clearing cancelled intent on Cleaned delivery must hit 1004/reclaimed=0.
Exact profile context is required; timeout/build failure cannot pass. Run all
45 prior cases plus these three under pinned SI-04/Rust 1.98.0/2024/BSP-only and
4 KiB clients. Retain inputs/artifacts/logs, prior comparisons and full checks.

Review event ownership, intent versus eligibility, delegated error preservation,
repeated cancellation and acquisition/budget side effects. Foundations O-04,
I-03–06/E-01–08 apply. Shared ABI/pins/markers, dependencies and unsafe primitives
stay unchanged. In-process route cancellation is not a real control channel,
unknown-result reconciliation, timed restart or complete native driver.

BG-058 next consumes routed cancellation for an admitted live worker and its
observed terminal event; routed stop-error handling remains to be qualified.
BG-057 full journal/cut integration and BG-033 recovery remain open.

## Validation — 2026-09-06

All 48 native cases pass with 177 frozen inputs unchanged. Thirty-two of 45 prior
clients match; thirteen changed clients pass their previous semantic oracles,
individually recorded in witness/comparison.json. New raw clients are 992 bytes
(routed-cancellation), 544 (cancel-drop) and 608 (cancel-reset), within 4 KiB.
No failed native attempts occurred.

All eight development gates pass in out/checks/run-dnzy4kn8: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
540 outcomes across 27 bundles and 8,836 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; native source
unchanged. Retained evidence: docs/evidence/native-routed-cancellation-2026-09-06/.
