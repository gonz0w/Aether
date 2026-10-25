# UL-007 AECAT002 consumer qualification plan

2026-09-08, before execution. Selected producer shell-user-metadata-2026-09-08,
manifest b34cc35c104bfab28d7d53225517599c19fdf83b4f6a49632e8e937a1d7b627b.
Reproduce the original 309-case command suite on a private verified snapshot and
matching reused SDK. Preserve sibling source, public defaults and released pins.
Applicable previously read PROCESS, Foundations O/I/E, Distribution NC/PX/ID,
adopted TD/TC/TE/CP and the local METADATA.md consumer checklist remain in force.

Codex reviewed captured decoder/getters/client/owner changes against the qualified
parent snapshot: read version header before body; validate all descriptors and
metadata before caches/readiness publish; getters gate on startup_ready; legacy
selection retained; sender closes truncated/version headers and accounts for the
writer already closed. Zero effective UID is checked against input-write and
PID-based stop denial. Actual initvar selects PS1 with an empty environment.
The public-signal failure oracle preserves descriptor/mask readiness while dropping
only the inapplicable signal-action EAGAIN expectation for that selected profile.

Select all 309 existing native cases because shared bootstrap parsing/admission
and owner cleanup changed. Require exact original case inventory and semantic
oracles, matching source/SDK/libc/tools, unchanged hashes after execution, outer
exit 0 and complete cleanup. Reuse the existing owned-process helper, controlled
PATH/LC_ALL/private TMPDIR, 1800-second deadline and 512 MiB outer stream limit;
retain guest watchdogs and all logs/attempts. No fresh host-kernel/M4 claim.
Fourteen new cases: valid/zero UID, eleven invalid/version records and skipped
publication. Independently check their serial terminal order, statuses and reclaim
counts. Accepted invalid inputs should return110 with four reclaims; publication
mutation rejects105/1501 with zero native reclaims, not a recovery claim.

Checklist limits identified before the run: identity_unpublished does not reset
errno between individual getters; raw credential assertion covers only geteuid;
truncation covers16 bytes of metadata; mismatch senders close after header rather
than queue an incompatible full body. Existing malformed-descriptor cases do not
automatically qualify their V2 composition. Report these as partial coverage,
not a defect proved by inspection or grounds to waive the later required cases.
Map all twelve checklist rows to exact selected labels after execution.

Simplicity: reuse the snapshot and original runner, without another startup probe
or decoder implementation. No runtime path removal; reference objects and prior
receipts remain unchanged. Runtime provenance and independent execution are not
full source/reader review. Preserve the prior native-main ENV configuration gate.
Run quality and executed-driver syntax/identity checks; update planning/coverage.
UL-007/M3, raw credential completeness, CWD, full main/processes and UL-016/063/081
remain separate follow-ons. Final results belong in README/results, not this plan.

## Actual disposition

Original309-case native suite passes on one local attempt with complete outer
cleanup and unchanged source/SDK inventory. Final14-case serial checks against the
completed hashed receipt pass. The incomplete early log inspection is retained;
its original failing observed list was not saved, so its cause is not promoted to
a proven runtime failure or proven log-read race. No oracle or source change.
Quality and driver syntax/identity pass. Codex reviewed the source changes and
maps twelve consumer rows to seven bounded-evidence/five partial dispositions.
Independent technical/reader approval is still pending. The five coverage gaps
remain work, and bounded reproduction is not full metadata-contract acceptance.
