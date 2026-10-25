# Native startup closure and honest diagnostics

Before implementation,2026-10-04; R1-03. Verify/reuse the three sealed build packets
and source/SDK/tool inventories. Build a genuine static kernel_init/fini image;
do not equate linking or SDK exports with runtime support. No sibling, kernel,
quota, released pin or historical evidence changes. No engine/volume execution
until native configuration, CPU-state and required runtime authority are reviewed.

Keep upstream algorithms and assertions. A private AETHER_NATIVE_PROFILE adapts
SPL assertion reporting to a constant ASCII diagnostic on inherited stderr and
_Exit(125), without allocation, identity/thread-name discovery, mutable diagnostic
locks, unwind or format/argument disclosure. Nonfatal assertion mode is unavailable:
enabling it terminates125 rather than permitting invariant failure to return.
This is deliberately minimal diagnostic information for the port witness, not a
full diagnostic/debugging interface. Upstream CDDL notices remain on derived files.
Traceback fallback uses real write to the caller's existing descriptor and says
trace unavailable; no frames or successful unwind are invented. Neither failed
diagnostic output nor denied descriptors may turn assertion failure into success.
This profile has no capability-bearing data and does not print untrusted names.
Inherited stderr delivery remains open if the fixture has no FD2 binding.

The two device-discovery imports originate in a mixed path utility. Rebuild only
that source with function/data sections, select actual startup reachability with
strict --gc-sections and retain its whole-object unresolved comparison. Never
implement ambient import paths, directory enumeration or a successful device stub.
Root both discovery functions in a separate strict negative link: they must still
fail with the actual missing platform imports. No general utility API is silently
promised by a startup-only image.

Bind __aether_io through the existing source-built native-memory conformance adapter
only. Its mappings require an actual memory grant; its I/O trap supports fixture
operations and does not implement filesystem descriptors. Label that distinction
and keep volume/config/entropy/clock/thread/grant work open. Inspect image segments/
imports and resource geometry before native startup admission is proposed.

Tests: fresh optimized native diagnostic objects and real strict link; native
no-trace denied-descriptor errno observation, actual fatal assertion and attempted
nonfatal mode; mutant no-op trace fallback must fail at its named check. Use the
existing memory fixture's unchanged output/yield/terminal contracts. Inspect image
TLS/layout; unknown platform and host-header denials; full host/pin/workflow,
Experience and simplicity checks, scoped source formatting/syntax/link checks.
Freeze all actual inputs during qualified runs; preserve failures, argv, timestamps
and binaries. Native stderr delivery, interruption/reentrant reporting and general
SPL compatibility are not proved by a fixture terminal test.

Simplicity: choose the upstream no-unwind fallback plus a small fatal-only profile
over adding a full unwinder or identity subsystem solely for startup. Use section
reachability rather than inventing a device registry. Reuse the existing conformance
adapter over a fake filesystem runtime. Added cost is private port/review evidence;
it removes four unresolved-link assumptions, not four runtime requirements. Future
Rust filesystem service owns policy; userland owns production SDK. Foundations
O/I/E and SE-01–05 apply. Update STATE/ROADMAP/OPENZFS-FEASIBILITY/THIRD-PARTY and
scoped Experience note. Private recipes are evidence, not normal entry points.

After initial link attempts: keep actual tunable registration sections under
-z nostart-stop-gc; do not discard configuration to pass. Inspect musl's zero-valued
LOCAL/HIDDEN/UND _DYNAMIC sentinel and lack of relocations separately from external
imports; no missing external platform symbol is waived. Recompile unchanged Linux
getmntany.c with function/data sections to discard unreachable mount-table code
and its4110-byte TLS buffer, rather than increasing the kernel TLS quota. Add a
real initialized TLS marker checked at startup, matching the loader's existing TLS
view requirements. Retain all earlier link/audit failures and exact final geometry.

Before runtime prerequisite probes: execute actual public SDK clock_gettime,
uname, physical-page sysconf, getentropy and random-device open only in the existing
isolated memory fixture, without calling kernel_init or using storage. Record exact
unsupported errors and buffer integrity; a failed expectation is a retained failure,
not a platform success. Check the linked engine with unchanged loader/parser copies
under ordinary and large limits, including W+X and excessive-TLS denials. This
classifies native runtime/resource gates; it does not qualify feature configuration,
engine startup, entropy quality, production SDK or grant-bound providers.

First prerequisite attempt rejects230 because public monotonic clock maps the raw
ENOSYS to EINVAL. Preserve it and test both layers explicitly. Linked-code inspection
also shows the realtime fallback ignores failed gettimeofday. Before the next run,
add a direct syscall denial and sentinel-based characterization of false realtime
success; this is a blocking runtime defect, not a passing clock implementation.
Keep engine execution unavailable. Userland owns its SDK fix; no sibling is edited.

Second prerequisite attempt passes the realtime false-success characterization,
then rejects232 at physical-page sysconf. Source and linked-code review establish
that musl ignores failed sysinfo and reads an uninitialized result. Preserve this
attempt; do not execute that unsafe public query again. Replace it only in the
classification probe with actual sysinfo denial and buffer-integrity checks, then
complete entropy/device-open checks. This avoids interpreting indeterminate page
counts as capacity; production SDK error guards and real providers remain required.
