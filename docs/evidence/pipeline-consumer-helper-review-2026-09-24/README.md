# Consumer helper qualification review — 2026-09-24

This completes the review of the unchanged [sealed native run](../pipeline-consumer-helper-2026-09-24/README.md).
Its README retained pending wording because the post-run summary check failed before
summary publication. That packet remains immutable; this reviewed outcome supersedes
its pending qualification wording. The run itself passed all87 native cases and105
Python host tests plus Zig/Rust checks in one attempt. Native recorded case duration
is246.139 seconds. There was no failed native run.

The pinned unchanged consumer helper copy body runs in both replacement workers,
using inherited fd0/1 and real libc read/write. It transports exact ten-byte input
through both pipes/capture and EOF, with8 waits and15 reclaims over three generations.
Private bootstrap/report/readiness, diagnostic probes and explicit close remain in
the wrapper; parent process creation/wait is still the fixture, not dash main/eval.
Larger payloads, EINTR and other helper modes are not newly qualified by this workload.

The negative skips relay main after the forced first write, closes its ends and lets
the real final helper see EOF. Slots1..4 exit normally; missing output rejects2743
with zero reclaims. Parent wait replies finish, but parent exit is not observed or
required before rejection. A post-run assertion incorrectly required all five exits;
that analysis failure caused the summary to stop. The shell then ran the finalizer,
which archived/verified/cleaned outputs and sealed the pending packet. No runtime
sources or native oracle were changed in response. This review reads that retained
archive and corrects only the unsupported parent-exit expectation.

All281 runtime input hashes stayed frozen. Only libc-worker.c and pipeline_capacity.py
changed. All110 prior ELF/raw images remain identical. Both new owners equal the
previous17512-byte owner and linked stack audit (3968 of4088 usable bytes,120 margin).
The positive consumer worker ELF is21072 bytes and links the pinned helper instead of
32 dash objects. The sealed worker audit shows the call to consumer_helper_main and
frames of4136 bytes for the helper,104 for its wrapper, plus bounded facade calls on
the existing64-KiB native C stack. This is scoped review and target evidence, not an
exhaustive stack proof. No kernel/SDK, authority, resource, sibling, dependency or
released-pin changes. The Rust supervisor stack and C worker stack are distinct.

Native reproduction commands, all logs, input snapshots, compiler commands, artifacts,
worker disassembly and verified cleanup are in the original packet. This review
contains negative/compatibility analysis and updated documentation snapshots, linked
to that packet by manifest hash. The original generated directory was archived and
hash-verified before deletion; no historical evidence was removed.

Next connect actual dash main/init and process creation/waits using existing scoped
startup facilities. Parent sequencing, report/readiness, descriptor expectations and
fixed wait probes still need the real workload contract. Empty-environment/fixed-vector
exec remains explicit. Independent consumer replay, unchanged-script acceptance and
serial-shell assembly remain open, followed by persistence/OpenZFS, packages and
sys-init R1 assembly. No public full-shell handoff is claimed.
