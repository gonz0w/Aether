# Granted virtual clock and actual timed conditions

`contract.md` records the preimplementation ABI and virtual-time limitations.
0x2800e adds only pair-mode, thread-grant-checked delivered-tick observation;
the user-space fixture converts it to a declared virtual CLOCK_MONOTONIC.
No realtime/calibration/suspend/full-POSIX claim or supervisor-ABI change.
The conversion uses a fixed 10-ms quantum and accepts private relative waits
only up to one second, rounded upward. Existing native deadline and pin cleanup
semantics stay intact. Long/general durations are outside this fixture facade.

Two actual musl conditions exercise timeout, notification, mutex reacquisition,
expired and invalid deadlines, rejection of realtime and wrong/reserved authority,
cleanup and supervised replacement. Frozen adapter time must fail exact status
271 even though native waits complete; pair-disabled query must fail exact 274.
Existing future timed/cancelled/detached lifecycle requirements remain separate.

Attempt 1 failed C compilation under -Werror due to signed/unsigned thread-ID
comparison. The explicit unsigned conversion matches the validated native ID;
no warning suppression was added. That build failure and snapshot are retained.
Final suites keep runtime inputs frozen; the complete older lifecycle cases remain.
Kernel changes require fresh memory, raw-pair and M4 coverage, not reuse of old
kernel hashes. The final host and auxiliary suite receipts record this selection.

Reproduce lifecycle with `python3 scripts/thread_smoke.py --pthread-lifecycle`
and `--large`, using the SDK/tools arguments recorded in each log/receipt.
Auxiliary commands are retained in the qualification receipt. Every suite has
owned outputs, bounded builds/VM execution, source snapshots and raw semantic logs.
Independent consumer acceptance, physical time, full engine and release readiness
remain open. Next: detached completion/reaping contract and bounded cleanup,
then measured engine budgets; do not silently broaden this fixture's time facade
for libzpool wall-clock calls.

Final qualification passes 122 target cases: 70 lifecycle, 20 raw pair,
25 memory and seven M4 cases. All 98 Python tests and Zig host checks pass,
as do format/workflow/diff checks. Final runtime source hashes remain unchanged
through the selected suites; `final-sources.tar.gz` retains those inputs. The
only failed attempt was the preserved initial warning-as-error compile failure.
