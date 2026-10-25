# Native memory / descriptor consumer rerun

2026-09-05: the current userland-owned adapter and probe pass all twelve cases
against the Aether kernel snapshot, using sys-init's I/O supervisor. The frozen
runner exits 0 and every captured source hash verifies after execution. Kernel
host tests, 44 Python tests and all three offline standards checks also pass.

The positive and metadata-retry cases each execute two successful generations,
with 24 backing pages used / 104 remaining on admission and two explicit reclaims.
Allocation, failed-realloc data preservation, zeroing and protection run through
the userland adapter alongside descriptor operations. Missing authority, skipped
protection, missing metadata-denial injection, disabled memory, descriptor
controls and three malformed-image cases produce their required rejections.

This is normal exit/reclaim/replacement. Forced stop with live memory remains the
separate kernel-owned fixture; combined forced-stop consumer acceptance is not
claimed. General process, filesystem, TTY, native SMP memory and release readiness
remain outside this witness.

An earlier attempt completed the guest cases but exited 1 because the live
sys-init builder changed during the run. It is rejected evidence, not a pass.
The successful rerun uses byte-verified frozen companion sources and SDK payloads
in private /tmp directories. No companion working-tree changes were made.

See `summary.json` for exact invocation, scope and retained-file digests;
`capture.json` for original and copied companion inputs; `sources.json` for the
kernel and producer snapshot; `commands.json` and case logs for execution.
Large images and payloads remain under the private run paths named in the report.
[Userland reproduction contract](../../../../Aether-userland/docs/NATIVE-MEMORY.md)
owns the consumer command and broader limitations.
