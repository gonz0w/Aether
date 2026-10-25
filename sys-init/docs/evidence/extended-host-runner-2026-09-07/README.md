# Local EHT-01 runner — 2026-09-07

Decision 0147 implements the local eight-seed campaign and one-seed replay.
The actual campaign completed 432 executions with zero skips in approximately
12.48 seconds on the recorded macOS arm64/Python profile. This duration describes
one run, not a performance threshold or scheduling-coverage claim.

`campaign/` retains all eight worker stdout/stderr logs and the parent results,
actual IDs/order, commands, source/implementation identities and capture outcomes.
`focused.log` records six runner tests (including controlled supervisor outcomes,
malformed evidence, source identity, deadline, publication and CLI contracts).
Mocks are not new real timeout/cleanup witnesses; the full evidence gate runs the
existing real capture, interruption and cleanup regressions. `validation/` and
`checks.log` retain all ten passing gates with unchanged sources during validation.
The campaign's implementation and 16 corpus input hashes still match current files.

`review.json` records unchanged native audit output, 24 native inputs, catalog
and release locks. No sibling or retained native inputs were changed. The campaign
runs trusted host tests; it does not execute new Aether target cases or qualify
PID 1, other platforms, full process containment or production readiness.

Initial manual lint found four overlong lines; original manual/logs are retained.
Reflow after full checks passed final lint and 78/60-column ASCII and HTML rendering.
Automated rendering does not supply independent visual/reader sign-off.

Source snapshots and a SHA-256 manifest retain this bounded implementation review.
No automatic retry, scheduler, hosted CI or release age policy is configured.
Independent review and additional host qualification remain BG-054 work.
