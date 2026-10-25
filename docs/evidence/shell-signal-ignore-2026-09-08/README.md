# Musl default/ignore flag compatibility

Qualified 2026-09-08: 287 command-runner cases, seven M4 target cases, 98 Python
tests and host/pin/workflow checks pass. Sources stayed frozen during qualification;
there were no failed or interrupted attempts. See host.log, native.log, m4.log and
matching results. Exact source and target receipts are retained and hash-verified.

Pinned dash trap.c ignores signals through signal(); redir.c also restores
SIGPIPE to DFL through signal(). Musl adds SA_RESTART. The experimental public
route now retains that flag for DFL/IGN only. Neither enters a handler, so this
requires no interrupted syscall restart. Custom handler restart remains ENOTSUP.
All other unsupported flags and the private setter's original restrictions remain.

The actual-musl witness verifies returned previous handlers, public/private flag
queries, invalid SIGKILL, rejected custom replacement, queued/future ignore discard,
DFL restoration and the original handler/nonlocal-return checks. It completes two
generations/four reclaims. Skipping ignore rejects client101/owner1501; disabled
public routing still rejects as before. The new host test checks unsupported flag
bits and unchanged state on rejection. Existing private flag rejection tests pass.

Commands from the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/regression.py
python3 docs/evidence/shell-signal-ignore-2026-09-08/collect.py
```

The collector verifies the prior public-action packet, matching frozen inputs and
simplicity snapshot, then every retained archive member. qualification.json names
exact run directories and counts. dash-review.tar.gz preserves the two upstream
review inputs with original notices; dash-review.json records origin and hashes.
manifest.json seals this packet. No sibling was modified.

See the [pre-code review](../../NATIVE-SHELL-STARTUP.md#dash-defaultignore-flag-review--2026-09-08)
for rationale, authority/resource boundaries and selected coverage. No new build
option, record storage, service, authority or release pin. Existing consumer defaults
remain unchanged. Actual dash setup, signal production/child notification, broader
delivery and process/I/O composition still require qualification. No syscall restart,
full-dash acceptance or independent owner/reader sign-off is claimed.
