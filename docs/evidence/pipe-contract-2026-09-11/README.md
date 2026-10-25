# Pipe contract and implementation review

Completed the design step selected by STATE. The authoritative
[local contract](../../NATIVE-SHELL-STARTUP.md#bounded-pipe-and-command-substitution-contract--2026-09-11)
chooses a bounded owner-local FIFO, authenticated endpoint holders and one-child
command substitution within existing worker/channel limits. No runtime code was
changed. Native pipe acceptance is NOT RUN; the prior 254-case redirection packet
remains the current runtime evidence.

The critical ordering comes from the verified dash sources: expand.c reads to EOF
before waitforjob; eval.c closes unused ends and redirects child stdout. A child
writer retained until wait acknowledgment would deadlock. Current copied-child
exit0 and pre-exec I/O handling also need explicit changes. The design specifies
those boundaries, versioned opt-in records, strict publication, terminal-based
retirement, unknown outcomes, resource bounds and negative cases. It does not
pretend that 16-byte frames provide full POSIX pipe atomicity or that EPIPE alone
qualifies signal behavior.

Reviewed inputs are preserved under inputs with their existing notices. The four
dash C files match the prior frozen reference-sources.json digests. Userland's
captured STATE records independent serial-dash acceptance and requests the next
repeated-child handoff; this review does not rerun or approve its consumer tests.
Production facade/service ownership remains separate from Aether's private fixture.
No sibling repository, released pin, SDK object, kernel or runtime source changed.

Checks for this documentation-only change: verify prior evidence/input hashes,
local links and source inventory; run workflow, standards, experience, distribution,
simplicity-snapshot checks and `zig build test`. No unrelated QEMU run is needed.
`checks.json`, source hashes/snapshot and the final manifest record the results.
The implementation acceptance cases in the contract are planned tests, not passes.

External reference discovery used the Open Group pipe/read pages and an explicitly
labelled older write reference. Direct fetching of the Issue 8 pipe/write pages
returned 403; indexed primary-source results supplied pipe/read context. No missing
Issue 8 write text was guessed or vendored, and no mutable remote standard became
a build input. Failed source-path lookups during review were corrected to the
pinned reference inventory before copying/validating the actual files.

Next implement the owner/adapter and endpoint retirement, with real parent/child
probes, then actual dash substitution. Signal delivery, full atomicity, arbitrary
pointer handling, asynchronous cancellation, two-child pipelines, external/file
redirection and assembled R1 acceptance remain explicit gaps.

All six commands in `checks.json` passed, including `zig build test`. The 255-file
source snapshot was read back and verified; runtime/build inputs remain unchanged.
Introduced local links pass. The first full-file link scan stopped on a pre-existing
sibling backlog link; the failed attempt and the corrected scope are preserved.
`local-links.json` inventories existing unresolved targets separately.
