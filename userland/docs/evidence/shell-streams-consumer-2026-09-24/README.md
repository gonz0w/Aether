# UL-007 serial forwarding consumer qualification

All **105 native capacity cases and110 Python host tests pass**, plus required
Zig/Rust host checks. Seven prior parent/early-reader lifecycle checks and four
independent serial controls pass. Native and host execution each passed first
attempt; retained collector/acceptance failures are described below.
[Acceptance](acceptance.json) binds the scoped result.

Real dash runs long stdout/stderr builtins, a parent-created pipeline and long
follow-up output in three fresh shell generations. Each positive or corrupted
run has nine exact command events/prompts,15 successful terminals,12 image
admissions and15 reclaims. The positive combined UART stream matches exactly;
returned pipeline prompts follow all three child terminal records. Expected data
per generation is178 stdout bytes and75 stderr/prompt bytes. This is a combined
UART observation, not independent stdout/stderr capture or full SESSION acceptance.

The corrupted native run completes and reclaims normally, but the host rejects
exactly `pipeline UART output mismatch`. Independent comparison requires exact
`PiPe data` in place of `pipe data`, with every other byte unchanged. A crash,
timeout, panic or missing cleanup cannot pass this control. Wrong UART grant
rejects2795/reclaims0 before a prompt; disabled006 rejects before admission.

Serial owner bytes match the sealed17960-byte audit: reviewed critical stack
depth3888/4088 leaves200 bytes, compared with88 in the prior serial profile.
This is scoped linked-path inspection, not a whole-program stack proof. Native
authority, frame bounds, EAGAIN, short transfers and holder closure remain required;
only script-specific capture state was removed. Fixed job topology still remains.

## Inputs, selection and limits

Consumed Aether shell-streams-2026-09-24, SHA256SUMS digest
`e1eed328c23cd77b8c2f1a86708bd1a4e2b84612552ffe4b808be3f1a5291756`.
Entire producer and prior consumer seals were verified before restoring source.
Final287 runtime,306 host inputs and12 review inputs were overlaid onto the
verified prior scaffold. All658 source/support/metadata and4311 SDK files stay
unchanged. The six producer-pinned consumer SESSION inputs match local bytes.
Tools, SDK, process helper, driver and plan identities are retained in preparation.
Large producer artifacts archives remain in the original sealed packet; this local
copy retains its source archives, reports, audits and failed-attempt descriptions.

Only output.rs and the capacity/pipeline console harness paths changed. Fresh
selection is full105 affected capacity cases and110 host tests. Earlier898-case
consumer regression remains **prior qualification, not a rerun**. All105 locally
rebuilt kernel runtime images match the earlier archived consumer: ELF identity,
entry, program headers, load payloads and nondebug sections. Full ELF hashes differ
in nonallocated debug sections; no whole-file reproducibility claim is made.
See [kernel investigation](kernel-review.md) and the complete comparison.

Native elapsed362.21 seconds meets the1800-second review ceiling. Owned outer
limits are3600 seconds native,300 host and512 MiB per stream; existing guest
watchdogs are unchanged. All process cleanup is complete. No sibling source,
released standard, installed SDK, existing script/helper or native resource cap changed.

## Retained local failures and corrections

1. The independent collector initially expected only the first p to change in
   `pipe`; the native one-byte corruption branch changes both. Original checker
   and failure log remain; the exact corrected literal passes without native rerun.
   The first dependent acceptor failed because the collector result was absent.
2. Whole-file kernel equality failed on all105 images. All-pair archived analysis
   established equality of runtime bytes and isolated the debug differences. The
   original comparison and failed accept log remain. Final acceptance uses the
   reviewed narrower claim, not a silently changed hash baseline.
3. A shell command list started compaction despite a failed acceptance precheck.
   Compaction verified every archive member and unchanged original before removing
   duplicate outputs. All1773 suite files remained available in the archive for
   investigation. No failed native evidence was lost. See kernel-review.md.

Independent owner/reader approval remains pending. These corrections are not
native failures, but this packet does not claim every local check passed first try.

## Retention and next action

run.py supports fresh prepare/host/capacity replay; existing timing files prevent
overwriting attempts. retain.py/check-serial.py verify completed logs; compare-kernels.py
reads verified archives; accept.py requires their successful evidence. All105 serial
logs, QEMU logs and serial exchange events are retained. The generated suite and
its compiler cache were compacted with hash/size/mode readback checks, reclaiming
761,028,608 allocated bytes (725.8 MiB). Preserve source, SDK and prior archives.
Final quality, whitespace, Python syntax, source/SDK, retained input revisions,
archive and prior-packet integrity checks pass; see [validation](final-validation.json).

The twelve-script matrix remains12/12. SESSION-01–06 has NOT RUN. Aether's newer
session-channel delivery is a prerequisite with no native caller yet; it is not
consumed or accepted here. Next consume the implemented whole composed.sh session
with its frozen lifetime/authority controls and matching regressions. Shared SDK,
independent reviews, TTY/general signals, filesystem, packages and sys-init/R1
assembly remain open.
