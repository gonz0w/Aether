# 0152 — Offline Linux image reload

BG-054, 2026-09-07. Verify the saved OCI archive SHA-256 before loading, check
its exact image ID/OS/architecture, then run all eight EHT-01 seeds with networking
and pulls disabled. Use the previous read-only source snapshot and Rust homes;
check all four tool identities/versions before and after. Require all 432 case
executions with no skips and the same plan, corpus, implementation and actual
orders as the prior campaign. Keep normal budgets, private results and named
container cleanup. Startup/load/execute stay in one live session.

No source or runtime change is required. Record real reload evidence separately
from prior image inspection. Update the reuse guide and current planning handoff;
run full local development checks. No new BSD/illumos image is available under
repository out; QEMU binaries alone do not provide platform qualification. Actual
reviewer and additional platform environments remain needed; no scheduler, native
feature or sibling change follows from this work.

## Result

Decision 0152 verifies saved OCI reload and exact image identity, followed by all
432 EHT-01 executions passing offline with unchanged Rust tool identities.
Complete worker records match the original campaign. All ten macOS gates pass in
`run-77kd5nez`; native inputs/output and release pins remain fixed. Linux full
qualification (0151) and offline reuse (0152) are now witnessed. Next: provision
an additional BSD/illumos test environment and obtain independent technical/reader
review. Hosted CI needs a selected provider and repository remote. No new native
work or repeated Linux run can substitute for those requirements.
Evidence: `docs/evidence/linux-offline-reload-2026-09-07/`.
