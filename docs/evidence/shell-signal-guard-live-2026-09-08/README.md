# Handler reentry after guarded I/O

Before implementation: arm one fixture hook at the end of a guarded read, before
restoring its saved mask. Post signal10 while masked and assert no entry yet.
Restoration must enter the handler, which queries/duplicates/closes a descriptor
and writes exactly D-newline through the same guarded transport. The original read
must return its bytes normally and the full copy must complete. Preserve errno and
exact backend byte/close oracles across two generations/four reclaims.

A fixture-only skip-restore control keeps the handler masked and must fail at
client95/owner1501. The hook is compiled only into this test; no public handler
API or production injection path. Reuse the existing mask-return kernel option,
owner and protocol; no new kernel state, authority, quota or allocation. This is
smaller than inventing an asynchronous signal source. Handler entry occurs after
the completed operation, not inside partial IPC; nonlocal exits remain next.

Run full command and host/pin checks on frozen sources with existing strict C
warnings and scoped whitespace validation. Kernel bytes are unchanged; previous
M4 evidence remains scoped to its recorded sources. Preserve all attempts and
pins; no sibling modification or consumer acceptance claim.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain commands, tool and
source hashes, target artifacts and serial logs. collect.py verifies the prior
automatic-retry packet, simplicity snapshot and every archive member.

Results: all 268 command-runner cases and host/pin checks (98 Python tests) pass.
Returning-handler reentry completes two generations/four reclaims with exact
copy and diagnostic bytes. Skip restoration rejects client95/owner1501/reclaimed0.
Sources stayed frozen; no failed or interrupted attempts occurred. Scoped
whitespace checks pass. Nonlocal handlers and partial IPC remain unqualified.
