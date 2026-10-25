# 0084 — Specify native pending-history comparison

Accepted local design, 2026-09-06; BG-058 NT-06/07 and BG-057 ND-03.

The source review finds a missing boundary between one-shot bound sampling and
journal acceptance. Current Driver prevents more reads but does not implement
retained-view comparison, conflicting raw-history storage or retirement. The
model's projected event equality and inbox clearing cannot supply that boundary.

Accept [Native pending history v0](../specs/NATIVE-PENDING-HISTORY-V0.md): privately
bound terminal views, duplicate no-op, ordinary identity denial, one retained
conflict with closed admission, two fixed primary sample slots and one diagnostic
slot, while preserving the current single active/terminal pending position.
Live/error/interrupt histories cannot be promoted into terminal facts. No replay
performs a syscall or acknowledges journal application. No retirement API is
accepted without a named whole-cut coordinator contract.

[Findings, source citations and alternatives](../research/NATIVE-PENDING-HISTORY-REVIEW.md)
explain the decision. Follow-ons PH-01–06 are assigned to BG-058 before closing
this review; PH-07 is assigned to BG-057 and unknown recovery remains BG-033.
Next implement PH-01/02 private origin binding and duplicate/identity comparison,
then qualify conflict/capacity in separate bounded slices. Record exact new native
oracles before changes and preserve all 143 current cases and the 4 KiB bound.

This turn changes documentation/process only. Ten native consumer inputs and the
worker/builder must remain byte-identical to decision 0083. Run all nine offline
development gates and retain reviewed source/adoption/validation records. No new
target run, implemented PH surface, independent sign-off, shared ABI/pin change,
production conformance or kernel blocker is claimed. Documentation impact includes
the terminal contract cross-reference, standards scope, quality gap and planning.

Validation: all nine development gates pass in `out/checks/run-bydil6k6`,
with no skipped gates and unchanged checked sources. Ten current native consumer
inputs and both worker/builder inputs match decision 0083. All fourteen reviewed
source snapshots match their recorded digests. This is offline validation; no
new target run was performed. Complete check and sample-receipt artifacts are
retained under `docs/evidence/native-pending-history-contract-2026-09-06/validation/`.
