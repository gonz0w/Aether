# Independent review handoff — UL-075–077

The maintainer approved this scoped technical review on 2026-09-07; see the
[approval record](../evidence/dash-review-2026-09-07/README.md). Scoped checks pass.
The reviewed maintained-source hashes are in
[review-sources.json](../evidence/dash-create-response-2026-09-07/review-sources.json),
with all 12 source hashes rechecked when recording approval. The checklist below
remains the review scope; no additional reviewer command logs were supplied.

## Review scope

- UL-075: audit-imports.py pin checks survive optimization; bounded nm sessions,
  empty-input rejection, unchanged symbol subtraction/report keys and stale-report
  handling. Original 32 objects/99 imports match retained evidence.
- UL-076: host-build.py owns compiler cleanup, bounds output/wait and preserves
  streams. Full guest integration and identical helper-byte evidence are supplied.
- UL-077: create/inspect/start/remove/absence handling, frozen client/connection,
  unconfirmed-create rejection, exact ownership checks, read-only guest input and
  narrow writable generator child mounts. Top-level generation avoids nested cleanup
  owners beneath make; guards reject unexpected generator execution.
- Test fixtures: relay half-close handling, observer group ownership, actual
  post-create connection refusal and committed-create/lost-response controls.
  Recovery is separate and never promotes an unresolved original run.

## Evidence to inspect

- [Import auditor](../evidence/dash-import-process-2026-09-06/README.md)
- [Host compiler](../evidence/dash-host-build-2026-09-06/README.md)
- [Guest lifecycle integration](../evidence/dash-container-integration-2026-09-06/README.md)
- [Target generators](../evidence/dash-generator-2026-09-06/README.md)
- [Relay EOF failures and correction](../evidence/dash-relay-eof-2026-09-06/README.md)
- [Revised live qualification](../evidence/dash-transport-qualified-2026-09-07/README.md)
- [Create-response loss](../evidence/dash-create-response-2026-09-07/README.md)

Check that actual failure statuses cannot masquerade as guest success, all claimed
cleanup has witnesses, partial results retain their limitations, and the supported
host/SSH/image assumptions are explicit. Labels are not native authority; private
outputs are not host sandbox evidence. Per-call deadlines are not a total watchdog.

Offline checks from repository root: `python3 -B docs/quality/check.py` and
`python3 -B experiments/dash-reference/test-container-process.py`. The latter is
model evidence. The linked experiment README gives source-pinned live/build commands;
run them only with the documented local inputs available. In this execution environment,
VM startup and live commands needed one session. Do not silently repin or provision
alternate tools/images to obtain a pass.

Return reviewer identity/date, exact source or commit identity, files/evidence checked,
commands actually run (if any), findings and their disposition, and approval scope.
A technical approval is not packaged manual lookup, independent onboarding/recovery
reader evidence, publication authorization or native acceptance. Never invent those
separate gates. No external review request was sent by this task.
