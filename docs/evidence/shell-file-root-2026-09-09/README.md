# Explicit read-only root for actual dash script input

All369 command cases, seven fresh M4 regressions and98 Python host tests pass,
including pin/workflow checks. No unexpected failed target attempt; the passing
preflight host log is retained.

This packet qualifies the first bounded V4 bridge, not the entire planned V4
failure matrix or a consumer-adopted filesystem interface. See qualification.json
for the completed suite results and source/artifact inventories.

AECAT004 explicitly appends a read-only file-root record to the unchanged V3
field layout. Only its selected adapter exposes open/open64. The launcher binds
the root to the current client channel and unchanged Rust file-service instance;
CWD/identity metadata never becomes file authority. No native endpoint is exposed
to the shell, no resource pool grows, and old V1–V3 profiles retain their behavior.

Actual `sh hello.sh` executes the unchanged service's `printf 'hello\n'` script.
The owner requires one open, actual service reads, exact stdout `hello\n`, empty
stderr/input, no live file records, and ordered client0/stream17/file17 terminals
across two generations with six reclaims. The final exit adapter also requires
one file F_DUPFD_CLOEXEC allocation at or above10. Both aliases refer to the same
owner file description and offset; the final alias close reaches the service.
Independent opens, exhaustion and adversarial alias offsets need follow-up cases.

The initial planned `. hello.sh` command was corrected before execution: pinned
dash searches PATH with stat64 for that builtin, which would need regular-file
stat behavior beyond this basename-only step. Running the script as main's input
uses its real setinputfile/read/parser path without inventing stat results or
normalizing slash paths. This is neither ENV execution nor an interactive shell.

Controls:

- `...files-root-skip` omits root publication. Dash exits2; owner1501 rejects with
  zero reclaims. No file authority is substituted from the CWD grant.
- `...files-root-close` skips remote close. Dash still exits0; owner1599 rejects
  the retained open record with zero reclaims. This is a semantic failure control,
  not successful native resource recovery. Outer VM teardown is separate.

The unchanged backend has two slots with three open generations each. New bridge
profiles start with a fresh service and omit the older composition's allocating
pre/post probes; all older composition cases remain in the full suite. Owner
references include native generation, sequence and slot; backend handles stay
private. The adapter retains the existing16-FD limit and masked synchronous I/O.

Remaining work: V4 admission corruption/version/truncation matrix; independent
opens, exhaustion and stale-reference target controls; malformed/lost open/read/
close replies and confirmed service-stop cleanup. Unexpected backend failures in
this first fixture still reject the experiment through its existing check path;
they are not qualified recoverable errors. Do not infer full ambiguous-outcome
recovery from shared client poison machinery or from these normal-close results.
Then run actual-main ENV loading/suppression, existing dash workloads and matching
userland intake. Persistent OpenZFS, external child composition and R1 remain open.

Commands from the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/regression.py
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 scripts/check_workflow.py
python3 docs/evidence/shell-file-root-2026-09-09/collect.py
```

M4 uses permission for QEMU's private control sockets. Native sources remain frozen
through qualified runs. The collector verifies source digests, the previous sealed
composition packet and the simplicity snapshot, and reads back both archives.
C changes preserve the touched files' existing compact style under DEVELOPMENT's
migration exception. Rust uses edition2024 formatting. No sibling, SDK default,
upstream object, service engine, kernel ABI, released pin or publication changes.
