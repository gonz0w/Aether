# 0086 — Pending-history conflict comparison core

Accepted host implementation, 2026-09-06; BG-058 PH-03/04 under decision 0084.

Implement a pure private comparison/retention core beside the existing bound View.
It owns one primary view and at most one diagnostic view, borrowing both immutable
Samples. Validate request identity before calling the explicitly synthetic candidate
producer; revalidate the produced view's identity before comparing complete Sample
state/count/raw triples. An independent equal sample is Duplicate without replacing
the primary. A different qualified sample retains both views and closes this local
store. Further offers must not invoke the producer. Invalid identity or a producer
that supplies no terminal view denies without changing retained state.

This is host qualification of comparison and borrowed retention, not native Driver
closure. Existing View construction remains private and unchanged. The callback
is trusted synthetic fixture code, not an arbitrary service callback or authority
boundary. The core allocates no Sample/queue and owns no kernel resources. Its
one-diagnostic-view bound does not implement pre-reserved physical sample storage,
the full two-attempt/nine-triple budget, or lifetime after the guard is destroyed.

Before native integration, use a guard owning the exclusive Driver borrow and the
primary/diagnostic storage association. Only that guard may propagate local
Conflict to Driver.closed; neither evidence view may escape it. Reserve diagnostic
storage before producing a candidate, retain it through closure, and qualify exact
resource/pending/generation preservation with a fresh consuming target witness.
Do not evade the borrow boundary with raw pointers, interior mutation or dropping
retained views. That integration remains the next BG-058 slice; PH-05–07 stay open.

Acceptance: host independent duplicates, differing revision/result/kind/readiness,
identity denial before production, revalidation of produced identity, absent
terminal view denial, exact first/conflict retention, and no production after
closure. Four separately compiled controls must fail named assertions: primary
replacement, skipped local closure, skipped closed guard and ignored content.
Keep the original view/sample tests and controls. Run all nine development gates.

No native call site changes: rebuild all 151 current native configurations with
the unchanged profile, compare every raw image against decision 0085 and recheck
inputs/tools. Byte-identical clients retain their previous execution evidence;
any differing image requires fresh consuming execution before runtime claims.
No new native conflict behavior is claimed by build comparison. Retain commands,
source/tool hashes, results and failures. Shared pins and historical evidence stay
unchanged; no new dependency, unsafe code, kernel operation or POSIX API is added.


The first host run rejected an invalid synthetic fault pair (kind 4/result 14)
before the intended conflict assertions. This was not accepted as omission
coverage. The corrected fixture uses the pinned mapping (kind 2/result 135), and
a separate case compares equal-result normal/fault and normal/stop pairs. The
failed run and all original inputs are retained in host-attempt-1.


## Acceptance and remaining work

Decision 0086 qualifies the pure pending-history conflict core on the host.
An independently qualified equal sample is Duplicate without replacing the first.
A different qualified sample retains both immutable views and closes the local
store. Wrong request identity denies before invoking the synthetic producer;
produced-view identity is rechecked. Once closed, even an equal offer cannot
invoke the producer or replace retained history. No native read or effect exists
in this core.

Nine named view/conflict tests and nine existing sample tests pass. Four new
omission controls fail their exact assertions for replacing the first history,
skipping closure, producing after closure and ignoring content. The three previous
controls still pass. An initially invalid synthetic fault pair was rejected before
its intended assertion and is retained as failed evidence; corrected tests include
equal-result normal/fault and normal/stop collisions.

All 151 current native configurations rebuild byte-identically to decision 0085,
with unchanged tools/profile and maximum 4096-byte image. The native call sites
are unchanged and the new core is not consumed by them; this is build equivalence,
not native conflict execution. The previous 151-case target witness remains the
runtime checkpoint. Ten consumer sources are unchanged; pending_history.rs has
only the new unconsumed core appended.

Next BG-058: a private guard that owns the exclusive Driver borrow and both sample
storage associations, propagates Conflict to Driver.closed and prevents views
escaping. Reserve the diagnostic slot before synthetic production; qualify both
histories, resources, pending state and generation in a fresh native witness.
This host core's one-diagnostic-view bound does not establish the full physical
nine-triple allocation or storage after guard destruction. PH-05/06 capacity and
sealing, BG-057 PH-07 retirement, full launch composition, additional O1 injections
and BG-033 recovery remain open. No new kernel blocker is identified.


Review: fields and constructors remain private to the binding module. Held moves
views, never copies native authority; Sample equality compares retained state,
count and all raw triples, not only result or revision. The normal conflict branch
retains the original and candidate in distinct fields before closing. The closed
check precedes both identity validation and callback invocation. Denied/duplicate
offers leave Held unchanged; the caller retains ownership of rejected samples.
There is no allocator, raw pointer, unsafe/FFI call, mutable Sample accessor, reset
or retirement method. The trusted callback may operate only in its declared
synthetic fixture scope; this API is not a sandbox against arbitrary callback code.

The future guard must prevent moving retained views out while Driver becomes
mutable. Local Held.closed alone cannot close native admission; no integration
claim is made here. No independent reviewer sign-off is claimed. Documentation
impact includes the PH contract, standards scope, checks, inventory and backlog.

Validation: all nine development gates pass in `out/checks/run-o0vylm5y`,
with no skipped gates and unchanged checked sources. The nine wrapper cases
exercise nine sample tests, nine view/conflict tests and seven exact omission
controls. Native audit remains 2209 historical outcomes across 45 bundles; no new
native execution is added. All 151 rebuilt native clients match decision 0085
byte-for-byte, with unchanged tools and a 4096-byte maximum. Exact validation,
source/adoption snapshots and failed-fixture evidence are retained and sealed.
