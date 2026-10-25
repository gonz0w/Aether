# Native consumer helper child

All 431 command cases and 98 Python host tests pass, along with Zig, offline pin
and workflow checks. Final run: command-runner-suite-wa_xlavm; about1437 seconds
within the1800-second review ceiling. No native attempt failed.

The unchanged userland helper is pinned locally by SHA-256, retaining its BSD notice.
Only its main symbol is renamed for the native wrapper. The wrapper bootstraps the
existing descriptors, calls the real helper, then closes its inherited input/output.
An opt-in owner admits `/inputs/helper` with argv `argv`, `a b`, literal `*` and
environment LC_ALL=C, WITNESS=value through the existing isolated-image launcher.

The positive witness requires exact `argv ok\n` output, no input consumption,
empty diagnostics, child0/parent0/backend17, consuming collection and six reclaims
across two generations. Independent parent/child connections and address spaces
remain; inherited descriptors retain their existing shared open-description state.
The wrapper changes its private TLS sentinel and the parent checks its own value.

Corrupting either the spaced argument or WITNESS after request validation yields
helper91 and owner1407. Skipping the helper body yields owner1405; missing child
closes yields1403. All four controls require zero reclaims and exact child status.
These are deliberate implementation mutations, not expected successful launches.

## Scope and reproduction

This qualifies the helper boundary. Dash does not yet perform fork/exec/waitpid to
launch it; the full unchanged DASH-argv workload remains unqualified. No kernel,
SDK, wire, quota, upstream dash object, sibling or released-pin change is included.
No fresh M4 run was selected because kernel/M4 paths are unchanged. The scoped
owner namespace uses the existing supervisor image grant; a path string grants no
authority. Three workers and six channels fit the current profile.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --command-runner \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

The new cases run first, followed by the existing cases in their prior relative
order. The before-code selection in NATIVE-SHELL-STARTUP and scope-review.json
record ownership, forbidden outcomes and the simpler existing-launch alternative.
The new owner sizes are7368–7384 bytes; the suite maximum remains8152 within8192.

Scoped Rust formatting, Python syntax and the four simplicity snapshot hashes
pass. The recursive formatting attempt found preexisting style differences in
unchanged cat-roles.rs; rustfmt-recursive.log retains that attempt. No broad
formatting was performed. Host, native and timing logs remain separate evidence.
The collector verifies frozen runtime sources, previous sealed evidence and archive
readback. This is producer evidence, not independent consumer or release acceptance.

All 284 previous cat/shell owner binaries remain byte-identical. Exact timing,
selected serial receipts, source hashes and target artifacts are retained here.

Verified archives retain 216 frozen sources and8,795 target artifacts. The final
manifest binds all packet files; source and artifact archives passed readback.
