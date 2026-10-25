# Mixed stream aliases and observed close — 2026-10-21

UL-007/081/082 host qualification of `aefd_mixed_dup`,
`aefd_mixed_set_cloexec`, `aefd_mixed_close` in the existing tagged C table.
[Contract](../../proposals/FS-FD-STREAMS.md), [plan/review](review.md),
[final results](summary.json), [source-only candidate receipt](candidate.json).

Actual Python3.10.21 and3.14.7 each pass269 live C/Rust file cases, fourteen host
pipe/injected-completion scenarios per C child and six compiling semantic controls.
C17 strict warnings/format/UBSan and Rust2021/default Clippy/rustfmt/unsafe denial
pass. No suppressions. Exact predecessor source/service policy stays pinned;
107 host SDK headers plus sources/tools/resource/runtime verify and recheck.
Raw argv, environment, process receipts, deadlines, stdout/stderr, original checker,
source snapshots and binary hashes are retained for every attempt.

Real host pipes check surviving-alias read and final-close lifetime. Structured
observations distinguish known unconsumed error, consumed terminal error and unknown
with either physical endpoint state. Explicit fixture teardown closes unresolved
endpoints and checks EBADF; file admission retirement cannot stand for stream
cleanup. Console alias tests are local metadata only. The269 file cases use the
real existing Rust handler/process/AF07 policy and synthetic storage over host
pipes. File entry operations exercise the mixed delegate branch; original file-only
unsupported-stream tests still use their original API. This is not native console/
pipe execution, POSIX conformance, a selected shell, fork/exec or a fit measurement.

Six omissions require specific C assertions plus observed failed C child in Rust:
ignore alias class, close every alias, skip consumed clearing, accept unknown,
accept unconsumed success and skip stream flag update. First attempt passed its
baseline but skip-consumed-clearing failed earlier at successful final-close slot4,
not the later terminal-error slot3 expected by the checker. Retained failure;
corrected only that assertion oracle, then current and final minimum/current runs
pass. No production workaround or warning suppression.

Twenty-member source-only handoff:
`build/service-deliveries/filesystem-fd-streams-2026-10-21-v1`, manifest SHA256
`587b22a1192f5ac6f768c7becfe3f8144e4d42a2e56b6530bbf9b7dbb0b96e2c`.
Includes selected C headers/implementation, exact predecessor host fixtures, new
host tests, license, contract and dependency receipt; Rust dependency closures
remain separately pinned. No native SDK/engine copy, linked executable, profile
activation or silent replacement of prior immutable packets.

[Retention](retention.json) describes four exact owned attempts in
[attempts.tar.xz](attempts.tar.xz):20,124,533 logical file bytes removed after one
streaming readback verifies every retained member hash and size;4,289,052 archive
bytes retained. Physical disk reclamation was not measured. The failed checker
snapshot and all failed control logs remain available. Retention uses current
Python lzma only; the qualification checker runs on minimum Python independently.

Local quality output and final source hashes accompany this record; SHA256SUMS
seals the evidence after review. Implementing-agent technical review only;
independent affected-owner and reader review remains pending. All released pins,
predecessor candidates/evidence, machine markers and native limits unchanged.
No sibling edit/message, new guest, target installation or monitoring.

Next: consuming-owner reconciliation and selected shell startup/table with actual
native console/pipe adapters and pipe creation/write. Native copy/failed-exec
parent/FD preservation, immutable executable authority, complete code/stack/heap/
workspace/backing/channel fit, dispatcher/readiness/shutdown and matched native
command/error/cleanup/fresh boot remain required. Full UL/M3/R1, Zsh/packages/TTY
acceptance remains open. Per-logical C cloexec is metadata, not native exec proof.
