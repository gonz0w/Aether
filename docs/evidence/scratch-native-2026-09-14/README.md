# Native scratch backend transport — 2026-09-14

Real IPC between the existing supervisor and stream backend now exercises the
bounded scratch component. [Contract and prior review](../../NATIVE-SHELL-STARTUP.md#native-scratch-transport-selection)
define the opt-in bootstrap, authenticated lifetime, routing and cleanup. No
kernel, syscall, quota, worker slot or application-facing descriptor change.

Three focused cases and all325 connections cases pass. The positive requires
exact AB readback after close/reopen, denied wrong-root/read/write requests,
stale-handle rejection and an initially absent file in each backend lifetime.
It then completes the unchanged copied-process fixture: source71/child72/backend17
twice, six reclaims. Dropped-write rejects2502/reclaimed0; stale-epoch rejects2501
in the second lifetime after three reclaims. These are deliberate semantic failures,
not timeout-based acceptance. Both focused and full-run traces are retained.

The full suite took1011.94seconds, within the1800second review ceiling, with
unchanged frozen source hashes. Host tests pass, including102 Python tests and
all offline standards checks; Rust formatting, workflow and simplicity hashes pass.
There were no unexpected test failures. Kernel/build inputs are unchanged, so no
scheduler rerun was selected. Of620 comparable existing ELF/raw images,607 are
byte-identical;13 backend images changed and were covered by the full suite.
This does not substitute for matching command-runner qualification, still open
before the combined producer handoff. Independent consumer review remains open.

Sources, tool/SDK identity, commands, result manifests and serial traces are retained.
Target trees are archived, read back member by member and compared to originals
before deletion of their exact generated duplicate directories. Cleanup records
name those directories and byte counts. No previous evidence or sibling was changed.
The recorded runners identify the original experiment; reruns need fresh output
locations and must not overwrite this sealed packet.

The backend's generation is supplied by its authenticated supervisor, checked
against the launched connection there, and bound into root/open references. The
backend is not a public path service. Shared-offset/FD9/CLOEXEC inheritance and
real dash writable-file scripts are next; this test does not claim them. Scratch
remains RAM-backed and does not satisfy persistent storage or release assembly.
