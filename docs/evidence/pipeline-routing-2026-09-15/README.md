# Two-pipe routing — 2026-09-15

A new private routing adapter distinguishes the two pipes needed by the unchanged
three-stage pipeline. Each existing PipelinePipe remains the sole owner of its
FIFO, holders and generations. The adapter stores no mutable state and allocates
nothing. Existing native paths do not import it; this is host execution and target
compilation evidence, not native multi-stage pipeline qualification.

## Requirement, ownership and review

The [preimplementation review](../../NATIVE-SHELL-STARTUP.md#two-pipe-routing-review--2026-09-15)
records authority, reference layout, bindings, errors, limits, pending/reply
obligations, standards and test selection. References carry exact object,
generation and endpoint identity. Bindings reserve 0–2 for stdio, 3/4 for the first
pipe and 5/6 for the second. Neither field grants authority: the authenticated
caller must still be ready and hold the selected endpoint in that object.

O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply. A small adapter over existing
cores avoids a registry, duplicated FIFO, aggregate holder ledger or new global
generation allocator. Two unmodified cores alone cannot route equal-generation
references. No kernel, capacity, dependency, unsafe/FFI, public SDK, sibling or
released-pin changes. Aether owns this private adapter; consumer intake remains
with userland and supervision policy with sys-init.

## Checks and limits

checks.json records exact commands, times, statuses and logs:

- 42 Rust tests pass: 34 existing core tests plus eight routing tests. They cover
  equal-generation object separation, exact references/bindings, independent data,
  holder enforcement, malformed routes, binding mismatch, stale reuse, selected
  object exhaustion, local EOF/EPIPE/Pending and staged/stale participants.
- Both deliberate controls compile and fail exactly one named test. wrong-object
  redirects to the first pipe and fails data isolation; unchecked-binding removes
  the binding check and fails malformed-route atomic rejection. Their sources,
  commands, failing logs and binaries are preserved. No unexpected failures.
- x86_64-unknown-none no_std compilation passes, including public routing methods.
  target-core.o is compilation evidence only.
- zig build test passes all 104 host tests and required Zig/pin checks. Formatting,
  workflow, standards and diff checks pass. Final checks also verify the four
  simplicity snapshot members and its pinned manifest digest.
- All 268 prior native runtime/support inputs match the sealed participant packet.
  Native import inspection finds only the new host wrapper referencing this module.
  No QEMU run was needed for unchanged existing native paths; the earlier 358-case
  result is not qualification of this new adapter.

Run the normal gate from the repository root:

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 -m unittest discover -s tests -p test_pipe_owner.py
rustfmt +1.98.0 --edition 2024 --check user/native-connections/pipeline.rs
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

sources.tar.gz and sources.json preserve qualified code, host support, workflow
and the preimplementation review. qualify.py records this packet's one-shot run;
replay its commands in a fresh output directory, preserving this sealed packet.
The two deliberate control sources are paired with the same pipe.rs and exec_fds.rs
in the source archive. Review inputs and final checks are separately retained.
Generated test binaries are archived and verified before deleting their exact
unpacked duplicates. No previous evidence or unrelated temporary files are removed.
SHA256SUMS seals this packet; archive members have their own hash manifest.

## Remaining work

The owner must integrate seven bindings with two-object fork/exec validation and
cleanup, then the opt-in native worker/channel capacity. Lifecycle effects on both
objects require validated plans before either mutation, staged holder reservation
before readiness, and exact confirmed peer stop before uncertain cleanup. The
routing adapter is not a multi-object transaction or a lifecycle dispatcher.
Actual pipeline/early-reader execution, matching runner, independent SDK/userland
acceptance, persistence/OpenZFS, package execution and sys-init R1 assembly remain.
