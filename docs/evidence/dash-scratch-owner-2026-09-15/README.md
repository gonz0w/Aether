# Dash scratch owner fork grant — 2026-09-15

Owner-internal AESFC001 construction now validates canonical descriptor counts
and live scratch holders before the existing reference/generation inheritance
transition. The authenticated caller must already have frozen the source, checked
stream authority and admitted the native child. This helper does not perform
those operations, send the grant or recover a failed child.

## Results

- `controls.json`: all32 composed Rust tests pass. Coverage includes FD9/11/15,
  CLOEXEC-only reader inheritance, shared offset and final-holder closure,
  malformed records/counts, missing holders, stale refs, replay and empty slots.
- The bypassed holder check fails
  `fork_grant_rejects_invalid_snapshot_without_owner_mutation`; publishing the
  parent reference fails `fork_grant_keeps_cloexec_aliases_and_shared_lifetime`.
  Both compile and exit101 with the named assertion; neither relies on timeout.
- `native-compile.json`: enabled shell_files boundary compiles as no_std for
  x86_64-unknown-none with Rust1.98.0, edition2024, panic=abort. Object compilation
  is not native process/transport evidence.
- `focus.log`: permanent host wrapper passes, including enabled target compilation.
- `host.log`: required `zig build test --cache-dir .zig-cache
  --global-cache-dir .zig-cache/global` passes, including104 Python tests.
- `checks.json`: Rust formatting, workflow inventory, released standards and all
  four pinned simplicity inputs pass. No released pin changed.

No native profile selects shell_files yet. The new method and its descriptor
validator inclusion are cfg-gated out of current native builds. Existing native
holder/gateway behavior is unchanged. No QEMU run, SDK acceptance or release
readiness is claimed; no sibling repository was modified.

## Inputs and retention

`sources.json` and `sources.tar.gz` retain seven scoped review inputs; they are
not a complete native replay kit. `artifacts.json` and `artifacts.tar.gz` retain
exact positive and mutant sources, host executables and the target object.
Every archive member was hash-verified and each original rehashed before deleting
only its generated temporary duplicate. Deliberate failures remain in the packet.
There were no unexpected build/test failures in this step.

## Remaining integration

Carry the file owner through real dash dispatch and freeze/admission, issue the
separate grant before child readiness, and restore surviving file descriptors in
the replacement helper. The unchanged fd-leak-control workload must produce actual
helper95 and parent22 with empty output and complete cleanup. Full connections
and matching command-runner qualification precede consumer handoff. Failed-child
cleanup, poisoned-close recovery, persistence and R1 assembly remain separate work.
