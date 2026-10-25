# Legacy runner command bounds evidence

Decision 0107 adds bounded, retained command capture to lifecycle and native
supervision harnesses. Actual nonzero exits reach the existing semantic oracles;
timeout, overflow and infrastructure failure raise separately. The helper now
accepts cwd; legacy builder defaults remain unchanged. Receipts add cwd and
record command, caller/helper identities, bounds and outcomes. Lifecycle client
builds retain merged output and replay it on stdout only after success.

Six focused host tests pass: recorded and CompletedProcess-style calls cover
success, real nonzero exits, working directory isolation, timeout, 128-byte
accepted overflow prefix and missing tools. All ten repository gates pass in
out/checks/run-rzmxebis; final logs and source hashes are retained in validation/.
The earlier all-gate pass is retained in validation-initial/.

Verified retained producer sources before execution: 753 lifecycle and 3,284
supervision files, with zero mismatches (producer-checks.json). Fresh QEMU
execution passes three lifecycle and five supervision cases. Expected negative
cases preserve actual smoke exit 1 and their existing semantic markers.
comparison.json confirms every client envelope matches its earlier retained
profile. This does not assert identical ISO bytes. All 24 native source inputs
also match the preceding boundary-review snapshot; no native behavior changed.

The first lifecycle attempt failed before boot because the host sandbox denied
QEMU's Unix control socket. Its logs, partial results and receipts remain in
lifecycle-socket-failure/ and lifecycle.stdout/stderr. The unchanged command was
retried in a new private workspace with approved sandbox escalation for the
local socket, then passed all three cases. Commands include both attempts.
No host service installation or sibling repository modification was performed.

The lifecycle/ and supervision/ directories retain results, command receipts,
source manifests, clients and serial logs. Full producer trees, dependency
caches, ISOs and framebuffer images remain in the named temporary workspaces;
they are not included in this compact bundle. Their recorded hashes are not
claims of archival availability. Original producer evidence remains separate.

Both updated manuals lint cleanly (exit 0) with the recorded local mandoc and
render at 78/60 columns and as HTML. Initial sentence-format warnings and their
renderings are retained in manual-initial/. Terminal output fits the requested
widths; independent reader review, HTML visual review and target lookup remain
pending. No independent technical approval is claimed.

Cleanup covers the owned group of non-detaching children. Nested builders start
independent compiler groups; an outer interruption does not prove their cleanup.
This composition gap remains under BG-056, along with other runner bounds and
record/API documentation. Copy/hash time is outside command deadlines. Results
establish these host and x86-64 QEMU profiles, not containment, production init,
physical hardware, SMP or general POSIX conformance. Shared release pins and
vendored bytes remain fixed; the standards candidate remains unpublished.
