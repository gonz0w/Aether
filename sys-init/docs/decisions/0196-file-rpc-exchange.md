# 0196: Serve one bounded authenticated file exchange

2026-10-21 / BG-067. Consume the selected20-member AEFD0001 v3 wire/process
candidate (including stale-key checks for unsupported requests), its15-member
process baseline and unchanged77-member AF07 service. Prepare sys-init's small
server transport wrapper around the actual handler. Current linked ABI29 shell
still does not speak this protocol; startup/console/pipe facade selection and
immutable executable admission remain separate.

The simpler alternative is to duplicate operation decoding or treat send-header
success as completion. Choose one exchange method using the sealed Connection/
PreparedReply: bound input first, assemble only required padded name frames in
caller-owned4096-byte workspace, prepare once, deliver header and ALL body frames,
then call delivered exactly once. No automatic4096-byte local buffer, generic
RPC framework, alternate wire or native quota is added. The accepted serial/AF07
owners and endpoint/core sources remain immutable. Nothing can be removed yet.

Trusted caller binds an actual authenticated live peer channel to an opaque
ProcessFiles key and nonreused channel generation, after actual admission.
Metadata labels grant no authority. Each Channel operation must be bounded and
return Ok only for complete64 bytes. Native endpoint adapter/Framed supplies its
existing <=16-byte chunk/per-frame100000 limit; whole lifecycle deadline and fit
remain external. Requests cannot admit/rebind processes or invoke exec commit.

On receive/header/body/protocol/prepare/send failure, abort the actual shared
file source, clear workspace, retire the peer and independently close its two
endpoint obligations once. Preserve raw peer cleanup; source cleanup remains
separately observable through ProcessFiles. No resynchronization, replay or new
I/O after retirement. One peer failure retires all shared file views per the
candidate's fail-stop policy; it is not generic fault isolation or native recovery.
A known semantic errno reply advances only after complete delivery and may
continue. Bare peer Drop only closes local endpoints; trusted caller still owes
explicit source/process/lifetime settlement and cannot claim successful cleanup.

Validate actual handler/process/client/service interoperability with synthetic
storage and deterministic peer failure injection: open/read/shared offsets,
sequence continuation, caller workspace clearing, unsupported current/stale key,
all required body sends, no advance on lost header/body delivery, no replay and
both raw cleanup results. Compile host/no_std objects with pinned tools and
source dependencies, strict formatting/default Clippy and compiling omission
controls; run full local checks. If current C transport input matches, use it in
a fresh host exchange witness, without claiming linked shell/native IPC. No guest.

Placement of ProcessFiles/peer state/workspace is not solved by these borrows.
Do not assume a4096-byte buffer plus tables fits init's4088 usable stack. One
AF07 greeting consumer and one live Owner/SPA remain mandatory. Userland still
owes selected shell FD/console/pipe routing and full path/immutable executable/
failed-exec semantics. Sys-init then owes full dispatcher/readiness/shutdown/fit;
Aether qualifies exact matched native command/error/cleanup/fresh-readback.

Foundations O-01–05, I-01/03–06 and E-01–08, Distribution RL-01/02/05 apply;
no new exception, shared ABI, pin or sibling edit/message. Document API/authority/
failure bounds, quality inventory and BG-067 current handoff; no independent
release/reader review or native acceptance is invented.
