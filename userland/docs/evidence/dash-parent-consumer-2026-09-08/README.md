# UL-007 direct-launcher parent consumer — 2026-09-08

PASS: all 295 native command cases run locally from the completed parent-identity
snapshot. The [native receipt](native-results.json) retains the original case
inventory, build flags, tools, artifacts and outcomes. The [outer receipt](results.json)
records exit 0 and complete owned-process cleanup. No failed local attempt.
All 545 scaffold/overlay source files and 4311 reused SDK files retain their hashes.
The local quality gate passes; quality.log retains its scoped result.

The [four independent serial checks](parent-cases.json) confirm the new cases:

| Case | Exact native result |
| --- | --- |
| Parent query, client slot 0/backend slot 1 | Client 0/backend 17, two generations, owner 100/four reclaims |
| Swapped client slot 1/backend slot 0 | Same statuses and two generations in swapped order, owner 100/four reclaims |
| Parent route disabled | Client 104, owner 1501, exact rejected-profile panic |
| Self-PID substitution | Client 104, owner 1501, exact rejected-profile panic |

Negative cases report zero native reclaims and do not qualify recovery. Outer
process cleanup is a separate observation. Raw logs for all 295 cases are in
cases/; parent-cases/ retains the four focused observations. These are command
regressions, not 295 full dash scripts.

The unchanged guest fixture checks actual musl getppid, dirty unused registers,
parent/worker separation and generated dash PPID=4. The root supervisor checks
its own PID=4 and parent=0. Worker identities vary with placement/generation;
parent lifetime is fixed. The query grants no capability and introduces no parent
table. Reparenting, orphan behavior and native-thread parent semantics are excluded.
Disabled profiles retain ENOSYS; the old init diagnostic still expects PPID=-38.

Selected producer packet: shell-parent-2026-09-08, manifest SHA256
`cf8529a67ffc99eb31856d7369c22fd46f2ffdfefb0ff9121d7d631986ce8f56`.
All 26 manifest entries were checked before consumption and again at retention.
The 217-member source archive is verified before private extraction. The retained
producer-packet/ subset includes the source, final receipts and two earlier
producer attempts; packet-retention.json names the verified target archive omitted
from this copy. Producer failed attempts are not local failures and remain intact.
The producer's seven M4 regressions and 98 host tests are separate evidence; neither
suite was rerun or promoted to a new local result here.

[Intake comparison](intake.json) identifies ten changed scaffold files relative
to the prior 291-case consumer. All 32 imported dash objects are unchanged and
remain Linux-configured reference inputs with upstream terms. No fresh dash/libc
source build or native configuration qualification is claimed. SDK reuse is bound
to sdk-reuse-receipt.json and the prior verified tools; the recipe checks matching
libc identity. Runtime client/owner/kernel sources are built with the original
producer recipe and oracles, without local runtime edits.

Run: `python3 -B docs/evidence/dash-parent-consumer-2026-09-08/run.py` with the
recorded dependencies. Private output: `build/dash-parent-consumer-g7jdua6v`.
The one-off driver retains exact executed source and uses the existing owned-process
helper, controlled PATH/LC_ALL/private TMPDIR, 1800-second outer deadline, existing
guest watchdogs and a 512 MiB outer stream bound. Actual interpreter: Python 3.14.7;
syntax compatibility is not minimum-version execution. [Review](review.md) records
test selection, ownership, source review, simplicity and remaining review gaps.

Next UL-007: validated launcher-supplied user/group metadata, then scoped directory/
CWD support. Generated init still diagnoses unsupported geteuid, empty PWD and the
exact getcwd warning. Actual main, external command/failed exec/wait, redirection/
pipeline/EOF and cleanup remain unqualified. No new startup probe or optional
utility expansion. UL-007/M3, UL-016, UL-063 and independent reader/technical review
remain open; no sibling source, released pin or consumer default was changed.
