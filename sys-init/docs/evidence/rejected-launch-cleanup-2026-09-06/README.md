# Rejected launch cleanup evidence — 2026-09-06

Decision 0047 / BG-058. The trusted fixture retains reader and writer ownership
following a confirmed pre-admission launch rejection. Both must close before
local reclaim qualifies, and its executed acknowledgment precedes cleaned.

Commands run from the sys-init repository:

```sh
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-rejected-cleanup-20260906.json > /private/tmp/sys-init-rejected-cleanup-20260906.log 2>&1
python3 scripts/check-runtime-model.py --output docs/evidence/rejected-launch-cleanup-2026-09-06/model.json > docs/evidence/rejected-launch-cleanup-2026-09-06/model.log 2>&1
python3 scripts/check-all.py
git diff --check
```

Initial model run: 205 tests and 20 mutation controls passed. Final run adds a
reclaim-identity/duplicate-rejection test: 206 tests and 20 controls passed. Both
include 100 seeded traces and a 1,000-trace benchmark. No failed runs occurred.
initial-source/ retains the earlier test file; all other model inputs match source/.
Every initial and final source hash was verified against those copies.

validation/ retains run-k_wjrcd4, with all eight offline gates passing: 206 model
tests, 48 host tests and 37 harness tests. Its sources_unchanged flag is true.
Final validation notes were appended to the decision and planning state after
that run; executable model inputs remain unchanged. source/ retains model inputs
and affected documentation/tracking. reviewed/ and reviewed-files.json retain the
producer and adapter source evidence: the existing native invalid-slot probe is
local validation, not a fresh kernel-rejection cleanup witness.

Only the fixed rejected-launch profile with two supervisor endpoints is covered.
Endpoint IDs and supplied return records are trusted synthetic inputs, not proof
of authority or real cleanup. No native reclaim is applied in the model's retry
trace. A successful-launch inventory, waits/helpers/devices, complete driver
composition and fresh native consuming witnesses remain outside this result.
Unknown launch and unknown local reclaim remain unresolved and owned.

No native source, shared standard release or pin changed. No fresh native run was
performed. SHA256SUMS.json covers every retained file except itself.
