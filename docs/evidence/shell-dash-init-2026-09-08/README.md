# Actual generated-init diagnostic

Qualified 2026-09-08: all 291 command-runner cases and host/pin/workflow checks
(98 Python tests) pass on frozen sources. No failed/interrupted attempts. Scoped
Rust formatting and diff checks pass. No fresh M4 run was selected: kernel/build
bytes remain unchanged from the prior signal qualification.

The unchanged pinned dash generated init runs with an empty environment and the
existing native memory grant. It initializes IFS, OPTIND and CHLD. Under today's
missing calls, PPID becomes -38, PWD is empty and geteuid returns raw unsupported
data. The owner verifies exact stderr:

```text
sh: 0: getcwd() failed: Function not implemented
```

Ordinary copy and cleanup complete across two generations/four reclaims. The
skipped initializer fails client103/owner1501. This diagnostic requires the known
gaps to be visible; it is not a successful-main or shell-startup qualification.
Update these expectations when truthful contracts land. No quota increase or
new kernel API was necessary to execute init in this bounded experiment.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 docs/evidence/shell-dash-init-2026-09-08/collect.py
```

host.log/native.log and command-results.json retain checks. The collector verifies
the prior packet, exact frozen sources and simplicity snapshot, then reads back
all source/target archive members against their hashes. qualification.json names
exact run directories and counts; manifest.json seals this packet. Original dash
object provenance and notices remain in the retained source snapshot.

See the [pre-code diagnostic contract](../../NATIVE-SHELL-STARTUP.md#generated-init-diagnostic-execution--2026-09-08).
No sibling, released pin, consumer default or authority changed. Next: truthful
launcher parent/user metadata, then scoped directory/CWD semantics with the file
owner. Full main, external commands, pipelines and independent consumer acceptance
remain open. Existing signal-routine qualification stays separate from these gaps.
