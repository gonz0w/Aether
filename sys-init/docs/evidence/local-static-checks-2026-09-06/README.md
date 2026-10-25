# Local static gate evidence

2026-09-06; decision 0095 / BG-056.

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

`before/` retains both initial host test sources. `baseline.stdout/stderr` retain
the expected format rejection. `formatting.json` binds the mechanical conversion;
`native-inputs-before.json` verifies the unchanged native boundary. `validation/`
retains ten passing gates and the nine harness failure cases. `source/` binds
final tooling, test, lock and adoption records. No production/runtime conformance
or complete Coding adoption is claimed.
