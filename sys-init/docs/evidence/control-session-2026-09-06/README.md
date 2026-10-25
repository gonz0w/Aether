# Control session ownership evidence — 2026-09-06

Trusted deterministic model execution on macOS arm64. No process/native control
transport, authentication or restart recovery is established. The external
boundary document is a proposal; only the one-facade lifetime guard is implemented.

Commands from the repository root:

- `python3 -m unittest discover -s tests -p test_runtime_model.py`: before.log
  records 52 tests with three expected missing-guard assertion failures.
- `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-session-model-20260906.json`:
  model.json records 52 passing tests and three caught lifecycle mutations.
- `python3 scripts/check-all.py`: validation/results.json and raw logs record
  52 model tests/three controls, 48 host cases, 37 harness cases and all offline
  standards, quality and retained native checks passing. Native audit covers 215
  historical outcomes and is not a fresh target run.

An intermediate post-fix test failed because deepcopy of an instance-bound method
compared a copied receiver identity. test-oracle-failure.log retains the failure.
The test now removes the temporary method override before comparing state. This
was an oracle correction; no runtime workaround was needed. The initial pre-fix
log predates that correction; all three failures were missing guard assertions.

source/ retains the final source, specification and planning checkpoint. The
full-run source hashes identify exactly what ran; final Markdown result notes
were added afterward. No hashed implementation or quality-inventory input changed
after the successful full run. Runtime source hashes in model.json match source/.
SHA256SUMS.json binds every retained file except itself. Previous bundles are
unchanged. This review supplies no independent owner sign-off or production claim.
