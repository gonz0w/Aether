# Inherited-PWD identity comparison

All 333 command cases and host/pin/workflow checks (98 Python tests) pass on frozen
runtime inputs. Three new positive selections supply PWD=/work and observe actual
unchanged generated init: stat(/work), stat(.), with getcwd required only after a
device or inode mismatch. Final PWD remains /work in every case, so the Rust owner
checks exact request order and count, not just a matching string or normal exit.
Positive selections preserve ordinary copy/output and four reclaims across two
generations. Existing standalone directory probes remain in their own cases.

Two deliberately broken adapter selections collapse the differing device or inode
to the current directory's value. Actual init incorrectly omits fallback; the
client still exits0 and the owner rejects1594/reclaimed0. These semantic mutants
prove the owner detects lost identity information. They do not establish cleanup
for a broken adapter. Injected mismatch replies are adversarial fixture data,
not additional filesystem objects or a change to the normal namespace contract.

No failed or interrupted attempts occurred. The collector verifies predecessor
packet bytes, final source hashes and the simplicity snapshot, then reads back
all archived sources and target artifacts. qualification.json identifies the run;
manifest.json seals this packet recursively. No normal adapter behavior, kernel,
sibling, SDK default, released pin, upstream object or license changed. No fresh
M4 selection for these fixture/mutation checks.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-cwd-pwd-2026-09-09/collect.py
```

See the [pre-code selection](../../NATIVE-SHELL-STARTUP.md#inherited-pwd-identity-selection--2026-09-09).
Next: remaining V1/V3 and truncated-bootstrap controls, then complete directory
evidence review for consumer intake. Full-main secure ENV, exec/wait, general
paths/chdir and persistent OpenZFS remain open. This is neither full shell startup
nor independent technical review or consuming-project acceptance.
