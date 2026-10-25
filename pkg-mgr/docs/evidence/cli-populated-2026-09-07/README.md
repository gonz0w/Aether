# Populated CLI state witness

2026-09-07 UTC. The package-state fixture registers base/app/spare through the real
state helper, with app depending on base and app selected in world. A new Python
test compares seven read-only CLI views to real helper bytes/status and independent
expected list/dependency/orphan rows. Base files include a path containing spaces.
Missing package and permission drift require exact status 1 and exact error/report.

Before and after every helper and CLI call, entry paths/types/modes and regular-file
hashes must match. The deliberate permission mutation is restored in finally; the
whole fixture snapshot must match its initial value afterward. No timestamps, race,
power-loss or native guarantees follow. This adds tests only, no runtime changes.

Selected checks: development inventory, changed-shell lint, pinned standards,
coverage controls and fresh full sh tests/check.sh under its 600-second watchdog.
Wrong views, lost failure statuses, changed payload/records or missing completion
are forbidden. Retain exact dirty inputs and every attempt. Controlled fixture
packages do not establish production installation or real-prefix authority.

Result: all nine populated-state cases and the full suite passed in
214.1 seconds. Both exact completion markers appeared once.
All executable/fixture names, sizes, hashes and modes remained unchanged from
inputs.json. This is real-helper execution on a controlled host fixture; human
rendering and native installation/persistence remain outside the claim.
