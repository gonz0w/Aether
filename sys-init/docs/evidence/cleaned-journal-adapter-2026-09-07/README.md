# Cleaned journal adapter — 2026-09-07

Decision 0162 integrates Cleaned admission with the actual lifecycle model and
journal. It retains the exact reclaim token emitted by Terminal and requires its
executed disposition independently of a fresh, exact-source resource inspection.
Reader, writer, worker and wait ownership must all be empty, with no unresolved
cleanup. All cut members are preflighted before model mutation. Completion leaves
the same generation unowned with cleanup complete and no deadline; exact receipt
replay neither inspects nor applies again. Retry policy can schedule a future
attempt but this fixed-time cut does not launch a replacement.

All 280 model tests pass, including nine Cleaned tests and two source omission
controls. All ten local gates pass in `run-wpld9nvb`, with unchanged checked
inputs. All twelve native consumer sources, three release locks and catalog bytes
match the preceding checkpoint. Resource inspection and executed acknowledgments
remain trusted synthetic inputs; this is actual policy-model/journal integration,
not native resource disposal. No independent reviewer sign-off is claimed.

Next BG-057: combine the actual three-phase journal adapter with pending release
and retirement, including mixed cuts. BG-058 retains native provenance/disposal;
BG-060 retains sustained reuse and BG-033 recovery. The 185-case native checkpoint
and BG-056 producer source-closure limitation remain unchanged.

`source/` and `sources.json` retain checked adapter/runtime/model/test/runner inputs.
`validation/` and `checks.log` retain the full local run. `model-fast.log` retains
`python3 -m unittest discover -s tests -p test_runtime_model.py` against the same
model/test sources before the runner source-list/documentation updates.

Source omission controls separately remove executed-reclaim and empty-resource
checks, requiring named assertion failures. Positive tests include two-member
completion, exact replay and a scheduled future retry. Denials cover all resource
positions, malformed/foreign inspections, unresolved cleanup, incomplete/rejected
reclaim, stale generation, callback failure/reentry and a missing transition.
No native resource operation or arbitrary service executes in these fixtures.
`sha256.json` seals the package; native evidence and release pins are unchanged.
