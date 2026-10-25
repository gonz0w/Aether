# 0051 — Native acquisition and cleanup witness

Accepted 2026-09-06 for BG-058's bounded ABI-6 consuming experiment.

## Contract and selected evidence

Use the retained SI-04 producer summary
3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155
and the original helper images, existing offline boot dependencies and Rust
1.98.0/x86_64-unknown-none/edition 2024. Keep the 4 KiB supervisor bound, native
smoke markers and existing cases unchanged. Native sources are frozen by the
runner before build; mutable sibling code is not consumed. BG-058 owns this
witness for model decisions 0047–0050; it is not a port of the Python driver.

Add one fixture-only native workload and two cleanup omission controls:

1. Create both channel pairs. A third creation must return operation 0x24000,
   errno 16 without changing the adapter's owned resources.
2. Invoke 0x23001 through a fixture probe with missing factory authority and an
   owned writer. Require the actual kernel return -13. This bypasses the adapter's
   local invalid-slot guard: it witnesses kernel pre-admission rejection. Close
   both retained reader/writer pairs explicitly, then require clean accounting.
   Omitting the first writer close must fail assertion 951 with reclaimed=0.
3. Run three normal workers in slots [0,1,0]. The first worker must have native
   generation one, confirming rejected launch did not consume slot generation.
   Each returns 17 (observed terminal 18). Register a wait at its current terminal
   revision with a distant bounded tick deadline; close reader and reclaim target.
   Require retained wait status Reclaimed, then explicitly release it before clean.
   Omitting release must fail assertion 953 with reclaimed=1. Complete the positive
   case only with result=100/reclaimed=3 and INIT PASS.

Expected assertions 950–954 are fixture diagnostics, not new operator output.
No service input, secrets or grants are printed. Preserve all existing smoke and
machine formats under the current Experience migration scope. Missing tools,
link overflow, watchdog expiry and generic boot failure cannot satisfy negatives.
The native trap probe uses the existing ABI argument/register contract, performs
no host mutation, and is explicitly outside the enforcing kernel boundary.

## Review and acceptance

Native resource operations and existing adapter accounting stay unchanged; only
fixture control flow and a fixture-only probe extend. Original images, grants,
standards pins, target ABI and retained historical bytes stay unchanged. Apply
Foundations O-01/O-04, I-03–06, E-01–08; scoped CE/CR ownership/unsafe review and
Experience stream/plain-marker rules. No new dependency or POSIX process claim.
Run all existing non-custom-worker cases plus these three, retain source/artifact
hashes and raw logs, compare unchanged legacy binary bytes, then run full checks.

Only busy channel creation and authority-denied launch are selected negative
returns. Other errno branches, uncertain-return recovery, full driver port,
large graphs, helpers/devices and automatic stop/force remain open under BG-058/
BG-033/BG-032. A successful witness proves this native sequence on this producer,
not complete Python/native behavioral equivalence or production init readiness.

Decision 0051 validation: all 17 native cases pass with 176 frozen inputs unchanged
and 14 compatibility binaries byte-identical. Full checks pass: 228 model tests /
23 mutation controls, 48 host tests, 37 harness tests and all eight offline gates.
The native catalog now audits 232 outcomes / 18 bundles / 4,880 listed files.
Evidence: `docs/evidence/native-acquisition-cleanup-2026-09-06/`.
