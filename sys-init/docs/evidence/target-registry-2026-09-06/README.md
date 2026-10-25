# Target registry evidence — 2026-09-06

Decision 0045 / BG-058: trusted Python target reservations, independent native and
service generations, typed terminal facts and reclaim/retirement ordering.

Commands run from the sys-init repository:

```sh
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-target-registry-20260906.json > /private/tmp/sys-init-target-registry-20260906.log 2>&1
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-target-registry-final-20260906.json > /private/tmp/sys-init-target-registry-final-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

Initial run: 189 tests and 18 distinct mutation controls passed. Final run adds
one cross-slot independent-generation test: 190 tests and 18 controls passed.
Both ran 1,000 seeded traces. No failed runs occurred. The initial test source is
under initial-source; all other initial executable inputs match source/. Both
reports' source hashes were verified against these retained copies.

validation/ retains full run-wu0mnkx4: all eight offline gates passed, including
190 model tests, 48 host tests and 37 harness tests. Its sources_unchanged flag is
true. Final validation notes were appended to the decision and planning state
after that run; executable model source hashes remain unchanged. Existing Model,
EventJournal, JournalRuntime, ResultApplier and confirmed-result sources also
match the prior result-applier bundle.

These are trusted fixtures with synthetic owner identity and producer hashes,
not native execution or authenticated producer evidence. The selected fault
projection covers #UD only. Registry bookkeeping neither invokes native calls
nor automatically applies Model observations. Lifecycle mapping, failed-launch
cleanup and fresh consuming native witnesses remain under BG-058. No native
execution was rerun; shared pins and native implementation remain unchanged.

source/ retains final model inputs and affected decision/tracking documents.
SHA256SUMS.json covers every retained file except the manifest itself.
