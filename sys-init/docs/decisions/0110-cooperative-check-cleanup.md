# 0110 — Cooperative aggregate cleanup

BG-056 host harness change, 2026-09-06. Aggregate failure currently kills its
owned gate group immediately. A Python wrapper cannot then unwind and clean a
worker started in another group by bounded_capture.py or bounded_tools.py.
Send SIGINT to the owned gate group first, allow at most one second for the
direct gate to exit, then force-kill the remaining owned group and reap the gate.
Preserve the original timeout/output-limit/interrupted/error classification.
The one-second grace is additional to the command deadline, not extra execution
budget. Per-gate records add cleanup_grace_seconds; normal output is unchanged.

Exercise an actual aggregate -> capture helper -> separate worker chain with a
ready handshake, and prove cooperative cleanup reaps the worker before wrapper
exit. Include ignored-SIGINT fallback and existing overflow/timeout/nonzero tests.
Retain a before-fix witness and clean up its deliberately surviving test worker.
No external services, native runtime, compiler helper, release pins or sibling
repositories change. The change uses POSIX process groups/signals already in the
harness and adds no dependency.

This is cooperative cleanup for responsive trusted Python wrappers. Detached
uncooperative descendants, abrupt aggregate termination, deep nested wrappers
that force-kill intermediate owners and repeated interruption during cleanup
remain outside the guarantee. Output during the grace is not newly drained;
pipe pressure can force fallback. Forced cleanup alone does not establish
separate-group cleanup. Keep these gaps under BG-056 and run all local checks.
Evidence: docs/evidence/cooperative-check-cleanup-2026-09-06/README.md.

Validation: the new nested regression fails against the retained old runner
and passes with cooperative cleanup; ignored-SIGINT fallback and twelve prior
runner tests pass. All ten gates pass in out/checks/run-zayzuf8u. The after-probe
retains direct-worker reap/closed-pipe evidence. Native inputs and inner helpers
remain unchanged. Manual lint is clean after retained line-style corrections.
