# Combined roles and denied launches — 2026-09-07

AERIO001 is a separately selected, atomic four-role carrier: independent runner
stdout/stderr plus explicit child input/output authority. AEOUT001 and existing
child/startup profiles retain their wire bytes and selection. The backend adds
one 64-byte child-output record; no native capacity or kernel ABI is changed.
See the [preimplementation contract](contract.md) and
[NATIVE-COMMAND-IO](../../NATIVE-COMMAND-IO.md) for fields and exact semantics.

The owner observes one complete existing-format launch request and actual ENOENT
from name validation, EACCES from a rights-widening request, or EBUSY from partial
channel reservation before native child admission. It verifies exact copied
proposed stderr text, normal parent status2, empty stdout/child output, unchanged
input, four explicit alias closes, all backend closes/stale denial and two native
generations/four reclaims. A child image in the envelope is not an admission.

Controls reject skipped/repeated launch at1340, wrong text at1305, wrong reply errno
at1301 (client125), and a leaked held pair at1342. Invalid fourth-role rights must
publish nothing and terminate with bootstrap110, zero requests and owner cleanup.
No output/exit number substitutes for the actual request/error and cleanup evidence.

## Retained failures

Attempt1 failed during compilation of the pre-existing capacity-bypass control:
its disabled check left the new capacity table unused under -Werror. No QEMU cases
ran. The table is now declared only when that check is compiled; no warning was
suppressed. Source/artifact/log snapshots remain in `attempt-1.tar.gz`.

Attempt2 passed ENOENT/EACCES but failed EBUSY at owner1342 after two native reclaims
(first generation complete). Channel slots have a monotonic three-generation
budget. Probing available slots after every denial used generations needed for
second-generation verification. This was a test-budget error, not evidence of a
kernel leak. `attempt-2.tar.gz` retains the failing source and serial evidence.

Final scheduling uses reservation generations1/2 and probes two available pairs
at generation3 after the second denial, then requires third-pair EBUSY and closes
all probe endpoints. Successful second reservation also witnesses first cleanup.
The intentional leak control probes early and must reject before native reclaim.
No generation limit was raised, and no reset/unbounded reuse is claimed.

## Scope

The C fixture is not userland's parser. The three diagnostic files are copied
first-party proposals with hashes retained in `text-origin.json`. Successful child
execution under the combined carrier, denial diagnostic/close failures, full
carrier truncation coverage, remaining RL cases, affected-owner review and the
immutable consumer handoff remain open. Existing successful child profiles still
run separately. Neither UL-059, UL-067 nor R1 is accepted by this slice.

Reproduce with NATIVE-COMMAND-IO's command, SDK
`/Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and tools lock
`/Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use the same arguments with `--connections` and `--inherited-launch` for regressions.

## Final qualification

Attempt3 passes all 111 command cases (previous 102 plus three denials, five exact
negative controls and fourth-role startup rejection). Nine inherited-launch and
six connections regressions pass, alongside 98 Python tests and Zig/offline
pin/workflow checks. Rust/C formatting and diff checks pass. Final source hashes
match all three frozen suites. All 34 kernel/build inputs and SDK/libc/tool-lock
identities match the previous startup qualification; release pins/siblings are
unchanged. The largest combined supervisor is 6,792 bytes within the 8,192-byte bound.

`final-artifacts.tar.gz` retains frozen sources, generated headers, compiled/native
envelopes and logs. ISOs, duplicate installed boot files and kernel.elf are omitted;
ISO hashes/build commands remain in receipts. The two failed attempts are retained
separately. `qualification.json` uses filesystem receipt modification times, not
exact start/per-case timestamps. Independent owner review, extended evidence and
consumer acceptance remain open; inventory success does not waive those gates.
