# Dash scratch replacement helper — 2026-09-15

The opt-in FORK_SHELL_FILES command helper restores validated scratch survivors
before calling the unchanged consumer helper and closes all surviving aliases
on normal return. It retains the existing mask/identity and removed-FD10 checks.
The expected receive order is stream bootstrap, table, saved mask, AESFD001 grant,
and two sixteen-byte description records. Owner-side integration must publish
that order; no existing launch profile selects this mode.

## Evidence

- `native-compile.json`: both the actual replacement and unchanged consumer helper
  compile with the captured musl SDK and pinned LLVM21.1.8. The consumer source
  SHA256 is 3fdea5d515011e49516f35cf8b9abdc214024a226bb3ba560480fa9775cebcf8.
  These are separate objects, not a linked or executed native image.
- `compatibility.json`: all eight existing helper launch selections preprocess
  identically after blank-line removal. `dash-command-before.c` preserves the
  pre-change source; quote include paths resolve against its original directory.
- `host.log`: required Zig/104 Python host tests pass, including the existing
  scratch restore malformed-record, stale-reference, CLOEXEC and atomicity checks.
  They do not execute this replacement main function or prove its cleanup order.
- `checks.json`: pinned formatting, workflow, standards and all four simplicity
  snapshot inputs pass. No new tool entry point or launch profile was added.
- `sources.json/tar.gz`: eight scoped source/reference inputs, not a full replay
  kit. `consumer-helper.c` retains the unchanged consumer bytes. `objects.json`
  and `objects.tar.gz` retain both object files. Archive members and originals
  were rehashed before removing only verified generated duplicates.

No unexpected failed attempts occurred. No sibling repository, released pin,
kernel behavior or resource limit was changed. No native/QEMU or consumer
acceptance, persistence or R1 readiness is claimed.

Next wire the owner dispatcher and actual fork/exec admission, issue the matching
records, then run the unchanged leak workload: actual helper95, parent22, empty
output and complete cleanup. Full connections and matching command-runner suites
remain required before handoff.
