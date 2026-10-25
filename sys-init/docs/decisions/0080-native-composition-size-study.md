# 0080 — Measure compiler profiles for retained-sample composition

Completed build study, 2026-09-06, BG-058.

Before selecting another implementation rewrite, compile the exact retained
session-composition source from decision 0079 attempt 2 with Rust 1.98.0
optimization levels 2, s and z. Compare the same twelve selected configurations
and source paths under each setting: eight sampling cases plus four older probes
near the image limit. Preserve the existing linker script, target, panic behavior,
static relocation and all source assertions. Record linker maps, actual sizes,
raw artifacts, failures, tool identity and source hashes. Recheck inputs afterward.
The installed compiler lists all three settings; no tool download is permitted.

This tests build feasibility, not execution, timing, target semantics or production
performance. Do not change current native source, default optimization, producer
pins, case oracles or the 4096-byte bound. Select follow-on work only after comparing
results. A candidate profile needs all current consumer cases, omission controls
and a fresh pinned native run before implementation acceptance. If no profile
fits, retain that evidence and evaluate a different composition structure.

Foundations E-01–08 and existing Distribution/quality constraints apply. Shared
ABI/standards remain unchanged. Research findings must cite local frozen sources
and preserve remaining work under BG-058 before this study is marked complete.
Run all nine development gates and record documentation/inventory impact. No
independent review, kernel blocker or runtime conformance is presumed.

## Findings and disposition

Decision 0080 identifies a build-feasible retained-sampling candidate: all 120
compiler configurations fit, with a 4048-byte maximum (48-byte margin). The candidate
uses optimization s, recorded inlining choices and normalized diagnostic paths;
all twelve paired-path images match. Nine candidate host tests and two omission
controls pass. This is build/host evidence only; the current runtime is unchanged.
Next: explicit profile/default compatibility decision and a fresh 127-case native
witness before adoption. Seeded admission, full launch composition, malformed native
injections, NT-05–07, journal retirement and recovery remain open.

[Findings](../research/NATIVE-COMPOSITION-SIZE.md) cite all source, build and failure
evidence. The investigation expanded from compiler levels to two narrowly recorded
inlining changes, normalized diagnostic paths and the complete candidate. No current
runtime source, harness default or standards pin changed. Candidate native acceptance
is not claimed. The unchanged runtime still has decision 0079's 125-case witness.
Documentation impact: findings, profile acceptance gate, standards adoption, quality
inventory and planning. No independent sign-off or kernel change is required by this
study. Original source/assertion bytes and earlier failed evidence remain preserved.

Validation: all nine development gates passed in `out/checks/run-k0yx267y`;
results and fresh host sample-receipt artifacts are retained in the study evidence
under `validation/`. The ten current native inputs and worker/builder hashes still
match decision 0079. No candidate target execution or runtime adoption is claimed.
