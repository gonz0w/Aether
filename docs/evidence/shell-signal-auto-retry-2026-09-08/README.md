# Automatic entry failure preserves completed mask calls

Before implementation: use the private automatic mask-return profile and existing
invalid-stack probe pattern. At four invalid stack positions, a successful unmask
must return zero and copy the old mask even though handler preparation fails.
A second query at the same invalid stack must return the committed zero mask,
without handler entry. Record bytes remain unchanged. A normal-stack query must
then deliver exactly once without reposting. Repeat across two generations.

The naked C probe keeps original RSP in r11 and restores it before returning;
set/old pointers refer to live ordinary caller stack storage, not the invalid RSP.
No C code executes on the invalid stack. Use existing frame checks, pending owner
and mask API; no kernel change, allocation, authority, quota or ABI extension.
A deliberate ignore/reinstall discards pending state before retry and must fail
client94/owner1501. This is smaller than adding a kernel injection switch.

Full command and host/pin suites, scoped whitespace checks and existing strict C
compilation are selected on frozen sources. M4 runtime is unchanged; earlier
M4 evidence remains scoped to its recorded source. Preserve attempts and pins;
no sibling edits or public/consumer adoption. Guarded/nonlocal handlers remain next.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain command/tool/source
identity and target serial output. collect.py verifies the prior mask-return packet,
simplicity snapshot and archive members; manifest.json seals retained evidence.

Results: all 266 command-runner cases and host/pin checks (98 Python tests) pass.
The positive completes two generations/four reclaims; pending-discard rejects
client94/owner1501/reclaimed0. No failed or interrupted attempts occurred; sources
stayed frozen. Scoped whitespace checks pass. This closes native automatic
preparation-failure/result preservation only; guarded/nonlocal handlers remain open.
