# Interactive serial dash substitution

Status: qualified for the scoped native producer cases below. See [PLAN](PLAN.md).

Real interactive dash reads four host commands at four observed prompts across two
shell sessions. The first shell completes two substitutions in separate children;
the second runs builtin `echo clean` and exits. The owner independently verifies
stdin/stdout/stderr bytes and positions. Empty UART reads remain pending without
false EOF or offset changes. Pipe data goes through the private pipe owner and
actual EOF/wait acknowledgment before retirement; only shell output reaches UART.

The console backend keeps its grant across both sessions and resets stream state
between them. Its replacement must be denied UART access. Two children, two shells,
one granted backend and its denied-grant replacement produce six actual reclaims.
Parent direct UART access is denied. Existing nonserial and serial-exec profiles
remain separate regressions; no kernel, ABI, quota, SDK, sibling or pin changed.

The altered-input control requires owner2182 and zero reclaims before any fork.
The stale-token control requires child1 exit0 then owner2179 after one reclaim.
The host rejects timeouts, unrelated panics, wrong command counts and wrong terminal
history. Its first preflight passed the positive but checked a partial panic line
too early in the wrong-input case. The driver now waits for the complete line;
all three focused cases pass. Both attempts are retained with matching sources.

Use the existing commands:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This is a bounded producer workload, not a general interactive filesystem shell.
Combining exec with pipe descriptors, installed SDK and independent userland
acceptance, broad interruption/copy rollback and R1 assembly remain open. The
simpler-alternative and ownership review is in PLAN. The existing dispatcher and
console backend are reused; the focused serial driver borrows the old driver's
bounded process lifetime without adding flags to its separate exec workflow.
No new allocator, unsafe block, dependency or wire protocol. Existing synchronous
native-call buffer obligations and ASCII presentation exception remain applicable.
Independent reader review remains open. Retained audit scripts name frozen paths;
use fresh output directories rather than rerun them over sealed packets.

## Results

All274 connections, five launch and two console cases pass (281 QEMU cases).
Focused positive, altered-input and stale-token controls pass. Host/harness,
scoped Rust/C format, workflow, three released pins, simplicity and incompatible
configuration rejection checks pass. Every previously qualified copied public-fork
client ELF remains byte-identical. The maximum owner is 12320 bytes under the
unchanged16KiB bound; no worst-case stack or performance claim follows.

Exact commands/tool identities, run timings, source hashes/archive/patch and all
target artifacts are retained. Both preflight attempts are archived, including
the partial-line assertion failure. Archives were read back and hash verified
before deleting only their unpacked preflight duplicates. Final suite outputs
remain available. Independent reader and installed consumer acceptance remain open.
