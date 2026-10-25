# Session runtime independent review handoff — UL-007 / UL-081

Prepared2026-09-29. Reviewer identity and disposition are **pending**. This task's
technical audits and passing tests do not supply an independent reader walkthrough.

Review [current boundary](../SESSION-SDK-BOUNDARY.md) and the sealed
[serial consumer](../evidence/serial-session-consumer-2026-09-29/README.md), including
source-review.md, exact inputs/source reconciliation,35 bound raw/ELF owner images,
11 native comparisons,151 checker controls, cancellation and retained correction.
Its702-member manifest digest is
`485c32579591d9ff3001c82fea6705e1a7a56fdb8d052da94a73ebaeda2d55a4`.

Then inspect the [SDK boundary audit](../evidence/session-sdk-boundary-2026-09-29/README.md):
exact accepted ELF relink, strong-provider maps, omitted memory fallback, missing
facade/process and duplicate controls, _DYNAMIC sentinel correction and all receipts.
The mutations are static evidence; no mutant native behavior was accepted.

Check owner-only UART and generation references, per-peer FD/pipe holders, actual
EAGAIN/short progress, prompt boundaries, independent streams and confirmed
terminal/reclaim. Trace public/internal mask state, native libc rebind and strict
memory-protection failure through actual musl callers, including ignored upstream
errors. Confirm bounds and unsupported cases at each claimed scope. Read source
and disassembly where necessary; neither source counts nor successful tests prove
security or whole-program stack safety.

Walk through cold offline preparation, missing/stale inputs, failure evidence,
archive recovery and exact next action from current STATE. Record actual commands,
findings, reviewer identity, source/artifact digests and disposition in a new review
record. Do not rewrite sealed evidence, infer approval or reuse the older UL-005
SDK/package review as approval for this native session runtime. Independent owner
runtime delivery and assembled-target acceptance remain separate prerequisites.

## Assigned runtime candidate — 2026-09-29

The maintainer assigned implementation to userland after this checklist was
prepared. Review the [extracted candidate](../evidence/session-runtime-extraction-2026-09-29/README.md),
its bundle seal/recipe, application policy boundary, startup guard, eight pre-effect
bundle controls and49 fresh native/independent comparisons. Inspect retained
build/metadata corrections and exact rebuilt ELF equality. Reader identity and
disposition remain pending; implementation ownership is now agreed. This new
checkpoint does not retroactively approve prior reviews or full SDK/R1 acceptance.

## Builder minimum-version follow-up — 2026-10-03

Review the [Python3.10 repair](../evidence/session-runtime-python310-2026-10-03/README.md)
and its new exact candidate seal alongside the prior support-module fix. Both
minimum/current interpreter builds reproduce native-qualified whole ELF hashes;
20semantic controls preserve denial and cached-module isolation. This is actual
local technical evidence; independent reviewer identity/disposition stays pending.

## Maintainer deferral — 2026-10-03

The maintainer will perform SSDK-06 reader review later, after lab boot work, and
explicitly directs continued coding. Reader evidence remains pending; this does
not pause local implementation or tests. No retrospective independent approval
or release exception is recorded. [Bootable lab-kit evidence](../evidence/lab-image-2026-10-03/README.md)
is available for that later walkthrough.
