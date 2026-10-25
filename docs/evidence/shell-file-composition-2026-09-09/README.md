# Existing file service alongside actual dash main

Final qualification passes366 command cases, seven M4 regressions,98 Python host
tests and four build-selector checks. All earlier attempts are retained below.

The selected composition uses all three existing worker slots and six existing
channels: file service in slot2, stream backend in slot1, actual dash in slot0.
It reuses the unmodified Rust read-only file server and its existing wire protocol;
no kernel limit, directory stub or new server is added. Only this profile selects
the file-server image for the third image capability. The launcher supplies worker
argv to that service; other profiles retain their prior selection.

The owner verifies its exact root hello, open/read/EOF of real hello.sh bytes,
foreign stream-handle root rejection, denied write-open/write, missing name,
consuming close and stale handle rejection. It repeats the probe after dash's
terminal observation, requiring the next open generation on the same connection.
Then EOF stops the service and both endpoint closure and native reclaim complete.
Two generations require terminal order client7/stream17/file17, exact dash output
and six total reclaims. Roots and file handles remain bound to that connection;
matching numeric values in a fresh service are not cross-connection authority.

The substituted-payload control selects the existing command_runner file bytes
(abcdef) and must fail owner1596. Skipped remote close must fail the stale-read
assertion at1597. Both fail before shell admission with zero reclaims; no invented
child terminal or timeout is accepted. These are semantic controls, not accepted
normal cleanup. Outer VM cleanup remains separate.

This is owner-side service composition, not a shell open facade or ENV-script
execution. The shell has not received a file root. A separately versioned explicit
root grant and descriptor bridge is next; existing V3 CWD query rights must not
silently become open rights. Userland consumer acceptance, native external children,
persistent filesystem, login/TTY and complete ENV security remain open.

Commands from the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs user/native-command/owner.rs user/native-connections/supervisor.rs
python3 scripts/regression.py
python3 docs/evidence/shell-file-composition-2026-09-09/collect.py
```

The collector verifies the predecessor/configuration packets, frozen sources and
simplicity snapshot, then reads back archived sources and target artifacts. The
recursive manifest seals the result. No sibling, C adapter, SDK default,
upstream object or release-pin change. A positive native-runner-files build selector retains runner-local authority gates
and selects exact6 reclaims; legacy local profiles still require4. Native transport,
scheduling and resource limits are unchanged. Fresh M4 is selected for the scoped
build/kernel completion check. Rust2024 retained.
See [pre-code selection](../../NATIVE-SHELL-STARTUP.md#existing-file-service-composition-selection--2026-09-09).


## Retained attempts

command-runner-suite-_q3ksiqx passed11 cases, then the composition owner completed
six reclaims but the final kernel gate rejected: the harness selected the old
native-runner-local four-reclaim expectation. This was not an overall pass.

command-runner-suite-ovy8sibi was interrupted during compilation with zero target
cases after review found that turning runner-local off also disables required
parent/action interfaces. Its source snapshot/report and host log are retained.
The final correction keeps local mode and explicitly selects native-runner-files
for these three cases. No authority gate is bypassed and exactly six reclaims are
required. Four build-selector cases reject missing-local/image and SMP selections
and accept a valid composed selection. Boolean classification includes this positive
profile choice; it is not a negative-control escape.

regression-1kxp5go_ failed before boot: the sandbox prohibited binding its private
QMP Unix socket. This is an infrastructure failure, not a kernel failure or pass.
The M4 rerun uses the required socket permission. All attempt directories, logs,
reports and source identity are retained with the final results.


command-runner-suite-5rrxfv6o passed11 cases, then its valid six-reclaim native run
was rejected by the harness's older blanket ban on slot2 terminals. The corrected
oracle permits only the exact positive file-composition case, checks all six
ordered terminals, and requires no terminal at all in the two pre-admission
negative controls. The prior seven-case M4 pass (regression-3m9i67h2) and host log
are retained; final suites run again on the corrected harness snapshot.
