# 0204: Validate fork streams against the owned pipe cores

2026-10-22 / BG-069/070. Local component and host qualification complete; native composition pending.

Require a complete captured Plan at copy admission, with explicit stream validator
as well as the existing authoritative FILE comparison. A candidate State owns two
actual existing SESSION pipe cores and the parent's live console source records.
Derive used streams from all sixteen tagged bindings. Compare complete console
records and actual pipe parent holdings, rights, source labels and retained history,
including history for an empty/retired pipe. Shape or authoritative mismatches must
close admission before the native copy callback without mutating streams/files.

Reuse the existing tested ring/holder/epoch algorithms via a separate source copy
with one read-only parent view. Preserve the accepted ABI24 source/owner/provenance;
no historical source edit, new ring implementation or parallel holder ledger.
The local copy has existing BSD-2-Clause provenance. One read-only trait connects
the safe generic gate to actual state, with no default successful implementation.
Trusted test doubles are labelled; a trait implementation is not native authority.

Simpler alternative: let a caller validate in an optional callback. That leaves
copy admission bypassable; this gate now requires an explicit stream view. Reuse
of the existing core is smaller than replacing holder/EOF/EPIPE/epoch algorithms.
The snapshot seam avoids cloning two rings just to inspect them. No new heap,
queue, source handle or service; whole linked footprint/stack still needs measurement.

Before implementation, select tests: exact/empty/aliased/CLOEXEC stream maps,
all source fields and omitted/extra holdings, inactive retained history, real pipe
staging/readiness/refusal/unknown/EOF/EPIPE, and no copy/source/pipe mutation on
denial. Retain earlier FILE/gate cases, semantic compiling omissions, strict
format/default Clippy, host/native no_std builds and full local checks. Native
copy/grants/console close/TLS/transport/whole-fit/witness remain separate obligations;
this is the next owner component, not a complete native transaction.

## Implementation and result

The copy gate now requires a complete Plan and explicit ForkStreams state. Actual
State validates console/source fields and existing pipe parent holdings/history.
No native copy callback runs on mismatch. The read-only seam uses existing private
state rather than a mirror. Copy validation has exclusive ownership through
serialized inheritance; all normal mutation remains closed.

A concrete integration gap was also closed: exact child context-ready must activate
actual staged pipe holders before parent success. New Activating phase keeps
admission closed during the hook; partial activation/error retires without losing
child obligations, and activation unwind remains closed. Context-ready cannot
invent a no-child refusal after positive copy. The trait has no default-success
methods; nine retained FILE/admission tests explicitly use a stream double.

Fifteen tests pass: nine earlier admission/FILE cases (including new activation
unwind branch) plus six concrete State/core tests. Forty malformed source/holding/
history cases, inactive retained history, terminated parent, EOF/EPIPE, known
refusal epoch reuse, unknown holder retention and failed/partial activation are
covered. Four strictly compiling omissions each fail a selected semantic test;
borrow reentry and a pipe reference escaping callback are compiler-denied. Thirty
bounded final Rust commands pass, including host/native libraries, format/default
Clippy. Original pipe source hash a33f3c63899139ae7b78cddcedd74b08a29e59ef68a786d03a786851ae2b4c13
is unchanged. The new candidate's exact selection diff/provenance is retained.

During this work userland supplied corrected TLS85, manifest
f14badab992cf50de4b3443093ccd4b65aa01b1ba1bcf4fa7447672d26b962d4.
Verify23 service closures/840 listed members plus unchanged linked580. Fresh
independent host execution of the unchanged actual Aether parser accepts the
279568-byte real-TLS ELF366287d33cff71c33db24247fb214dd6099bcb6359d28b3f6866e9de11dc2b96
and rejects old no-TLS stage81/malformed TLS/WX. All seven parser tests pass. Pin
Zig binary and installed19,542-file library closure before/after. Missing TLS input
is resolved; parser acceptance does not establish native loading/execution/whole fit.

All ten aggregate development checks pass with captured sources unchanged:
out/checks/run-u7_xmbg1/results.json. Final scoped quality-record check follows
documentation updates. [Evidence](../evidence/authoritative-fork-stream-view-2026-10-22/README.md)
retains exact commands, successful/failing attempts, source/artifact/tool hashes,
negative controls and scope. No lint suppressions, sibling changes/messages,
guests, quota/default/release pin changes, unsafe/native boundary or sign-off.

Documentation impact: fork guide/candidate README, current state/roadmap/priorities,
BG-069/070, OQ-025, integration/standards/handoff and quality inventory now reflect
actual stream validation, activation and corrected TLS input. Full native owner
holder/copy/refusal/startup/ready/parent transport, terminal/endpoint/readiness/
shutdown, complete fit and fresh matched target witnesses remain BG-069/070 work.
