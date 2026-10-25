# Actual dash ENV execution

All 423 command cases and 98 Python host tests pass, with Zig, offline pin and
workflow checks. Final run: command-runner-suite-tdmlupfw. This packet covers
actual pinned dash main, with its selected native identity guard, in the existing
AECAT004 file-root fixture. It does not establish a terminal shell, login/set-ID
policy, persistent storage, full dash workloads or consumer/release acceptance.

The equal-ID interactive case uses `sh -i +m -c` with ENV=hello.sh and explicitly
disables job control. The granted script prints hello; the command prints dash-main
and exits7. UID-only and GID-only mismatches, noninteractive mode, absent ENV and
empty ENV must produce only dash-main, with zero client file opens/reads. All six cases
require empty diagnostics, descriptor cleanup and six reclaims across two
instance generations. Equality supplies no authority: the separately admitted
file-root grant remains required and existing denial cases remain regressions.

Two omission controls link the original pinned main object instead of the guarded
replacement. The client checks that the script descriptor was duplicated with
CLOEXEC above9, closes all descriptors and exits7. The owner rejects the forbidden
file access with1598 and zero reclaims. Positive loading additionally checks exact
script stdout; the omission controls reject at the earlier file-access check.
No upstream object is rewritten. Unsupported `-p` must produce exactly
`sh: 0: Illegal option -p` plus newline on diagnostics, empty stdout, status2 and
four reclaims. Skipping main returns0 and must reject1501 without reclaim.

## Reproduction

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The before-code selection in NATIVE-SHELL-STARTUP records ownership, forbidden
outcomes, cleanup/bounds and the simpler existing-service approach. Runtime changes
are confined to the C fixture adapter, Rust owner expectations and harness case/
object selection. C retains its documented compact-style migration exception;
Rust uses edition2024. No new unsafe/FFI boundary, kernel API, wire format, service,
resource increase, sibling edit or released-pin change. Original dash32-object
hashes and the separately pinned guarded main are checked before linking. Existing
source trust/configuration limitations remain. No fresh M4 run is selected because
kernel and M4 paths are unchanged. Userland's inspected workload contract is retained
under consumer-inputs; that is review context, not independent acceptance.

The initial size-list preparation error is recorded in preflight-note.txt; it
invoked no compiler or VM. Ten corrected owner size preflights pass within8192.
collect.py verifies frozen inputs, the prior sealed packet and simplicity snapshot,
then reads back source and target archives. manifest.json seals the final packet.

All 271 prior cat-owner images are byte-identical. The largest new owner is8024
bytes; the overall maximum remains8152 within the unchanged8192-byte bound.

Verified archives retain 213 frozen sources and 8,590 target artifacts.
The filesystem-observed run interval was about1,411 seconds, below the1,800-second
review ceiling; it is not instrumented per-command timing. See review-checks.json.
