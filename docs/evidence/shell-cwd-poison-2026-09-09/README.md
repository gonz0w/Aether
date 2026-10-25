# Directory reply poison and teardown

All 328 command cases and host/pin/workflow checks (98 Python tests) pass on frozen
runtime inputs. Four owner injections cover reserved reply bytes, invalid cwd
length, invalid stat mode and a 16-byte reply followed by EOF. The client requires
EIO, unchanged buffers/stat object, poison publication and restored native signal
mask. Subsequent cwd/stat/read/write reject; the owner rejects further received
requests and verifies no partial queued frame, unchanged stream data and four
reclaims across two generations. These controlled failures exit1, not startup0.

A fifth case deliberately omits poison publication after semantic reply rejection.
The client detects it at107; the owner rejects1501 with zero reclaims. This mutant
proves the check detects the omitted behavior; it does not qualify recovery for a
broken adapter. The normal decoder/poison path required no fix. The owner uses the
existing half-frame sender and explicit writer-close accounting for truncation.

No failed or interrupted attempts in this step. Sources, commands, raw logs,
artifacts and exact results are retained. The collector verifies predecessor packet
bytes, final source hashes and the simplicity snapshot, then reads back every
archived member. qualification.json identifies the run; manifest.json seals the
packet recursively. No kernel/build, sibling, SDK default, released pin, upstream
object or license changed. No fresh M4 run selected for this fixture/test change.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-cwd-poison-2026-09-09/collect.py
```

See the [pre-code selection](../../NATIVE-SHELL-STARTUP.md#directory-reply-poison-selection--2026-09-09).
Next: directory identity/inherited-PWD mismatch controls. V1/V3 and other bootstrap
truncation boundaries remain open, as do full directory consumer acceptance,
actual-main secure ENV, exec/wait and persistent filesystem integration. The owner
proves no accepted later traffic, not absence of every attempted failed syscall.
