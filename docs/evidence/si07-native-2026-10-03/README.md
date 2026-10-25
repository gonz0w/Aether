# SI-07 matched v2 integration — 2026-10-03

Before-code requirement: consume userland's sealed NATIVE_SUSTAINED_V2 runner/
bytecount and integrate matching AERIO002/NIO2/0x7b owner paths under unchanged
AENSI001/ABI22. Existing compiled/default legacy behavior and evidence stay valid.
Aether owns grants/identity/lifetime enforcement and its private witness; userland
owns transport and payload semantics; sys-init owns supervision and consuming review.

Required selection: verify complete client seal/payloads; opt-in owner carrier,
child bootstrap, receipt and full-width cohort checks; fresh positive native five
cycles/idle/cleanup/halt; exact semantic rejection controls and legacy regressions;
host/pin/workflow and linked code/stack inspection. Retain every attempt in separate
roots. No quota/ABI/kernel authority change or public runtime adoption is required.

Security: private wire epochs remain16-bit and separate from typed native handles.
Validate cohort before publishing grants/bindings and retire on private exhaustion
before admission. Stop, terminal, endpoint closure and reclaim remain distinct.
Borrowed trap buffers stay live during synchronous calls. Paths/receipts cannot
create native authority. Unsupported interruption/recovery remains explicit.

Simplicity: use opt-in branches within the existing owner rather than a second
supervisor or new kernel protocol. Preserve defaults until matching replacement is
qualified. No shared standards or sys-init policy is implemented here. Forbidden:
claiming SI-07 complete from a positive alone, silent v1 fallback, generation masking,
resource growth, sibling writes or fabricated consumer/reader approval.

## Native boundary test scope, before implementation

Use an isolated frozen source copy with worker initial generations seeded to65534
only before first admission, and the owner loop fixed to65535 then65536. Run one
real runner/bytecount command, assert exact terminal/cleanup at65535, then reject
65536 before another launch and authorize halt. Production sources, generation
limits, grants and defaults stay unchanged. This tests the native boundary rather
than claiming65535 sequential executions or a new reseeding operation. Preserve
exact mutations and source/artifact identities. The simpler host arithmetic test
already passes but cannot exercise the native generation syscall/transport/cleanup.
No normal runtime mechanism or shared standard is added.

Additional pre-code selection: isolated native epochs255,256,65534 exercise role-bit boundaries with one real command and orderly cleanup/halt per fresh cohort. Both old/new parent-carrier mismatches must reject before child/backend effects; a test-only observer checks exit110, untouched backend, explicit parent/backend closure and reclaim, then halt. These observers do not implement general recovery policy.

## Result and consumer gate

The production-owner opt-in hooks pass five actual runner/bytecount/backend cycles
at1–5, including generation3, exact `6\n` checked inside the owner, terminal0/0/17,
15 reclaims and authorized halt at3044 total/3004 idle ticks. Native cohort-divergence
stop/terminal/close/reclaim/stale denial and65536 pre-admission rejection pass.
Four isolated seeded cohorts complete actual commands at255,256,65534,65535; each
has three reclaims and halt. The final cohort rejects65536 before another launch.
Both parent-carrier mismatch directions exit110 before child admission, assert
untouched backend stdout/stderr, close/reclaim both peers and halt. The observer
branches exist only in frozen test copies, not the production owner.

`native-comparison.json` compares nine final traces and rejects66 deliberate
corruptions. Five fresh legacy cases (positive, empty, fault, wrong-role, skip-close)
pass in `legacy-results.json`; legacy application inputs remain frozen. Host/pin/
workflow checks pass. Production owner code/stack maxima are9344/16384 and3816/4088;
all nine final images, including test observers, reach10000 code/3832 stack. Raw
images equal linked ELF binary extraction, and all three formatted production-owner
rebuilds match native-tested raw bytes. `stack-bindings.json`,
`boundary-stack-bindings.json` and audit directories retain the scoped models.
Immutable GOT targets were inspected as memcpy/memset/memcmp; the conservative
model is not formal verification, kernel stack analysis or all-path assurance.

