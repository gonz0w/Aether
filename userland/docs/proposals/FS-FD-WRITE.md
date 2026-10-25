# Tagged stream output — UL-007/081/082

`aefd_routed_write` adds opt-in output routing over the [same tagged map](FS-FD-BINDINGS.md)
and [mixed alias lifecycle](FS-FD-STREAMS.md). Pipe and console entries reach an
explicit trusted writer by kind/selector. File entries are read-only and return
private -30, including zero-length writes; they never reach stream callbacks or
introduce an AEFD0001 opcode. This is a local proposed API, not libc/POSIX errno
interposition, a selected shell/startup, native binding or accepted sys-init API.

All input/map/client/workspace storage is valid, disjoint, exclusively accessed,
serialized and nonreentrant throughout the call. The owner supplies the decoded
canonical map, matching authenticated process/channel/source and live client with
borrowed4096-byte workspace. Shape/numeric selectors do not convey native rights.
Callbacks must not mutate map/client, retain the borrowed buffer or reenter.
Actual native authority, liveness, deadlines and settlement remain owner duties.

| Boundary | Result/effect |
| --- | --- |
| Nonzero count with null input, or count>4096 | -22 before source effects |
| Missing/retired client or released workspace | -5 before source effects |
| Invalid/stale table identity | Retire file admission, -5, no writer call |
| Missing logical FD | -9, no writer call |
| Read-only file entry | -30, clear workspace, no file RPC or stream fallback |
| Missing writer callback | -38, clear workspace, no successful no-op |
| Known complete1/count0..requested | Return exact count, including short/zero; clear workspace, no loop/retry |
| Known complete1/negative private errno | Return unchanged, clear workspace, retain live admission |
| Unknown/invalid completion or out-of-range count/errno | Retire file admission once, -5, no replay |

After validated lookup, clear workspace and copy requested bytes into it before
the one writer call. The callback receives const staged bytes; caller input and
map remain unchanged. Zero-length stream writes still invoke the source with
count0. Valid errno range is -2147483647..-1, complete must equal1. Explicit known
zero result on a positive count is zero progress, not fabricated completion of
the requested bytes. Higher layers must decide how to handle progress safely.
Argument/missing-FD rejections occur before workspace use; they do not promise to
clear preexisting unrelated workspace data.

An unknown write may have produced output already. It must never be retried or
interpreted as zero bytes sent. File-client abort zeroes/releases its workspace
and records raw file endpoint close results; it does not close/revoke native
streams, settle tasks or prove supervisor shutdown. Owner reconciliation and
actual stream cleanup remain required. No4096-byte automatic production buffer,
allocation, second descriptor ledger, automatic wait/retry or source policy.

## Qualification

```
python3 -B experiments/filesystem-service/check-fd-write.py
```

Eighteen cases per C child use real host pipes for full4096/short/zero output,
known-error continuation, unknown with and without actual bytes, invalid complete/
count/errno, readonly file including zero, missing adapter/FD, stale generation,
argument bounds and console-tag forwarding. The console-tag case writes a host
pipe, not an actual console. Completion/errors are injected observations; host
write/read/close and observed byte counts are real. Caller input, workspace,
unchanged map, once-only retirement/no replay and explicit pipe EOF/EBADF cleanup
are independent checks. No destructive exec, pipe creation API or native driver.

The child also runs all fourteen predecessor stream-lifetime scenarios unchanged,
then the269 live C/Rust file cases through mixed delegation. Rust service policy/
source fixtures stay pinned and use synthetic storage. Six compiling omissions
require specific C assertions plus observed failed C child: file fallback, accepting
unknown, accepting over-count, missing staging, missing post-call clearing and
missing stale retirement. Generic compiler/sanitizer/watchdog failure cannot pass.

Actual Python3.10.21/3.14.7 qualify strict C17/format/UBSan, Rust2021/default Clippy/
rustfmt/unsafe denial and exact source/tool/resource/runtime/host-header closure.
All inputs are pinned before consumption and relevant closure rechecked afterward.
Owned clean environment,60s compile/30s live suites and16MiB output bounds remain.
[Evidence](../evidence/filesystem-fd-write-2026-10-21/README.md) retains every owned
attempt, including earlier successful scope before healthy-error continuation and
more precise stale control. Source-only candidate:
`build/service-deliveries/filesystem-fd-write-2026-10-21-v1`.

Selected shell/startup and actual native console/pipe adapters, pipe creation,
native copy/failed-exec parent/FD preservation, immutable image admission and full
code/stack/heap/workspace/backing/channel fit remain open. Sys-init owns full
matching dispatcher/readiness/shutdown, Aether native command/error/cleanup/fresh
boot evidence. Independent owner/reader and full UL/M3/R1/POSIX/TTY/Zsh/package
acceptance is not supplied by these host tests. Existing ABI29 shell unchanged.
