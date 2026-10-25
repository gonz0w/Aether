# UL-067 three-role prerequisite — 2026-09-07

The direct AECAT001 conformance client receives separate input/read32,
output/write32 and diagnostic/write256 roles. Complete header/record validation
precedes any binding publication. The owner independently observes copying of
empty or 32-byte binary input, exact authoritative input preservation, stdout,
diagnostic separation, positions, explicit closes, terminal request EOF and
backend close/stale denial. Two generations use client/backend slots0/1 and four
native reclaims, not a runner+command child six-reclaim witness.

The conformance client uses actual musl read/write/close. It is not Toybox, does
not duplicate Toybox initialization/finalization and does not admit a cat command.
See [NATIVE-CAT](../../NATIVE-CAT.md) and [before-code contract](contract.md).
Exact inspected userland requests are retained under review-inputs/. No sibling,
old UL-059 return bytes or standards/consumer pin changed.

Four positive workloads are cat-roles-copy, empty, short (7-byte reads/3-byte
writes) and diagnostic (private D-LF sentinel). Four full-carrier rejection cases
change third-role rights, descriptor, generation or declared role count; each
requires terminal110, zero I/O/publication and owner cleanup. Four controls skip
or corrupt copy (1505), omit diagnostic close (1503), or publish bindings before
the final invalid record (1502). The early-publication control attempts an actual
write on the prematurely published stdout; owner rejection precedes backend effects.
These are exact semantic oracles, not watchdog or generic-panic acceptance.

The fixed binary input is user/native-command/cat-input.bin,32 bytes including
NUL and high bytes; source receipts bind it. Backend output is capped at 32 although
the reused static storage allocation remains 512 bytes. No allocator, capability
or kernel limit changed. Masks never grant authority: proposed initial 0077 state
remains for userland's process-local umask contract; this adds no field/stub/syscall.

## Reproduce

Run `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use --connections / --inherited-launch with the same arguments for regressions.
Host/pin/workflow checks use `zig build test --cache-dir .zig-cache
--global-cache-dir .zig-cache/global`; new C and Rust formatting is checked with
the existing pinned tools. Complete commands, flags, sources and artifact identities
remain in the final receipts. Timing files retain run UTC boundaries; per-case
clock records and independent/extended-stage evidence remain missing.

## Remaining scope

This provides producer prerequisites for portions of CAT-01/02/07/08 only. Exact
cat artifact admission/copied startup, invalid invocation diagnostics, actual native
Toybox initialization, I/O errors/unknown replies, callback/flush/finalization and
abnormal stop remain to qualify. Userland owns its patch/SDK and independent pin/
build/acceptance. No CAT row, native cat package, POSIX shell or R1 is accepted.

## Final qualification

All selected runs pass on their first attempts: 152 command cases (140 prior plus
12 role-prerequisite cases), six connections and nine inherited-launch cases.
All 98 Python tests, Zig tests, offline pin/workflow and scoped C/Rust format
checks pass. Three target receipts match frozen runtime sources. Kernel/build and
SDK/libc/tool-lock inputs match the preceding return qualification; existing
UL-059 bundle files are unchanged. Largest new role owner: 4,584/8,192 bytes.

`final-artifacts.tar.gz` retains frozen sources, client/backend binaries, native
envelopes and logs; duplicate installed boot files, kernel.elf and ISOs are omitted
with build/ISO receipts retained. `qualification.json`, timing files and manifest
bind retained evidence. No failed attempt was observed or discarded in this slice.
These results do not establish independent consumer/reader approval or full
extended-testing conformance.
