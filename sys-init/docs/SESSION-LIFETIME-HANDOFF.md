# SESSION lifetime dependency for a usable serial shell

2026-10-04 / BG-067. **Ready local producer request; not sent and no sibling
repository modified.** The bounded developer candidate already boots to a shell,
runs commands and halts. The blocker below concerns continued ordinary use,
not basic boot or a request to add general service-manager machinery.

## Observed limit

The exact009/ABI24 kernel/client closure supports fifteen lifetimes per child
slot. In a fresh sys-init-consuming VM, fifteen sequential `/inputs/helper closed`
commands succeed and are collected. The sixteenth attempt reaches the local
SESSION participant generation guard and returns -13. Normal owner policy then
fails, with no parent completion, another admission or authorized halt. A private
probe after that local denial confirms the actual kernel copy operation returns
-28 for the same exhausted child slot. No quota was reduced or generation seeded.

Evidence: [finite and cleanup controls](evidence/session-limits-2026-10-04/README.md),
[acceptance matrix](SERIAL-SESSION-ACCEPTANCE.md). The first two unaccepted traces
lacked the expected result marker; they remain retained. The final control binds
both local denial and the distinct producer quota result.

Read-only companion review on2026-10-04 found the kernel's STATE still explicitly
retains fifteen SESSION lifetimes under the serial lifecycle handoff. Userland's
ABI24-SESSION-HANDOFF qualifies this bounded009 closure; its newer recipe/denial
consumer records do not deliver a wider lifetime profile. ABI22 sustained command
cohorts are a different interface and cannot be imported into009 silently.
Companion excerpts/hashes are retained with the control packet. Builds still use
offline pins, never those mutable checkouts.

## Requested owner delivery

Aether should choose and document the smallest explicit SESSION profile/configuration
that permits continued normal child-slot reuse beyond this demonstrated limit.
Keep monotonic, nonwrapping identity and stale-handle rejection, real reclamation/
zeroing before reuse, current owner/grant boundaries, compare/register waiting
and quiescent halt. State practical process/channel/pipe lifetime bounds and
exhaustion outcomes. Do not reset epochs under live references, widen authority,
invent recovery or raise sys-init stack/code budgets to mask the constraint.

Userland should deliver matched bootstrap/PID/FD/pipe/endpoint-wait/runtime artifacts
for that exact identity profile, including source/SDK/CRT/tool/notice closure,
compatibility and ordinary repeated-helper witnesses. A larger kernel counter alone
cannot authorize changing `Children`, pipe participant bounds or application identity
arithmetic here. Sys-init will then consume the frozen contract and update only the
necessary local bounds/encoding, preserving no-replay and known-cleanup policy.

Acceptance for the next delivery: one parent stays alive and retains state; at
least sixteen real sequential external helper invocations complete with exact
streams/status and fresh identities, cleanup permits another ordinary command,
and shell exit still produces confirmed settlement and owner-authorized halt.
Exercise the newly selected final boundary/stale references and preserve old
profiles. Full indefinitely running sessions, general TTY/jobs/signals, persistence,
recovery and broader service configuration are separate work, not this request.

## Current stop point

Selected malformed-component, write-EPIPE, partial-cleanup and finite-exhaustion
controls are locally qualified. Further recovery or enlarging native lifetimes
without a matching producer contract would exceed this repository's authority.
The bounded developer build/boot recipe remains available unchanged. Independent
assembled/reader review and publication authorization remain separate gates;
no sign-off or supported distribution release is inferred.


Independent userland consumption now qualifies all eleven selected negative
controls; see [decision0189](decisions/0189-serial-negative-consumer-review.md).
Its exact producer seals match. This closes the supplied consumer witness gap;
the current fifteen-lifetime profile and wider matched-delivery requirement remain.
The final private exhaustion owner is15,464 bytes; the immutable packet README's
15,416 is an intermediate-size typo, not a changed code budget or artifact.
