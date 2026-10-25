# Runner startup field coverage — 2026-09-07

This slice exercises remaining AEOUT001 field categories without changing its
normal wire bytes or authority. See the [preimplementation contract](contract.md)
and [NATIVE-COMMAND-IO](../../NATIVE-COMMAND-IO.md) for exact scope.

Eight malformed full-carrier cases cover magic/version, role count one/three,
stale header generation, header padding, duplicate FD, wrong capacity and record
padding. Existing rights, role and reference cases remain. Each requires normal
bootstrap failure110, no published bindings/request traffic, empty sinks and
independently verified owner cleanup across two native generations/four reclaims.
A deliberately broken capacity check must reject at owner1302 on its first request;
a matching parent status cannot substitute for observed startup rejection.

This covers every defined carrier field category, not exhaustive byte mutation,
short/truncated carrier delivery or fuzzing. The parser's normal checks already
existed; the only parser addition is an explicit test-only bypass. No new kernel
ABI, native capacity, allocation, dependency or unsafe boundary is introduced.

The [denied-launch review](denial-review.md) records why the next slice needs
explicit combined runner and child-I/O authority, real request/error observations
and reservation-quota restoration. It is design work, not an implemented carrier,
allocated magic, consumer approval or a producer handoff. Exact denied-launch
cases, role/child composition, remaining RL coverage, owner review and independent
userland adoption remain open. Neither UL-059, UL-067 nor R1 is accepted here.

Reproduce with the NATIVE-COMMAND-IO command using SDK
`/Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and tools lock
`/Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Use the same arguments with `--connections` and `--inherited-launch` for regressions.

## Qualification

First attempts pass: 102 command cases (previous 93 plus eight malformed-carrier
cases and one bypass control), nine inherited-launch and six connections cases,
98 Python tests plus Zig/offline pin/workflow checks. Rust/C formatting and diff
checks pass. Sources stayed frozen and match all three suite receipts. All 34
kernel/build inputs and SDK/libc/tool-lock identities match the prior qualification.
No release pin or sibling was changed, and no failed attempts were discarded.

`artifacts.tar.gz` retains source snapshots, generated headers, native envelopes,
compiled artifacts, commands and serial logs. ISOs, duplicate installed boot copies
and kernel.elf are omitted; ISO hashes remain in receipts. `qualification.json`
records filesystem receipt modification times, not exact start/per-case timestamps.
That traceability limitation, extended coverage and independent owner/consumer
review remain open; passing inventory checks do not waive standards or release gates.
