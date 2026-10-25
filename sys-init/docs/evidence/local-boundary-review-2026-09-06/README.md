# Native boundary review and Clippy evidence

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

`before/` retains pre-lint host source; initial Clippy logs and failed compiler
report retain findings. The macro-hidden control issue is described in decision
0096; it was corrected before acceptance. `producer-protection.S` is the verified
retained kernel entry/restore input; its provenance and limit are in producer-source.json.
`validation/` records the complete ten-gate run. Subsequent contact/docs updates
do not change checked tooling or native behavior. `source/` binds final records.
