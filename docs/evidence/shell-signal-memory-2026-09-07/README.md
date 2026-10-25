# Signal frame memory preparation

Requirement before implementation: extend the CPU codec with owner-local page
permission checks, whole-frame copies and handler-entry preparation. The caller
provides authoritative page metadata and matching private backing slots under
serialization; the helpers retain no pointers or allocations. Actual native
syscall dispatch stays disabled until hardware FP-mask discovery, context
publication and the real restorer witness are qualified.

Allow only RX handler/restorer/return targets and RW/NX stack ranges. Reject
holes, non-user pages, changed permissions, overflow and malformed CPU frames
before writing anything. Return a CPU candidate, never publish Execution here.
No new authority, service, ABI number, profile, quota or sibling change.

Simplicity: direct functions over the existing owner page/backing representation
avoid a second address-space object or callback registry. A byte-at-a-time writer
would risk partial effects on a later invalid page; validate complete ranges first,
then copy under the same owner serialization. No old paths are removed yet.

Tests: host synthetic mapping fixtures exercise cross-page placement/return,
permission removal, unmapped holes, bad executable entries, malformed return,
red-zone preservation and unchanged backing on rejection. Run Debug/ReleaseSafe,
the full host suite and a permission-bypass mutant. These are host model tests;
no QEMU, actual FXSAVE/FXRSTOR, signal dispatch or dash acceptance is claimed.

Results: all eight final codec/memory tests pass in Debug and ReleaseSafe. The
initial seven-test passing run is retained in debug.log; debug-final.log includes
the added bad-target/backing-shape matrix. host.log records the passing existing
full host suite, including 98 Python tests and Zig/workflow/released-pin checks.
The permission-bypass mutant and its exact failure output are retained in mutant/.
No native runtime or consumer acceptance is claimed.

Commands from the repository root:

```sh
zig test kernel/arch/x86_64/native_signal.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig test kernel/arch/x86_64/native_signal.zig -O ReleaseSafe --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

For the deliberate negative control substitute this packet's mutant/native_signal.zig
in the first command; require TestExpectedError from permission rejection, not
compilation failure or timeout. Sources are retained under sources/. Prior sealed
evidence, SDK bytes, released standards and sibling repositories are unchanged.
