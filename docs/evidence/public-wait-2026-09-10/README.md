# Retained public waitpid — 2026-09-10

The isolated public fork candidate now calls a source-built musl waitpid entry point
backed by a private connection-owned collector. No kernel wait syscall, installed
SDK patch, sibling edit or shared standard is introduced. The older consume-before-
reply collector remains unchanged for its existing consumers.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#public-wait-first-execution-selection--2026-09-10)
defines the bounded wire protocol and limits. A peek returns pending0, an exact error
or the retained child PID followed by four encoded normal-exit status bytes. The
adapter copies those bytes directly to the caller using the existing native checked
channel read. An unmapped output returns EFAULT before dequeueing; draining to a
local word without acknowledgment preserves the result for another wait. NULL output
is explicitly discarded. Only acknowledgment consumes the result; native teardown/
reclaim remains a separate owner operation.

The owner serves WNOHANG while the child is still active and blocked on stream I/O.
It then finishes that I/O and observes native exit72 before offering encoded status.
The parent has already closed all its stream FDs: wait ownership is connection-bound,
independent of file-reference lifetime. PID or -1 selects only this connection's
child; options outside0/WNOHANG reject EINVAL. No numeric PID grants native authority.

| Case | Required observation |
| --- | --- |
| copy-inherit-public-fork-wait | Pending leaves sentinel intact; bad PID/options reject; actual output EFAULT preserves result; later wait returns child/exit72; repeat ECHILD; two generations/six reclaims |
| copy-inherit-public-fork-wait-null | Same boundaries, with successful explicit NULL-output discard; two generations/six reclaims |
| copy-inherit-public-fork-wait-status | Corrupt encoded status after actual terminal observation: parent82/owner1950, zero reclaims |
| copy-inherit-public-fork-wait-consume | Consume on peek, including failed output delivery: parent82/owner1950, zero reclaims |

Positive terminal order is child72/parent71/backend17 in each generation. Generic
panic, timeout or nonzero exit cannot substitute for the named negative controls.
The owner remains within its8,192-byte code bound; exact size and older payload/
kernel comparisons are in compatibility.json.

The first attempt failed compiling waitpid because header lookup selected the SDK's
public syscall header without musl's internal errno-conversion declaration. The
corrected command explicitly includes the pinned internal header. attempt1 retains
that compile failure, source snapshot, native artifacts and its host/launch results.
No failed attempt was discarded. The candidate uses musl errno conversion, not a
successful syscall stub; its link map and disassembly identify the actual entry point
and adapter. This scoped patch does not preserve libc's cancellation-aware wait4
path, so cancellation is explicitly unsupported in this single-context experiment.

Blocking wait polls under the private signal guard. This packet does not qualify
EINTR, SIGCHLD, rusage, wait4/wait3, process groups, stopped/signaled/faulted children,
threaded wait, fairness or general transport recovery. A lost acknowledgment reply
is unresolved and poisons the adapter with EIO; it is not transparently retried.
Wire-level acknowledgment idempotence is not proof of exactly-once API delivery.
Invalid/partial/lost reply controls and non-normal status translation remain next
work. Independent SDK/dash acceptance, exec/vfork and R1 remain unfinished.

Only the client, bounded owner and harness runtime sources changed. No kernel,
backend, rebind helper, existing SDK, sibling or release pin changed. Prior full
command/M4 execution remains historical. The design reuses native output validation
and one existing owner rather than adding a pointer-probe syscall, global PID table
or process service. Bounded synchronous buffers do not escape their calls.

Commands/timings, source/tool/SDK hashes and raw target artifacts are retained.
The collector verifies the previous sealed packet, simplicity snapshot, final source
identities and archive readback. runtime.patch records the scoped changes; final
checks cover standards/workflow and formatting. manifest.json seals the packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Final qualification passes 147 connections and five launch cases plus host/Zig/pin/
workflow checks including 98 Python tests. All final suites met review budgets.
Archive readback verified 226 final sources and 2,854 final artifacts, plus the
failed-attempt source/artifact archives. All143 older payloads match outside entropy
and their kernel images are identical. Maximum owner is 6,344 of 8,192 bytes.
