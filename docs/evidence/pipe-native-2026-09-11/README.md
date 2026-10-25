# Native pipe producer probe

The [pre-code plan](PLAN.md) scopes the private adapter and actual copied-process
experiment. The final focused preflight passes the positive case and three semantic
negative controls. Complete matching suites pass on the final sources.
No installed SDK, public pipe(), SIGPIPE or dash substitution is claimed.

Commands, using the existing frozen SDK/tool receipt:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The first compile failure and initial ABI expectation rejection are preserved under
attempt-1/attempt-2, with their exact original source snapshots. The focused
preflight rebuilds only the changed pipe inputs using dependency artifacts from
the second attempt; it is separate from the fresh complete suite qualification.
No failed attempt or unrun scenario is counted as a pass.

Verified duplicate cleanup removed eight superseded unpacked directories after
archive readback, per-file hash/identity comparisons and clean open-file checks.
Their approximately 3.1 GiB of allocated file blocks are recorded in cleanup.json;
archives, source snapshots and failure reports remain. Original temporary paths
in receipts are provenance, not live prerequisites. Final qualified outputs remain.

## Final results

| Check | Result |
| --- | --- |
| Complete connections suite | 251 QEMU cases pass |
| Launch and console regressions | Five launch and two console cases pass |
| Pipe positive | Exact 320-byte transfer, real full-buffer wait, EOF before waitpid, child/parent exit0, backend17; six reclaims |
| Premature EOF | Parent90 then owner2163, zero reclaims |
| Retained terminal writer | Child0 then owner2164, zero reclaims |
| Malformed create result | INT32_MIN becomes EIO/poison without FD publication or retry; parent92 observed before pipe retirement and deliberate owner2167 abort |
| Host/process | Full host suite, Rust/C format, workflow, three pins and simplicity snapshot pass |
| Incompatible profiles | STARTUP_FILES/FORK_EXEC combinations fail with the named diagnostics |

The pipe owner image is 9088 bytes; the suite maximum is 9944 bytes,
within the existing 16 KiB bound. The linked image limit and target run do not
measure worst-case stack depth or establish general performance/reliability.

The final records include exact commands, start/end times, source/tool identities,
images and raw logs. Archives were read back and hash-verified. Earlier harness
receipts retain their historical timing scope. No immutable evidence, kernel,
SDK object, sibling repository or released standard pin was modified.

Attempt-1 preserves the unused-witness compile failure. Attempt-2 preserves the
ABI17/ABI9 entry mismatch. Attempt-3 passed its 250 native cases but review rejected
unsafe negation of an unvalidated signed error; it is superseded, not final
qualification. Attempt-4 preserves the malformed-reply fixture's missing TLS
segment and loader rejection. Checking initialized TLS before its early-exit
branch fixes that fixture without weakening the loader. All attempts and both
successful focused preflights remain separate from final suite results.

Normal exit0 is the positive lifecycle covered here. Public pipe()/SIGPIPE,
partial/lost replies, abnormal in-flight cleanup, native copy rollback, pipe reuse
within one shell lifetime, actual dash substitution and installed-SDK acceptance
remain unqualified. The malformed-reply control stops the deliberately corrupted
fixture; it does not prove service continuation or automatic recovery. Existing
serial shell regressions remain passing, but R1 is not assembled.

Scripts retained in this packet are audit artifacts. Do not rerun them inside the
sealed directory. Use the documented live commands with new output directories.
