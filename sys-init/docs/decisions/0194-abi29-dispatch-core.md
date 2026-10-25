# 0194: Consume corrected ABI29 v2 and prepare dispatcher identity/wait core

2026-10-21 / BG-067. Userland now supplies corrected linked v2 parent/helper
inputs. Independently verify all580 outer/574 bundle members, selected images
and exact corrected header. Close the old boot-parent/absent-linked-input blockers
without promoting a shared SDK or claiming shell execution. Preserve all old
serial, AF06, AF07 and v1 evidence/defaults/released standards pins.

Prepare the transport-independent part of the matching sys-init dispatcher:
32-byte AEFSH001 startup with actual shell1/children2–4 identity, genuine boot
parent7, seven-domain PIDs and unchanged three-child wait reservation/delivery/
reclaim barriers. Reject engine0/spare5/owner6, invalid/nonwrapping generations,
noncanonical handles and mismatched parent observations before returning a frame.
These checks validate trusted dispatcher bookkeeping, never confer native grants.
An eventual caller must bind them to actual admission observations and the exact
owned live channel. No filesystem token/path/descriptor gains native authority.

The simpler alternative is to relabel old ABI24 startup frames or clone its entire
1246-line dispatcher and six-domain assumptions. Neither satisfies the versioned
startup/identity contract. Choose one small explicit startup encoder and a scoped
compatibility copy of the proven three-child ledger with only PID width changed.
No generic broker or lifecycle framework is needed. Nothing obsolete is removed
while immutable old delivery remains consumed. The copied ledger is deliberately
bounded; it does not absorb transport, native enforcement or filesystem policy.

Validate the actual Rust-produced frames against the exact sealed v2 C decoder
with strict C17/UBSan: all3 shell/135 copied-child cases, forged parent/memory/PID,
old/new framing and unchanged failed output. Host Rust tests cover startup bounds,
malformed/canonical identities and all retained child state/partial-reply barriers.
Compile/format/lint with pinned Rust1.98.0/2024; emit native objects only as a build
check, never call them native runtime/stack/authority acceptance. Keep exact tools,
source/input/output hashes and original failed attempts. Run full local checks.

The core cannot yet be connected to an honest persistent shell: userland's AF07
FD/path/immutable executable contract and client delivery remain missing. Keep
startup directory/FD/copy/exec transport adaptation pending those inputs; do not
reuse the old RAM scratch/directory fixture as filesystem-backed behavior. Aether
must later compose the full matched owner/client with fit, failure/cleanup and
fresh native command/readback witnesses. No VM or sibling write/message here.

Applicable Foundations O-01–05, I-01/03–06, E-01–08 and Distribution RL-01/02/05
preserve authority, finite bounds, input closure and scoped claims. No new shared
ABI or exception. Document impact: current state, corrected-parent research,
prototype guide, integration/boot handoff and quality inventory. Independent
reader/release review remains separate; no sign-off is invented.
