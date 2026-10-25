# Successful child with four explicit roles — 2026-09-07

AERIO001 now has a separately selected successful-child conformance experiment.
The parent delegates only its child input/output bindings, closes its own input
before child bootstrap, collects one actual normal0 terminal result and confirms
second collection returns ECHILD. The child runs actual libc bytecount, consumes
abcdef and writes 6-LF. Parent output-source read observes the shared cursor at
EOF. Runner stdout/stderr stay empty and are independently read back along with
input and child output. All aliases close, backend stale references fail, requests
drain at terminal and two generations finish with six native reclaims.

See the [preimplementation contract](contract.md) and
[NATIVE-COMMAND-IO](../../NATIVE-COMMAND-IO.md). This uses existing kernel and
backend primitives, immutable pins and fixed quotas. No sibling repository changed.
The owner is a bounded Rust fixture; it is not a production process service or the
userland parser. Exact carrier/launch wire bytes remain unchanged.

Positive cases are `success-child` and `success-short` (one-byte writes). Controls
omit collection (1401), omit the runner stdout close (1403), acknowledge discarded
writes or send child output into runner stdout (1405). The latter two require
independent backend readback rather than trusting returned write lengths.

## Failed attempts

Attempt1 was a compile failure: existing Rust helpers accept 32-byte arrays, but
the new carrier sender passed all 160 bytes. No QEMU test ran. The sender now emits
the identical carrier in five 32-byte frames, preserving existing helper bounds.
`attempt-1.tar.gz` retains the failing source and build logs.

Attempt2 reached QEMU but rejected the new parent ELF before admission. It lacked
PT_TLS, required by the existing bounded native ELF profile. The parent now uses
the same checked thread-local value as existing clients. The kernel parser was
not relaxed. `attempt-2.tar.gz` retains the ELF, source and serial rejection.
This was an implementation failure, not a successful negative-control result.

## Scope and reproduction

Run `python3 scripts/launch_smoke.py --command-runner` with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Replace the profile with `--connections` or `--inherited-launch` for compatibility.
Host checks use `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global`; scoped formatting and inventory checks accompany them.

Nonzero/fault mapping under these roles, logical AERUN001 startup composition,
unknown collection, remaining RL cases and an immutable producer handoff followed
by independent userland review/build remain open. This does not accept UL-059,
UL-067, the actual shell path or R1. Source identity and local checks do not replace
independent review or the missing extended testing coverage.

## Final qualification

Attempt3 passes all 127 command cases (121 prior cases plus two success witnesses
and four semantic controls). Six connections and nine inherited-launch cases pass.
All 98 Python tests, Zig tests, offline pins, workflow and scoped C/Rust formatting
checks pass. Final source hashes match all three target-suite receipts; all 34
kernel/build inputs and SDK/libc/tool-lock identities match the previous denial
failure qualification. Largest new supervisor: 7,136/8,192 bytes.

Final command and compatibility UTC start/end boundaries are retained in timing
files; per-case timestamps and complete extended-stage evidence remain missing.
Attempt1's dispatch observation is separate; earlier failed attempts retain logs
and source snapshots without invented exact end times. `final-artifacts.tar.gz`
contains frozen sources, generated artifacts, envelopes and logs; ISOs, duplicate
installed boot files and kernel.elf are omitted, with build/ISO receipts retained.
`qualification.json` and `manifest.json` bind the retained evidence. No independent
review, consumer approval or release-readiness claim follows from these checks.
