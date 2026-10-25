# Owned ABI24 serial session prototype

This opt-in sys-init entry validates009/ABI24 boot arguments, delegates bounded
SESSION dispatch and confirmed settlement, then requests owner-only halt.
It admits one shell, never automatically restarts its effects, and does not use
the ABI22 Backend/Runner/Command table. The kernel enforces actual holder/grant
rights. Dispatch shares the supervisor trusted computing base/failure domain.

`dispatch/` is an explicitly borrowed source copy from the sealed producer archive
in provenance.json. Seven reachable modules are retained. The selected source
removes the borrowed entry and panic handler, exposes one inline settlement/failure
boundary, and adjusts pipeline imports for module placement. The inline boundary
avoids a second large session frame. The local read path additionally reobserves
terminal state on EOF before existing cleanup (decision0184). Original source/history is preserved
in the sealed archive; no sibling or released standard is modified.

The fixed userland client owns runtime/bootstrap/FD semantics. Sys-init owns entry,
no-restart policy and final action. The settlement function returns only after
observed parent/child terminals, pipe/reference/backing reclamation and checked
console closure. Transport/ownership uncertainty takes the existing failed-owner
path, with no successful halt or replay. This is not recovery from arbitrary
service failures. Existing synchronous trap/buffer lifetimes remain in the dispatcher.

The prototype is assembled privately from the exact sealed wait-aware userland kit,
replacing its owner only. It consumes qualified kernel/client bytes rather than
source-rebuilding the kernel or SDK. The maintained offline candidate recipe is documented in
../../docs/AETHER-SESSION.md; never rerun an evidence
script into an already retained output directory. The native case drivers and
exact argv are retained by decision0183.

The borrowed linker keeps a stricter16KiB code limit within the24KiB profile and
requires no writable statics. Actual composed linked inspection is mandatory;
producer stack estimates do not carry over. This is a private single-core serial
shell with finite SESSION identities/lifetimes and fixed program/memory facade,
not login, persistence, general TTY/jobs/signals, unrestricted program loading,
package lifecycle or a complete v1 distribution.

The first native immediate/delayed positives and denial controls are recorded,
and a final-helper terminal/read-EOF interleaving is now reproduced and repaired.
Fresh native immediate/delayed and forced-interleaving workloads pass. Actual
wrong-endpoint errors and synthetic live-peer EOF still reject. The exact caller
of the first historical failure is unavailable; compatible reproduction is not
proof of exact attribution. The maintained recipe is qualified; full composition remains open.
See ../../docs/SERIAL-SESSION-ACCEPTANCE.md for scoped denial coverage. See BG-067 and docs/decisions/0184-terminal-transport-interleaving.md. The existing
ABI22 builder/profile/pins remain unchanged.
