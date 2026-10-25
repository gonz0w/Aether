# Directory bootstrap boundaries and consumer intake review

All340 command cases and host/pin/workflow checks (98 Python tests) pass on frozen
runtime inputs. Seven new cases cover V1 sender/V3 receiver, V3 sender/V1 receiver,
and EOF at offsets0/16/48/144/191 of the192-byte V3 carrier. Every case requires
client110, unpublished state, no client I/O, unchanged backend contents and four
reclaims across two generations. The byte-budget sender sends no further bytes
after its cutoff and closes explicitly; cleanup accounts for the consumed writer.
Normal frame sends and earlier half-frame controls remain passing.

No failed/interrupted target attempt. preflight-host.log retains a successful
initial host check; final host qualification followed review of writer-close
accounting. No C decoder/adapter, kernel, sibling, SDK default, pin or upstream
object change. No fresh M4 run for these sender/harness changes. Sources retain
Rust edition2024 formatting and the existing scoped Python style.

The collector verifies predecessor packet bytes, final runtime hashes and the
simplicity snapshot, then reads back every archived source/target member.
qualification.json identifies the run/count; manifest.json seals the packet
recursively, including the three hashed read-only consumer-review inputs.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-cwd-boundaries-2026-09-09/collect.py
```

See the [pre-code selection](../../NATIVE-SHELL-STARTUP.md#remaining-bootstrap-boundary-selection--2026-09-09)
and [intake review](../../NATIVE-SHELL-STARTUP.md#directory-and-metadata-intake-review--2026-09-09).
Userland reports reproducing the older319-case initial directory profile. Its
review still requests aliases to every stream and forced ENOMEM, plus five partial
metadata observations. Captured reviews are inputs, not a fresh consumer run or
acceptance of this340-case revision. New producer evidence fills selected directory
poison, identity and boundary gaps; it does not close the entire consumer matrix.
Next: remaining aliases/ENOMEM, then metadata errno, descriptor composition,
truncation, queued wrong-version body and raw-getter checks before full-main work.
