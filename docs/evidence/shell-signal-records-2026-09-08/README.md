# Retained signal action records

Before implementation: replace the host-only semantic action table with one
retained 32-byte record per public signal slot. Preserve mask, flags and restorer
for queries; derive delivery semantics instead of maintaining a second table.
Keep existing standard-signal post/commit limits, default-ignore discard and
checked frame preparation. Query 9/19 remains DFL; setters reject. Preserve DFL/IGN
configuration for 35–64 without claiming delivery; reject reserved 32–34. Custom
handlers require RESTORER and valid low-half targets; other flags reject before
mutation. Native RX checks and syscall output atomicity remain integration work.

Select owner/frame Debug and ReleaseSafe tests, exact query/flag/range/atomicity
controls, a lost-mask mutant and full host/pin checks. No dispatch, ABI allocation,
sibling changes or native conformance claim. One retained table costs 2 KiB plus
pending bits, replacing the prior at-most-1-KiB semantic table; this is host-only
storage, not a quota expansion. Simpler semantic storage loses successful query
fields; a second query table duplicates ownership. Remove that loss through one
representation and preserve existing experiment APIs as semantic projections.

Ten owner and nine frame tests pass in Debug/ReleaseSafe. All host/pin checks pass
(98 Python tests). The lost-mask mutant fails the exact retained-query test. No
failed normal build/run attempts occurred. Prior target evidence remains intact;
no target run is selected for a component still imported only by host tests.

Reproduce from repository root:

```sh
zig test kernel/arch/x86_64/native_pending.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig test kernel/arch/x86_64/native_pending.zig -O ReleaseSafe --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The archived mutant sets `next.mask = 0`; its exact source/log are retained. It
must fail `raw query retains flags mask and restorer across semantic changes`.
`collect.py` verifies source archives, prior packet and simplicity snapshot;
manifest.json seals the evidence. The existing native reference describes range,
flag and copy-validation limits. Native placement, public/raw routing and explicit
signal terminal interpretation remain open; no independent consumer sign-off.

The first collection verifier expected FAIL adjacent to the test name, but Zig
prints the mask comparison first. The exact failed collector and log are retained.
The corrected verifier checks the named test block and exact expected/actual mask
in the same mutant log; no rerun or runtime-source change was required.
