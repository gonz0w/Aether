# Abnormal termination and owner cleanup — 2026-09-07

This fixture tests owner cleanup when the cat conformance client's finalization
never runs. Isolated UD2 faults occur after validated startup, first copy write or
first diagnostic write. A separate owner-controlled stop occurs after the first
committed write but before its reply is sent. There is no Toybox image or callback.

| Case | Terminal detail/kind | Input consumed / stdout / diagnostic bytes |
| --- | --- | --- |
| Fault before input | 134 / 2 | 0 / 0 / 0 |
| Fault after copy write | 134 / 2 | 11 / 11 / 0 |
| Fault during diagnostic | 134 / 2 | 0 / 0 / 16 |
| Owner stop after copy write | 143 / 3 | 11 / 11 / 0 |

The owner requires all three remote aliases still live and request EOF, verifies
exact backend prefixes and unchanged input, closes its own backend handles and
checks stale denial before reclaiming both native instances. Two generations
produce four reclaims. Native child poll/stop/collect reject EBADF after reclaim.
The forced-stop case first requires live reclaim EBUSY; repeated stop must retain
the identical observed terminal tuple. No pending reply is sent after stopping.

Normal exit134 substituted for fault, wrong stop kind, corrupt prefix and skipped
backend close require owner1501/1501/1505/1506. The intentional UD2 has no operands
and no return path and is confined to the test client. Existing kernel authority,
ABI, resource limits and dependency identities are unchanged. Sys-init and userland
retain supervision and termination policy. See [contract](contract.md) and
[native reference](../../NATIVE-CAT.md#abnormal-termination-and-owner-cleanup).

## Reproduction

Run `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use `--connections` and `--inherited-launch` with the same SDK/lock for regressions.
Host: `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Scoped Clang21/Rust2024 formatting and workflow checks accompany the runs.

## Attempts and limits

[Attempt1](attempt-1-triage.md) passed three fault cases and reached100/reclaimed4
on forced stop, then failed a new serial-log expectation. The existing native stop
path emits no client terminal line. The corrected harness requires exact backend
terminal lines and100/reclaimed4, while preserving direct owner143/kind3 checks,
repeat-stop stability and the wrong-kind control. The failed source-matched archive,
receipt, timing and raw logs are retained. No new kernel marker was introduced.

These are selected interruption points, not exhaustive fault injection or production
supervision. Actual Toybox/SDK initialization and callback/flush/exit adaptation,
independent consumer pin/build and CAT acceptance remain open. No assembled R1
readiness follows. Release pins, prior UL-059 bundle and siblings remain unchanged.
Run boundaries are retained; per-case timing, independent review and extended
coverage remain unavailable.

## Qualification

Final attempt2 passes all 211 command cases (203 prior plus eight new). Six
connections and nine inherited-launch regressions pass, together with 98 Python
host tests, Zig tests, offline pins, workflow and scoped formatting checks. All
three final receipts match frozen runtime sources. The 34 kernel/build inputs and
SDK/libc/tool-lock identities match the preceding finalization qualification.
Largest new owner: 6,472/8,192 bytes. No limit increased.

The failed first attempt is retained with matching sources and triage; no failure
was discarded. final-artifacts.tar.gz retains final frozen sources, compiled
clients/backends, argument artifacts, native envelopes and raw logs. ISOs, duplicate
installed boot files and kernel.elf are omitted with identities retained in
receipts. Both archives' source and argument bytes are independently rechecked.
Qualification/timing files and manifest bind the evidence. The prior UL-059 bundle
artifacts remain byte-identical; archive identity is not consumer acceptance.
