# 0064 — Prioritize native driver identity and evidence integration

Accepted local work order, 2026-09-06, BG-058/BG-057.

The [source/evidence review](../research/NATIVE-DRIVER-INTEGRATION-REVIEW.md)
finds real native resource retention and bounded event transfer, but no issued
operation binding or journal acceptance. Its terminal value also omits the kind
required by the model. The current 57-case witness remains valid in its recorded
scope; no complete native driver, recovery or POSIX conformance follows.

Choose ND-01 identity/admission contract first, ND-02 exact terminal qualification
before lifecycle projection, then ND-03 cut acceptance/retirement. ND-04 composes
selected errors while retaining unknown ownership; ND-05 joins policy only after
those boundaries. Existing BG-058/BG-057 own the follow-ons, with BG-033 and BG-040
as recorded in the review. No kernel blocker is demonstrated for the next local
contract. Preserve current model tokens and pinned native ABI.

Direct inbox wiring, further isolated policy cases and wholesale model porting
were considered; each postpones or combines identity/evidence gaps. A bounded
contract makes required negative controls explicit before implementation and leaves
the production language/portable adapter choice open. No shared rule is forked.

This change is documentation and planning only. Retain the reviewed sources,
verify current native source identity against decision 0063's executed snapshot,
run all repository gates and retain their logs. No native runtime rerun is needed
for unchanged sources and unchanged acceptance claims (Foundations E-04–06).
Any subsequent native implementation requires its own fresh consuming witness.
This is a Codex technical review, not independent or affected-owner sign-off.

## Validation — 2026-09-06

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-fsthmyrq`. The retained native catalog still audits 702 outcomes
across 30 bundles; this review adds no target cases. All six consumer source
entries in decision 0063's source manifest match the current checkout.
`git diff --check` passes. Review inputs, comparison pins, check results/logs and
adoption records are retained in `docs/evidence/native-driver-review-2026-09-06/`.
Only validation notes and evidence copies are added after the checks; runtime
sources, tests, coverage catalog and quality inventory remain as checked.
