# Worker-driven detached cleanup with a blocked primary

Before-code scope,2026-10-05. R1-03 needs cleanup independent of the creator's
polling. Aether owns a private native conformance witness; production musl remains
userland-owned. The accepted VM/musl/clock/identity designs and existing eager
private profile remain authoritative. No kernel, public ABI/SDK, quota, sibling,
standards release or pin changes are needed.

Requirement: one joinable musl worker owns peer cleanup while the primary blocks
in actual musl pthread_join. It occupies one of the existing82 service/two peer
slots;81/one peers are detached. All82/two actual stacks, TLS, keys/destructors,
heap accounting and parked-worker limits remain. Each peer publishes saved
mapping/ID metadata, waits for permission, exits and is confirmed stopped before
unmap/retire through existing domain grants. The cleanup worker never reads an
unmapped TCB. No new privileged helper, ambient authority or parent RPC.

Ownership: main alone creates the fixed batch and publishes immutable records;
after gate release the cleanup worker alone mutates detached retirement records
and used count. The parent reads them only after successful upstream join, then
retires its cleanup worker. Atomic request/permission flags publish callback
results; upstream join/list-lock ordering establishes completion visibility.
The cleanup worker must use ordinary child yields, not increment the supervisor's
primary-only yield count. Saved pointers are fixture-owned and validated against
held grants at native operations. Deferred cancellation, orphaned-service recovery,
worker-origin concurrent creation and broader progress schedules remain open.

The parent join adapter records actual native compare-wait entry and completion;
positive completion must follow peer cleanup and actual join/clear-TID. This
records the exercised blocking call, not every scheduler interleaving. A separate
control removes worker-origin permission: the cleanup worker's first observe must
return EACCES, mapped into exact355, not generic timeout. Another deliberately
premature unmap must fail352 while the requester is still running. Stop/replacement
with the complete parked cohort retains existing exact supervisor observations.
Descending peer completion tests request selection independent of ascending slots.

Tests: ordinary joinable and primary-driven detached regressions, worker-driven
cleanup, descending cleanup, parked stop/replacement, disabled-origin355 and actual
early-unmap352. Sources freeze during180-second builds/30-second guests; teardown
3 seconds and all failed attempts retained. Full host/pins/workflow, scoped C21.1.8
reviewed format, Rust1.98/2024, simplicity digest and links follow. Older unchanged
runtime coverage binds exact source inputs, never claims fresh targets.

Simplicity: blocking the primary with the existing actual join and dedicating one
bounded ordinary worker is sufficient for this experiment. A generic reaper service,
new kernel self-unmap primitive or general VM rewrite adds unnecessary authority
and lifetime complexity. The extra worker consumes an existing slot and bounded
stack rather than silently expanding engine capacity. No production path is
removed now. Document the resulting limitation before actual engine integration;
this trial alone does not choose a production reaper policy or measure engine peak.
Documentation impact: native reference, workflow inventory, STATE and R1 roadmap.

Before-code rejection-path clarification: a failed cleanup worker cannot simply
return while a detached peer holds musl's list lock awaiting permission. On the
negative path it permits each remaining published peer to exit, synchronizes the
upstream list lock, and leaves every peer mapping/record allocated. No rejected
observe or unmap is converted into reclamation. Then real join can return the
exact error to the primary; supervisor rejects without a successful reclaim.

Before final controls: attempt1's five positive cases pass. The proposed disabled-
origin control correctly fails the existing build guard because82-worker storage
requires the origin profile; it is infrastructure/configuration rejection, not a
native control pass. Preserve it. Replace that impossible profile with actual
wrong-grant observation from the cleanup worker: EACCES maps to exact355. Keep
origin enabled and every build guard intact. Add an omitted-join-park control:
actual join loops with child-progress yields but no primary native park; completed
wait count stays zero and exact356 must reject after cleanup. A flag alone cannot
satisfy positive blocking evidence; zero native compare-park result is required.

Final evidence tightening after attempt2's eight passes: the inherited runner
hashed the rustup dispatcher for rustc+1.98.0. Resolve and freeze the actual pinned
compiler executable and invoke it directly for the final fresh attempt3. Retain
both earlier snapshots; no C/runtime behavior changes or compiler version change.

Attempt3's direct compiler invocation fails linking before any guest: on this
macOS installation rust-lld needs the library search environment supplied by
rustup. Retain this infrastructure failure. Final attempt4 restores the unchanged
rustc+1.98.0 entry, while freezing the resolved actual compiler, rust-lld and LLVM
library as well as the dispatcher. No host toolchain installation/change, injected
global environment or runtime C change. The resolver and explicit toolchain
selection are recorded; do not describe the final command as direct invocation.
