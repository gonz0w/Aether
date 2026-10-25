# 0075 — Qualify terminal kind with retained target observations

Accepted local experimental contract, 2026-09-06; BG-058 ND-02.

Adopt [Native terminal evidence v0](../specs/NATIVE-TERMINAL-EVIDENCE-V0.md).
The frozen producer's worker status returns kind separately from encoded result;
normal exit overlaps fault/stop numeric results. Require the exact pair, original
applied launch identity and actual retained target. For a terminal candidate,
observe/status/observe must agree before a terminal fact is qualified.

The selected profile maps normal detail 0–255, invalid-opcode fault detail 134 and
native stopped detail 143. Other producer fault vectors are not accepted implicitly.
The model's narrower mapping is preserved; no native or model code changes here.
A live observation is a point-in-time nonterminal result, not readiness or safety
to discard resources. Sampling failures and interruption retain partial evidence
and close admission without inventing a native errno or cleanup outcome.

The source review establishes retained terminal stability for the pinned single
BSP owner. Three reads are a consistency check under that invariant, not an atomic
snapshot claim for general concurrency. One global sample position and one pending fact
per attempt (two attempts); identical delivery is idempotent and conflicting evidence
cannot overwrite history. Consumer acknowledgment/retirement remains ND-03.

Numeric inference is incorrect; a single status lacks observation revision; a new
kernel snapshot mechanism would need separate justification. The local bounded
sequence uses existing producer operations without selecting a production language
or POSIX wait mapping. NT-01–07 record future positive, denial and semantic omission
oracles. First implement actual colliding-kind NT-01–02 probes, then bound retention
and identity integration. BG-058/BG-057 remain active for unresolved NT/NB/ND work;
BG-033 retains real unknown-effect recovery. No new kernel backlog request is needed.

Review sources and seven unchanged native consumer hashes are retained in
`docs/evidence/native-terminal-contract-2026-09-06/`. The existing 89-case witness
is unchanged. Documentation adoption adds no executed case or implementation claim.
Fresh native evidence is required for any subsequent status/worker change.

## Validation — 2026-09-06

`python3 scripts/check-all.py` passes all eight gates in
`out/checks/run-w4axn51_`: 228 model tests, 23 negative controls, 1000 traces,
48 host tests and 37 harness tests. An earlier passing run, `run-y5rb1zpa`, is
retained before clarifying global sampling capacity and positive terminal revision.
Both exact command logs and reports are retained; no failed check is hidden.
The native catalog remains 1293 historical outcomes across 38 bundles; this
turn adds no native execution. Seven current consumer sources match decision
0074's executed 89-case witness. The reviewed kernel source also matches that
witness's frozen input digest.

New contract/decision links resolve and `git diff --check` passes. Evidence is in
`docs/evidence/native-terminal-contract-2026-09-06/`. Only validation notes and
final evidence copies follow checks; contracts, inventory, runtime code and pins
remain as checked. Next is NT-01–02 actual terminal-kind collision evidence.
