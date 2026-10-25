# Public wait4/wait3 candidate — 2026-09-10

This private native build now links musl1.2.6 wait3.c unchanged to a narrowly
adapted wait4.c. The latter rejects non-NULL rusage at entry with ENOTSUP before
computing output addresses or making a request; NULL-rusage calls use the existing
retained-result adapter and musl's errno conversion. No accounting values are invented.

Pinned dash jobs.c calls wait3(status, flags, NULL). This packet supplies that libc
entry point, but does not execute dash's waitproc loop, SIGCHLD/sigsuspend handling,
job control or external commands. Installed SDK files and sibling repositories are
unchanged; independent intake is still required.

| Case | Target evidence |
| --- | --- |
| wait4 | Specific-PID pending, errors, EFAULT/drain/retry, normal collection, repeat ECHILD |
| wait3 | Actual -1 normal collection through upstream wait3 -> wait4 |
| wait3-fault | Actual child #UD translated to SIGILL, no core bit |
| wait3-broken-ack | Malformed consumed ACK returns EIO; mask restored, next call emits no traffic |
| wait4-usage-bad | Omitting accounting rejection requires parent82/owner1950 and zero reclaims |

Every new positive checks both APIs with sentinel and invalid-address non-NULL
usage pointers before normal waiting: ENOTSUP, no status/usage writes and no protocol
request. Four positives repeat two generations with child72 (or kind2/detail134 for
#UD), parent71/backend17 and six reclaims. Specific-PID checks use wait4; wait3 is
called for the -1 collection path. The malformed-ACK case retains consumed owner
state, full status output before EIO and poison without replay. The known partial
output/ACK ambiguity contract is unchanged. The negative control must fail precisely;
a generic panic, missing runner or watchdog is not acceptance.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#public-wait4wait3-selection--2026-09-10)
records scope, forbidden results, authority/ownership, resource and simplicity
choices. Existing bounded owner/protocol/kernel code is reused without change.
Only harness and C client runtime sources change; no new service, kernel ABI,
allocation, dependency version, global state or pointer-store mechanism is added.
Legacy waitpid objects and profiles remain intact pending SDK integration.
Cancellation/EINTR, SIGCHLD, stopped/continued jobs, accounting, transactional exec,
full dash and independent consumer acceptance remain open. R1 is unfinished.

Commands, timings and source/tool/SDK identities are retained beside this record:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Link maps and disassembly identify actual wait3/wait4 objects and their adapter
calls. Upstream source/COPYRIGHT and the reviewed dash call site are retained with
hashes. The collector verifies the prior sealed packet and simplicity snapshot,
freezes source identity and reads back source/target archives. All159 older payloads
are compared outside entropy and their kernel images exactly. Prior failed attempts
remain in their original packets. Only affected full connections and launch suites
are rerun; earlier full command/M4 evidence remains historical.

Final qualification passes164 connections, five launch cases and host checks,
including98 Python tests plus Zig/pin/workflow checks. Final documentation/inventory
checks rerun the host suite successfully. No qualified attempt failed in this slice;
prior failures remain retained in earlier packets. All suites met review budgets.
Archive readback verifies226 sources and3,152 target artifacts. All159 older payloads
match outside entropy bytes32–79; their kernel images and the backend are identical.
Maximum owner remains6,648 of8,192 bytes; owner source and binaries are unchanged.
