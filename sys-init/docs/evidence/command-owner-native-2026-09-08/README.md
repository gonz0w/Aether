# Native command owner — 2026-09-08

BG-068 resolves code capacity locally; BG-067 now has five fresh native component
cases with sys-init-owned acquisition/terminal/cleanup. The scalar byte comparison
helper preserves the unsigned memcmp sign contract and fits under the unchanged
8 KiB bound: positive8016, empty7992, fault8080. The other two cases reuse the
positive owner with their original malformed/omitted-close runner images.

Positive and empty preserve actual6/0 newline output and six reclaims across two
generations. Fault preserves command detail134/kind2, runner1/backend17, unchanged
input, empty output and six reclaims. Wrong-role and omitted-close reject at exact
1401/1403 with zero reclaims; these are not recovered cleanup. No ordinary pass
marker is substituted for the negative oracle. Raw serial/QEMU logs are retained.

Three host tests compare every pair of unsigned byte values, multiple offsets and
lengths, equal ranges, each differing position, overlap, zero-length null pointers
and first-difference precedence. Two private controls reject signed comparison
and fabricated equality. The helper's native export exists only on target_os=none;
host tests do not interpose on the test runner's libc. The unsafe native boundary
requires valid readable ranges, excludes concurrent mutation and is not constant
time. Volatile byte reads prevent compiler-generated recursion into memcmp.

The staged source map matches all196 producer entries except the intentionally
replaced success.rs. Four local modules are added. Original application ELF bytes
are reused from the verified producer envelope; only the supervisor length/tail
changes. This is native consumer composition, not a fresh userland source rebuild.
ISOs remain private under out/ with hashes in results; envelopes/raw supervisors
are retained here for reconstruction with the pinned producer source and boot
inputs from the earlier intake. No sibling runtime/build reads were needed.

Initial kernel build failed before boot because global DYLD_LIBRARY_PATH selected
Rust's libLLVM for Zig's Clang library. Its failed log/report is retained. The
corrected driver removes that override for Zig/QEMU; all five executions pass.
Compiler library setup remains confined to the Rust link commands. No runtime
failure was observed. The earlier oversized builds remain in their original bundle.

Actual native execution retains the existing4 KiB stack and shows no fault in
these cases; peak stack usage and further schedules are unmeasured. Link size is
not a performance or future headroom claim. BG-067 partial-allocation/stop/cleanup
error controls and sustained/operator shutdown acceptance remain incomplete.
Full local checks follow; sha256.json excludes only itself.

Final local validation passes all ten gates in run-ofiwdlg8 with checked inputs
unchanged. Fourteen Rust methods/fifteen named records pass, including three
comparison tests and both semantic controls. The first aggregate failed only
the stale13-record unsafe inventory expectation; validation-attempt-1 retains it.
The corrected expectation14 matches the reviewed new boundary. Native source
bytes are unchanged after their five passing runs, and released locks remain fixed.
`git diff --check` passes. No independent review or full BG-067 completion follows.
