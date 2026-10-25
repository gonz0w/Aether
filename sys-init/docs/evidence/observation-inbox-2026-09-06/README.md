# Observation inbox evidence — 2026-09-06

Decision 0041 adds opt-in QueuedRuntime: four immutable complete cuts, bounded
retained payloads, separate FIFO application, command ordering and sticky overflow
closure without dropping accepted data. Unknown acknowledgments remain unknown;
queued terminal evidence does not clear obligations or release lifecycle ownership.
Model's existing validation is extracted into a pure method shared with intake;
only the new inbox imposes the narrower retained integer/string-type bounds.

Commands from `/Users/cam/DEV/sys-init`:

```
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-observation-inbox-20260906.json > /private/tmp/sys-init-observation-inbox-20260906.log 2>&1
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-observation-inbox-final-20260906.json > /private/tmp/sys-init-observation-inbox-final-20260906.log 2>&1
python3 scripts/check-all.py
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-observation-inbox-bounded-20260906.json > /private/tmp/sys-init-observation-inbox-bounded-20260906.log 2>&1
python3 scripts/check-all.py
git diff --check
```

`initial-model` retains 164 passing tests and fifteen controls. `pre-bound-model`
retains the same tests after precomputing the next intake serial before enqueue.
`pre-bound-validation/` retains the first passing full run, `run-mhbd3z6p`.
Review then added explicit retained integer/string-type limits and a ninth test.
`model.json` / `model.log` retain the final 165 tests and fifteen distinct controls.
No failed implementation test runs occurred; earlier successful attempts remain
unchanged and do not claim coverage of the later payload bounds.

`validation/` retains final full run `out/checks/run-kufx87bj`: 165 model tests,
fifteen controls, 48 host tests, 37 harness tests and all offline adoption/quality/
native evidence audit gates. Native execution was not rerun. `source/` retains
final report inputs and affected adoption/planning documents. Earlier changed
inputs are in `initial-source/` and `pre-bound-source/`; unchanged inputs share the
final source copy. Every model report source hash was verified against these files.
Final Markdown result notes were added after full checks; tested executable
sources and quality inventory were unchanged. SHA256SUMS.json covers every
retained file except itself. Historical bundles and vendored releases were unchanged.

This establishes trusted model retention, not native buffering, real-time progress,
authenticated observations or reconciliation. On overflow the incoming fifth cut
is unaccepted and caller-owned; the four accepted cuts remain retained and the
owner closes. BG-033/BG-032 next require exact producer evidence before any unknown
obligation can be released. BG-057 retains that policy and control composition.
