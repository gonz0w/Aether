# Private handler entry on successful mask return

Before implementation: separately opt in native-signal-mask-delivery, requiring
private actions. After a successful native mask operation, prepare at most one
eligible custom handler before returning to user space. Preserve the committed
mask syscall result and register state. Failed mask calls must not trigger entry;
failed handler preparation retains pending state and the successful mask result.
Default termination is excluded from this automatic boundary. Explicit post/poll
and private termination behavior remain unchanged in existing profiles.

Reuse the existing pending selection/frame publication helper, separating it from
post argument validation. No allocation, new owner, pointer lifetime, quota or IPC
protocol. IF=0 covers mask commit, frame preparation, dequeue and publication.
One-successful-mask-return is the smallest useful boundary for transport guards;
it avoids timer/I/O/handler-return entry before those paths are qualified. Guarded
live handler/nonlocal and failed automatic frame preparation tests remain next.

Native test: block and post duplicates, reject an invalid old-mask output without
entry or mutation, then unmask and observe one handler before syscall return.
The existing exact handler mask, restored caller mask and no-duplicate poll oracle
must pass through two generations/four reclaims. A disabled option control must
fail client91/owner1501. Full command/M4/host suites and Zig formatting run on
frozen sources. Preserve all attempts and release pins; no sibling changes.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
python3 scripts/regression.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain commands, source
and tool hashes, target artifacts and serial logs. collect.py verifies the prior
live-resource packet, simplicity snapshot and every archive member. The native
automatic preparation-failure/result preservation case remains next; explicit
preparation failure is covered by earlier retained evidence.

Results: all 264 command-runner cases, seven M4 regressions and host/pin checks
(98 Python tests) pass. The positive completes two generations/four reclaims;
disabled automatic entry rejects at client91/owner1501/reclaimed0. Sources stayed
frozen; no failed or interrupted attempts occurred. Zig format and scoped
whitespace checks pass. Automatic preparation-failure/result preservation and
guarded/nonlocal transport witnesses remain open; no public adoption is claimed.
