# Launcher-supplied user/group metadata

Final qualification: all 309 command cases and host/pin/workflow checks
(98 Python tests) pass on frozen runtime sources. AECAT002 adds a validated
32-byte advisory identity record to the existing role bootstrap. Public C getters
publish only after complete admission. The launcher explicitly supplies distinct
real/effective UID/GID values across two generations; actual unchanged dash init
selects its prompt from effective UID. Zero effective UID grants no additional
capability rights. Each accepted/rejected input case completes four reclaims.

Eleven malformed/version cases reject at client110 with descriptors and IDs
unpublished: source kind, flags, reserved bytes, each sentinel ID, stale generation,
truncation and both version directions. Skipped metadata publication must reject
client105/owner1501. Header-first parsing avoids waiting for a mismatched body.
Legacy AECAT001 remains separately selected. Raw credential syscalls remain ENOSYS;
this experiment is neither account authentication nor native SDK adoption.

One failed attempt is retained in attempt-1: the first supervisor build rejected
a 16-byte slice passed to the existing 32-byte transfer helper (Rust E0308), before
any guest execution. The corrected truncation fixture uses a bounded partial send
and closes the writer. The shared full-frame helper is unchanged. Both attempts'
source snapshots, results, logs and target artifacts are retained and verified.
The failed build is not counted as target coverage.

Commands from repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-user-metadata-2026-09-08/collect.py
```

The collector verifies the previous parent packet, final runtime input hashes,
failed-attempt source hashes and the simplicity snapshot, then reads back each
archived member. qualification.json records runs and counts; manifest.json seals
all packet files recursively. No kernel/build inputs changed from the parent
packet, so its seven M4 checks retain their recorded scope without a fresh M4 run.
The public-signal malformed-bootstrap oracle now checks actual descriptor/mask
readiness: own-domain sigaction does not depend on descriptor admission.

See the [pre-code contract](../../NATIVE-SHELL-STARTUP.md#launcher-supplied-usergroup-metadata-review--2026-09-08)
for ownership, authority, bounds and test selection. No sibling, release pin,
upstream dash object or license changed. getcwd remains unsupported with its exact
upstream warning. Next: capability-scoped directory/CWD semantics, then full-main
and exec/wait composition. Independent review and consumer acceptance remain open.
