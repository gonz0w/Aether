# 0013: Complete bounded host readiness ordering evidence

Accepted 2026-09-05 for BG-040/BG-054. Decision 0003 retains the six-byte READY
newline-terminated first frame. Its rationale disposes of the older request to
implement two formats for this fixture: a versioned payload has no additional
consumer requirement here. This is a scoped design comparison, not an executed
versioned-parser comparison or selection of a production protocol. Preserve the
current wire bytes and ownership model.

Add real-child/pipe tests for early notification before Popen returns to adapter
registration, readiness just before/at/after the startup deadline, notification
after accepted stop, and a retained old writer during replacement. Use bounded
file handshakes to establish writes and injected adapter time for exact deadline
cuts. Do not infer ordering from sleeping for an arbitrary duration. Direct
children remain owned and reaped; extra test-owned descriptors are closed.

The deadline oracle must admit only the before-deadline case. Stop closes model
admission even if transport bytes arrive later. Reclaim closes the old reader;
an old retained writer must get EPIPE rather than affect the replacement. A
synthetic stale-generation event also must not release the new generation; label
that event injection separately from the real pipe behavior.

Run relevant host/model/harness/standards checks and a deadline-boundary negative
mutation. This is trusted macOS evidence with exclusive waiting, not all POSIX
hosts, PID-authenticated notification, crash containment or native clock behavior.
BG-040 remains partial for cross-host and wider protocol/authority acceptance;
health, external probes and graph-revision behavior stay with BG-041/BG-042.
