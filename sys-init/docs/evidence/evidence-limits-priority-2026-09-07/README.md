# Evidence limits and operational priority — 2026-09-07

Decision 0142 / BG-056. Documentation/inventory checkpoint, no runtime or checker
implementation changes. Current coverage and historical limits are consolidated
in EVIDENCE-LIMITS.md; G-CODING/G-DOCS milestones and current priority are updated.
New guide links resolve. No behavior-specific tests or manual renders are needed
for this Markdown-only change; all ten `python3 scripts/check-all.py` gates pass
in run-y2t_prwl with tested sources unchanged. Exact commands/source hashes are
in validation/results.json. All attempts passed; git diff --check passes.

Native audit code and stdout match decision 0141; catalog, 24 native inputs and
release locks remain fixed. RC1 remains unpublished; no native/sibling/pin or
historical-evidence changes. No review sign-off, scheduler or provider is invented.

Next implementation scope is aggregate source snapshots: current read_bytes calls
are unbounded and sit outside active-gate watchdogs. Acceptance requires inventory,
explicit file/root policy and byte/traversal bounds, stable read identity, unchanged
successful maps and malformed/change tests. Follow with aggregate report/error
paths. Historical missing artifacts, independent review and platform qualification
remain explicit blockers to their respective claims, not reasons to fabricate
completion. Planning/validation notes and evidence followed aggregate checks.
