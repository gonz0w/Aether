# Inner host/model capture evidence

Decision 0109 adds bounded_capture.py for two-stream worker capture. Both
callers keep their 30-second deadlines, now through pipe drain and direct-child
exit, and accept at most 4 MiB of combined raw output. The helper preserves
separate stream order, default host text decoding and universal newlines.
Actual nonzero statuses remain distinct from timeout/overflow exceptions.

Eight focused tests pass. Real child cases cover exact combined byte budget,
nonzero status/newline handling, each overflow stream, concurrent flooding,
timeout after pipe closure with retained prefixes, and missing tools. A synthetic
KeyboardInterrupt at selector wait uses a real child and verifies it is reaped
and both pipes closed. Host integration substitutes a real overflowing worker
and verifies failure with no stdout summary. Model integration injects an
OutputLimitError and checks the exact passed/error failure shape and prefixes;
that injection is not a real overflowing model computation. Full gates execute
both real normal workers. Three extra raw capture probes retain exact accepted
bytes and outcomes in capture-receipts.json.

All ten gates pass in out/checks/run-sr4k1ikf, retained in validation/. The earlier
pass before the coverage-inventory addition is retained in validation-initial/.
Model tests, pass flag, complete negative-control records and scenario counts
match decision 0108's run; host summary keys, profile and test count also match.
Benchmark times and source identities are expected to differ. Helper hashes
are included in both successful source maps. See review.json for comparisons.

Both manuals lint cleanly and render at 78/60 columns and HTML. An initial model
manual long-input-line STYLE notice is retained in manual-initial/ and corrected.
A first tool patch was rejected for escaping before the test file was created;
it did not change source or produce a test attempt. No failed test/check run
occurred. HTML visual review, independent technical/reader approval and installed
target lookup remain pending.

All 24 native source inputs match the retained boundary-review manifest. No
native behavior, compiler helper, native runner, release pin, vendored release
or sibling changed. There is no new native execution claim. Tests establish the
identified host capture boundary only, not native or production conformance.

Host timeout/overflow replays diagnostic stderr prefixes and discards partial
machine stdout; it has no standalone retained directory. Model errors keep
passed/error fields and include bounded raw-prefix detail with replacement
decoding inside error. Successful report shapes and normal command streams stay
unchanged. Existing internal developer-output exceptions remain in force.

Capture exceptions kill the owned group and reap the direct child. Abrupt outer
termination and detached nested groups remain unresolved BG-056 ownership work.
The byte cap does not limit worker allocations before emission, decoding copies,
child-created artifacts or all process memory. Remaining work includes nested
cleanup, other resource limits, record/API references and independent review.
