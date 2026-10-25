# 0096 — Boundary inventory and scoped Clippy

Accepted scoped review/tooling, 2026-09-06; BG-056 follows decision 0095. Review first-party native
Rust/C low-level boundaries without changing native bytes. Record site identity,
ABI, memory/lifetime, clobber, cleanup and unresolved proof obligations; textual
inventory is not soundness certification or an independent review.

Extend the host static gate with pinned Rust 1.98.0 Clippy on the two existing
host receipt/history harnesses and their imported pure modules. Deny the default
Clippy group, not every restriction/pedantic lint. Resolve two needless range
loops in host tests; retain the benign partial-harness dead_code diagnostic
without a global allow. Include source inputs and tool identities before/after.
Run in a private source tree with metadata output and existing duration/output
bounds. Never invoke native trap modules on the host.

Test a deliberately lint-invalid host source, missing/mismatched tool identity
and gate failures. Run the complete aggregate and existing host omission tests.
Preserve pre-fix findings, reviewed source hashes and all native source bytes.
No release pin, native ABI, C worker, post-R1 feature or sibling source changes.

The first lint edit accidentally changed an unrelated expected-prefix assignment;
the compiler rejected undefined `row` and the assignment was restored. The initial
clone-on-Copy control was hidden inside an assertion macro and produced no lint;
moving the clone to a standalone expression gives an actual denied lint. Both
findings are retained as review history, not waived or counted as passes.

## Results and next work

Decision 0096 records 50 textual low-level boundary occurrences in 13 native
Rust/C files, with exact hashes and scoped obligations. Source-drift/omission
checks now require an explicit inventory review. The static gate additionally
runs pinned default-group Clippy on two host harnesses and their pure imported
modules. Two host index loops were corrected; no native source bytes changed.
Eleven static-harness cases and all ten aggregate gates pass in
`out/checks/run-74_rx3ah`. The unused shared-method Rust warning remains visible.
The failed intermediate compiler edit and lint-control issue are recorded.

The maintainer supplied security@aethersys.org; SECURITY.md now publishes it.
Independent technical/reader review remains pending. Next local finding: bound
the older I/O worker builder's tools, then qualify exact artifact compatibility.
The boundary inventory is not full per-profile soundness acceptance or a waiver.
