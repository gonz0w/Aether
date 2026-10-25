# Standards termination — 2026-09-07

Decision 0124 / BG-056. Focused commands: python3 -m unittest discover -s tests -p
`test_harness_standard*.py` (20 tests) and `test_harness_offline_locks.py` (4).
All ten gates pass with `python3 scripts/check-all.py` in run-81w8wpg7; exact
commands/source hashes are in validation/results.json. All test/render attempts
passed. No native execution or runtime behavior change is claimed.

Three new tests exercise all wrappers: real SIGTERM after a staged child publishes
its PID/path; previous custom-handler restoration after success/timeout; and
background-thread capture with no signal-handler calls. The real subprocess cases
require exit 130, exact plain stderr, empty stdout, a reaped child and removed
private staging root. Synthetic children and wrappers run only in private fixtures.
Twelve manual lint/terminal/HTML commands pass.

SIGTERM maps to KeyboardInterrupt only after Popen during main-thread capture.
Secondary SIGTERM during capture cleanup is ignored. The previous handler is
restored before output replay and temporary-directory unwinding. SIGTERM in
startup, staging, postchecks, restoration windows, or repeated signals may still
bypass cleanup; SIGKILL and escaped descendants remain outside the guarantee.
The CLI also handles ordinary KeyboardInterrupt with exit 130. No OS sandbox,
complete process containment, blocked-I/O deadline or independent approval follows.

All three released reference stdout streams match decision 0123; lock bytes and
24 native input hashes are unchanged. RC1 remains unpublished. Source copies and
scoped diffs record this slice within the pre-existing dirty checkout. Independent
reader/HTML visual/narrow-layout publication review remains pending. Remaining
termination limits stay recorded; next local work is native catalog reference.
