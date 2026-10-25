# UL-007 consolidated dash consumer — 2026-09-10

PASS: all **431 native command cases and six connection regressions** reproduced
locally. **71 independent final serial checks** pass, covering every 30 added cases
and the 41 previously selected checks. Both owned executions exited 0 with complete
host cleanup. All 551 assembled source and 4311 SDK file hashes stayed unchanged.
One local native attempt passed; no local retry or interrupted attempt.

[Command receipt](native-results.json), [connection receipt](connections-results.json),
[outer execution receipt](results.json) and [independent checks](regression-cases.json)
retain exact commands, compiler flags, tools, ABI/artifacts, expected/observed terminal,
supervisor and panic records. All 437 serial/QEMU log pairs are retained in cases/
and connection-cases/. Guest output/masks/description assertions remain the original
reviewed native oracles; serial checks independently verify their lifecycle outcomes.

## Newly qualified scope

- Backend open/read/close zero-byte EOF, 16-byte partial EOF and silence poison
  delivery without publishing uncertain results or replaying operations. Late-open
  reply observation leaves unread bytes for confirmed-stop cleanup. Omitted-stop
  controls reject with owner 1601 and zero native reclaims. Positive recovery
  observes client 1/stream 17 twice and six reclaims; forced service stop has no
  normal slot-2 exit marker. The owner checks the actual terminal stop status.
- Actual dash main loads ENV with equal IDs and suppresses it for mismatched UID,
  mismatched GID, noninteractive startup, absent ENV and empty ENV. Deliberately
  selecting the old unguarded main detects policy failure with owner 1598.
  Unsupported `-p` rejects with exact native diagnostics and status 2.
- The unchanged syntax-error script bytes execute via dash `-c`: empty stdout,
  native syntax diagnostic, status 2 and four reclaims. Skipped execution and
  omitted closes are detected. This qualifies that bounded workload, not all
  twelve shell scripts.
- The unchanged userland helper runs as a separate child through the existing
  explicit image launcher: spaced argument, literal `*`, WITNESS, exact eight-byte
  `argv ok` line, private TLS, child/parent status 0 and six reclaims. Corrupt argv/
  environment, skipped helper body and omitted closes are detected. Dash itself
  does not yet launch this helper through fork/exec/wait; DASH-argv remains open.

The command backend now uses 4096 polling attempts; generic transfer retains
100000. This is not a wall-clock latency guarantee. The six connection regressions
exercise the changed shared transfer implementation. All 30 new owner images fit
8192 bytes; [maximum is 8152](owner-size-checks.json). Bounds were not increased.

## Reproduction and provenance

Run `python3 -B docs/evidence/dash-helper-consumer-2026-09-10/run.py` with the
recorded pinned dependencies. Actual interpreter: Python 3.14.7. Private output:
`build/dash-helper-consumer-0_56kqe5`. The command deadline is 1800 seconds and
connections 300 seconds, each stream limited to 512 MiB. Original guest watchdog
and native guard remain. PATH/LC_ALL/private TMPDIR and host cleanup are recorded.
[Review](review.md) was written before execution; [input comparison](intake.json)
records 17 changed files, no kernel/build changes, and 32 unchanged dash objects.
The separate ENV-enabled main stays pinned; helper bytes match the local reference.
[Consumer input identities](consumer-inputs.json) distinguish exact syntax input
from the helper launcher prerequisite.

Selected producer manifest SHA256:
`92b0c1abf626679479343614c25daf1a85af412b6041229bd3a791802366f971`.
All 29 entries verified before use; producer-packet/ retains selected sources and
receipts. Target archives are verified at the producer location but omitted here;
packet-retention.json lists them. Four [intermediate producer histories](producer-history/inventory.json)
retain original failures and source snapshots. Their earlier failed compile,
watchdog/native-guard and size attempts remain separate from this passing run.
No new SDK build, minimum-interpreter, fresh host-kernel/M4, installed SDK, real
prefix installation, sibling change or released-pin adoption is claimed.

## Remaining work

The [public-wait producer packet](next-public-wait/README.md) is verified and ready
for a separate source/dependency review and independent native intake. It includes
bounded public fork callbacks and retained normal-exit waitpid; it is **not run
locally here**. Its 147 connections/five launch results are producer evidence only.
Non-normal wait outcomes, reply failures, dash wait4/wait3, exec/vfork and full
external-command/pipeline/redirection/recovery workloads remain gates.

UL-007/M3 remains active. Source trust (UL-016), independent technical/reader review
(UL-061–063), integration/configuration complexity (UL-081), TTY and persistence
remain open. This packet advances bounded acceptance without closing those gates.

Final verification: local quality inventory check passed; source-audit/reader/
publication gates remain separate. Executed driver, SDK receipt and both native
receipts match recorded hashes. Retained drivers compile on Python 3.14.7.
Changed tracked documentation passes `git diff --check`. See [verification](verification.json)
and [quality output](quality.log). SHA256SUMS binds the retained packet bytes.
