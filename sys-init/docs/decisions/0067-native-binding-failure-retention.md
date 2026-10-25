# 0067 — Retain acquisition through later binding failure

Accepted experiment plan, 2026-09-06, BG-058/BG-057 NB-04.

Extend the private binding fixture with an explicit post-acquisition binding
completion boundary. The normal path completes it successfully. The new probe
injects a local binding mismatch after the actual channel returns and both
endpoints have been retained. Record the failed binding index, close admission,
retain the original token/slot, consumed entry, pending reservation and both
endpoints. No launch occurs. This local failure is distinct from native errno;
the successful channel call must not be represented as rejected or unknown.

Repeated acquisition, launch and reservation requests must deny without additional
acquisition or loss of retained state. The ownership-loss control forgets the
writer on binding failure; require exact 1017/reclaimed=0 and designated native
profile rejection. Build failure, timeout and generic panic do not qualify.

The positive fixture keeps the failed pair owned while three independent ordinary
workers use the other channel slot and are reclaimed. Explicit fixture disposal
then closes both retained endpoints. Adapter accounting is clean but the driver
stays closed, the token consumed and the failed reservation retained. This proves
neither journal cleanup/retirement nor a recovery path. Finish at 100/reclaimed=3.

Run all 61 prior cases plus the positive and ownership-loss control, with pinned
SI-04, Rust 1.98.0/2024, BSP-only and unchanged 4 KiB clients. Retain all attempts,
frozen inputs, raw clients and exact serial oracles, then all repository checks.
Review local/native error origin, ownership before validation, failure permanence
and fixture-only teardown. No new dependency, unsafe operation or shared ABI.

NB-05 selected creation/launch rejection remains next; predicted result/target
validation, exhaustion, lost replies and ND-02–05 remain open. This injected
completion failure does not implement producer channel-generation validation or
prove interruption at every instruction. Full ND-01 remains incomplete.

## Implementation review

The existing successful acquisition path calls `acquire_checked` with completion
accepted. The new positive injects false through a runtime test value after a real
channel call; `binding_failed` is a separate local cause, and `error` remains None.
`closed` and the non-resettable consumed entry gate all later driver calls. Both
endpoints are saved before the check; the writer-loss control is intentionally
incorrect only in its designated build. There is no new unsafe block, allocation,
dependency or output format. Existing private-index invariants remain unchanged.

An initial compile-only version called reader close with Writer; Rust rejected
all three selected compile probes. The fix uses the existing typed `close_writer`
method. Sources/logs are retained in build-attempt-1; no target ran that version.
Final local probes fit 4 KiB. This review adds no independent sign-off.

## Validation — 2026-09-06

All 63 native cases pass with all 178 frozen inputs unchanged. Forty-four of 61
preceding raw clients match; seventeen changed clients pass their previous oracles
and are recorded in witness/comparison.json. New clients are 3,424 bytes (failure)
and 3,440 bytes (writer-loss control), within the unchanged 4 KiB bound. The
control reaches exact 1017/reclaimed=0. No native execution failed.

All eight gates pass in `out/checks/run-7valvgao`: 228 model tests, 23 negative
controls, 48 host tests and 37 harness tests. The catalog verifies 826 historical
outcomes across 32 bundles and 11,842 listed files. Both targeted native-input
harness tests pass. All seven current consumer source entries match the executed
snapshot. New document links and `git diff --check` pass.

Evidence is retained in `docs/evidence/native-binding-failure-2026-09-06/`, including
the initial compile-only failure, final local builds and consuming artifacts. Only
validation notes and evidence copies follow checks; runtime sources, tests, catalog
and inventory remain unchanged. Next: NB-05 selected creation/launch rejection
under an explicit fixture ownership plan. Broader binding and ND-02–05 stay open.
