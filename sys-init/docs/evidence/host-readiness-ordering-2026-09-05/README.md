# Host readiness ordering acceptance — 2026-09-05

[Decision 0013](../../decisions/0013-host-readiness-acceptance.md) preserves the
existing first-frame format. Four new methods exercise real pipes and owned
children: notification before adapter registration completes; before/exactly at/
after deadline; notification after stop; and a retained old writer plus separately
injected stale-generation event during replacement. Handshakes establish writes;
exact clock cuts are injected. They are not native timing measurements.

[Full validation](validation/results.json) passes 42 host tests, 34 model tests/
three mutation controls, 23 harness tests, the 22-recorded-case native evidence
audit and three offline standards checks. No Aether execution was run. No runtime,
model, wire-format, shared-pin or companion working-tree change was required.

[Negative control](mutation.json) changes two deadline predicates only in a private
snapshot. The exact-boundary subcase fails; before/after and all other new tests
pass. The log records one assertion failure, no errors. Source digests identify
both the unchanged model and retained mutant. Commands/logs and source copies
are retained; the mutant is inert evidence and must not replace production code.

[Acceptance matrix](../../HOST-READINESS-ACCEPTANCE.md) distinguishes executed
cases, scoped criterion disposition and unresolved helper/flood/cross-host work.
BG-040 is active/partial. The old writer is test-owned, not an unowned descendant;
its real pipe receives EPIPE after the old reader is reclaimed. Stale-event
injection separately checks the model identity gate. PID/FD reuse is not forced.

Reproduce the positive suite with `python3 scripts/check-all.py`, or only these
cases with `python3 -m unittest discover -s tests -p test_host_readiness_ordering.py -v`.
The retained mutation.json gives exact substitutions and command for a separate
private source copy. SHA256SUMS.json fingerprints this evidence bundle.
