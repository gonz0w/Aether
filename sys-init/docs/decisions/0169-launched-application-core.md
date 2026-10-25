# 0169 — Fixed Rust Launched application and effect capture

BG-057, 2026-09-07. Implement the bounded application transaction needed after
0168 reservation binding. The native Driver's Applied launch is an input to
policy, not evidence that the Launched policy observation was applied. This
slice is host-executed Rust logic and no_std target compilation; native source
qualification and fresh consuming application remain the next integration gate.

One private owner contains both fixed reservation storage and two-attempt policy.
Offer independent starting attempts or one started-dependency pair. These are
fixed profiles, not descriptors, readiness, a scheduler or the Python Model.batch
implementation. The dependency starts pending only after the provider's Launched
observation. Selectors are synthetic in host tests; they supply no worker authority.
The future native owner must revalidate the original History before reservation
and application, using an exclusive borrow for the entire transaction.

Preflight every member and the exact reservation before mutation. Apply once,
retain before/after phases, and capture the complete generated launch obligation
in the twenty-entry pool with all ten symbolic token fields and Reserved
(disposition 1). Symbolic context is the existing fixed fixture domain; this
is not native issuance. Expected state and effect outputs derive from pre-state,
then are compared against actual mutation and retained output before publishing
an owner-bound Applied receipt. Exact replay returns the same retained cut without
applying policy again. Foreign/cancelled keys deny without mutation.

Before attempting application, mark Unknown and close. Any incomplete transition,
lost/corrupted capture or unexpected outcome retains actual phases and all captured
effects, keeps the reservation credits, and prohibits retry/cancel/new work.
Only successful verification publishes Applied and reopens inspection/replay.
No acknowledgment, effect execution, retirement, reset or recovery is exposed.
After one application even an empty-effect cut keeps its twenty-credit reservation;
this deliberately stops new admission until an explicit retirement contract exists.

Keep the 1976-byte storage and 1984-byte reservation layout. The application owner
adds a separate small policy; its size excludes native History, resources and
stack. Implement after existing code to preserve current fixture source locations.
No native consumer calls the new methods in this slice. Require host transition,
complete-token, denial, replay, cancellation, zero-effect and partial-failure
oracles plus omission controls; compile the same code for x86_64-unknown-none.
Rebuild the existing 194 native profiles and require byte identity. If any native
image changes, obtain fresh target evidence before claiming completion. Run all
local gates, preserve failures/pins/catalog, update quality and BG-057/058 handoff.

Applicable Foundations O-01–04, I-01/03–06 and E-01–08 retain authority, complete
outcome capture, bounded storage, explicit unknown and layer-specific claims.
Distribution SV-02/03 distinguish started dependencies from readiness; no candidate
format is adopted. No shared contract, public output or sibling repository changes.

## Validation and handoff

Decision 0169 implements a fixed Rust Launched application transaction with
exclusive policy/reservation ownership. Independent attempts and a single started-
dependency pair have explicit starting/started state. Whole-member preflight
precedes mutation; the provider's transition generates and retains its dependent
launch obligation with all ten occurrence-token fields and Reserved disposition.
Verified application publishes an owner-bound Applied receipt; replay does not
repeat policy mutation or effect capture. Foreign/cancelled/stale inputs deny.
Unknown is recorded and the owner closes before mutation; failed verification
retains actual state and captured effects, and blocks replay/cancel/new admission.
Read-only state/effect inspection grants no execution authority.

All seven new application tests and four omission controls pass, alongside the
five reservation tests and three reservation controls. All ten local gates pass
in `run-7zvhu56k`, including 287 unchanged model tests and ten Rust groups. The same
code compiles for x86_64-unknown-none. Storage stays 1976 bytes; Reservations stays
1984; Application is 1992, excluding native History/resources/stack. The profiles
generate at most one effect per cut but retain the twenty-entry pool. Even a zero-
effect Applied cut keeps twenty credits; further reservation remains Full until
explicit retirement exists. No acknowledgment, effect execution or reset API.

All 194 existing ABI-15 images and 151 ABI-6 rebuilds are byte-identical, with a
maximum ABI-15 image of 8056 bytes. The new methods are not called by the native
consumer: this is host Rust execution and target compilation, not a fresh Aether
application witness. The 194-case native checkpoint remains decision 0168. Full
native integration still requires an exclusive original-History owner, exact
source revalidation, actual worker binding and a fresh consuming witness. Tokens
use the fixed fixture's symbolic domain; native journal issuance is not claimed.
Release locks and the 50-bundle/3019-case catalog remain unchanged. BG-056 complete
producer source closure remains a separate catalog-acceptance gap.

The first image-comparison driver failed while mistaking `rustc --version` for a
build command; its frozen inputs, driver and traceback are retained. Filtering
actual output-producing compiler commands fixed the driver; the fresh full rebuild
then passed. No image failure or target-run result is inferred from that error.
Evidence: `docs/evidence/launched-application-core-2026-09-07/`.

Next BG-057/BG-058: bind this application owner to qualified native launch history,
verify complete generated effects and consume fresh target controls. The driver
return's Applied state and policy observation's Applied receipt remain distinct.
BG-058 keeps per-attempt cleanup/reclaim provenance; BG-060 sustained reuse and
BG-033 recovery stay open. No additional host-platform campaign or sibling change.

Technical review: policy and reservation storage share one private owner; lifetime-bearing receipt keys use its original external anchor. Every member is checked before mutation, with expected state/effect identity derived from pre-state. Mutation and retained-output verification remain separate. The tests inject an unexpected occupied tail slot to exercise post-mutation verification failure and retention; such internal corruption is not an input supported by the private API. Unknown is set before mutation so even an interrupted call cannot reopen this owner. No heap, unsafe operation, native call, shared ABI or renderer is added. The fixed profiles do not implement the complete Python policy model. No independent reviewer sign-off is claimed. Documentation impact: storage contract, native coverage boundary, quality inventory and BG-057/058 handoff.
