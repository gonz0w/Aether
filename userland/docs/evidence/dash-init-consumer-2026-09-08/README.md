# UL-007 dash signal/init consumer reproduction — 2026-09-08

PASS: all 291 native command cases run locally on the captured generated-init
snapshot. The [native receipt](native-results.json) retains the exact case
inventory, compiler/linker flags, artifacts and outcomes. The [outer receipt](results.json)
records exit 0 and complete owned-process cleanup. No failed or interrupted attempt.
Source hashes for all 545 scaffold/overlay files and all 4311 reused SDK files
remain unchanged. The local quality gate passes; its retained log is quality.log.

Selected producer: `shell-dash-init-2026-09-08`, manifest SHA256
`51058b97d7da8f37a2af56e42da8ca5a857cc100b605828a513c38d874a3cd24`.
All 11 sealed packet files were verified before consumption; the selected source,
receipt and manifest subset is retained in producer-packet/. The source archive
contains 211 hash-checked regular files. Target archives were verified but are
not used as substitute execution evidence. Prior scaffold and SDK receipt hashes
are bound in results.json; sdk-reuse-receipt.json retains the latter's full input
and tool inventory. No fresh libc build is claimed.

The [four dash observations](dash-cases.json) independently check exact serial
lifecycle/rejection records in addition to the unchanged producer suite:

| Case | Native observation |
| --- | --- |
| Real dash signal routines | Client 0/backend 17 in two generations; owner 100/four reclaims |
| Skipped CHLD setup | Client 102, owner 1501 and exact rejected-profile panic |
| Real generated initialization | Client 0/backend 17 in two generations; owner 100/four reclaims |
| Skipped initialization | Client 103, owner 1501 and exact rejected-profile panic |

Negative cases report zero reclaims; they are not successful cleanup/recovery
witnesses. Outer emulator/process cleanup is checked separately for the suite.
Raw serial/QEMU logs for all cases are retained in cases/; dash-cases/ supplies
the focused four-case copies. Source-built fixture clients, owners and kernels
use the original recipe and oracles. The [32 dash objects](dash-object-check.json)
match earlier userland native-link inputs exactly and are reused unchanged.
They retain Linux reference configuration and upstream terms; this is not a
fresh dash source build or full native configuration qualification.

The initializer assertion requires PPID `-38`, empty PWD and raw unsupported
geteuid while IFS/OPTIND/CHLD initialize. The owner checks exact diagnostic bytes:
`sh: 0: getcwd() failed: Function not implemented\n`. This demonstrates the
missing contracts; it does not accept those values as valid process identity.
Private SIGCHLD invokes actual dash onsig; public child notification is not proven.

Run: `python3 -B docs/evidence/dash-init-consumer-2026-09-08/run.py` on the recorded
Python 3.14.7 host with retained dependencies. The one-off executed driver reuses
the existing owned-process helper and prior verified scaffold. Private output:
`build/dash-init-consumer-gusow7bq`; full build artifacts remain there. The suite
has an 1800-second deadline, existing guest watchdogs and a 512 MiB outer stream
bound. [Pre-execution review](review.md) records selection and limits.

No fresh host kernel-test/M4 qualification, full source audit or independent
reader sign-off is claimed. UL-063 source migration, UL-016 source trust and
broader review remain open. These are 291 command cases, not 291 dash scripts.

Next UL-007: consume a completed truthful-parent delivery, then launcher-supplied
user metadata and scoped directory/CWD support. Qualify actual main, external
command/failed exec/wait, then redirection/pipeline/EOF and cleanup against the
prepared twelve workloads. No new startup probe, optional utility expansion or
sibling implementation was added. UL-007 and M3 remain active.
