# Owned ABI24 session consumption — UL-007 / UL-012 / UL-081

Sys-init's decision0183 now supplies an actual owned entry for the private009
serial shell. The matching kernel and userland dependencies are closed. Userland
independently consumes the frozen candidate in
[consumer evidence](evidence/sysinit-session-consumer-2026-10-03/README.md), keeping
supervision/dispatcher policy in sys-init and all native enforcement in Aether.
This supersedes the prior handoff's missing-composition dependency; it does not
mark sys-init's acceptance complete.

The consumer verifies every producer packet byte and reads all six actual boot
components from normal, wrong-ABI, busy-halt and diagnostic ISOs against the
qualified baseline. Kernel, three client images, entropy and other modules remain
exact. Selected owner raw bytes match the linked ELF load image. The private
source snapshot and stack/indirect-call inspection remain scoped producer evidence,
not a local source rebuild or whole-stack proof.

Native inputs cover immediate, paced byte input and35-second delayed prompts;
exact program bytes, PID/variable retention, helpers/pipelines/substitution,
prompt-relative input and ten terminal/reclaims are independently checked.
Wrong-ABI and actualEBUSY before admission have exact fail-stop paths and no
successful halt. The diagnostic owner is a separately pinned private artifact;
it is not the normal entry or a new userland runtime.

## Historical producer finding and diagnosis proposal

The retained first delayed failure used the same normal ISO and host-accepted writes
for all three complete commands; exact guest receipt of every byte is not directly
observed by that record. Nine child terminals, including the final helper, are
observed. The owner reports failure and vector6 at its generic failure path before
parent terminal, closed/session output or authorized halt. Its collector then
truncated the panic suffix. Collector truncation does not explain the preceding
real owner failure. Cause remains unestablished; successful new schedules cannot
classify it away or justify promotion of the candidate.

Required sys-init-owned follow-on: identify the first failing check/unwrap and its
actual result. If the existing check-caller diagnostic cannot reproduce it, propose
one bounded private failure record carrying the operation/result, peer+epoch,
partial-frame offset/reply state, and terminal/collected state relevant to that
check. Keep the record before fail-stop, with no authority tokens/pointer dump,
replay, synthesized cleanup or new failure recovery. Retain exact source/artifact
identity and inspect code/stack before boot. Exercise the final wait/result delivery,
child terminal/reclaim and next parent request with forced schedules only after
causal evidence points to that boundary. Do not guess a runtime/kernel fix from
the current generic fault address.

This is an explicit proposal, not authority for userland to modify that dispatcher
or close sys-init's acceptance. The next maintained recipe/new lab promotion should
bind the producer's diagnosed fix and affected negative/cleanup tests. The existing
qualified userland lab kit remains available. Independent SSDK-06 reader review
stays deferred; general TTY/jobs/signals, persistent storage/login, packages,
physical hardware and full M3/R1 remain open.

## Read-race repair consumed — 2026-10-04

Sys-init decision0184 now reproduces actual kernel read0 after the final helper
terminal and repairs that boundary by reobserving the same owned peer.
[Independent intake](evidence/sysinit-read-race-consumer-2026-10-04/README.md)
passes six fresh native cases: normal immediate/delayed, repaired yielded delayed,
old yielded EOF failure and actual EBADF/synthetic live-EOF rejection. Thirty
terminal/reclaims and exact270UART bytes pass;15 mutated traces reject.
All36 boot readbacks preserve existing kernel/clients/entropy/modules and five
owner ELF/raw pairs match. Matched developer kit is now
`build/lab-kits/sysinit-serial-abi24-2026-10-04`; its exact normal ISO passed both
immediate and delayed consumption, with an unchanged maintained-builder client
rebuild. Original failure evidence and previous kits remain immutable.

