# Metadata observation completion: rows03/05/06/11

All 357 command cases and host/pin/workflow checks (98 Python tests) pass on frozen
runtime inputs. Public getter checks independently reset errno to77 before each
call, before admission and after rejected admission. Four mutation cases suppress
one getter's errno assignment only after complete malformed-source rejection;
client105/owner1501 detects each. Mutant results make no reclamation claim.

Four V2 descriptor combinations reject incorrect rights, FD, reference generation
and descriptor count with otherwise valid metadata. Five EOF cases stop the V2
carrier at offsets0/16/48/144/159. All nine require client110, unpublished cached
IDs and descriptors, no client I/O and four reclaims across two generations.
Writer closure and consumed-endpoint cleanup use the existing bounded sender.
These selected boundaries are not exhaustive parser fuzzing.

Every selected valid identity init case now checks native raw getuid/geteuid/getgid/
getegid remain ENOSYS. Numbers come from the pinned SDK SYS macros plus the existing
native syscall prefix. Public getters continue to return admitted launcher metadata;
zero effective UID still does not grant native rights. No raw/public equality or
kernel credential implementation is claimed.

No failed or interrupted attempts occurred. The collector verifies predecessor
packet bytes, final runtime input hashes and simplicity snapshot, then reads back
all archived source/target members. qualification.json identifies the run;
manifest.json seals this packet recursively. No normal adapter behavior, kernel,
sibling, SDK default, released pin or upstream object changed. No fresh M4 run for
this fixture/mutation work. Existing local C style and Rust edition2024 remain.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-metadata-observations-2026-09-09/collect.py
```

See the [pre-code selection](../../NATIVE-SHELL-STARTUP.md#metadata-observation-completion-selection--2026-09-09).
Next: queued wrong-version body disposal (consumer row07), then matching consumer
reproduction. Header-only mismatch is not evidence of unread body disposal. These
producer results do not independently extend userland acceptance. Full-main secure
ENV, exec/wait and persistent filesystem integration remain open.
