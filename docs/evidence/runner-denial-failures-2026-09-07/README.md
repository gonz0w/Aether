# Denied-launch diagnostic failures — 2026-09-07

The AERIO001 client now attempts each of its four closes independently. Previously
`close(3) || close(4)` skipped child-output cleanup when child-input close failed.
The ambiguity assertion now checks all four local bindings. These are bounded
fixture changes; kernel primitives, release pins and sibling repositories stay intact.
See the [preimplementation contract](contract.md) and
[interface reference](../../NATIVE-COMMAND-IO.md).

Seven positive compositions retain actual launch denial before failed diagnostics:
ENOENT/zero write, EACCES/fatal write, EBUSY/zero write, ENOENT/consumed close EIO,
ENOENT/lost write reply, EACCES/eight-byte write reply and EBUSY/lost close reply.
Every case requires status1, exact accepted backend bytes, unchanged child data,
no child admission, all backend closes/stale denial and two generations/four
native reclaims. Unknown replies consume all client bindings without further
traffic; owner cleanup waits for terminal plus request EOF.

Three controls reject hiding failure as status2 (1301), omitting the last close
(1303), and resuming after poison (1320). These are exact semantic checks, not
watchdog acceptance. The final control sends a pending close request after the
reply endpoint is lost; the owner observes it at the request-EOF boundary.

Attempt1 passed the seven positive cases and first two controls, then rejected
the resume control at1320 rather than the mistakenly selected1301. Sources and
artifacts are preserved in `attempt-1.tar.gz`; the fix changes only that expected
oracle, not runtime behavior or the acceptance condition.

Reproduction uses `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Replace the profile with `--connections` or `--inherited-launch` for regressions.
Host/pin/workflow checks use `zig build test --cache-dir .zig-cache
--global-cache-dir .zig-cache/global`. Scoped C/Rust formatting and diff checks
are also required. See receipts and qualification below for executed results.

Successful combined child execution, remaining RL coverage, independent owner
review and consumer adoption are still open. This does not accept UL-059/067 or R1.

## Final qualification

Attempt2 passes all 121 command cases. Six connections and nine inherited-launch
cases also pass. Host qualification passes 98 Python tests, Zig tests and offline
pin/workflow checks; scoped formatting and diff checks pass. All final suite source
hashes match the frozen files. Kernel/build inputs and SDK/libc/tool-lock hashes
match the previous denial qualification. Largest combined supervisor: 6,968/8,192
bytes. `qualification.json` records receipt modification times, not exact run
start/per-case timestamps; extended evidence and independent reviews remain open.

`final-artifacts.tar.gz` retains sources, generated headers, binaries/envelopes,
commands and logs. ISOs, duplicate boot files and kernel.elf are omitted; their
build/ISO receipts remain. A packaging helper initially used the wrong prior receipt
filename (`command-results.json`); correcting it to `command-runner-results.json`
allowed the unchanged-input comparison. This did not rerun or change target tests.
