# Cooperative aggregate cleanup evidence

Decision 0110 gives a failing aggregate gate one second of cooperative SIGINT
before forced cleanup of the remaining owned group. This lets responsive Python
wrappers unwind and clean workers they started in separate groups. Gate records
add cleanup_grace_seconds; the original failure classification remains. The
extra second is a cleanup allowance after the command deadline. Accepted log
prefixes remain bounded and output is not newly drained during the grace.

The new two-case regression was run before implementation: the ignored-interrupt
case passed, but nested cleanup failed because the wrapper could not record
having reaped its worker. The old runner was then exercised separately using
its exact retained before/ source. before-probe/ and nested-comparison.json
retain readiness and the timeout with absent cleanup receipt. The probe's own
finally cleanup killed the deliberately orphaned owned worker session.

With the change, both new tests and all twelve prior aggregate-runner tests
pass. after-probe/ retains the wrapper's cleanup receipt: its separate-group
worker has a negative returncode and both pipes closed before wrapper exit.
The aggregate still classifies the operation as timeout. A separate real child
ignores SIGINT and is killed by forced fallback within the test's three-second
bound, using a 0.3-second command deadline and one-second grace. These witnesses
qualify the responsive aggregate -> capture wrapper -> worker chain, not
arbitrary descendant trees or complete cleanup for every gate.

All ten repository gates pass in out/checks/run-zayzuf8u, retained in validation/.
The helper and both host/model callers match decision 0109's source copies; all
24 native source inputs match the prior boundary-review manifest. No compiler
helper, native runner, native implementation, release pin, vendored release or
sibling repository changed. No fresh native execution is claimed.

The updated manual lints cleanly and renders at 78/60 columns and HTML. Initial
two input-line STYLE notices remain in manual-initial/; only line wrapping was
corrected after the full checks. Independent reader/technical approval, HTML
visual review and installed-target lookup remain pending.

Forced fallback guarantees only the existing owned group operation and direct
child reap. Unresponsive detached descendants, abrupt aggregate termination,
deeper wrappers that force-kill intermediate owners, repeated interruption
and blocking filesystem operations remain outside this result. Pipe pressure
can prevent cooperative exit before fallback. SIGINT responsiveness is an
explicit trusted-wrapper condition, not a containment mechanism. BG-056 retains
these limits plus remaining record/API and resource review work. Candidate
standards remain unpublished and release pins stay fixed.
