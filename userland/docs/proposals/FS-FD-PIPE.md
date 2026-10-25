# Paired pipe creation in the tagged table — UL-007/081/082

`aefd_table_pipe` adds opt-in paired publication to the [canonical tagged table](FS-FD-BINDINGS.md).
A trusted source creator performs actual creation; the local helper validates its
observation and publishes two logical entries together. It reuses [mixed aliases/
close](FS-FD-STREAMS.md), [read dispatch](FS-FD-ROUTING.md) and [output](FS-FD-WRITE.md).
This is not native pipe creation, libc pipe/pipe2 interposition, an accepted new
sys-init API or selected shell/startup. The existing ABI29 shell remains unchanged.

Caller supplies a successfully decoded canonical map, matching authenticated
process/channel/source bindings, live client/workspace, exclusive serialized and
nonreentrant access. Caller pair points to two valid ints, disjoint from all map/
client/adapter storage. Callback cannot mutate/reenter or retain caller state.
Only coordinated operations may change the map. Native authority, direction,
rights, reference/generation bounds, liveness, deadlines and settlement belong
to the creator owner; numeric selectors and decoded shape prove none of these.

| Boundary | Outcome |
| --- | --- |
| Null output pair or cloexec outside0/1 | -22 before source effects |
| Missing/retired client/workspace | -5, no source call |
| Missing/zero/stale map generation | Retire file admission once, -5, no source call |
| Fewer than two empty logical slots0–15 | -24 before source creation; no partial local reservation |
| Missing creator or callback | -38, unchanged output; no successful no-op |
| Complete1, valid negative errno, zero selectors | Return known error, preserve map/output and live admission |
| Complete1/status0, ordered unused pair3/4 or5/6 | Publish both lowest free logical entries and output ints, return0 |
| Unknown/malformed/colliding observation | Retire file admission, -5, preserve map/output, no retry/rollback |

Source callback returns `{complete,status,read_selector,write_selector}`. Complete
must equal1; private status must be0 or -2147483647..-1. Known errors carry no
selectors. Successful source pairs must be ordered3/4 or5/6, consistent with the
existing bounded stream namespace; arbitrary/reversed/same endpoints reject.
Neither selector may already occur in any PIPE entry. FILE selector3 is a separate
class and does not conflict with pipe3. Source limits can exhaust independently
of logical table capacity. No source capacity or generation is reset here.

Flags are per-logical C cloexec metadata only, not native exec enforcement or a
request for wider grants. Each new slot receives the requested flag and reserved0.
Read/write logical output need not equal their source selectors. Both entries and
pair are committed only after all checks; there is no intermediate live ledger or
allocation. Local-full precedes missing-adapter lookup; no POSIX error-order claim.

Unknown creation may already have allocated endpoints even though local map and
output remain unchanged. Malformed success/collision may name an occupied resource.
Never close purported selectors as rollback or reinitialize/retry the retired
client. Creator owner must retain/reconcile actual allocations and settle native
resources. File-client abort records raw file endpoint close results and clears/
releases its workspace; it is not native stream cleanup or process quiescence.
There is no new file wire opcode, native source implementation or supervisor policy.

## Qualification and handoff

```
python3 -B experiments/filesystem-service/check-fd-pipe.py
```

Twenty-two cases per live C child include real host pipe creation. Successful
cases create both distinct source pairs, publish at logical0/1 then0/4, transfer
bytes with the exact existing tagged read/write helpers, duplicate one read end,
close its original alias without closing the source, then close all four actual
endpoints through the mixed final-close adapter. Console/file entries survive;
file3/pipe3 coexist. Flags0/1, pair output and untouched table tail are checked.

Other cases cover no/one free slot before source effect, known source exhaustion
followed by successful creation AND read/write, known -5 with live admission,
stale identity, invalid flags/null output, unknown with/no actual allocation,
reversed/equal/out-of-range pairs, each occupied end, invalid status/complete,
error carrying selectors and missing adapter/callback. Host source cleanup explicitly
closes uncommitted/unknown endpoints and checks EBADF; map preservation is not
rollback. Structured source observations are injected, while OS pipe/read/write/
close are real. No actual native capability, generation or fork/exec claim.

The child also runs unchanged eighteen write and fourteen stream-lifetime scenarios,
then269 live C/Rust file cases using the real unchanged handler/process/AF07 policy
with synthetic storage. Six compiling omissions must fail specific C assertions
plus observed failed C child: effect before capacity, accept unknown, ignore pipe
collision, accept error selectors, reverse published write endpoint and skip second
pair output. Compiler/sanitizer/watchdog failures cannot satisfy fault controls.

Actual Python3.10.21/3.14.7 run strict C17 warnings/format/UBSan and unchanged
Rust2021/default Clippy/rustfmt/unsafe denial, pinning complete write24/streams20/
table18/routing16/bindings6/facade12/client9/wire20/service77 sources before use.
Tool/resource/library/host SDK/runtime/helper pins and relevant post-run rechecks
apply. Owned clean environment,60s compile/30s live suites/16MiB output bounds.
[Evidence](../evidence/filesystem-fd-pipe-2026-10-21/README.md) retains every attempt,
including initial19-case scope and final minimum/current22-case reruns. Source-only
candidate: `build/service-deliveries/filesystem-fd-pipe-2026-10-21-v1`.

Next actual native stream creator/read/write/close adapters with authenticated
bindings, selected shell startup/table/profile and owner reconciliation. Exact
redirection/replacement, native copy/failed-exec parent/FD preservation, immutable
image admission, code/stack/heap/workspace/backing/channel fit and complete matched
dispatcher/readiness/shutdown/native command/error/cleanup/fresh boot remain open.
Independent owner/reader and full UL/M3/R1/POSIX/Zsh/TTY/packages acceptance remain
incomplete. No sibling implementation/message, native guest, limit/pin/default
change or target installation is implied.
