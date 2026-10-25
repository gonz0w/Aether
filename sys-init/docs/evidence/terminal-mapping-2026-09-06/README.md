# Terminal mapping evidence — 2026-09-06

Decision 0046 / BG-058. Seven new model cases cover qualified terminal projection,
distinct stopped cause/detail, cleanup before retry, cancelled intent, same-cut
readiness, stale/duplicate observations and invalid input without mutation.

Commands from the repository root:

```sh
python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-terminal-mapping-20260906.json > /private/tmp/sys-init-terminal-mapping-20260906.log 2>&1
python3 scripts/check-runtime-model.py --output docs/evidence/terminal-mapping-2026-09-06/model.json > docs/evidence/terminal-mapping-2026-09-06/model.log 2>&1
python3 scripts/check-all.py
git diff --check
```

Both model runs passed 197 tests and 19 distinct mutation controls, including the
stopped-kind omission. Each ran 100 seeded traces and a 1,000-trace benchmark.
Between runs only the new invalid-stopped diagnostic was made specific while
preserving the existing invalid-exit diagnostic. initial-source/ retains that
first model source; other initial model inputs match source/. All initial and
final report source hashes were verified. No failed attempts occurred.

validation/ retains run-vxg_mfm5, all eight offline gates passing, including
197 model tests, 48 host tests and 37 harness tests. sources_unchanged is true.
Decision/planning validation notes were appended afterward; executable model
inputs remain byte-identical to their passing report. source/ retains affected
tracking documents and executable model inputs. SHA256SUMS.json covers all bundle
files other than itself.

This is trusted Python fixture evidence. The terminal projection performs no
native calls, authentication or lifecycle mutation; the driver explicitly submits
the event. Terminal evidence requests reclaim but does not prove cleanup. The
integration test supplies a separate synthetic cleaned observation for all model
resources. It does not derive that observation from native reclaim alone.

BG-058 still needs complete driver resource accounting, a no-target cleanup path
for confirmed pre-admission launch rejection and fresh consuming native witnesses.
Unknown-result recovery remains unsupported. No native code, shared release bytes
or consumer pins changed; no fresh native execution was performed.
