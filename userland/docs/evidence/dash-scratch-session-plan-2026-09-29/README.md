# Scratch session handoff preparation — 2026-09-29

UL-007. **Consumer workload ready; native SCRATCH-SESSION-01–06 NOT RUN.**
The [contract](../../../experiments/dash-native/SESSION-SCRATCH.md) pins the complete
script,52-byte stdout,19-byte stderr, stale-data/protected-object seeds and unchanged
helper. It checks truncation, shared-offset aliases and surviving last alias, denied
write, reopened reader/EOF, then healthy argv/pipeline, descriptor closure, unchanged
parent PID and working parent stderr. Native execution repeats three fresh domains.

Original script passes `/bin/dash -n` and ShellCheck with the declared dash dialect.
All11 explicitly relocated host references pass on the recorded non-root macOS host:

| Reference | Observed shell result and checked state |
| --- | --- |
| Positive | exit0, exact52/19-byte streams, scratchAB, protected bytes unchanged |
| Lost B | exit0 but scratchA and stdout fail the ordinary oracle |
| Separate writable offsets | exit0 but scratchB and stdout fail the ordinary oracle |
| Skipped truncation | exit0 but retained stale suffix and stdout fail the ordinary oracle |
| Protected write allowed | exit64, no output; protected mutation recorded and rejected |
| Denied command skipped | exit64, no output; protected bytes unchanged |
| Missing reopened reader | exit65 after denied prefix; scratchAB remains |
| Wrong WITNESS | exit66 after denied/AB prefix |
| fd3 leaked to closure helper | exit68 after healthy pipeline prefix |
| Corrupted pipeline byte | exit0 but exact-output oracle rejects |
| Parent stderr closed | exit70, pre-diagnostic stdout prefix and empty stderr |

Host protected-file mode0444 is a reference fixture, not native capability evidence.
Only /inputs/ and /scratch/ prefixes are relocated under the private build root;
mutants have separately retained derived script bytes. No original target path is
created/executed and no real-prefix installation occurs. Reopened-reader failure
mutant additionally closes only that failed command's stderr to keep its expected
reference output independent of diagnostic path spelling.

Pinned Clang21.1.8 C17 builds the unchanged helper with an absolute hashed host
linker, recorded SDK metadata and separate clean build environment. Script PATH
remains /nonexistent. Owned commands have30-second bounds and16MiB streams; all
exits and process cleanup are checked. Source/tool/input hashes remain unchanged.
No failed or incomplete attempt preceded the passing run. Exact process receipts,
fixture before-state, after-state bytes, derived scripts and results are retained.
No new sanitizer, minimum-Python-version or native qualification is claimed.

Native expected work is21 copies,15 helper replacements,18 image admissions and24
terminal/reclaims across three parents. Existing slot reuse appears to reach15;
owner identity/binding/channel/description reconciliation and new linked code/stack
review are required. Retire scratch descriptions before pipe use; do not turn file
selectors into pipe grants or silently widen resource/observation bounds. The
protected object must stay unchanged; seed/reset is explicit fresh-domain setup,
not persistence. Parent-stderr denial must use actual native wrapper/close outcomes,
which may differ from the host script70, as earlier native evidence demonstrates.

Next: owner implementation and sealed complete delivery with malformed, denied,
stale/retained-description, output and cleanup controls; then independent native
replay. Existing scratch component, SESSION/recovery/failed-exec acceptances remain
unchanged. SI-07, real serial composition, shared SDK, reader reviews and full M3/R1
stay open. Final local gates and prior-seal checks are in final-checks.json.
