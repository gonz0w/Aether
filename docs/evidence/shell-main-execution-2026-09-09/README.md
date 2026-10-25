# Actual dash main: noninteractive builtin and exit

All363 command cases and host/pin/workflow checks (98 Python tests) pass on final
frozen runtime inputs. No failed or interrupted target attempt occurred.

The explicit main selection calls real dash main after V3 startup admission,
without running the earlier init or startup probes. It supplies PWD=/work,
LC_ALL=C, no ENV and sh -c "printf 'dash-main\n'; exit 7". The selected main object
is separately pinned from the ENV build comparison; the other31 original objects
remain unchanged. Dash owns init, parsing, printf, exit builtin, trap cleanup and
flush. The adapter wraps only final _exit to close each present facade descriptor
before native termination, retaining status7 unless close fails (112).

The positive oracle requires exact stdout dash-main/newline, no diagnostic or
input consumption, terminal7/backend17 and four reclaims across two generations.
Skipping main must fail client0/owner1501; skipping the final facade close must
fail client7/owner1503. Those controls make no reclaim claim. Native endpoint
teardown alone cannot substitute for owner-observed service alias retirement.

No kernel, sibling, SDK default, released pin or original upstream object changes.
The copied replacement and its narrow patch retain upstream terms and existing
source/generator review limits. No new open/path service, exec, wait, pipe, login,
TTY or ENV-script execution is claimed. This is actual main execution of a bounded
noninteractive builtin command, not an interactive shell or full consumer intake.
Existing C style and Rust edition2024 remain; no fresh M4 selection.

Commands from the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
rustfmt +1.98.0 --edition 2024 --check user/native-command/cat-roles.rs
python3 docs/evidence/shell-main-execution-2026-09-09/collect.py
```

The collector verifies predecessor and configuration packets, final runtime inputs,
new replacement inputs and simplicity snapshot, then reads back archived sources
and target artifacts. The manifest seals the completed packet. A successful
preflight host run is retained separately from the final host run.
See [pre-code selection](../../NATIVE-SHELL-STARTUP.md#actual-main-first-execution-selection--2026-09-09).
Next is actual-main ENV loading/suppression with observable file access, then the
existing consumer argv/signal/syntax and native child exec/wait workloads.
