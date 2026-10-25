# Nonlocal exit after an ambiguous read

Before implementation: combine the existing poisoned-read and musl nonlocal-handler
fixtures. Malformed/truncated replies poison before handler entry. After failed
handler I/O and local diagnostic retirement, siglongjmp must restore the saved mask
without clearing poison. Static sentinel buffer remains untouched; remaining local
closes generate no channel calls. Owner verifies backend state/cleanup and two
generations/four reclaims. No-mask-save rejects client99/owner1501.

The abandoned read wrapper returns no result: do not infer caller errno from it.
Check poison, mask, actual channel counts, buffers and cleanup directly. Static
buffer/jump storage avoids changed automatic-variable use across longjmp; pointer
and failure-code locals are initialized before setjmp and not changed. Reuse the
existing kernel, guard, musl and owner with no extra state/protocol/authority/quota.
This is post-reply escape, not cancellation during partial request transmission.

Full command and host/pin checks use frozen sources and existing strict C flags;
scoped whitespace checks apply. Preserve attempts/pins/siblings. Kernel/Rust remain
unchanged, so previous M4 evidence stays scoped with no fresh M4 claim.

Initial setup invocation used a mistyped tools-lock path and failed before builds
or QEMU. setup-attempt-1.log retains that error. The corrected invocation uses
zig-out/init-capacity-2026-09-06/tools.lock.json with unchanged source bytes.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain commands, sources,
tools, artifacts and serial logs. collect.py verifies the prior poisoned-read
packet, simplicity snapshot and all archive members before sealing.

Results: all 279 command-runner cases and host/pin checks (98 Python tests) pass.
Both ambiguous-reply/nonlocal positives complete two generations/four reclaims.
No-mask-save rejects client99/owner1501/reclaimed0. Sources stayed frozen; no
native qualification failed or was interrupted. The initial setup path error is
retained separately. Scoped whitespace checks pass. Ambiguous close and arbitrary
partial-request cancellation remain separate work.
