# Nonlocal exit from guarded handler

Before implementation: extend the returning-handler fixture with sigsetjmp/siglongjmp
using the pinned musl implementation. A completed first 11-byte read triggers the
handler at mask restoration; after its descriptor and diagnostic operations the
handler jumps to a saved point instead of returning through the signal frame.
Verify saved mask zero, exactly one handler, then forward the static read buffer
and continue transport/copy/cleanup. Existing owner verifies every byte and four
reclaims across two generations. Saving no mask must reject client96/owner1501.

Use static jump/read storage so no modified nonvolatile automatic local is read
after longjmp. The alias is initialized before setjmp and not modified. The read
is a fixture-known 11-byte operation; this does not invent general EINTR replay or
partial-request semantics. No kernel handler-active slot, stack reclamation API,
new service or authority. Reusing musl and the existing fixture is smaller than
adding a nonlocal kernel protocol. User-stack frame is abandoned; later transport
and normal termination must remain usable. Broader signal/error cases remain open.

Run full command and host/pin checks, strict C compile and scoped whitespace checks
on frozen sources. No kernel or Rust change; prior M4 evidence remains scoped.
Preserve pins, all attempts and sibling files. No public signal adoption claim.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain commands, source
and tool hashes, artifacts and serial output. collect.py verifies the previous
guarded-reentry packet, simplicity snapshot and every archive member.

Results: all 270 command-runner cases and host/pin checks (98 Python tests) pass.
The positive completes two generations/four reclaims with exact copy/diagnostic
bytes; no-mask-save rejects client96/owner1501/reclaimed0. Sources stayed frozen;
no failed or interrupted attempts occurred. Scoped whitespace checks pass.
This qualifies nonlocal exit after a completed read, not general partial IPC
cancellation, error-path handler injection or public signal support.
