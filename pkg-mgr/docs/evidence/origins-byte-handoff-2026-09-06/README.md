# OC-H1 host byte-handoff evidence

2026-09-06. The executable test is tests/origins-source-handoff.py. It runs the
exact pinned origins exporter in fixtures/origins-exporter, then the existing
pkg-mgr verify-source command against a synthetic externally pinned binary payload.
No sibling checkout is executed or required. Original fixture retains its LICENSE.

Attempt 01 failed private-root initialization because the new harness omitted the
required DISTFILE environment variable; its inputs/commands/errors are preserved.
Attempt 02 corrects that setup and passes 13 cases. Each case preserves package
sentinel names/modes/bytes, absence of test trust state and stored object identity.
These are controlled private host observations, not confinement or real installed
package qualification. Producer partial/complete-output failures are deterministic
injected children, not a claim of physical interruption/durability coverage.

Run python3 tests/origins-source-handoff.py from the checkout. The printed retained
.pkg-mgr-live-origins-* directory contains raw stdout/stderr, inputs.json, result.json
and private state/store outputs. Every child has a 10-second timeout. No network,
make, archive extraction, recipe or install command is executed. The frozen shell
wrapper execs Python; injected children spawn no descendants. The normal host gate
runs the test under its existing 600-second process-group watchdog.

Inputs record producer/input hashes, consumer/harness hashes, available executable
identities, Python and platform. Python's standard library and shared libraries
are not a complete hermetic bootstrap closure. Same-UID hostile writers and physical
storage failure are outside the inherited exporter fixture assumptions.

Cases: exact export, retry, same-size corruption, truncation, extra byte, partial
producer failure, complete-output producer failure, missing exporter, absent hash
tools, symlink root, FIFO input, dot-component root, identical put. Required tools
missing outside deliberate negative cases fail the test. Timeouts cannot pass as
semantic rejections. Package sentinel content is explicitly synthetic, not an
invented valid installed record. New source records/TUF/time/base admission and
native Aether remain unimplemented. Full-suite results are recorded separately.


Final validation: sh tests/check.sh exits 0. All sixteen shell fixture scripts,
13 OC-H1 cases, required lint/standards/watchdog/manual checks pass. The compiler
manual example is not selected by the ordinary suite and remains explicitly NOT RUN.
Attempt 03 retains the actual integrated OC-H1 inputs and results; suite.log and
result.txt preserve the full run. Native/TUF/power-loss tests were not run or claimed.
