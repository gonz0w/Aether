# ABI24 channel-wait consumer — UL-007 / UL-081

Requirement: keep a real bounded dash session usable after genuinely delayed
input without an iteration-based transport timeout. Aether owns opcode 0x24004,
endpoint authority and one-parent lifecycle. Userland owns the client adaptation.
No sibling changes or new shared standard are authorized by this experiment.

Success: explicit AENMX009/ABI24 clients retry actual reads/writes at the same
partial offset after a zero readiness hint, and a real prompt survives 35 seconds
without input, then completes the existing three-command workload and ten reclaims.
The default ABI23 parent/helper must remain byte-identical. Forbidden: treating
readiness as data/EOF, replaying a partial request, hiding ENOSYS by polling,
claiming signal delivery/restart or publishing an SDK without outstanding reviews.

Implementation: preserve frozen vendor/provenance bytes. Derive a local transport
header with explicit vendor include paths and one opt-in wait transfer function.
Default runtime still includes the original vendor transport directly; new selection
requires SESSION_SERIAL and SESSION_CHANNEL_WAIT. No automatic ABI negotiation.
Synchronous FD transactions already mask signals. A nonzero wait result, including
EINTR outside that mask, poisons this protocol and fails closed. It does not consume
signals, inject handlers or automatically retry an ambiguous request. Retain this
narrow interruption policy; general interactive signal/TTY semantics remain open.

Tests: scripted host read/write fragmentation, repeated/spurious readiness,
partial prefix across EAGAIN, no effects after poison, EOF, oversize/error transfer,
wait ENOSYS/EACCES/EINVAL/EINTR/positive-invalid return; native matched frozen
kernel/owner/client delayed prompt, immediate replay and old polling-client limit.
Build exact default clients and new clients with pinned Clang/LLD/SDK. Use the
unchanged owned process helper, bounded logs/deadlines, explicit environments and
complete cleanup; all attempts retained. Host instrumentation does not establish
native endpoint enforcement. Actual source review and independent reader review
are separate; SSDK-06 remains deferred by the maintainer.

Simplicity: (1) keep polling or increase its budget; (2) insufficient because healthy
idle has no iteration deadline and Aether now provides endpoint readiness; (3) new
profile removes the polling budget/yield loop, while default compatibility remains
until its consumers migrate. A local derived header costs limited duplication but
avoids rewriting frozen inputs or preprocessor tricks. No service framework,
waitset, cancellation grant or timeout API is introduced.

Evidence/results: pending. Review includes endpoint identity, reserved zeros,
partial offset, request bound, poisoned state, mask boundaries and owner cleanup.
General signals/jobs/TTY, unrestricted lifetimes, physical hardware, sys-init
composition, package/storage integration and SDK promotion remain follow-ons.

## Closure and actual findings

Aether wait kernel and lifecycle owner packets were verified in full before intake;
the reused lab packet/SDK closure was independently verified. New clients are
source-built with the sealed C17/Clang21.1.8/static-musl recipe; the kernel/owner are
qualified producer artifacts consumed without local rebuild. There are no sibling
edits. Applicable O/I/E, NC, TE/CC/CP and SE requirements are scoped to this work.

Completed28host cases in plain/UBSan, five semantic source mutants, eight SDK
profile controls per interpreter, two matching lab profile builds and three lab
profile/SDK denials per interpreter, CLI stream/exit contracts, four native exact
comparisons (three healthy sessions plus expected old-client polling limit), and
eight oracle corruptions. The final maintained-kit delayed witness has4467ticks,
3904idle ticks and ten reclaims. Whole default008 client ELF hashes stay exact.
All selected gates pass; syntax/format checks apply to maintained/new original
sources. Derived vendor style is preserved, not mechanically reformatted.

Tests retained three infrastructure/test-source corrections plus partial-halt
framing correction. Initial attempts are not acceptance. Full private work,
compiler/helper/inspection/native logs and artifacts are archived/read back before
compaction. No automatic pruning or external publication is installed.

Documentation: ARCHITECTURE defines the wait/mask/profile contract; STATE points to
current evidence and next owner action; ROADMAP/BACKLOG preserve UL IDs and remaining
acceptance. README/experiment boot guidance, handoff and draft coverage are updated.
No shared pin/adoption, machine marker or exit protocol is changed.

Technical reviewer: implementation agent (source-review.md). Independent SSDK-06
reader review remains pending/deferred. General signal/TTY/native wait-EINTR,
additional native backpressure schedules, actual sys-init assembly, package/storage,
physical hardware and full UL-007/063/081/M3/R1 remain incomplete. This closure is
local wait adaptation and lab delivery, not overall project completion.
