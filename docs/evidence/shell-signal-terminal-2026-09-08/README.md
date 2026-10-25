# Signal terminal candidate and compatibility boundary

Before implementation: define a host-only signal terminal candidate with distinct
kind/detail, preserving native exit/fault/stop bytes and their ownership semantics.
Inspect actual sys-init and userland consumers read-only. Do not emit new tags to
legacy profiles or treat signal death as normal exit 128+signal. Qualify the
candidate's bounded default-termination construction and compile the captured
userland result decoder to demonstrate legacy compatibility and rejection of the
new tag. Retain input hashes/notices and prior evidence. Run owner/frame Debug,
ReleaseSafe and host/pin checks; no native behavior changes or target claim.

Simplicity: a distinct cause tag in the existing conceptual terminal tuple avoids
ambiguous overloaded detail values. It requires explicit consumer/profile adoption,
not a silent compatibility conversion. No new service, negotiation framework,
allocation or published ABI is introduced by this candidate. Shared lifecycle
policy remains with sys-init; the exact native fixture contract belongs here.

Results: eleven owner tests plus nine frame tests pass in Debug/ReleaseSafe;
98 Python host tests and pin/workflow checks pass. The fault-tag mutant rejects
kind 2 where kind 4 is required. The actual captured userland decoder passes three
legacy terminal cases and rejects all 31 candidate signal details with unchanged
output. Sys-init was source-inspected only; no consumer acceptance is claimed.
No failed normal build/run attempts. No native code dispatch changes or target run.

Inputs came from Aether-userland/experiments/command-runner/runner-result.{c,h}
and sys-init/prototypes/native-command/lifecycle.rs. inputs/manifest.json binds
their bytes; notices remain unchanged. Native source/consumer-copy snapshots,
exact host compile/run commands and identities are retained by collect.py.

Reproduce from the repository root:

```sh
zig test kernel/arch/x86_64/native_pending.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig test kernel/arch/x86_64/native_pending.zig -O ReleaseSafe --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 docs/evidence/shell-signal-terminal-2026-09-08/collect.py
```

The decoder check is a macOS host test using pinned Clang 21.1.8 and the recorded
local SDK path, not a freestanding native qualification. The archived mutant
changes candidate kind 4 to CPU-fault kind 2 and must fail the named test.
manifest.json seals the evidence; previous packet hashes and simplicity snapshot
are verified. Native profile negotiation and independent owner reviews remain open.
