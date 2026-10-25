# Private native action copies

Before implementation: add build-selected action-record copy/query on the existing
single-context runner fixture. Reject in legacy builds. Snapshot input before
validating/writing old output; reject overflow, unreadable input, unwritable output,
non-RX custom targets and invalid records without changing retained state/output.
Keep per-domain record ownership and reset after reclaim. No delivery or kind-4
emission, new ambient authority or sibling changes. Use existing mask/frame owner
contracts and current native byte mappings. Small private operation separates copy
qualification from handler activation without a second disposition table.

Select full command suite, host/pin checks and M4 regressions. New native cases
exercise overlap/cross-page copies, failures and reset over two generations; a
legacy build must reject the private operation. Preserve previous evidence and
freeze runtime sources. This allocates fixed record state only in the opted-in
build; it does not change user memory grants or public syscall behavior.

The first build failed strict C warnings on variables used only in the enabled
branch. The exact first C source and failed directory are retained. The disabled
branch now compiles only its query/status check. Existing C styles are preserved
without a whole-file formatting migration; changed Zig files use zig fmt 0.16.0.
No new dependencies or assembly were introduced. The existing memory-clobbering
trap and IF=0 native owner serialization define the copy boundary.

The first host check rejected the unclassified native-signal-actions boolean.
It is classified as an ordinary opt-in feature (checks remain enforced), alongside
runner-local. That host-only inventory edit occurred while runtime sources stayed
frozen; the failed host log is retained. It does not classify a fault-injection
option as releasable or publish the private interface.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
python3 scripts/regression.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The harness selects native-signal-actions only for cat-roles-startup-actions;
cat-roles-startup-actions-disabled uses the legacy build. The run used read-only
Aether-userland/build/native-c-5olokhku and the retained native lock at
zig-out/init-capacity-2026-09-06/tools.lock.json. Exact commands/tool/source digests
are recorded by the harness. collect.py captures the successful and failed native
build directories and verifies the previous packet and simplicity snapshot.
manifest.json seals the packet. The independent build-check.log is a successful
compile-only preflight with the previous guarded-client image, not an action test.

Remaining scope: absent-page/protection-change copy tests, peer native ownership,
private self-delivery and signal termination, public/raw adapter routing and
live guarded error/nonlocal-exit injection. No independent consumer acceptance,
full dash, asynchronous signals or published action API is claimed.

Results: all 246 command-runner cases, seven M4 regressions and 98 Python host
tests pass. Both enabled and disabled action clients complete two generations
and four reclaims with the existing terminal kinds. Runtime sources stayed frozen
through qualified runs. Workflow/Python syntax, Zig formatting and simplicity
snapshot checks pass. No new terminal kind was emitted.
