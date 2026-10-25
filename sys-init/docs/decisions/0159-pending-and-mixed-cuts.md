# 0159 — Pending disposition and mixed-cut retirement

BG-059 NC-06/07 model slice, 2026-09-07. Extend the existing single Retirement
owner with exact-member pending release and selective retirement from a mixed
Applied cut. No native source, real journal, kernel operation or shared pin changes.

Release requires the exact retained Applied receipt, a Terminal member identified
by its original source object, and the synthetic adapter's single pending source
matching that member. Retain started/confirmed status and any return before/after
callback; confirmation also requires the pending position to be empty. Failure
closes without rerunning application/release. Exact replay cannot release another
member's later position. This is one logical pending position, not a new native
capture or two-simultaneous-terminal-history claim.

Retirement selects only Cleaned members but retains the complete cut receipt.
Every selected member must have a confirmed pending release under its earlier
Applied Terminal receipt, matching empty resources and applied reclaim. Preflight
all selected members before marking any. Other-phase members, their pending
position and histories remain untouched. Cleaned without confirmed release denies.
The lifecycle model itself is not yet wired to gate Cleaned application on actual
resource disposition; BG-057 retains that real adapter integration.

Test release/replay and exact membership, changed pending identity, missing release,
wrong/no-op/lost release results, reentry, mixed Cleaned/Terminal and Cleaned/Launched
selection and partial mixed-cut failure. Add source controls for wrong-member
release and false pending-release confirmation; preserve existing retirement/core
controls, adapting only the phase-selection anchor. Retain all prior semantics.
Run full local checks; logical storage adds two per-attempt release records,
observations and return slots. No reset, replacement, recovery or native memory
claim. O/I/E and Distribution exclusions remain as in decisions 0156–0158.

Qualification adds eight test methods (254 model tests total), two pending
omission controls and the previously outstanding explicit core ordering control.
Existing three retirement controls remain, with their early-retirement anchor
updated for selective membership; no prior semantic oracle is dropped. The model
suite now contains four core, three retirement and two pending source controls.

## Validation and handoff

Decision 0159 qualifies exact-member pending release and mixed-cut retirement in
the pure model. Applied Terminal receipt and actual synthetic pending/source identity
must match; success requires both a matching return and an empty position. Replay
does not release another member's position. Uncertain release retains started state,
source, returned diagnostic and Applied receipt while closing without retry.

Mixed cuts retire only Cleaned members, after confirmed earlier Terminal pending
release and resource preflight. Other members and their pending position/history
remain untouched, including when marking fails. All 254 model tests pass, including
eight pending/mixed-cut tests. Four core, three retirement and two pending source
omission controls pass their expected assertion-failure oracles. All ten local
gates pass in `run-v7stuqiq` with unchanged checked inputs. Native consumer sources,
release locks and catalog bytes remain unchanged; no new target run is claimed.

BG-059's pure synthetic qualification is complete; this is not full native NC
conformance. Next BG-057: integrate the actual lifecycle/journal adapter with exact
source qualification, whole-cut effect capture and cleanup/admission gates, then
obtain fresh native consumption. BG-058 retains complete native launch provenance,
BG-060 sustained history/reuse and BG-033 unknown recovery. BG-056 producer source
closure remains separately pending; the existing 185-case native witness is unchanged.

Review: pending release and retirement remain separate operations bound to exact
immutable receipts and source objects. Both use the existing guarded callback
boundary and single disposition owner. Receipt inspection never reapplies lifecycle
work. Release confirmation checks the observed position as well as the returned
receipt; failure retains evidence without claiming rollback. Selective retirement
retains the complete mixed receipt, not a fabricated subset cut. There is no reset
or sample eviction. Python allocation, synthetic registration and read-only adapter
assumptions remain explicit; no independent sign-off or native authority is claimed.
Documentation impact: model count/reference, contract checkpoint, quality surfaces,
standards applicability, BG-059 completion and BG-057 integration handoff.
Evidence: `docs/evidence/pending-mixed-cuts-2026-09-07/`.
