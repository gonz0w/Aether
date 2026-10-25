# Actual dash signal routines

Qualified 2026-09-08: all 289 command-runner cases and host/pin/workflow checks
(98 Python tests) pass on frozen sources. No failed or interrupted attempts.
Kernel and build sources match the preceding ignore/default packet, which retains
seven passing M4 cases. This fixture/harness change did not select a fresh M4 run.

The local dash-inputs snapshot contains 32 unchanged reference objects with original
COPYING and userland's build/hash receipts. Every object is verified before linking.
The linker wraps main to the conformance client; dash setsignal, ignoresig and onsig
remain their real linked implementations. The fixture selects root interactive
option state with job control disabled and checks INT/CHLD handler records,
QUIT/TERM ignores, restorer/mask fields and HUP ignore flags. Private SIGCHLD sets
dash's gotsigchld through actual onsig. Normal copy and two generations/four reclaims
complete. Skipping CHLD setup must reject client102/owner1501, so a silent setup
failure cannot count as success.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 docs/evidence/shell-dash-signals-2026-09-08/collect.py
```

host.log/native.log and command-results.json retain execution evidence. The
collector verifies prior packet bytes, unchanged runtime sources, the simplicity
snapshot and every archived source/target member. qualification.json names exact
runs and counts; manifest.json seals the packet. sources.tar.gz includes the
pinned dash objects and receipts; target-artifacts.tar.gz includes linked images,
commands, maps and native serial results. The sibling checkout was read only.

See the [pre-code review](../../NATIVE-SHELL-STARTUP.md#actual-dash-signal-setup-experiment--2026-09-08).
This does not run dash main or generated init; it does not qualify a native dash
configuration, parser, external commands, child notification authority or pipelines.
The imported Linux reference configuration and its source/generator trust review
limits remain explicit. No successful syscall stubs, new kernel primitive, quota,
consumer default, public signal producer or pin. No full-dash or independent owner
acceptance is claimed. Next is actual main/init under bounded startup grants.
