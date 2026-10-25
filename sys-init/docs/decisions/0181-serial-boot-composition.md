# 0181: Select one matched serial SESSION boot composition

Date: 2026-10-03. Scope: BG-067 source/contract review and local work order.

Select the [smallest serial boot composition](../SERIAL-BOOT-COMPOSITION.md):
one shell, one boot supervisor authority domain, sys-init policy plus matched
userland runtime dispatch, and Aether-enforced idle/wait/halt. This adopts a
bounded integration direction, not an unsealed native ABI or a sibling fixture
as the sys-init implementation. Aether's sealed design review supplies the same
authority/profile finding; our [capture](../evidence/serial-boot-review-2026-10-03/README.md)
verifies that record and retains source-current divergence during implementation.

A simpler alternative is running008 unchanged as a brief demo. Its healthy tick,
iteration, parent-count and finish gates cannot serve a manual prompt. ABI22 alone
lacks the SESSION copy/exec/memory/pipe closure. Choose a narrowly selected producer
profile reusing established mechanisms and one authority owner; do not introduce
a delegated process server, new resource quotas, generic restart or another
service graph. No maintained path is removed now. The eventual composition should
remove test-driven startup/finish policy from its selected normal path while
preserving old fixtures as compatibility evidence.

Profile IDs and grants come only from a qualified producer contract; changing
source names/magic or linking code cannot establish authority or compatibility.
Co-location shares the dispatcher/owner trusted computing base and failure domain.
No automatic retry of shell effects follows from the private bytecount retry proof.
Unknown cleanup retains ownership and blocks admission. The guide names exact
matching delivery and consuming acceptance, including code/stack review and fresh
native controls. Userland's SDK promotion and independent release review remain
separate claims, with no invented owner acceptance.

Foundations O-01–05, I-01/03–06 and E-01–08 apply. Distribution B-01–04 define a
separate transport; SV-01–05 do not transform our native table into a shared service
format. Preserve all released pins, prior evidence, machine protocols and output
contracts. This review adds no runtime, unsafe/FFI, dependency or presentation
change. Portability boundaries remain explicit; no additional OS campaign runs.
Documentation impact: composition guide, delivery map, current work order,
BG-067, adoption notes and quality inventory. No public command changed, so the
command documentation inventory needs no new entry.
