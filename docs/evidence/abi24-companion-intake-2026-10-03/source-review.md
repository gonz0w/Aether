# Source assessment and next diagnostic

Userland's sealed runtime retains partial channel-transfer offsets, requires the
explicit009 selection and poisons ambiguous transactions on wait errors including
EINTR. The actual ISO parent/helper/spare hashes match its composition receipt.
The ISO kernel matches Aether's qualified wait kernel. Sys-init's actual entry
validates the six boot scalars, invokes the borrowed dispatcher to settlement,
then requests owner-authorized halt. No ordinary child acquires its grants.
The sys-init owner has its distinct15056-byte identity; this is no longer the
15184-byte fixture entry. Its3816/4088 stack inspection is delivered evidence,
not independently recalculated here. The sealed diagnostic image differs and
its pass cannot substitute for a normal-image pass.

The normal image fails locally after slot2/generation5 exits0, before `closed ok`,
parent terminal or final halt. This matches sys-init's retained initial delayed
failure. The result is an actual guest owner invariant failure, not a missing
tool, input collector error, expected semantic rejection or watchdog. The fresh
delayed normal image and immediate diagnostic image pass their own exact oracles.
No root cause or fix follows from those passes.

One concrete candidate merits a deterministic witness. `Session::poll` first
observes a peer as nonterminal, then invokes channel read or write. Those are
separate traps and user execution/timer preemption can occur between them. A peer
may terminate after the observation and before transfer; native `finish` closes
its endpoints. A read can then return EOF0 or a write EPIPE-32, while the owner
currently requires positive progress (aside from EAGAIN). The kernel itself does
not promise that a terminal observation and later transfer are atomic. The same
poll code is in Aether's fixture and sys-init's borrowed dispatcher.

This is a source-derived hypothesis, not the identified failing line. Next build
a bounded test that forces terminal publication between the observation and
transfer, with separate read/write and still-live malformed/closed-peer controls.
If confirmed, re-observe the exact task before accepting a terminal-related
transfer outcome; do not treat EOF/EPIPE alone as successful settlement, relax
positive-byte bounds, retry an ambiguous frame or reclaim on stop acceptance.
Keep the owner stack bound and matching older-profile regressions. A producer
fix/handoff here must then be explicitly consumed and qualified by sys-init;
no sibling policy change or generic recovery framework is justified.

Full composition acceptance stays open. The canonical009 runtime dependency and
missing actual entry are resolved; the reproducible owner failure is the next
local diagnostic priority. Independent SDK review, cleanup-negative coverage,
maintained recipe, persistence and native packages remain separate gates.
