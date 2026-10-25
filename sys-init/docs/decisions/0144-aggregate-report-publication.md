# 0144 — Aggregate report publication and snapshot failures

BG-056 host slice, 2026-09-07; Foundations E-01–08 and internal Experience output
exception apply. Publish reports through owned same-directory temporary files and
atomic replacement, cleaning temporary files on exceptions. No fsync/durability
claim. Preserve successful schema/fields, gate logs, commands and exit contracts.

Create a running report before initial source snapshot. Catch expected filesystem/
validation errors and KeyboardInterrupt during snapshots/gate/report stages; retain
completed checks, explicit not_run and sources_unchanged=false on failure. Failed
reports add error {stage,type,message}, bounded to 4,096 message characters. Source
hashes are empty when initial capture failed. Interruption exits 130; other failures
exit 1. Emit the normal result summary only after final publication succeeds.
If reporting itself is unavailable, emit an escaped stderr diagnostic and fail;
never claim a saved report or success. Existing active-gate cleanup remains owned
by run_check. Output-directory creation and fatal/repeated signals remain separate.

Tests: atomic failure preserves previous bytes and removes temporary file; initial/
final snapshot errors preserve correct gates/omissions; interrupt outcome; final
publication failure emits no success summary. Use temporary files/mocked gates.
Run focused/full checks. No native/sibling/pin changes. This is host run reporting,
not filesystem crash durability or complete process-signal lifecycle coverage.

Validation: six focused tests and ten gates pass in run-k7q8lxv3. Four final
manual lint/render commands pass after two overlong source lines were reflowed;
initial lint result is retained. Native identities and release pins remain fixed.
Evidence: ../evidence/aggregate-report-publication-2026-09-07/.
