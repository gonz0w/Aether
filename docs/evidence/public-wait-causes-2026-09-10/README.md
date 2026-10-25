# Retained wait causes — 2026-09-10

The bounded waitpid translator now distinguishes normal exit134, an actual CPU
invalid-opcode fault and actual default SIGTERM termination. The child triggers each
cause only after completing its stream I/O and closing descriptors. Native records
remain unchanged; no signal number is guessed from an untyped numeric detail.

| Cause | Native kind/detail | Wait word |
| --- | --- | --- |
| Normal return134 | 1/134 | 134<<8; WIFEXITED, exit134 |
| Executed UD2 | 2/134 | SIGILL4; WIFSIGNALED, no core bit |
| Native default SIGTERM post | 4/15 | SIGTERM15; WIFSIGNALED, no core bit |

A shell's conventional128+signal display is not the encoded wait word. This
translation qualifies only the observed #UD vector and SIGTERM in addition to
normal exits. Other causes reject2022 rather than inventing a mapping. No core
dump file/bit, stopped/continued status, arbitrary CPU exception or arbitrary signal
support is claimed. The exact [pre-code selection](../../NATIVE-SHELL-STARTUP.md#public-wait-abnormal-exit-selection--2026-09-10)
records authority, policy ownership, resource and verification scope.

All three positives run the existing pending WNOHANG, PID/options denial, actual
EFAULT followed by retained collection and repeat-ECHILD sequence. Each retains
parent71/backend17 over two generations and six reclaims. The child terminal kind/
detail must match the table exactly. Two deliberate controls encode the fault or
signal as a normal exit and require parent82/owner1950 with zero reclaims. Generic
panic, timeout or nonzero exit is not sufficient. Native fault/termination logs
are preserved alongside the parent status checks.

Only client, owner and harness runtime sources changed. The SIGTERM cases explicitly
select existing native signal/action/copy/termination flags; no kernel branch or
default profile changes. The translator is one small explicit match over an observed
cause pair, not a new process service, signal framework, allocation or global table.
It reuses the existing result/output/acknowledgment contract and bounded owner.
The kernel, backend, rebind helper, installed SDK, siblings and released pins are
unchanged. Earlier full command/M4 execution remains historical.

These deaths follow descriptor closure: early death with abandoned references and
arbitrary cleanup is not qualified here. Reply truncation/loss, acknowledgment
ambiguity, SIGCHLD/EINTR/cancellation, wait4/wait3, other causes, exec/vfork and
independent SDK/dash acceptance remain open. R1 is unfinished.

Commands, UTC timings/status, source/tool/SDK identities and native artifacts are
retained. The collector verifies prior sealed evidence, simplicity pin, final source
hashes and archive readback. Compatibility.json compares the147 older payloads and
kernel images and records owner bounds. Link maps and disassembly identify the
source-built waitpid candidate; formatting and pin/workflow checks have receipts.
The prior wait packet retains its compile failure; this packet does not rewrite it.
runtime.patch records scoped changes and manifest.json seals all evidence.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Final qualification passes 152 connections and five launch cases plus host/Zig/pin/
workflow checks including 98 Python tests. No qualified attempt failed; all final
suites met review budgets. Archive readback verified 226 sources and 2,939 target
artifacts. All147 older payloads match outside entropy; their kernel images are
identical. Maximum owner remains 6,344 of 8,192 bytes.
