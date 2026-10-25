# 0087 — Native conflict guard: qualification blocked by image size

Prototype/build study, 2026-09-06; BG-058 PH-03/04. No runtime adoption.

Decision 0087 retains a native conflict-guard prototype but does not accept it
into the runtime. It consumes Sampling into an exclusive Driver/storage guard,
reserves one diagnostic Sample, invokes only the labelled synthetic candidate
producer, retains both histories and propagates Conflict to Driver.closed. Failed
construction returns the original session and diagnostic storage. New omission
probes target primary replacement, missing Driver closure and lost reader.

Eight strict build revisions produced 52 checks: 36 new-probe links rejected by
the unchanged 4096-byte limit; 16 existing identity/index probe links still pass
at 4096 bytes. The smallest conflict probe maps 4464 bytes (revision 7); the
smallest resource probe maps 4624 bytes (revision 5). These minima come from
different revisions and are not a passing combined artifact. No new native
probe executed. The proposed 1052/0, 1053/0 and 1054/0 omission outcomes remain
unqualified; linker rejection is not semantic rejection coverage.

Retained revisions remove formatting pulled in by bounds panics, adjust inlining,
share the already-validated diagnostic binding, split history/resource probes and
share exact raw-history predicates. Checks and bounds were not dropped to accept
an image. The prototype core's nine host wrapper cases pass, but they do not
execute the Driver guard. All prototype sources, logs, maps and failures remain
under docs/evidence/native-conflict-guard-2026-09-06/.

Only this turn's four native-source edits were restored from decision 0086's
accepted source snapshot. All eleven current consumer inputs match that snapshot;
its 151 byte-identical native rebuilds and decision 0085's 151-case target witness
remain the runtime checkpoint. No broken native case is added to the live harness.

Next BG-058: bounded layout/compiler analysis of the complete guard paths against
the 4096-byte budget, including the still-unqualified denied-construction and
reoffer paths. Preserve all existing 151 oracles. If fitting requires changing the
image/loader profile, obtain a separately scoped producer/consumer contract and
fresh pins before adoption; do not silently widen the current profile. This is a
local fixture-size blocker, not a demonstrated missing kernel operation or a claim
that all possible layouts have been exhausted. PH-05–07, full launch, additional
O1 injections and BG-033 recovery remain open.

## Plan and review disposition

The original acceptance plan is retained below. None of its new native runtime
claims is marked complete. The split plan adds guard-resources with expected
100/reclaimed=3; this was build-only and never executed. All proposed positives
retain the original raw prefix and closure assertions; separate probes cover
complete diagnostic data and resource/counter identity. Fixture disposal is not
journal retirement.

The prototype uses safe Rust borrows without a new dependency or shared ABI.
Its guard owns the mutable Driver borrow and primary/diagnostic storage references;
no public accessor moves a view out. The final candidate's compact core retains
the diagnostic Sample under the primary's already-revalidated equal binding;
identity checks remain before comparison. Equality checks fact/state, count and
raw triples. Host tests qualify that core change only. Guard construction denial,
physical reserve exhaustion, malformed synthetic candidates and post-closure
preservation require consuming evidence before adoption. There is no independent
reviewer sign-off or complete lifetime/recovery claim.

The captured prototype cannot replace accepted runtime sources while its required
links fail. Historical releases, pins, machine protocols, kernel markers and
native coverage catalog remain unchanged. Documentation impact includes this
study, standards scope, quality gap and planning; no standards exception is claimed.

## Original implementation plan (unfulfilled native acceptance)

Implementation plan, 2026-09-06; BG-058 PH-03/04, decisions 0084–0086.

Consume a qualified Sampling session into a private guard owning the exclusive
Driver borrow, primary view and a caller-reserved diagnostic Sample. The guard
must not expose movable views or mutable sample access. Its only candidate producer
is a labelled synthetic fixture: keep the primary O1/S/O2 returns and construct
a separate valid result-19 sample from their revision/readiness. No additional
native sample, syscall cancellation or contradictory kernel behavior is claimed.

The comparison core retains both views before the guard propagates Conflict to
Driver.closed. Primary fact, pending index, full token, generation, worker/reader,
issuance and counters remain unchanged. Repeated offers cannot produce another
sample or change either history. The single diagnostic reserve is consumed once;
there is no reset/retirement API. Invalid admission must return the still-owned
session/storage to the caller or remain borrowed without losing evidence.

Planned native oracles: conflict positive 100/reclaimed=3 after retention checks
and known fixture cleanup; primary-overwrite omission 1052/0; skipped Driver
closure 1053/0; forgotten reader 1054/0. Split probes if needed but preserve all
151 previous cases, exact retention/denial assertions and the strict 4096-byte
profile. Additional probe oracles will be recorded before execution. Run host
core/omission checks, strict build preflights, a fresh native witness and all nine
development gates. Retain failures, exact commands and source/tool identities.

This remains fixture-seeded admission and one diagnostic slot, not full launch
composition, two-attempt capacity, storage across guard destruction or BG-057
whole-cut retirement. Known fixture disposal is not journal retirement. No new
unsafe code, dependency, shared ABI, kernel operation or released pin is planned.

Validation: all nine development gates pass in `out/checks/run-lufy0jhm`,
with no skipped gates and unchanged checked sources. All eleven current consumer
inputs match the accepted decision-0086 snapshot; compiler inputs are unchanged.
Native audit remains 2209 historical outcomes across 45 bundles. The current
151-case native runtime is preserved; no new guard execution is claimed. Full
validation, prototype host evidence and all failed strict links are retained.
