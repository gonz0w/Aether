# Authoritative file view v1 — UL-007/081/082

Additive `ProcessFiles::file_view_v1(process)` supplies the read-only metadata
requested by sys-init Decision0202/BG-071. It reads the existing private descriptor
array; there is no second FD ledger or cached flag copy. Old APIs, sealed
candidates, defaults and released pins remain unchanged.

## Contract

Input is an opaque current Process key, obtained only after the existing trusted
admission/authenticated observation. The result is `Result<(u16, u16), ProcessError>`:
`(presence, cloexec)`. **Bit n means remote FILE FD n**, not logical map slot n.
Only bits3..15 may be set; bits0..2 are zero. Cloexec is a subset of presence.
An empty view is `(0, 0)`; full presence is `0xfff8`. Duplicate aliases have
independent flag bits and may share one description/offset. All four process
views are supported. Streams/console/pipe selectors are separate domains.

Active source and exact current key are validated before the read. Stale, foreign,
settled/replaced keys return existing Stale; retired/unknown source returns
Files(Retired), never an apparently valid empty view. Exactly thirteen bounded
iterations produce four bytes of inert metadata. No heap, persistent state,
source/native callback, flag mutation, offset change, exec-close or cleanup.
Inspection does not retire or settle anything. No new error or callback type.

## Owner composition

The owner holds exclusive admission from snapshot capture through actual copy,
local inheritance, child context-ready and parent disposition. During pre-copy
capture, derive claimed presence and cloexec from the **complete** validated tagged
FILE map and compare both complete u16 masks for equality with file_view_v1.
An omitted/extra FILE selector, a flag difference, flags on holes or unused low
bits must reject before copy. Do not mask away claim bits or normalize parent
flags. Stream/source holdings/history still require their own actual comparison.

For example, actual remote FILE3 and15 with only15 flagged produces
`(0x8008, 0x8000)`. Claimed `(0x8000, 0x8000)`, `(0x8008, 8)` or
`(0x8009, 0x8000)` must fail. A caller may not trust the two masks sent by a client
or use a prior export after mutation. This API supplies metadata, not the final
owner gate, snapshot authenticity, per-open generation tokens or native authority.
The consumer must enforce exact comparison and the no-interleaving window.

## Qualification and remaining boundary

[Evidence](../evidence/filesystem-file-view-2026-10-22/README.md) records31 actual
process-profile host tests (26 retained/five new),13 compiling semantic controls,
borrow-reentry compiler denial and external host/target no_std consumer builds.
New controls omit high slot, omit flags or select the wrong process view. Default
remote-profile regressions also pass. Strict Rust2021, unsafe denial, pinned
rustfmt/default Clippy; generic x86_64-unknown-none libraries only. Host tests use
real AF07 service/Owner with synthetic storage and scripted native outcomes.

Matching sys-init consumption/comparison, actual stream gate, complete native
copy/refusal/ready/parent and terminal/endpoint/holder settlement/readiness/shutdown,
whole resource fit and fresh Aether witnesses remain required. No native execution
or affected-owner approval follows. Full UL-007/082/M3/R1, immutable exec/public
dup2/wider shell/Zsh/TTY/packages/ISO and independent reader remain open.
