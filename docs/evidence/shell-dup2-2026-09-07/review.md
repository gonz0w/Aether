# UL-007 descriptor replacement review

Before implementation, 2026-09-07: user authorized prioritizing actual dash
integration over OpenZFS. The current userland twelve-workload packet requires
redirection, descriptor restoration and inherited pipeline endpoints. Implement
only the missing dup2 primitive in the existing opt-in single-context startup
facade first; custom signal delivery, process cloning/exec/wait and pipes remain
separate required work. No full-dash delivery or owner acceptance is claimed.

Required semantics: validate both indices/source before mutation; equal valid
indices return unchanged including CLOEXEC; otherwise replace the exact target
and clear its CLOEXEC, even with no free table slot. Preserve the source binding,
shared offsets and capability rights. Consume the displaced binding exactly once
only on its last alias. A complete remote close EIO confirms consumption under
AECAT001 and is discarded by dup2; malformed/unknown close poisons the connection
and must fail without publishing the replacement. Application pointers remain
subject to existing isolation. No new kernel pointers, allocations, quotas, ABI,
SDK modification, wire format or shared policy. Publication is atomic only under
the existing one-context/no-handler/no-exec bound; future handlers require review.

Forbidden: clearing self-dup flags, closing an invalid source's target, premature
source close, leaking replaced ownership, requiring a free slot, publishing after
uncertain close, or treating local aliases as process inheritance authority.

Tests: target two-generation dup2 sequence, unchanged consumer startup, exact
self-dup/flag/displaced-close mutants, current malformed admission controls and
complete command-runner suite. Verify real alias I/O and owner-observed closes,
terminal results and four reclaims. Host/pin/workflow and pinned C format; no
unrelated QEMU modes because kernel/loader/ABI remain unchanged. Retain every
attempt and freeze sources for qualification. Documentation: startup reference,
STATE, ROADMAP, existing workflow group. Foundations O-01/03/04, I-01/03/05,
E-01/04/05/06 and approved local DEVELOPMENT apply. Original BSD-2-Clause;
no dependency or sibling change. Legacy harness formatting is scoped, not migrated.
