# UL-072 / UL-063 quality process ownership

Scope: quality checker and standalone local release wrappers. Reuse the existing
experiments/command-runner/process.py unchanged; no new process supervisor or
runtime dependency. CP-01–03, CE-02/04/06, TE-01–05 and E-01–08 apply.
Pins must be verified before release code executes. Preserve version/help,
0/1/64 outcomes and raw success/NOT RUN marker bytes. No native changes.

Each reference execution gets an owned session, 30 or 60-second deadline,
16 MiB output-file bounds, explicit trusted Python and minimal PATH/LC_ALL/TMPDIR
environment, empty stdin, and retained build-root receipts. Replay each stream
only after process cleanup; do not merge stdout/stderr. Failure, timeout, leftover
descendants or unresolved cleanup must fail. Parent quality calls trusted local
wrapper entry points directly so wrapper child sessions are never nested under a
second killable owner. Copied validators retain their own byte verification.

No claim to contain hostile children that escape their session, SIGKILL of the
owner, or a total in-process validation deadline. Require POSIX host primitives.
Document changed child environment and delayed reports. Retain original wrapper
source and all attempts. Review sources, then test actual subprocess success,
nonzero, missing executable, timeout with descendant, leader-exit descendant,
output bound, hostile environment and wrong-pin no-execution. Preserve original
failure in receipts even if output replay fails. Use the existing process controls
and complete quality/CLI/manual regressions. Test 3.14 and installed 3.13; absent
minimum-version runtimes remain pending, not inferred from syntax.

Current-task technical review is not independent review. UL-061/071 manual visual,
reader and packaged lookup remain blocked separately. No sibling changes or
release-pin migration. All new original code BSD-2-Clause.