The original userland packet seal verifies1800 members. `client/` is a selected
local input copy, not a claim that all1800 members are duplicated here. Its original
manifest/profile/README and selected payloads are retained; our final seal covers
exact local bytes. The fresh backend is993272 bytes, SHA256
`1baca5d0f8c99aba3f062640d7b5d8af8ae052f8852abb09ed8d09e5d7d8ad80`.
The supplied v2 parent/child hashes are in intake.json. Exact Rust/Zig/client SDK/
LLVM pins and flags are in command records, profile.json and tools.lock.json.
The fixed48 experiment entropy bytes make no production entropy/security claim.

This is a kernel-owner replay checkpoint, not full SI-07/SUSTAIN-01–06 acceptance.
The next independent gate is userland technical replay/findings and sys-init's real
policy owner consuming the frozen AENSI001/ABI22 closure. Neither repository/chat
was modified or messaged. Sys-init must define how outstanding bounded work settles
before interruption/shutdown; a fixture observer is not that policy. Remaining
native child-bootstrap mismatch, malformed/stale/foreign endpoint schedules and
partial/poisoned-close cleanup are explicit gaps. Host decoder/transport checks and
older kernel authority/wake controls retain their own scope and cannot silently
fill them. A seeded65535 witness is not an endurance run of65535 sequential cycles.
Independent reader approval, runtime SDK disposition, persistent storage/packages
and assembled R1 remain separate gates. No released pin, grant, quota or kernel
source changed in this integration step.

## Reproduction and retained failures

Run from the repository root with the pinned offline tools. Commands below refer
to retained drivers; build roots deliberately reject reuse. Replaying a native case
requires restoring its indexed artifacts and (for seeded/mismatch tests) the exact
staged sources before running, or making a new uniquely named build attempt.

```sh
python3 docs/evidence/si07-native-2026-10-03/build.py positive-5
SI07_CASE=positive-5 PROBE_ATTEMPT=positive-5 python3 docs/evidence/si07-native-2026-10-03/run.py
python3 docs/evidence/si07-native-2026-10-03/boundary-build.py
python3 docs/evidence/si07-native-2026-10-03/boundary-run.py
python3 docs/evidence/si07-native-2026-10-03/epoch-build.py 255
python3 docs/evidence/si07-native-2026-10-03/epoch-run.py 255
python3 docs/evidence/si07-native-2026-10-03/mixed-build.py v2-owner-v1-parent
python3 docs/evidence/si07-native-2026-10-03/mixed-run.py v2-owner-v1-parent
python3 docs/evidence/si07-native-2026-10-03/check-native.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The65534/256 and reverse mismatch commands use the corresponding driver arguments.
The all-case build/source/attempt inventories distinguish qualified runs, failed
runs and build-only outputs. Earlier positive runs used a retained backend; the
three final production-owner cases use a fresh source-built backend. Failures:
initial legacy setup referenced a nonexistent sibling tools.lock (no native case
ran); local exact profile tools lock corrected it. First full recursive rustfmt
check included legacy formatting; scoped edited-file formatting passes. Initial
control readers stopped on a partial line; the cohort cleanup also used output-read
instead of stop. Both were corrected before the final native controls. Boundary
builds1/2 omitted toolchain/LICENSE; build3 attempted a nonexistent notice directory
and failed before compilation. All are retained. Initial mismatch host oracles
still expected the successful command terminal sequence; the guest had correctly
rejected and reclaimed. A corrected oracle was rerun against unchanged artifacts;
original failed JSON/logs/driver remain. No failed attempt is relabelled passing.

Artifacts are compressed into `available-artifacts.tar.gz` with per-member digest
index and full readback verification before deleting only this turn's redundant
build roots/caches. Frozen per-case source exports and all attempt logs remain.
`cleanup.json` records exactly which owned roots were removed. The final packet
SHA256SUMS covers every retained member except itself; no earlier evidence changed.

The first final link check found an inherited ROADMAP link to a removed sibling captured BG-061 story. The local reference now points to the current sys-init integration-gates document; sibling bytes remain unchanged. checks-attempt-1 retains that failed check and its preceding passing outputs. Full local checks rerun after the link correction.
