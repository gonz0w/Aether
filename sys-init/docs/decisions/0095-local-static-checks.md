# 0095 — Local static checks after RC1 review

Accepted bounded tooling slice, 2026-09-06; BG-056 / ADP-03. Apply candidate CR-03, CP-01/03,
CA-01/02 and TD/TE as local process guidance; release pins remain unchanged.

Add an offline required static gate: compile active first-party Python source
without executing it or writing bytecode, and require exact rustfmt output for
`tests/native_sample_receipts.rs` and `tests/native_pending_history.rs` only.
Use installed Rust 1.98.0 rustfmt, edition/style edition 2024, skip child modules.
Pin its actual version and macOS arm64 executable hash in a developer-tool lock.
Unknown hosts, missing tools, identity mismatch and timeouts cannot pass. Report
machine JSON on stdout, escaped diagnostics on stderr, exit 0/1/2/64 for
pass/failure/precondition/usage. Do not install tools from the check.

Keep the native modules, upstream/generated sources, archived/vendored evidence
and other legacy Rust outside formatting scope. Formatting the two host tests is
a separate mechanical change: native input bytes must remain identical. Snapshot
before/after source and check normalized formatter equivalence and execute their existing positive and
omission test suite. Python syntax is not lint, type checking or Python-version
matrix qualification. Clippy, C diagnostics expansion and wider migration remain
explicit BG-056 work, not claimed by this first gate.

Test missing/mismatched tools, syntax/format rejection, empty scope, bounded input,
nonzero tool exit and timeout, then run the full development suite. Keep the
initial formatting findings and exact tool/source identities. Existing report
schemas and native markers remain unchanged; the aggregate gains a required
static check. No native behavior, post-R1 feature or sibling source change.

## Results

Decision 0095 adds the required static gate: 61 active Python
files compile without execution, and two host Rust test files match pinned
Rust 1.98.0 rustfmt with edition/style edition 2024. Nine failure-path harness
cases pass; all ten aggregate gates pass in `out/checks/run-4_gbjn_w`. Initial
formatting rejection is retained. Reformatting the before snapshots reproduces
both final host test sources exactly. All 22 native source/build files retain
their before hashes; no fresh native execution is needed for this tooling slice.
Existing host Rust behavior/omission suites pass with the formatted sources.

Native/C formatting, Clippy, unsafe/FFI inventory, complete manuals and release
review remain BG-056. Scheduled extended testing remains BG-054. macOS arm64 is
the sole pinned formatter host; missing/unreviewed hosts block rather than pass.
Candidate and release pins remain unchanged; this is scoped local process work.
