# UL-007 next shell workload packet — 2026-09-07

Prepared twelve candidate native scripts from the existing retained reference
cases. Verified every record in the reference summary, then removed only the QEMU
helper prefix. Original script identities and expected output/exits are preserved
in the [manifest](../../../experiments/dash-native/workloads.json). The
[handoff](../../../experiments/dash-native/WORKLOADS.md) specifies logical namespace,
argv/environment, helper build, stage ordering, negative controls and cleanup gates.

Static adaptation check passes; native execution NOT RUN. No new full-dash delivery
was found in Aether STATE/evidence during this check; the completed startup pair
retains its222 local results. Full-dash work is reported in progress by the user.
No sibling edits or messages were sent. This packet is ready for owner agreement
and independent execution once the matched delivery exists, not a new shared API.

Review: Codex checked all twelve original scripts and the current helper, exact
exit/stdout mapping, absence of emulator execution in candidate scripts, inherited
WITNESS requirement, denied-path assumptions, 4096-byte helper buffer and16 MiB
bounded EPIPE loop. No runtime/helper behavior changed. Foundations O/I/E and
quality TD/TC/TE apply. Independent technical/reader review remains pending.
The current helper is newly content-pinned; no historical source identity is inferred
from reference command labels. Original evidence remains unchanged. Full UL-007/M3,
source trust and package acceptance stay open; quality results retained here.
