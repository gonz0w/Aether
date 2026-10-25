# UL-080 simplicity adoption review — 2026-09-07

User authorization: adopt the Coding v0.2.0 handoff locally, verify hashes, run
checks and commit; preserve released pins and avoid sibling/runtime refactoring.
The source extension is clean at Aether-standards commit
049fa158c1b9e799c799a0713a418601d4885c2e. Four documents and SHA256SUMS are copied
verbatim under docs/vendor/aether-review-snapshots/2026-09-07/coding-v0.2.0.
Manifest SHA256: 8c3d8095acc9b6283a5f6970bc4ce6e7e4646a04fb759f8cf2940ed494cbeff8.
This is explicit prospective adoption of an unreleased additive process snapshot;
it is outside the 2026-09-05 approval receipt and frozen rc1 kit.

## Scope and simplicity assessment

Current requirement: make SE-01–05 actionable through local guidance and the
existing review and integrity gate. Changed surfaces: AGENTS, STANDARDS, PROCESS,
change-review, quality checker/test/source record, manual and existing backlog/state.
No runtime contract, release pin, historical evidence or sibling changes.

1. Simpler alternative: document a manual hash command without changing the gate.
2. Chosen approach: reuse the existing verifier with optional explicit snapshot/pin
   arguments. A second call enforces this adoption on every ordinary quality run;
   the manual-only alternative could omit the new pin. No registry/framework,
   new runtime dependency or parallel review system is needed.
3. Complexity removed: no runtime removal now. One existing verifier and review
   outline serve both snapshots, avoiding duplicated verification/review machinery.

Responsibility remains manifest verification. Control flow adds one sequential
verification before validators; all existing path, symlink, inventory and digest
checks apply. Explicit optional arguments preserve the original default API/tests.
No persistent state is introduced. Failure still exits1 before loading validators;
help/version/usage and owned-child cleanup remain unchanged. Cost is four additional
file hashes and one manifest hash per gate, not a claimed measured speed result.

Testing: existing integrity boundaries plus explicit-snapshot valid/tampered-content
control; default quality gate (all three standards wrappers); help/version/release
CLI behavior and manual lint/render. Keep exact commands/results and cleanup in
checks.json/streams. No runtime tests are needed because runtime code is unchanged.
Release preflight is expected to reject existing draft coverage; that is not a
waiver or regression. Released pins and approved snapshot must match HEAD.

Technical reviewer: Codex inspected the scoped diff, defaults, fail-before-validator
ordering, exact copied bytes and documentation routes. Independent reader/design
sign-off is pending, not inferred from the user's adoption instruction. This policy
update does not claim implementation simplicity/conformance. The next substantial
UL-007 integration must answer these questions in its existing review. Concrete
compatibility/tooling triage is UL-081; no implementation is part of this adoption.

Final checks: quality passes (including both snapshots, integrity controls and all
three release wrappers), help/version pass, release exits1 as expected for existing
draft inventory, ASCII rendering passes. This host mandoc lint exits1 with exactly
three pre-existing STYLE notices (two long source lines and explicit Os); comparing
against HEAD produces identical normalized diagnostics. No new warning/error was
introduced. Initial stricter lint expectation and streams are retained; no unrelated
manual cleanup was made. Runtime/refactoring tests were not selected. Released pin
and approved-snapshot equality against HEAD and whitespace/staged scope are checked
before commit. Commit scope excludes the existing unrelated dirty roadmap work.
