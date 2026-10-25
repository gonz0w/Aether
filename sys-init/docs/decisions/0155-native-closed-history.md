# 0155 — Native closed terminal history

BG-058 PH-03/06, 2026-09-07. Qualify read-only inspection through the existing
private History storage; add no accessor that mints replay authority after closure.
The pinned AENIN002/ABI-15 producer and worker remain unchanged. Foundations
O-01/O-03/O-04, I-01/I-03–06 and E-01–08 and the scoped local quality rules apply.

Capture one real terminal O1/S/O2 sample, replay it as Duplicate while open, then
close by accepting the explicitly synthetic contradictory diagnostic. Repeated
closed replay must deny; conflict must return Closed without entering its producer;
capture must deny without reading. Inspect both complete stored samples and their
original association. Preserve fact, token, owner, pending position, native slot,
generation, counters and resources. Explicit fixture disposal clears only known
reader/worker ownership; neither history nor consumed issuance is reset. This is
fixture cleanup, not PH-07 retirement or applied journal acknowledgment.

One positive must finish at 100/3. Four local omission controls erase primary
(1067/0), erase diagnostic (1068/0), reopen before replay (1069/0), or clear pending
(1070/0), each failing its named oracle. Keep the nine-triple container and strict
8192-byte image bound. No allocation, unsafe site, syscall or production API change.
Run all 185 cases with fresh QEMU consumption, compare previous images, and run
all local gates. Keep the evidence catalog unchanged: decision 0154's reused
producer source-closure limitation still applies to these separately retained
witnesses. BG-056 needs a complete producer bundle; no new waiver is authorized.

Preflight retained: the first revision had a fact-type mismatch. After explicit
field comparison, two controls exceeded the image bound. Moving inspection before
further denied operations fits all five images without dropping an assertion.
Source review also corrected the fixture's normal kind/readiness expectation to
1/true; the already-frozen first native run is retained as an unsuccessful attempt.

## Validation and handoff

Decision 0155 passes all 185 fresh Aether native cases, including closed terminal
inspection before and after explicit fixture disposal. Replay denies, conflict
production remains closed, and both complete samples, association, pending position,
issuance and generation remain retained. Four omission controls reject exactly at
1067/0, 1068/0, 1069/0 and 1070/0; the positive finishes at 100/3. All 180 previous
ABI-15 images and all 151 ABI-6 rebuilds are identical. Five focused runner tests
and all ten local gates pass in `run-qgv2e68c`; maximum image is 7592/8192 bytes.

Evidence: `docs/evidence/native-closed-history-2026-09-07/`. No producer, worker,
shared ABI, release pin or sibling repository changed. These are bounded private
fixture witnesses, not production init or PH-07 retirement. Catalog acceptance
remains pending under BG-056 because the reused historical producer omits two
recorded metadata inputs; no new waiver or catalog entry was added.

Next: BG-057 PH-07 coordinator/whole-cut acceptance and retirement contract review
before any acknowledgment or reset API. BG-058 full launch composition and further
O1 failure combinations, and BG-033 recovery, remain open. Other-platform
qualification remains deferred under decision 0153.

Technical review: the added probe reads private fixed storage directly; no new
view constructor, mutable accessor, reset, syscall or unsafe site exists. The
synthetic diagnostic remains explicitly distinct from the actual terminal capture.
The two full Sample clones are oracle snapshots, not additional production storage
or a new stack-budget claim. Documentation impact: coverage, quality inventory,
tracked source/boundary digests and planning handoff updated. No independent
reviewer sign-off is claimed.
