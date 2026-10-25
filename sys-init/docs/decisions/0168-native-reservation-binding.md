# 0168 — Native Launched reservation binding

BG-057/BG-058, 2026-09-07. Connect the fixed Rust reservation owner to an immutable
borrow of original History. Private requests carry attempt/phase, full launch token
and actual worker; reserve validates the same native Context, Applied acquisition/
launch, ownership, native target/generation and exact token before reserving any
record. The History borrow prevents concurrent source changes during this slice.
Reservation/cancellation do not mutate lifecycle, acknowledge effects or release
pending history. Existing synthetic issuance/context labels remain explicit.

One actual native attempt is sufficient for the first consuming witness. Deny a
received-but-unapplied launch, a foreign owner, substituted token and an absent
second attempt; then capture real terminal history, reserve/replay/cancel/re-reserve
Launched without another native read. Retain sample, pending position, resource
association and consumed issuance through explicit fixture disposal.

Positive 100/3; omission controls bypass native owner (1075/0), applied launch and
generation qualification (1076/0), or token equality (1077/0). Native two-live-
member application is not claimed. Preserve 190 previous native outcomes, ABI-6
image bytes and 8192-byte limit. Run 194 fresh consuming cases, relevant host tests
and full local gates. Keep producer/worker/release pins and catalog fixed; no new
BG-056 source-closure waiver. No syscall, unsafe operation or shared API is added.

Preflight: the first layout and a no-inline revision exceeded the strict native
image limit. A retained linker map measured 11496 bytes and showed slice-panic
formatting code. Checked get/get_mut access and explicit bounded member copying
remove those panic paths, preserving ordinary denial before mutation. The third
layout links all four images at 8176/8112/8096/8048 bytes; the limit stays 8192.
Host reservation tests and controls are rerun for the changed core. The positive
has only 16 bytes of image headroom; no future capacity or stack budget is implied.

The first consuming run passed the 190 prior cases but the new positive faulted
(vector 14, error 6) before worker effects. It is failed evidence, not acceptance.
Assembly showed a 3736-byte probe frame and a constructor with 3912 bytes of
aggregate temporaries against the pinned supervisor's 4096-byte user stack.
A constant zero initializer eliminates the constructor temporaries. Separating
reservation inspection from launch/capture gives the probe a 1064-byte frame and
the reservation helper a 2464-byte frame; compiler frame sizes exclude saved
registers and callees. The resulting four images fit at 8056/7992/7976/7928 bytes.
A diagnostic run restricted to those four cases passes, including positive 100/3;
full source-frozen acceptance is rerun after this fix. Preflights 4–6, assembly,
the failed full run and the restricted diagnostic driver are retained separately.

## Validation and handoff

Decision 0168 passes all 194 fresh Aether native cases. A private reservation
binding validates original Context, complete launch token, owned reader/worker,
Applied acquisition/launch and full target/generation before reserving any cut.
The source History is immutably borrowed throughout reservation/cancellation.
Received-but-unapplied launch, foreign owner, substituted token and absent second
attempt deny; the subsequent valid request still receives serial one. Duplicate,
cancellation and new serial two preserve the real terminal Sample and pending
position without another read or launch. Explicit fixture disposal is separate.

The positive finishes at 100/3. Three controls reject at 1075/0, 1076/0 and 1077/0.
All 190 prior ABI-15 images and 151 ABI-6 rebuilds remain byte-identical. All ten
local gates pass in `run-_kw_g65q`, including 287 model tests and the ten Rust
groups with five reservation tests/three source controls. The maximum image is
8056/8192 bytes. Failed preflight layouts, the stack-fault run and assembly are retained;
checked accesses remove slice-panic formatting without changing the size limit.
A constant zero initializer removes constructor temporaries; a separate probe helper
keeps reservation storage out of the launch/capture frame. The 4096-byte native
stack and all image limits remain unchanged. Native execution validates these
particular paths; emitted frame sizes do not prove a general worst-case budget.
Evidence: `docs/evidence/native-reservation-binding-2026-09-07/`.

This is native reservation/cancellation with one actual attempt, not lifecycle
application, effect acknowledgment, two-live-member application or retirement.
Issuance remains the fixed fixture token set. Producer/worker and release pins are
unchanged; the catalog remains at 50 bundles/3019 historical outcomes pending
BG-056 complete producer source closure. No historical exception is extended.

Next BG-057: bounded native Launched application and complete effect capture before
publishing any Applied receipt. The immutable reservation borrow must evolve under
one explicit mutation owner; receipt publication cannot substitute for actual
state transition. BG-058 retains cleanup/reclaim provenance, BG-060 sustained
reuse and BG-033 recovery. Image headroom is 136 bytes in this probe, not a promise
that additional code will fit; future probes require their own size review.

Technical review: requests remain private selectors and never create worker authority. Every member passes before the core reserves credits, and an immutable History borrow prevents mutation between selection and cancellation. The native consumer now captures cut_reservation.rs explicitly. Checked accesses return errors instead of pulling slice-panic formatting into the image; core host tests remain unchanged and pass. No unsafe site, syscall or public API was added. Documentation impact: storage contract, native coverage, source/boundary digests, quality references and both backlogs. No independent sign-off is claimed.
