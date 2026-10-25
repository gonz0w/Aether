# SI-07 matched intake and local producer replay — 2026-10-03

The missing-input blocker is closed. Aether's new matched AENSI001/ABI22 packet
is available for sys-init-owned integration. This intake verifies identities and
replays the producer owner; it does not yet execute the sys-init owner or accept
all SUSTAIN-01–06 requirements.

## Verified inputs and execution

All1,800 userland sealed members and382 Aether sealed members verify. Aether's
final source archive is unpacked locally and every file checked against its source
manifest. All3,592 available artifact files verify against their recorded hash and
length; eight archived symlink targets match metadata and are not materialized or
followed. `verification.json` binds both seals and the artifact archive. Retained
copies are a selected subset, not a replacement for either complete upstream seal.
No source or build uses a mutable sibling tree after staging.

The pinned userland v2 runner/bytecount ELFs are retained. The producer positive-5
ISO is restored from the verified archive under out/si07-intake. Pinned local QEMU
and firmware hashes are checked before replay. Its original serial driver is used
unchanged with a local working directory and output prefix; commands and raw serial
are in replay/. It completes five actual useful cycles with ordered0/0/17 terminals,
3044 total/3004 idle ticks,15 reclaims and authorized halt. Existing guest assertions
verify exact6-newline backend output. No additional producer controls were reexecuted
here; the nine comparisons/66 corruptions and other boundary results remain producer
claims tied to the retained packet.

An intake-only first attempt compared unpacked firmware against the compressed
archive digest and stopped before QEMU. The correct unpacked_sha256 field matches
both local firmware files; intake-attempt1.py retains that error. The corrected
intake and native replay pass. No runtime source, released pin, ABI or sibling file
changed. Aether updated its own backlog while this intake began; no stale status
was written over the new checkpoint.

## Consumer review and next implementation

Use existing fixed paired owners for backend/runner/command. Preserve the explicit
ABI22 grant tuple and protocol v2 selection; no v1 fallback. Native instance/channel
identities remain full-width. The private cohort epoch is1..65535, validated before
publication; exhaustion must reject before admission, and cohort mismatch must
settle actual owned peers without inventing successful command output.

Keep a complete cycle before admitting another. This bounds live resources without
turning the acceptance test's five-cycle counter into a production lifetime rule.
Use the selected serial authority for request input; snapshot before checking input,
then compare/park to avoid lost wake. Final halt needs separate authority, settled
protocol references, observed terminals, closed channels and closed UART. A successful
stop request alone does not permit reclaim; finish(100) is not shutdown in ABI22.

For the first consuming slice, accept shutdown at quiescent command boundaries.
Do not interrupt/replay an issued backend effect to serve shutdown. Retain partial
frames until complete; malformed, lost or ambiguous replies fail closed and must
not yield a clean-shutdown claim. General asynchronous cancellation, poisoned-close
recovery and serial queuing across an in-flight command remain outside that slice.
These are explicit integration limits, not claims that the producer has qualified
every partial/reordered schedule.

Next implement the opt-in ABI22 binding/protocol hooks in sys-init's existing
command-owner path, then freshly build/run idle, five useful cycles, cleanup/halt,
cohort/exhaustion rejection and relevant omission controls. Review the linked stack
for the actual consuming image: producer maximum3832/4088 is not our stack proof.
Preserve ABI9/ABI17 defaults and run their affected compatibility checks. Independent
userland replay and full SI-07 acceptance remain separate outstanding dispositions.

SE-01–05: reusing the bounded owner is simpler than adding a new service manager;
the existing ABI17 fixture cannot provide sustained wait/final action. Select only
the required new boundary and remove no historical path. O-01/04, I-01/03–06 and
E-01–08 govern scoped authority, no ambiguous replay and frozen evidence. Distribution
identity/native-runtime scope stays experimental. No standards exception or pin
upgrade. Documentation impact is the existing handoff, BG-067, current plan and
quality inventory; runtime/native-boundary inventories are unchanged.

## Local validation

All ten gates pass in `run-3lg789q4` with unchanged checked sources. All three
released lock hashes remain unchanged; `git diff --check` passes. The fresh native
producer replay is retained separately from these local checks. Maintained runtime
code is unchanged; no sibling repository was modified in this intake.
