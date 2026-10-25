# Malformed and truncated cat replies — 2026-09-07

This producer conformance fixture tests an operation committed by the owner whose
response cannot be trusted by the client. Each of read, write, diagnostic write
and input close receives either a complete reply with corrupt reserved byte4 or
only16 reply bytes followed by actual response-channel closure. The client must
poison transport, return1 (usage64), retire local bindings, and receive EBADF on
repeated local closes without another channel trap. The owner independently rejects
any subsequent request at1532 and observes the remaining remote aliases.

| Operation | Input position | Stdout bytes | Diagnostic bytes | Remote aliases still live |
| --- | --- | --- | --- | --- |
| Read | 11 | 0 | 0 | All three |
| Write | 11 | 11 | 0 | All three |
| Diagnostic | 0 | 0 | 16 | All three |
| Input close | 32 | 32 | 0 | Output and diagnostic |

Each sink matches the exact source prefix; input storage is unchanged. The owner
waits for terminal EOF before backend cleanup, stale-handle denial and four native
reclaims across two generations. A truncated response endpoint is already closed;
its repeated native close must return EACCES, distinct from local POSIX EBADF.
There is no inferred remote acknowledgment from local table retirement.

The three deliberately broken clients force zero status, omit local diagnostic
close or clear poison before cleanup. Exact owner rejections are1501/1501/1532.
Instrumentation is opt-in CAT_UNKNOWN and counts actual channel traps, including
partial transfers. No new kernel ABI, quota, dependency or production recovery
policy is introduced. See [pre-code contract](contract.md) and
[native reference](../../NATIVE-CAT.md#malformed-and-truncated-replies).

## Reproduction

Run `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use `--connections` and `--inherited-launch` with the same SDK/lock for regressions.
Host: `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Scoped Clang21/Rust2024 formatting and workflow checks accompany the runs.
The shared transport header retains legacy formatting for narrow instrumentation.

## Attempts and limits

[Attempt1](attempt-1-triage.md) failed because the new native stale-close oracle
expected EBADF rather than the established EACCES. It reached client status1 then
owner1506; this was not an accepted negative case. Its source-matched archive,
receipt and logs are retained. The expectation was corrected before attempt2.

[Attempt2](attempt-2-triage.md) passed every new cat case, then exposed an older
pad-launch-eof observation race: request EOF after admission could precede the
parent terminal poll and produce990 instead of exact104/970. The negative control
now yields/re-polls only in that state within its existing bound. Production EOF
behavior and required rejection remain unchanged. Its source-matched archive,
receipt and raw logs are retained. Attempt3 reruns the full suite.

These are conformance-client tests, not actual Toybox, callback/flush acceptance,
general unknown-result reconciliation or an assembled release. EINTR, finalization
re-entry, abnormal-stop coverage, native Toybox/SDK integration and independent
consumer review remain open. Release pins, UL-059 bundle and siblings are unchanged.
Run UTC boundaries are retained; per-case timing, independent review and extended
coverage remain unavailable.

## Qualification

Final attempt3 passes all 193 command cases (182 prior plus 11 new). Six
connections and nine inherited-launch regressions pass, as do 98 Python host
tests, Zig tests, offline pins, workflow and scoped formatting checks. All three
final receipts match frozen runtime sources. All 34 kernel/build inputs and
SDK/libc/tool-lock identities match the preceding complete-error qualification.
The largest new owner is 6,056/8,192 bytes; no limit increased.

Only pad-launch-eof.raw changed between attempts2 and3; 162 other owner binaries
are byte-identical, as recorded in control-scope-check.json. The fixed control
produces the unchanged exact parent104/owner970 oracle. Both failed attempts remain
in this directory with source-matched archives, receipts, logs and triage.

final-artifacts.tar.gz retains final frozen sources, compiled clients/backends,
argument inputs, native envelopes and raw logs. ISOs, duplicate installed boot
files and kernel.elf are omitted with their identities retained in receipts.
Archive source and argument bytes are independently checked. Qualification,
timing and manifest files bind this scoped evidence; no consumer sign-off follows.
