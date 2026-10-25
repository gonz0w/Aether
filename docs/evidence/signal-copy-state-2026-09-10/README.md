# Staged signal-copy state — 2026-09-10

Added the owner-local `State.inheritFrom` operation and wired it after successful
child execution initialization, before publication. It copies all 64 validated
records by value and clears destination pending bits. It does not mutate parent
state. Both action-profile freeze/copy rejection gates remain unchanged; this
code does not yet admit a signal-enabled process copy.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#signal-copy-state-staging-selection--2026-09-10)
records scope, ownership, forbidden outcomes, resources and selected tests. One
bounded record assignment and pending reset avoid duplicating signal occurrences
or adding a snapshot service. The source and destination are distinct serialized
kernel objects. No user pointer, allocation, build option, quota or syscall is added.

Three new host tests cover exact record inheritance (including DFL, IGN, custom
handler, supported flags and signal 64), masked/coalesced parent pending state,
empty child pending state, independent mutation and delivery commits, parent reset,
and overwrite/reuse of a previously populated destination. The direct signal-state
and frame suite passes all 24 tests. These are host semantics, not copied-handler
execution or native pending-delivery qualification.

Three isolated source mutations fail the named inheritance test with
TestExpectedEqual: copying pending bits, dropping inherited records, and clearing
parent pending state. The first pending-mutant collector rejected the expected
failure because Zig prints its value diagnostic before FAIL; its source and log
are retained as attempt-1. The first dropped-record mutant did not compile because
its source parameter became unused; its source and log are retained as attempt-1.
The corrected mutant explicitly discards that parameter and fails semantically.
Neither setup failure is counted as a successful negative test. Final results and
exact commands/timings are in mutants.json. No live source changed for mutations.

The complete 91 connections and five launch cases are selected on frozen source,
including the existing action-profile freeze rejection and all earlier mask,
publication, rollback and uncertainty controls. Final reports and timings record
results. Host build, formatting, pins and workflow have separate receipts. Prior
full command/M4 execution remains historical: no dispatcher, scheduler, delivery,
client or backend behavior changes in the admitted profiles. Signal-enabled copy
and its handler-return/rollback target matrix remain unqualified.

The collector verifies the preceding mask packet, frozen source hashes, simplicity
snapshot and source/target archive readback. Runtime changes are retained relative
to that packet. All other runtime sources remain unchanged. No sibling source,
released pin or independent consumer acceptance changes. Manifest seals retained
receipts, including both failed mutant setup attempts. Full dash and R1 remain open.

Next: qualify native single-context action-enabled copy in an explicit experiment,
including inherited handler return, parent pending delivery, private child state
and copy-failure/reuse before lifting its rejection for consumers. Then compose
inherited-stream publication and installed SDK fork/exec/wait.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig test kernel/arch/x86_64/native_pending.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Final host, 91 connections and five launch suites pass within their review budgets.
All 91 envelope payloads match the previous packet outside entropy; the backend
image is byte-identical. No qualified runtime suite failed.

Archive readback verified 225 sources and 1,684 target artifacts; all three final
mutated source identities match their retained archives.
