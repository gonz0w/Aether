# Active aggregate termination evidence

Decision 0111 installs a temporary SIGTERM-to-KeyboardInterrupt handler during
main-thread gate capture, after Popen succeeds. Existing cooperative cleanup
then runs and the gate returns interrupted. The aggregate's existing mapping
uses exit 130. SIGTERM is ignored during cleanup and the previous disposition
is restored afterward. Background-thread calls do not install global handlers.
No new report schema, flags or normal stream behavior is introduced.

Three focused tests pass: a real SIGTERM after nested-worker readiness, handler
restoration after success/timeout, and background-thread behavior. The signal
probe invokes actual run_check in an owned Python process and applies the
aggregate's interrupted exit mapping; it is not a full ten-gate CLI invocation.
Its wrapper records the separate worker's negative returncode and closed pipes
before exit. Two prior cooperative-cleanup tests and twelve aggregate-runner
tests also pass. All seventeen are included in full gate discovery.

termination-comparison.json and before-default/after-default/ retain exact
before/after outcomes using the old runner source and current runner. With the
default SIGTERM disposition the before process exits -15 with no result; the
current probe exits 130 with interrupted result, restored handler and nested
cleanup receipt. The fixture cleans its owned surviving sessions in the failed
before case. No host services or unrelated processes are targeted.

Initial test development produced a default-argument typo in the shared fixture,
recorded in initial-test-import-error.log. It was fixed before runtime changes.
The initial custom-handler baseline returned 143 instead of 130; that failure
and the subsequent passing custom-handler test remain retained. The final
comparison and tests use SIG_DFL to demonstrate ordinary termination behavior.
These earlier artifacts are not substituted for the final default-signal witness.

All ten repository gates pass in out/checks/run-pe9urad8, retained in validation/.
Manual lint, 78/60-column output and HTML generation pass; terminal output fits
the requested widths. Independent technical/reader review, HTML visual review
and installed-target lookup remain pending. All 24 native inputs and the inner
capture helper match their retained source references. No native runner,
compiler helper, release pin, vendored release or sibling repository changed.
No fresh native execution is claimed for this host-only change.

Coverage is limited to active main-thread gate capture after process creation.
Startup/Popen windows, between-gate hashing/report work, SIGKILL, repeated SIGINT,
unresponsive detached descendants, deep ownership chains and pipe-pressure
fallback remain outside the guarantee. This is not complete process containment
or a promise of a final report under arbitrary termination. These limits and
remaining record/API coverage stay under BG-056. Candidate standards remain
unpublished; published release pins stay fixed.
