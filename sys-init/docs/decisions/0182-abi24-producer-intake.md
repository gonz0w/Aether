# 0182: Recognize qualified ABI24 mechanisms and the remaining client boundary

Date: 2026-10-03. Scope: BG-067 producer evidence intake, not runtime adoption.

[Retained intake](../evidence/abi24-producer-intake-2026-10-03/README.md) verifies
three producer packets and distinguishes final witnesses from incomplete attempts.
AENMX009/ABI24 now has lifecycle, selected SESSION owner and endpoint waiting
producer evidence. The [composition guide](../SERIAL-BOOT-COMPOSITION.md) no longer
labels those kernel mechanisms unsealed. Actual sys-init ownership and matched
wait-aware userland payloads still need consuming evidence.

The observed idle defect lies in the client's finite EAGAIN polling loop, not an
absent owner wait. Userland must bind a wait-aware client to009, preserve partial
frame offsets and explicit EINTR/signal handling, and qualify real dash with delayed
input. No endless polling, raised iteration budget, ABI22/23 fallback or borrowed
numeric grants can satisfy that requirement. Independent SDK review is a promotion
claim, separate from authorized bounded coding/integration.

Simplicity: the simpler next step is consuming the existing bounded dispatch with
one genuine sys-init policy/entry. Choose it over a new privileged process server,
service graph or general restart framework. Client waiting removes the selected
polling cutoff rather than adding init workarounds; legacy fixtures stay unchanged.
No runtime path is removed now. The inspected producer owner has only224 bytes
of estimated stack headroom, so actual composition must be inspected again rather
than inheriting its footprint claim. Dispatch remains in the owner TCB/failure domain.

Foundations O-01–05, I-01/03–06 and E-01–08 apply. Distribution boot transport and
candidate service semantics remain separate. This review updates documentation,
coverage and the current work order; it creates no ABI, unsafe/FFI, authority,
new dependency, operator command or presentation behavior. Released pins and
historical evidence stay fixed; no runtime or other-platform tests are necessary.
Remaining work is the matched client delivery and sys-init composition/recipe/
native acceptance described in the guide. Full protocol, assembled-v1 publication
and independent review remain separate.