This supersedes the missing concrete diagnosis/fix action above for readEOF only.
It cannot identify the original uncaptured caller, qualify writeEPIPE or every race,
or close sys-init acceptance. Sys-init retains maintained recipe and remaining
composition/cleanup qualification; userland local work can continue. Release,
SSDK-06 independent reader, full TTY/storage/packages/recovery/physical lab remain
open. The kit's OWNER.md states these boundaries beside the boot instructions.

## Maintained recipe rebuilt — 2026-10-04

[Decision0185 consumer](evidence/sysinit-recipe-consumer-2026-10-04/README.md) now
freezes and runs the owner's actual offline recipe entirely under userland build/.
Minimum/current Python each rebuild exact repaired owner raw/ELF. Actual ISO
module/client/entropy checks and pre-effect source/input/tool/output controls pass.
The maintained userland builder rebuilds matching clients and delivers
`build/lab-kits/sysinit-rebuilt-abi24-2026-10-04`; maintained boot.py passes fresh
immediate/35-second delayed consumption with20 terminal/reclaims. Owner source
and payload reproducibility are established; differing ISO metadata is explicit.

This supersedes prior missing maintained-recipe/build actions, not sys-init's
remaining mismatch/exhaustion/uncertain-cleanup/composition acceptance. Exact
historical failure attribution, writeEPIPE and broader system/release gates
remain open. Original immutable deliveries/kits and deferred reader status stay
unchanged. Recipe supervision policy remains sys-init-owned.

## Owner denials consumed — 2026-10-04

[Decision0186 consumer](evidence/sysinit-denials-consumer-2026-10-04/README.md)
independently replays eight exact native controls with complete linked-fault/panic
and result/identity checks. Five expected-handle mismatches reject at entry;
actual console read/write with halt grant deny(-13). Late actual halt denies(-16)
after90UART/eight admissions/ten terminals with console retained. These terminal
records do not directly measure reclaim; host teardown does not close guest
authority.38 trace corruptions reject. No maintained runtime/grant/kit changes.

These scoped witnesses close only the supplied owner denial consumer cases.
Finite admission exhaustion, uncertain close/reclaim, component-loader matrix,
writeEPIPE and remaining composition/system/release gates stay open. Existing
positive source-rebuilt lab kit remains qualified; SSDK-06 reader stays deferred.


## Final controls consumed and continued-use boundary — 2026-10-04

[Decision0187/0188 consumer](evidence/sysinit-final-controls-consumer-2026-10-04/README.md)
qualifies eleven fresh native denials: real fifteen-helper lifetime exhaustion,
close/reclaim denial, synthetic settlement receipt loss, six exact loader negatives
and actual reply-write EPIPE after stopped-child terminal. Both full packets,
72 boot-module readbacks, five linked owner/source/UD2 bindings and81 trace
corruptions on minimum/current Python pass. Host reap is not guest reclaim proof.
Selected writeEPIPE and finite/uncertain-cleanup/loader consumer gaps are closed;
broader races, parser matrix, recovery and assembled review remain separate.

The next product dependency is an explicit Aether-owned wider SESSION identity/
lifetime profile, preserving nonwrapping identities, stale-reference denial,
real reclamation before reuse, wait semantics and quiescent halt. Current userland
bootstrap/wait accepts child epochs1..15, shell generations1..3 and pipes1..9;
PID/memory/reference encodings cannot be widened independently. The minimum next
consumer workload retains one parent/state through at least sixteen sequential
external helpers, another command and confirmed cleanup/authorized halt; exercise
new final bounds/stale references too. Preserve old009 artifacts and default pins.

This is a ready local owner proposal, not a sent message or permission to edit a
sibling. Aether first supplies exact contract/kernel evidence, then userland builds
and qualifies matching runtime/SDK artifacts, then sys-init consumes its owned
composition. The guarded-musl candidate is a separate SDK correction; it supplies
neither wider SESSION lifetimes nor clocks/storage. Existing bounded lab kit and
deferred SSDK-06 reader status stay unchanged. No blanket M3/release acceptance.
