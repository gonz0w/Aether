# 0205: Acquire fork capture before decoding its wire sequence

2026-10-22 / BG-069/070. Capture component qualified; full native composition blocked on placement.

The sequence is at byte296 of a304-byte request, beyond its16-byte header. Add a
single capture operation that closes admission before invoking body read/decode,
then validates/reserves the decoded nonzero increasing sequence. Capture failures,
replay/zero and unwind stay closed; no native copy/source request/implicit cleanup
or thaw follows decoding failure. Keep the known-sequence begin API for existing
component callers. No predicted wire sequence, second ledger or extra buffer.

Compose the actual selected frame decoder with a bounded native-channel transfer
helper using existing Kernel transfer/wait semantics and caller-owned304-byte raw
and scratch buffers. Preserve partial offsets,16-byte transfer bounds, one shared
poll budget and raw failures; inspect header after exactly16 bytes, never consume
an unsupported body. Clear buffers on failure before external settlement. Native
identity/channel authentication and parked-parent reconciliation remain owner work.

Simpler alternative: read the full body while Idle, then call begin. That permits
conflicting work during partial input and cannot establish the admission window.
A capture closure is chosen instead of another transport queue/state framework.

Validate exact selected decoder/actual FILE and owned-stream libraries with short
reads/EAGAIN, every truncated request, corrupt header/body, zero/replayed/gapped/
final sequence, no source/copy effects and unwind closure. Strict pinned formatting/
Clippy, host/native libraries, compiling omission controls and full local checks.

Also measure the real placement prerequisite, not a quota guess: selected RPC
requires an initialized caller-owned4096-byte workspace, while current ABI29
supervisor maps one stack page with entry RSP0x801000-8, no writable image data,
and memoryOperation explicitly rejects supervisor allocation. Record pinned actual
kernel sources and target layout sizes, investigate existing placement alternatives
and capture a focused affected-owner request if no permitted placement exists.
This does not authorize a kernel limit change or a second filesystem service.

## Result

Owner.capture closes Receiving before decoder I/O. Only a complete nonzero strictly
increasing wire sequence reserves the watermark and enters Capturing. Known-sequence
begin now also remains Receiving until callback completion. This fixes the earlier
host-unwind path where the Capturing phase could permit copy before capture had
returned. Parse/replay/zero errors reject without advancing source state or thaw;
partial/unknown I/O and unwind never reopen admissions or authorize copy.

fork_transport::receive performs this acquisition itself; its raw request helper
is private. It uses the unchanged endpoint Kernel adapter, exact16-byte header,
304-byte request, at-most16-byte transfers, shared call budget and raw errors.
RAII clears caller-owned buffers on normal return/error/host unwind; no additional
automatic304-byte packet or4096-byte workspace. There is no wall-time guarantee
inside a blocked native wait and no unwind guarantee for native panic-abort.
Authentication, parent parking/token reconciliation and full native lifecycle
remain owner duties, not inferred from frame labels or successful parsing.

Twenty actual gate/core/capture host tests and four strictly compiling omissions
pass; initial15 tests remain, with five new capture tests. Every truncated prefix
0..303, corrupt headers/body/identity, gaps/zero/replay/final sequence, EOF/overcount/
EAGAIN/raw wait/budget errors and clear-on-unwind/copy-denial are covered.33 bounded
final Rust commands pass with pinned sources/tools/reused dependencies, strict
format/default Clippy and actual generic host/native libraries. One additional
native LLVM layout command confirms Files2208, State736, gate2968, workspace4096,
Plan216 and two transient fork buffers608. No failed command occurred here; earlier
successful source/recipe snapshots are retained rather than overwritten.

Full aggregate checks pass (all ten, captured sources unchanged):
out/checks/run-6rnzwjmo/results.json. Final scoped quality check follows documentation
updates. [Evidence](../evidence/gated-fork-capture-2026-10-22/README.md) preserves
commands/logs/source/artifact pins, target IR and actual kernel source excerpts.
Old0202/0203/0204 packets, accepted owner and primitive source stay unchanged.
No new unsafe/native boundary, guest, sibling change/message or release pin change.

The selected current native owner has no permitted writable placement for these
resident objects: gate+workspace7064 exceeds mapped4096 bytes, even Files+workspace
alone is6304. The stack's entry headroom is4088; code is RO, raw image writable
data is rejected, supervisor allocation denies and backing aliases are kernel-only.
This is target object-layout/current-policy evidence, not a full executable/peak-
stack measurement or a claim that no differently versioned architecture can fit.
BG-072/OQ-027 and [focused handoff](../OWNER-PLACEMENT-HANDOFF.md) request a separately
qualified opt-in8192-byte private zeroed RW/NX region within existing128-page owner
backing, preserving all quotas/old profiles/code/stack bounds. Two-page proposal
fits the known base only; complete future peer/layout/code/stack fit must still
be proved. Reuse transient buffers and simplify before any further mapping request.

Stop full native initialization/owner composition at this actual authority boundary;
do not invent writable addresses/caps, reuse kernel aliases, shrink a pinned array
or create a second FS owner. Aether owns the next matching placement contract;
userland metadata/stream/TLS inputs are already present. Sys-init resumes explicit
initialization/transport/transaction/terminal/readiness/shutdown, full fit and fresh
matching Aether witnesses once that placement is supplied. Local current-state,
backlog/priorities/roadmap, fork guide/README, standards/integration/handoff and
quality inventory record this scoped block; no independent review is invented.
