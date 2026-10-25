# Transaction semantic-oracle strengthening

Test-only change, 2026-09-07 UTC. No package runtime, pin or sibling changes.
Five replacement interruptions must return a shell signal status resolving through
POSIX kill -l to KILL and emit no completion receipt before retry. Stale payload
must independently produce exactly size-mismatch/app/app from state verification
in a disposable probe copy; finish remains status 1 with empty output/diagnostics.
Changed world must return 1, empty stdout and its exact existing error diagnostic.
Both stale attempts must preserve all target file paths, hashes and ordinary modes
and must not displace payload. Probe authority is moved only within test-owned roots.

Forbidden outcomes: generic nonzero substituted for signal termination, wrong
rejection reason, false completion or changed target bytes/modes. Existing positive
recovery assertions remain. This does not prove directory metadata, hostile races,
power-loss durability or all shell implementations. The runtime deliberately
suppresses the shadow verifier report; this test does not invent a new diagnostic.

Selected checks: all pinned standards, changed-shell ShellCheck 0.11.0, development
inventory and full sh tests/check.sh with its 600-second owned-group watchdog.
Exact dirty-tree input manifest, every attempted log/status and final checks are
retained here. No old run is substituted for this changed fixture execution.

Result: full suite passed in 216.0 seconds, within its
600-second deadline. Both transaction and whole-suite completion markers occur
exactly once. All selected source-tree names, sizes, hashes and modes remained
unchanged from inputs.json. This is one host execution; no native, independent
review, all-shell or publication qualification is claimed. The prior mapping
evidence is historical and unchanged; current case definitions supersede its two
identified assertion gaps within the limits above.
