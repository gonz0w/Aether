# 0073 — Retain launch returns and writer transfer before application

Implemented bounded launch receipt slice, 2026-09-06, BG-058/BG-057 IR-05–06.

Extend decision 0071's bounded receipt position to launch. Keep a separate
per-attempt launch phase; reserve the shared pending index and mark Started before
Adapter invocation. The original writer remains inventoried but unavailable during
Started. Capture the actual returned worker and record writer transfer before
Returned. Only matching local application increments the native generation and
permits launched-event qualification. Closed admission retains receipt/resources
and consumed identity; no retry, journal acknowledgment or Cleaned is implied.

Two native positive probes, launch-receipt and launch-receipt-close, must finish
100/reclaimed=3. Check original reader/worker, transferred writer, single invocation,
blocked further admission and no generation advance before application. Successful
application happens once; duplicate application and invocation deny. Local closure
holds the original pending receipt and denies application. Fixture disposal uses
only positively retained reader/worker; two ordinary workers complete accounting.
Semantic controls launch-keep-writer and launch-early-generation must reach exact
1030/reclaimed=0 and 1031/reclaimed=0 respectively. General ownership/phase oracles
use 1029. All 80 previous native cases retain their original expected outcomes.

This is a trusted local pause after an actual synchronous return. It is not a lost
kernel reply, durable receipt or public cancellation API. Local index application
is private to the retained driver/context, not an authenticated message protocol.
Existing full token/target ownership and selected busy-error contracts remain.
IR-07 synthetic absence and remaining NB/ND/BG-033 recovery requirements stay open.

Review applies Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 under unchanged
offline pins. Distribution identity/recovery limits remain authoritative. No new
unsafe primitive, dependency, shared API, output protocol or exception. Resource
bounds remain two attempts, one receipt position, no allocation and 4096-byte
native clients. Full pinned target evidence and all development checks are required.

## Result and review

Decision 0073 passes 84 native cases. Successful launch returns retain the actual
worker/reader and mark the writer transferred before local application. Pending
receipts deny additional invocation/admission and launched-event qualification.
Matching application advances generation once; injected closure preserves receipt
and consumed identity. Controls hit 1030/0 and 1031/0.
All 178 frozen inputs unchanged; 44 of 80 prior raw clients match, and changed
clients pass their prior oracles. This qualifies IR-05–06 in the trusted local
fixture, not missing kernel replies, journal acceptance or recovery.
Next: IR-07 synthetic Started-with-no-return closure. Other NB/ND requirements and
BG-033 unknown-effect recovery remain open.

Separate channel and launch phase fields retain each call's progress using the
same finite phase vocabulary. The original driver-owned pending index now covers
both call types. receive_launch checks the real launch predicate, reserves that
position and marks Started before the Adapter call. The writer stays inventoried
but inaccessible for another operation during that phase. Success retains Worker
and removes supervisor writer ownership before Returned. The launch counter is
bounded by the two consumed attempts; no resetting or replay path is added.

apply_launch consumes no new native call. It preserves the selected launch-busy
error transition, retains unknown/mismatched outcomes with closed admission, and
only increments generation after matching the actual worker to the reserved
target. The launched predicate now requires applied launch state; a held return
cannot satisfy it. Synchronous launch uses the same receive/apply path as the
new probes. Native Adapter, unsafe trap, external protocols and pins are unchanged.

Private index application refers to the retained original context and attempt;
it is not a new incoming-result interface. There is no public call identity codec,
cancellation transport, event queue or journal acknowledgment. Typed wrappers are
Copy, so logical ownership still relies on this trusted driver and enforcing
kernel. No Rust type-level exclusive ownership or hostile-caller boundary is claimed.

Two preflight snapshots retain 196 compiler invocations: the first has two link
size failures, the second passes all 98 valid configurations. The closure probe
checks denial after closure separately from the normal probe's pre-closure duplicate
checks. The early-generation omission probe terminates at 1032 if its expected
1031 assertion unexpectedly survives, so it does not duplicate the full normal
fixture body. No compiler flag, linker limit or ownership oracle was weakened.
The full native run passed without a failed build or execution.

Both success and closure probes dispose the actual retained worker and reader,
then run two ordinary workers for the fixed accounting oracle. The original token
remains consumed. This fixture teardown does not implement receipt retirement or
unknown-effect cleanup. The writer-retention omission is detected as incorrect
ownership state; no duplicate close or re-use of that transferred endpoint is
attempted by the probe. Failures are expected negative oracles, not clean teardown.

Evidence: `docs/evidence/native-launch-receipt-2026-09-06/`. The witness retains the
exact command, inputs, raw clients, logs and comparisons. Applicable documentation,
standards adoption, quality inventory and work order are updated. No independent
reviewer sign-off, new exception or full NB-09 conformance is claimed.

## Validation — 2026-09-06

The full pinned native run passes 84 cases; all seven current consumer inputs
match its frozen source hashes. New raw sizes are 3848 (launch-receipt), 3880
(launch-receipt-close), 2088 (launch-keep-writer) and 2168 bytes
(launch-early-generation). The existing binding-admission client is 4080 bytes;
all clients satisfy the unchanged 4096-byte limit.

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-h71nacli`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. The catalog verifies 1204 historical outcomes
across 37 bundles and 15,498 listed files; these are not distinct current tests.
`git diff --check` and local reference link checks pass. Evidence is retained in
`docs/evidence/native-launch-receipt-2026-09-06/`, including both initial local
link-size failures. No native build/execution failed in the full consuming run.
Only validation notes and final evidence copies follow checks; runtime sources,
tests, inventory, catalog and pins remain as checked. Next is IR-07 synthetic
Started-with-no-return closure, with real unknown-effect recovery still open.
