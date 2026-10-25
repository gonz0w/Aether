# Partial pipe request and child fault

Status: qualified for the scoped native producer cases below. See [pre-implementation review](PLAN.md).

The real copied child writes 256 patterned bytes, sends 17 bytes of its next write
request and executes UD2. Its parent must drain the 256 committed bytes through EOF
before waiting, observe SIGILL without a core-dump flag, then exit0. Two complete
parent/backend/child lifetimes produce six real reclaims. The owner observes the
actual fault and accounts for all terminal-channel bytes before discarding the
unapplied partial frame or dropping holders. Buffered bytes survive child death.

Controls retain the partial frame through retirement (owner 2166) or falsely report
normal exit134 (parent 90/owner 2163); both require zero reclaims and the actual
kind2/detail134 child terminal. Generic panic, boot failure and timeout do not pass.

Run from the repository root with the existing pinned inputs:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The focused positive and two semantic controls passed on their first attempt.
No kernel, SDK, sibling, released ABI/pin, resource quota or service change.
This is one named partial-request fault schedule, not all interruption races.
Fully pending write cancellation, forced stop, silent stalls, copy rollback,
SIGPIPE, same-client pipe reuse and actual dash substitution remain separate work.
R1 filesystem/package/sys-init assembly and consumer acceptance remain open.
Retained scripts are audit artifacts: use fresh outputs, never overwrite sealed
packets. Unpacked preflight duplicates may be removed only after archive/member
hash verification and open-handle/stat checks; qualified suite outputs remain.

## Results

- Complete connections suite: 258 QEMU cases pass.
- Launch and console regressions: five plus two pass (265 target cases total).
- Focused preflight: real child-fault positive and two semantic controls pass.
- Host/harness, scoped Rust/C format, workflow, three pins and simplicity checks pass.
- Positive: child kind2/detail134, parent 0, backend 17 in generations1/2; six reclaims.
- Retained-frame: child fault then parent 0, owner 2166 and zero reclaims.
- False-status: child fault then parent 90, owner 2163 and zero reclaims.

Owner sizes and artifact/source inventories are in qualification.json. The maximum
owner is 9944 bytes under the unchanged 16 KiB bound; image size does not measure
worst-case stack, memory or performance. All runs use frozen runtime sources.
Sources, patch, exact tool/command identities, logs, results and start/end timings
are retained; archives were read back and hash verified. No failed attempts
preceded qualification. Independent reader and consumer acceptance remain pending.
