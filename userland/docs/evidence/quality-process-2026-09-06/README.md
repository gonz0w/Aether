# Quality process ownership — UL-072 / UL-063

The quality command and standalone release wrappers now use the existing
command-runner process helper through a small local adapter. Each trusted
reference execution owns its session, bounded output files, deadline and cleanup.
Nonzero exit, timeout, surviving descendants or unresolved cleanup cannot pass.
The top-level quality command calls local wrapper entry points directly to avoid
nesting session owners. Release bytes are still verified before reference code
runs. No release pin, native code or sibling repository changed.

Reference output is retained separately and replayed after cleanup; stdout and
stderr bytes/markers remain unchanged, with no cross-stream ordering promise.
Children use the same absolute Python with -B, fixed PATH/LC_ALL and a private
TMPDIR; arbitrary parent environment variables are no longer inherited. Inputs,
outputs and receipts stay in build/quality-process-*; there is no automatic pruning.
The manual and source-bound command record describe this deliberate host behavior
change. Shell wrappers are not added and there is no new runtime dependency.

## Tests and review

Eight unittest methods execute ten real process cases on both Python 3.14.7 and
the installed Python 3.13 interpreter: separate raw streams, nonzero, missing
executable, timeout with descendant, leader exit with descendant, output bound,
hostile environment and wrong-pin no-execution for all three standalone wrappers.
The 16 CLI/manual regression invocations pass with the new implementation.
See final-controls.stderr, final-313.stderr and manual-regression/results.json.

All started case groups were checked absent and cleanup complete. Missing
executable fails before a group or output files exist; the initial test incorrectly
expected those files and failed. Its source and diagnostics are retained under
attempt-1; the corrected test requires empty replay when files were never created.
The original process helper source was not modified.

The large output-limit payloads remain in their owned build directories. Exact
paths, sizes and hashes are in retained-artifacts.json; small streams and process
receipts are copied here. This is explicit local retention, not durable artifact
storage. Do not discard those build outputs before a reviewed retention handoff.
Final check results and current source/tool identities accompany this packet.

Current-task technical review checked verification-before-execution, un-nested
ownership, error propagation, byte-stream separation, minimal environments and
retention before replay. Python 3.10 grammar passes but 3.10/3.12 runtime checks
remain unavailable. No native or whole-repository coding compliance is inferred.

## Remaining boundaries

This is cleanup for trusted POSIX children that remain in their owned session.
It is not a sandbox for malicious session escape. Uncatchable owner termination,
all interruption schedules and a total deadline for in-process validation are not
qualified. A broken output consumer can abort replay, but original receipts and
bytes have already been retained. Independent technical review is still pending.

The source/manual coverage is implemented and host-tested; UL-063 remains open for
minimum-runtime and independent review plus broader source migration. UL-071 still
needs HTML browser visual review, independent reader review and packaged lookup.
The browser previously rejected local file URLs; no workaround is introduced here.
