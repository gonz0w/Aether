# UL-007 AECAT002 consumer qualification — 2026-09-08

PASS for the delivered bounded profile: all 309 native command cases run locally.
The [native receipt](native-results.json) binds exact original cases, compiler/linker
flags, artifacts and results. The [outer receipt](results.json) records exit0 and
complete owned-process cleanup. All545 source and4311 reused SDK hashes remain
unchanged. The local quality gate passes; quality.log retains its scope.

[Fourteen final serial checks](metadata-cases.json) independently verify the
completed receipt and raw log hashes:

| Selected cases | Native observation |
| --- | --- |
| Distinct IDs and zero effective UID | Client0/backend17 in two generations, owner100/four reclaims |
| Eleven malformed/version cases | Client110/backend17 in two generations, owner100/four reclaims |
| Skipped metadata publication | Client105/owner1501 and exact rejected-profile panic; zero native reclaims |

The unchanged guest asserts four distinct getter values per generation, actual
initvar PS1 selection from effective UID, correct PPID, and denied input writes/
PID-based stop even for effective UID zero. Source/flags/reserved, each sentinel
ID, stale header, shortened metadata and both version directions are exercised.
The V1-receiver mismatch has no V2 getter facade; V2 cases check caches/getters
unpublished. Values are advisory developer metadata, not authentication or grants.
Raw geteuid remains ENOSYS; broader raw credential coverage is not inferred.

## Coverage disposition

The [checklist mapping](coverage.json) records seven rows with bounded native
evidence and five partial rows. Remaining observations are independent errno
checks before each getter, V2 malformed-descriptor/rights composition, header/body
truncation boundaries, queued incompatible-body teardown and raw getuid/getgid/
getegid. The inspected code is not thereby shown defective; the evidence does not
cover those complete requirements. The309 total is a command-regression count,
not309 full dash workloads or complete AECAT002 acceptance.

Directory/getcwd still emits the expected upstream unsupported warning. The
[full-main configuration gate](../../../experiments/dash-native/METADATA.md#full-main-configuration-gate)
also remains: current Linux-reference objects omit the source-conditional ENV
identity guard. Actual main, external command/failed exec/wait, pipes and M3 are
not qualified by the bounded initializer.

## Attempts and provenance

The native suite passed on its first local attempt. An early secondary serial
inspection raised an error while the suite was running; the failing observed list
was not saved. [That incomplete inspection](serial-inspection-attempt-1.json) is
retained with its uncertainty. A later read showed the expected record. The final
checks ran only after suite completion, compare receipt-bound logs, retain expected
and observed lists, and all14 pass. No runtime oracle or fixture was changed.
The producer's separate pre-execution Rust type-error attempt is retained in its
packet and is not local target coverage.

Producer manifest SHA256:
`b34cc35c104bfab28d7d53225517599c19fdf83b4f6a49632e8e937a1d7b627b`.
All17 sealed files verify before consumption and retention. producer-packet/
retains source/receipts/attempt evidence; packet-retention.json lists target
archives omitted after verification. [Intake](intake.json) identifies eight changed
files from the previous parent snapshot. Kernel/build and32 imported dash objects
are unchanged. No fresh dash/libc build, host kernel suite or M4 result is claimed.

Run: `python3 -B docs/evidence/dash-metadata-consumer-2026-09-08/run.py` with the
recorded dependencies. Actual interpreter: Python3.14.7. The existing owned-process
helper enforces the1800-second suite deadline and512 MiB outer stream bound, with
controlled PATH/LC_ALL/private TMPDIR and the original guest watchdogs. Outputs
remain under `build/dash-metadata-consumer-j4_v0t9a`; all case serial/QEMU logs are
retained here in cases/. SDK reuse and tool identity are bound to the prior receipt.

[Review plan](review.md) records source/authority/cleanup review and limitations.
Independent technical/reader sign-off and broader UL-063/minimum-version/source
review remain open. Next: close the five focused coverage gaps and consume scoped
CWD support, preserving the separate native-main configuration decision. UL-007/M3,
UL-016/063/081 remain active. No sibling edit, consumer-default or release-pin change.
