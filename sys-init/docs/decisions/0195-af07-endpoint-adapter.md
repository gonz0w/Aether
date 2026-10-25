# 0195: Bind the sealed AF07 client to owned native endpoints

2026-10-21 / BG-067. Userland's five-member read-only client and unchanged77-
member AF07 service now provide exact wire/framing semantics. Prepare the
sys-init endpoint adapter for that client, preserving all accepted owner/default
and release pins. This closes a transport preparation seam, not FD/path/exec,
a linked full dispatcher or native shell acceptance.

The simpler alternative is to duplicate framing and reply parsing in sys-init.
Choose the actual sealed Client/Framed implementation with a small owned-endpoint
adapter instead. It preserves short offsets, per-frame100000-poll limit and
result-bearing same-direction waits. No generic broker or second Owner/SPA is
added. The accepted handwritten AF07 activation remains byte-identical; it cannot
be removed until a new complete composition has fresh consuming evidence.

Trusted caller supplies two distinct nonzero endpoints acquired for one live
service connection. Constructor shape rejection returns the kernel adapter with
ownership retained by the caller; it does not close unknown/aliased values.
Successful construction owns both local close obligations. Tokens/epochs/frame
bytes never authenticate a connection or grant authority; actual kernel holder,
direction and state checks remain authoritative. Read uses reader/0x24001, write
writer/0x24002, wait0x24004 the same endpoint with unused arguments zero, close
0x24003 both independently. No pointer survives a synchronous transfer. Native
trap wrapper has explicit outputs/clobbers and no nomem/preserves_flags claim.

Cache both raw close results once, even when the first fails; no retry or reuse.
Reject I/O after local closure. Bare Drop is best effort, not confirmed cleanup.
Explicit Client disconnect acknowledgment plus Ok([0,0]) still requires engine
terminal/export/quiescence/EOF/EPIPE/reclaim separately. Ok([-9,-5]) must never
be interpreted as successful local settlement. Unknown/partial transport retires
the actual client, clears output/tokens and closes once without request replay.

Test the actual sealed Client/Framed over the adapter with typed native doubles:
reader/writer/wait selection, short/EAGAIN, failed wait and wait exhaustion,
malformed/partial greeting, invalid rights, partial disconnect, independent close
errors, returned cleanup and no I/O/replay after retirement. Compile native adapter
object with the exact pinned dependencies, strict format/default Clippy, and
compiling omission controls. No guest or native stack/authority/loader claim.
Run full local checks; bind sources/tools/dependencies and old-source stability.

Next userland must connect shared FD/path/binding translation and immutable
executable authorization to this client, not to a duplicate dedicated Owner.
Sys-init still owes full startup/descriptor/copy/exec/wait/endpoint dispatcher and
AF07 shutdown/fit composition after that exact contract. Fresh Aether consuming
witnesses must qualify actual native calls and failure/cleanup/readback. No sibling
writes/messages, guessed file messages, RAM fixture substitution or new campaign.

Foundations O-01–05, I-01/03–06, E-01–08 and Distribution RL-01/02/05 apply;
no new shared ABI or standards exception. Documentation impact: adapter guide,
quality/boundary inventory, state/BG-067 and existing integration handoff. Native
unsafe review is local and scoped; no independent sign-off is invented.
