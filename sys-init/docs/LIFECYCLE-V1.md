# Aether lifecycle v1 experiment

Validated 2026-09-05. BG-034 is complete: a sys-init-owned, independently authored native conformance client boots through Aether's external lifecycle image seam. The production init remains unimplemented.

[Decision 0001](decisions/0001-lifecycle-v1-experiment.md) accepts this bounded subset of the kernel handoff. The [exact consumed contract](evidence/lifecycle-v1-2026-09-05/AETHER-M4-LIFECYCLE-V1.md) is retained with [snapshot hashes](evidence/lifecycle-v1-2026-09-05/source-sha256.json), [client source hashes](evidence/lifecycle-v1-2026-09-05/client-source-sha256.json) and [commands/results/artifact hashes](evidence/lifecycle-v1-2026-09-05/results.json). Earlier research describes earlier companion snapshots; this report supersedes their blanket native-work waiting condition.

## What runs

[The client](../prototypes/aether-lifecycle/main.rs) checks bootstrap registers and ABI, limited rights, holder-slot and worker quotas, generation identity, stale handles, terminal detail retention, and cleanup ordering. Its policy is to observe termination, destroy the task, release backing, and acknowledge the retained terminal record before replacement. Forced termination publishes the record during destruction. Wrong-generation acknowledgment, premature acknowledgment and allocation before acknowledgment must fail without losing the record.

Aether selects the finite workload: one normal exit, seven protection faults, then one live worker to stop. Our client checks all nine generations, including repeated terminal reads before/after destruction and release. It uses the factory supplied by the kernel; it has no ambient filesystem or console authority.

The positive image contains **2,480 bytes of code/constant data**, plus the **32-byte envelope** (2,512 bytes total). The profile supplies a separate 4 KiB stack. These are fixture sizes, not total system memory, production-init size or performance measurements.

## Reproduce

Host prerequisites: Python 3, Rust 1.98.0 with `x86_64-unknown-none`, and Aether's documented Zig/QEMU/ISO tools and boot assets already installed. Rust and Python are experiment tooling choices, not production language decisions. The target uses no libc or Cargo dependencies.

From the sys-init repository:

```sh
python3 scripts/build-lifecycle.py out/lifecycle
python3 tests/lifecycle-native.py --aether "$HOME/DEV/Aether" --work /tmp/sys-init-lifecycle-new-run
```

Choose a new, nonexistent work directory. The test copies Aether source and `.deps`, records source hashes, and builds all three clients using separate output prefixes. It never builds in the companion checkout. Each kernel invocation uses `zig build smoke -Dsmp=false -Dlifecycle-image=ABSOLUTE_CLIENT_PATH`; full commands are in results.json. All three expected outcomes must match for the test script to exit successfully.

The native profile has a 1,000-PIT-tick kernel watchdog; it is not a user-space monotonic clock or calibrated service timeout. Aether's emulator has its own watchdog; this runner also bounds each build/smoke subprocess at 120 seconds. Client polling relies on that finite fixture watchdog. QEMU needs permission to bind a local Unix control socket. The first sandboxed attempt failed at that socket before boot; the recorded successful run used the same isolated source snapshot with that permission.

## Observed results

| Client | Expected and observed | Evidence |
| --- | --- | --- |
| Normal | `AETHER LIFECYCLE V1 PASS`; nine releases, seven faults, one exit, one live stop; every generation acknowledged after reclaim | [Serial log](evidence/lifecycle-v1-2026-09-05/pass-serial.log) |
| Wrong terminal detail | Client expects exit 111 instead of 110; completes with diagnostic 311; kernel panics, smoke fails, no v1 pass marker | [Serial log](evidence/lifecycle-v1-2026-09-05/wrong_detail-serial.log) |
| Fault at entry | External client executes an illegal instruction; documented supervisor-failure panic, smoke fails, no v1 pass marker | [Serial log](evidence/lifecycle-v1-2026-09-05/fault_entry-serial.log) |

The negative cases show that our supplied envelope controls execution and that a client-side semantic mismatch is detected. They do not exhaustively validate kernel mechanisms. Other Aether kernel regression cases were not independently rerun here. Build logs are alongside serial logs; hashes also cover generated artifacts retained in the temporary run directory. No sibling project was modified.

Client diagnostics: 200 + operation number means unexpected syscall status; 301–307 cover bootstrap/identity/state checks; 310 + instance means a terminal mismatch; 330 + instance means unstable repeated observation; 399 means Rust panic. Successful completion uses 100.

## What remains

BG-032/BG-033 retain general loading, event/deadline/grant semantics and supervisor recovery. The current kernel deliberately panics on supervisor death; it does not restart sys-init. BG-007/BG-022 readiness research is the next independent step. BG-020/BG-028 retain configurable supervision policy and runtime ownership; BG-030 retains production Aether toolchain evaluation. Package activation, device teardown, SMP supervision, POSIX process semantics and a usable boot/recovery environment are outside this proof.

The canonical [builder manual](man/sys-init-build-lifecycle.1) covers current
inputs, options, output lifetime, receipts and build-only limitations. See
[documentation coverage](DOCUMENTATION-INVENTORY.md) for review status.

The canonical [native-runner manual](man/sys-init-test-lifecycle-native.1) covers
current inputs, profile selection, workspace and error behavior. Target
acceptance still requires the matching retained producer/consumer evidence.

Decision 0107 adds bounded legacy command capture with retained log prefixes
and adjacent attempt receipts. Actual nonzero smoke exits still reach the
existing semantic checks; timeout/overflow cannot become expected rejections.
Nested compiler groups have their own bounds; full nested interruption cleanup
is not established by an outer group kill. See the decision and source manual.
