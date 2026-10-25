# UL-007 actual dash command and script consumer — 2026-09-09

PASS: all369 original native command cases reproduced locally. The
[native receipt](native-results.json) binds exact commands, tools, artifacts and
case inventory; the [outer receipt](results.json) records exit0 and complete owned
process cleanup. All549 source/4311 reused SDK hashes remained unchanged. One local
native attempt passed; no local failed or interrupted execution.

[Nine main/file serial checks](main-cases.json) and [18 metadata serial checks](metadata-cases.json)
pass against completed receipt digests and exact expected lifecycle/rejection records.
All369 serial/QEMU logs are retained in cases/. The [metadata mapping](metadata-coverage.json)
now records bounded evidence for all12 selected rows; the five previously partial
observations are addressed within their stated fixture/boundary limits.

## Actual execution scope

This consumes the first completed AECAT004 read-only file-root bridge and intervening
metadata/directory/main deliveries. Main calls are real dash initialization, parser,
evaluator, builtin and exit paths. The wrapper admits startup and supplies a controlled
PWD=/work, LC_ALL=C, no-ENV environment; it does not pre-run init or the old probe.

| Case | Required result |
| --- | --- |
| Actual `sh -c "printf 'dash-main\n'; exit 7"` | Exact dash-main newline, empty stderr/input, client7/backend17; four reclaims over two generations |
| Same command with independent file-service composition | Same output/status, service file probes/closure; six reclaims |
| Actual `sh hello.sh` | Real open/read/parser execution, exact hello newline, client0/stream17/file17; six reclaims |
| Skipped main/root publication | Exact client0/client2 and owner1501 rejection, zero reclaims |
| Omitted facade/remote close | Exact owner1503/1599 rejection despite client7/client0, zero reclaims |
| Substituted service file / omitted precondition close | Owner1596/1597 before client terminal, zero reclaims |

The script case checks one F_DUPFD_CLOEXEC allocation at or above10, actual service
reads and no live file records. Names and CWD metadata confer no file authority;
AECAT004 grants a separate basename-only read root. Two connection-local file
descriptions share offsets through aliases under existing signal masking. Existing
16 facade FDs, backend slots/generations and native resource limits are preserved.
`sh hello.sh` does not invoke an external child or demonstrate the source builtin's
PATH/stat search. The file service is an immutable fixture, not persistent storage.

The independent serial checks verify completed receipt digests and exact terminal/
supervisor/panic records. Command output, file transactions, masks, errno and raw
getter assertions remain the reviewed original guest/owner oracles. Zero-reclaim
mutants detect errors; they do not establish successful recovery. Outer emulator
cleanup is a separate observation.

## Remaining work

V4 admission corruption/version/truncation, independent opens, exhaustion/stale
references, adversarial alias offsets, malformed/lost replies and confirmed service
stop cleanup remain unqualified. Unexpected backend failures currently reject the
fixture; recoverable ambiguous outcomes are not implemented or accepted.

The separately selected main object enables the upstream UID/GID ENV guard. Its
retained enabled object equals the candidate linked here. Actual ENV loading versus
suppression, unsupported -p, login/launch policy and authenticated identity remain
separate requirements. No security conclusion follows from this no-ENV run.
Existing userland argv/signal/syntax and external-child/exec/wait/redirection/pipeline
workloads remain NOT RUN. UL-007/M3, source trust UL-016, source/reader review UL-063
and native configuration/integration UL-081 remain open.

## Provenance and reproduction

Producer shell-file-root-2026-09-09 manifest:
`d42fc56af2eab7262ad9cc07fcaa3a5ee3b0f2a3f1c523bbedce7478c6330b9f`.
All14 manifest entries and source members verify before use. producer-history/
retains nine verified predecessor packets, including main-object build inputs,
queued-body and file-composition failed attempts. Each retention inventory names
verified target archives omitted from this copy. Old evidence is preserved; no
producer failure is relabeled as a local attempt or successful cleanup.

The original32 reference dash objects are unchanged. Explicit main cases substitute
a separately pinned enabled main.o, preserving the other31 objects and upstream
terms. Generated headers are captured build inputs, not independently regenerated.
No fresh dash/libc source build or source-authentication claim. main-provenance.json
binds the candidate to the archived build receipt.

Kernel/build changes select six reclaims only for the new opt-in runner-files test
profile, requiring runner-local; native ABI and pool limits are unchanged. The full
local command suite exercises old and new selections. Producer's seven fresh M4
regressions are retained as producer evidence; they are not a local M4 reproduction.

Run `python3 -B docs/evidence/dash-file-consumer-2026-09-09/run.py` with the pinned
SDK/tools on observed Python3.14.7. Exact compiler flags, ABI, tool paths/hashes,
commands and artifacts are in the native receipt; the outer receipt binds controlled
PATH/LC_ALL/private TMPDIR, 1800-second deadline, 512 MiB stream bound and cleanup.
Full builds remain under `build/dash-file-consumer-wlqucht1`. Reproduction checks
source and SDK hashes before/after and preserves original case order and oracles.
Minimum-interpreter and broad source qualification are not inferred.

[Review](review.md) records pre-execution selection, scope, bounds, failure oracles,
simplicity and pending independent technical/reader review. No sibling/default/pin
changes or milestone closure are selected.


## Intake and verification limits

[Intake](intake.json) records20 assembled-source differences from the last local
bootstrap snapshot. Eighteen are selected packet files; docs/NATIVE-C.md and
tests/test_build_policy.py come from the hash-verified historical scaffold because
this producer archive omits them. They are not selected runtime inputs. Every
source named by the producer command receipt matches the assembled snapshot.
No local host/build-policy test result is inferred from those scaffold files.
The current producer M4/host receipts and failure history remain separately labeled.

Final quality gate, driver syntax/receipt identity, retention/checker syntax and
tracked-document whitespace checks pass. The quality gate checks pins/inventory
structure; pending independent technical and reader review remains separate.
