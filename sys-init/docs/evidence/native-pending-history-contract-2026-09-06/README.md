# Pending-history contract evidence — 2026-09-06

Decision 0084 is a source review and local design acceptance, not a native run.
`source/` retains the reviewed inputs at review time; `reviewed-files.json`
records their original repository paths and SHA-256 digests. Current terminal
specification adoption adds a cross-reference after that snapshot.

The two current comparison files verify unchanged native consumer and worker
inputs against decision 0083. Its 143-case native witness remains authoritative;
PH-01–07 are not implemented by this bundle. `adoption/` records this milestone's
planning, standards and contract documents; `validation/` retains development
checks. Root `SHA256SUMS.json` seals all retained files except itself.

Validation: all nine development gates pass in `out/checks/run-bydil6k6`,
with no skipped gates and unchanged checked sources. Ten current native consumer
inputs and both worker/builder inputs match decision 0083. All fourteen reviewed
source snapshots match their recorded digests. This is offline validation; no
new target run was performed. Complete check and sample-receipt artifacts are
retained under `docs/evidence/native-pending-history-contract-2026-09-06/validation/`.
