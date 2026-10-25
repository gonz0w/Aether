# Native conflict-guard build study — 2026-09-06

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

`preflight-1` through `preflight-8` retain exact source, commands, linker maps and
logs. `size-review.json` distinguishes failed-link mapped extents from linked raw
sizes. `prototype/` retains the final unadopted edits; `prototype-host/` tests only
the comparison core. `current-consumer-comparison.json` verifies restored accepted
source, not execution of the prototype. Validation/adoption records follow; root
SHA256SUMS.json seals every retained file except itself.

Validation: all nine development gates pass in `out/checks/run-lufy0jhm`,
with no skipped gates and unchanged checked sources. All eleven current consumer
inputs match the accepted decision-0086 snapshot; compiler inputs are unchanged.
Native audit remains 2209 historical outcomes across 45 bundles. The current
151-case native runtime is preserved; no new guard execution is claimed. Full
validation, prototype host evidence and all failed strict links are retained.
