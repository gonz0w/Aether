# Memory-XDR and nvpair build/behavior scope

Before-code scope, 2026-10-04; R1-03. Extend the sealed native supporting-library
closure using upstream libtirpc1.3.6 memory-XDR, matching the recorded host baseline
version. Reuse mature serialization rather than write a format implementation or
pull network RPC into the service. Fetch/setup is explicit and separate from offline
builds; pin archive SHA256
bbd26a8f0df5690a62a47f6aa30f797f3ef8d02560d1bc449a83066b5a1d3508
before extracting. SourceForge upstream release and Buildroot's recorded checksum
are research inputs, not signer authentication. Retain all notices and source bytes.

Build the memory encoder/decoder, primitive/array encoding and only its actual
support closure against the pinned native musl SDK. Rebuild unchanged nvpair.c and
nvpair_alloc_system.c with real RPC types/headers. Keep XDR formats and boundary
checks; no fake RPC headers, dropped encodings, successful allocator/clock/I/O stubs,
Linux/glibc archives, host headers, network runtime, kernel, sibling or pin changes.
The bundled Linux SPL XDR backend is a different kernel API; do not silently swap
it into the existing userspace libtirpc interface.

Scope tests before claims: source/header/tool/SDK inventories frozen, isolated
native objects, complete import attribution and honest strict startup link; exact
unknown-import/host-header denial, full host/pin/workflow and simplicity checks.
If executable behavioral coverage is added, require independent expected XDR bytes,
roundtrip typed/nested nvpair data, truncation/length/unknown-type denial, immutable
input/canary buffers and a deliberately broken implementation rejected at a named
semantic check. Identify host versus native target explicitly. Build-only success
cannot close parser/runtime/engine qualification or select memory/admission budgets.

Security: serialized data will be untrusted persisted metadata. Require bounded
length/overflow/cursor checks, owned allocation/free and failure cleanup before a
native service consumes it. No pointers or decoded names confer resource authority.
Existing file/config/entropy grants and stop/reap remain runtime gates. No engine
executes or volume is touched during this private build audit. Userland owns SDK;
Rust service owns policy; Aether owns this port experiment. Future native diagnostic
profile must preserve assertion failure and report absent traceback explicitly;
no fake backtrace is introduced as part of XDR work.

Before native probe implementation: isolate serialization objects from the engine.
The existing memory-grant/I/O conformance adapter supplies only fixture operations.
A probe-only libspl_assertf handler terminates with217 and never returns; explicitly
invoke it in a separate rejection image. This keeps upstream assertions enabled
without importing Linux diagnostic discovery or inventing a traceback. It is not
a native SPL diagnostic implementation and cannot satisfy the engine's unresolved
libspl_backtrace. Keep the actual engine strict-link failure unchanged. Probe checks
use exit210 for encoding,211 for decode,212 for boundaries,213 for nvlist roundtrip,
214 for malformed nvlist,215 for guard/input mutation and216 for owned allocation
cleanup. The broken memory encoder must be rejected at210, not by timeout.

Native attempt5 found an incorrect new test expectation: upstream decodes an unknown
root nvl_version without rejecting it. Preserve the failure; characterize acceptance
explicitly in the next frozen run, with cleanup/canary checks. No production service
consumes these objects. Future Rust metadata ingress must validate the supported
root schema/version before consumption; parser success alone cannot authorize it.
Unknown encoding/type, excessive lengths and truncation remain rejection checks.

Simplicity: use only upstream memory-XDR plus existing nvpair rather than a whole
RPC daemon, a new serialization framework or an in-house filesystem rewrite. This
adds no active kernel/service mechanism and removes unresolved encoding assumptions.
No normal build follows mutable sibling dependencies. Preserve all failures and
private outputs until archive readback; reuse prior sealed inputs by hash rather
than duplicating them indefinitely. Foundations O/I/E and SE-01–05 apply. Update
STATE/ROADMAP/OPENZFS-FEASIBILITY/THIRD-PARTY; private recipes are retained evidence,
not maintained developer entry points. No filesystem, CPU-state, release or owner
sign-off follows from library object generation.
