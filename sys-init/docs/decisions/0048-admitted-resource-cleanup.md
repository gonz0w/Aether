# 0048 — Admitted target resource cleanup

Accepted 2026-09-06, trusted BG-058 model.

## Scope and source basis

The frozen ABI-6 producer's launchOperation transfers the writer only on success.
The supervisor keeps the reader. Native reclaim retires the target but does not
release the supervisor's wait slot. waitOperation(0x25005) explicitly releases
that slot, including a pending wait; status/cancel outcomes do not release it.
The frozen native_wait.zig gives one domain-wide slot and 64 non-reused tokens.
Sources: [producer](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/kernel/arch/x86_64/native_c.zig),
[wait implementation](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/kernel/native_wait.zig).
This source basis is not fresh native execution.

## Decision

AdmittedResources attaches once to an already admitted TargetRegistry record for
the current owned service generation and epoch. The trusted driver supplies its
retained reader ID; the transferred writer is not a supervisor cleanup resource.
Reject duplicate attachment or duplicate reader identity across live records.
The fixed profile has one reader, one target and optionally one wait; helpers,
devices, extra channels and borrowed resources are unsupported. This is a
post-admission inventory; pre-launch resource acquisition and outcome routing
still require composition with decision 0047.

Reserve the registry's single wait slot before invoking registration, with the
next expected token 0xe1000000 | generation (1..64). A pending registration holds
the slot even without a reply. A selected confirmed rejection releases only the
reservation; success consumes the next generation. No token wraps or resets on
service replacement. Admission/registry ownership is trusted and exclusive;
external calls bypassing it invalidate this bookkeeping profile.

Resource replies are exact seven-field trusted dictionaries: schema
abi6-resource-return-v1, profile, producer, target, resource, syscall and result.
For registration resource is the predicted token; for release it is the admitted
wait token; for close it is the reader. This context is recorded by the synthetic
driver, not an additional native output or authentication mechanism. Only an exact
success changes ownership. Register errors -13/-9/-22/-16/-28 release the reserved
slot; close errors -13/-22 and release errors -13/-9/-22 preserve ownership.
Malformed, mismatched and unknown replies reject without clearing state.

Reader close and wait release can occur in either order, before or after confirmed
target reclaim. Wait status/cancellation is never release evidence. New wait
registration after target reclaim is rejected. cleaned_event requires the registry's
retained confirmed native-cleanup-v1 fact, closed reader and no pending/owned wait,
and revalidates the current owned generation/epoch. It returns an event for explicit
runtime delivery, not direct ownership mutation. Registry retirement still requires
that model cleanup to have been observed. Unknown effects cannot be reconciled here.

## Bounds, alternatives and validation

At most two attached inventories follow the registry's two slots, one pending or
owned wait is shared across them, and only a scalar wait generation grows to 64.
No unbounded queue/history, dependency or actual native call is added. Standard
library Python models the selected ABI-6 contract; no POSIX wait or cross-platform
process claim follows. Treating terminal/cancelled/reclaimed wait status as release
was rejected because the producer retains the occupied slot until explicit release.
Native target reclaim alone remains insufficient for complete generation cleanup.

Apply Foundations O-01/O-04, I-03–06 and E-04–08, with unchanged shared pins and no
new exception. Test all cleanup orders, pending/failed/mismatched reply retention,
domain-wide contention, token exhaustion/reuse denial and stale generations. Add
an omitted-wait cleanup control. Run model/full checks and retain sources/logs.
BG-058 next composes launch/result/resource/observation paths and obtains fresh
consuming native witnesses; BG-033 retains unknown recovery. No native change.

Decision 0048 validation: 213 model tests / 21 distinct mutation controls,
48 host tests, 37 harness tests and all eight offline gates pass. Evidence:
`docs/evidence/admitted-resources-2026-09-06/`. No fresh native execution.
