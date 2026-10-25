# Successful child under AERIO001

Before implementation, 2026-09-07. Reuse the existing four-role carrier, validated
384-byte launch and consumed receipt. A bounded parent delegates fd3/read and
fd4/write to bytecount fd0/1. Parent fd3 closes before child bootstrap, proving
retained child authority. Child reads abcdef and writes 6-LF to its separate sink;
runner stdout/stderr stay empty. Shared child-output cursor leaves parent read4
at EOF. Require child terminal0/kind1, exactly one collection, second ECHILD,
explicit client closes, request EOF, independent backend readback/stale checks,
two generations and six native reclaims. No admission from names alone.

Use a separate Rust owner experiment with existing native primitives and fixed
round-robin polling; existing denial and legacy profiles remain selected separately.
Normal and one-byte short writes must pass. Missing collection/close, fabricated
write success and redirected child writes must fail exact named checks. No global
state, quota increase, allocation, new ABI, dependency or kernel change. Stack
frames are fixed two-by-384-byte arrays; synchronous trap slices remain live and
exclusive through each call. No new unsafe block or pointer lifetime mechanism.

Aether owns this conformance fixture; userland owns actual parser and independent
consumer acceptance. O/I/E Foundations and PX scoped adaptation rules apply.
No sibling edits or pin changes. Update NATIVE-COMMAND-IO, workflow and STATE.
Run full command suite, connections, inherited launch, host/Zig/pins/workflow and
scoped C/Rust formatting. Freeze runtime sources, retain failed attempts, record
run UTC boundaries prospectively. Nonzero/fault composition, startup forwarding,
unknown collection and remaining RL/consumer acceptance remain separate work.
