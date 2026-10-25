# 0059 — Cleanup-delivery-gated native replacement

Accepted 2026-09-06, BG-058/BG-057. Extend the private pending route with one
explicit replacement, composing decisions 0052, 0057 and 0058.

## Contract

RoutedAttempt::retry refuses ineligible routes with local 0/16 before calling
Attempt::retry. Under the trusted route's existing transitions, eligibility means
all resources cleaned and Cleaned transferred to the inbox; pending failure,
terminal or Cleaned cannot authorize acquisition. The existing Attempt guard still
requires generation one, retained native busy error, no cancelled intent and an
unused retry. Acquisition success alone consumes the one-retry allowance.

Return a new route owning the new Attempt, with no pending event or inherited
outcome-delivery acknowledgment. Keep the original error/retried record. The
replacement's logical generation is two; its Launched, Terminal and Cleaned events
carry two. Old inbox contents provide backpressure, not authorization for the new
route. Duplicate retry of the original and retry of generation two are local
0/28 once eligible. This is explicit bounded retry, not timers/backoff, automatic
restart, journal acknowledgment or recovery. Private caller bypass remains outside
the trusted fixture contract; no public API or authority boundary is introduced.

## Fresh witness

Launch a blocker, then route a native busy failure. Retry before failure delivery
is denied. Deliver failure and clean endpoints; retry while Cleaned is pending
must remain denied before channel creation and must not consume retried. A full
inbox preserves Cleaned. Transfer Cleaned, dispose the blocker, then explicitly
retry: require fresh endpoints, generation two, no inherited error/event/delivery
state, and one consumed original allowance. Duplicate original retry is denied.

Launch replacement into the reclaimed slot and require fresh worker identity and
exact generation-two Launched event. The still-full generation-one inbox must
not consume it. Observe terminal 18, deliver generation-two Terminal, clean and
deliver generation-two Cleaned. Generation-two retry remains subject to the existing fixed Attempt budget; this
new event case does not independently invoke it.
One separate ordinary worker completes actual result=100/reclaimed=3.

Controls: bypassing the route delivery gate permits premature channel acquisition
and must hit exact 1001/reclaimed=0. Rewriting replacement Launched generation to
one must hit 1002/reclaimed=1. Neither generic panic nor timeout/build failure
satisfies an oracle. Run 41 prior cases plus four new cases on pinned SI-04,
Rust 1.98.0/2024, BSP-only and 4 KiB clients. Retain raw logs, exact inputs,
artifacts and comparisons, then all development checks.

Review ownership on failed acquisition, original versus replacement state,
success-before-budget-consumption and pending-event retention. Foundations
O-04/I-03–06/E-01–08 apply; shared pins, ABI and markers remain unchanged.
No dependency, allocation or unsafe primitive is added.

BG-058 next integrates cancellation intent with the routed replacement gate;
BG-057 retains complete journal/cut and issued-operation identity; BG-033 retains
unknown-effect reconciliation and recovery. Broader launch errors, timed restart
and full native driver/POSIX conformance remain open.

## Fixture size review

The initial combined case exceeded the unchanged 4 KiB linker bound before native
execution. Two inline-control size probes also failed; those temporary annotation
changes were reverted. Split the witness into routed-replacement (gate, fresh
state and duplicate-original denial, followed by direct fixture cleanup) and
replacement-events (actual replacement plus generation-two event delivery).
The event case omits duplicate retry probes covered by the gate/Attempt cases.
The first split still exceeded the bound for event cases; final size probes pass:
3,520/3,952/1,280/3,968 bytes. All probes, commands and source copies are retained
under attempts/. These compile probes are not target acceptance. A fresh complete
45-case run must qualify final sources. No bound, toolchain or producer change.

The gate fixture's final direct Attempt cleanup is test teardown and leaves its
route's Launched notification undelivered. It is not evidence of complete routed
retirement; replacement-events separately exercises full routed terminal/cleanup
delivery. The two scopes share the final implementation and are reported separately.

## Validation — 2026-09-06

Final 45-case native run passes with all 177 frozen inputs unchanged. Thirty-one
of 41 preceding clients match; ten changed clients pass their previous oracles,
identified individually in witness/comparison.json. Final runner raw sizes are
3,576 bytes (routed-replacement), 4,008 (replacement-events), 1,280 (skip-delivery)
and 4,024 (old-generation), all within the unchanged 4 KiB bound. These are the
accepted artifacts, distinct from earlier standalone size-probe outputs.
Initial link-bound failure and all failed/passing size probes remain retained.

All eight development gates pass in out/checks/run-ab0s5vrb: 228 model tests,
23 negative controls, 48 host tests and 37 harness tests. Native catalog audits
492 outcomes across 26 bundles and 8,300 files. Development sources unchanged;
current native consumer bytes match the executed snapshot. git diff --check passes.
Only decision/planning validation notes were appended after checks; native source
unchanged. Retained evidence: docs/evidence/native-routed-replacement-2026-09-06/.
