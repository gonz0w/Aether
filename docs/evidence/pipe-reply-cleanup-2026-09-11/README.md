# Interrupted pipe creation cleanup

Status: qualified for the scoped native producer cases below. See [pre-implementation review](PLAN.md).

The native probe cuts a committed create reply at zero, one or 31 bytes. The
adapter must preserve its mask, publish nothing, return EIO and refuse retry.
Confirmed terminal observation and an empty request route precede holder release,
backend cleanup and real reclamation. Three complete interrupted lifetimes stay
within existing task/channel/generation quotas. A retained-holder mutant must
reject retirement with exact parent92/owner2168 and zero reclaims.

Run from the repository root with the pinned SDK and tools already installed:

```sh
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/console_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Attempt1 reached four real reclaims after two interrupted lifetimes, then failed
the unchanged kernel's six-reclaim profile check. Its full sources, artifacts and
logs are retained in attempt-1.tar.gz with the file index in attempt-1.json.
The corrected probe uses three real lifetimes, without dummy processes or a
kernel/limit change. This is a fixture mismatch, not accepted target evidence.

No public pipe API, SIGPIPE, silent-stall recovery, native copy rollback, abnormal
child cleanup, same-client pipe reuse, actual dash substitution or assembled R1
acceptance is implied. Scripts retained here are audit artifacts: use fresh
output directories for reruns, never overwrite a sealed evidence packet.

## Results

- Complete connections suite: 255 QEMU cases pass.
- Launch and console regressions: five plus two cases pass (262 target cases total).
- Focused preflight: three interrupted-create positives and two exact rejection controls pass.
- Host, harness, Rust/C format, workflow, three released pins and simplicity snapshot checks pass.
- Original successful copied-process transfer and malformed INT32_MIN rejection remain passing.
- Each interrupted-create positive observes parent92/backend17 in generations1–3,
  then owner100/six actual reclaims; no child admission.
- Retained-holder control observes parent92 then owner2168/zero reclaims.

Owner sizes and exact artifact/source inventories are in qualification.json.
The maximum owner is 9944 bytes under the unchanged16KiB bound; image size
is not a worst-case stack, memory or performance measurement. Final sources,
patch, tool/command identities, raw logs, results and start/end timings are retained.
Archives were read back and hash verified, including the failed first attempt.
No independent reader or companion acceptance is claimed. The kernel, SDK,
siblings and released standards pins are unchanged.
