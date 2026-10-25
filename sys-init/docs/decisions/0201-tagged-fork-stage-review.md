# 0201: Narrow the next work to an authenticated tagged fork transaction

2026-10-22 / BG-067. Source-only intake of new libc61/predecessors and process15
(18 deliveries/570 member hashes), unchanged linked v2 580 members and seven
pinned source excerpts. Research is in docs/research/TAGGED-FORK-STAGING.md.
No native code or wire is selected by this review.

Libc/startup wiring components now exist; producer reports the complete shell link
fails only on __aether_fork_stage. Our old stage cannot carry the new tagged128
map. Kernel copy success resumes parent before a subsequent local view clone,
whereas current ProcessFiles.inherited_child requires parent frozen through it.
Do not silently violate that precondition or assert a new kernel primitive is
needed. BG-069 captures the exact owner ordering/wire/child transition decision;
BG-070 captures its minimal implementation/link/native witness follow-on.

The simpler alternative is supplying a linker stub or pasting the old stage.
Both misrepresent required state. Choose concrete source review and bounded
transaction requirements; no new runtime/ledger or generic framework. No existing
accepted path is removed. Current implementation is blocked on that matching
contract, not on the existence of libc helper symbols. This review supplies no
independent owner agreement, C/native execution or replay of producer link claims.

Documentation impact: update the existing handoff/current state/quality gap and
open question. Run full offline checks. Preserve source/evidence/default/release
pins; no sibling writes/messages, guests or quota changes. The exact source audit,
raw input identities and validation are retained in the evidence packet.
