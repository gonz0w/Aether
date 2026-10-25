# ABI9 composed owner capacity — 2026-09-08

BG-067 implementation attempt. The candidate replaces reference launch,
observation and cleanup with the existing paired-connection owner while retaining
the pinned command/file protocol and its five-case semantics. No new native
execution occurred: the unchanged linker rejects the candidate above 8192 bytes.

The final nonzero-handle variant measures positive8608, empty8640 and fault8688
bytes. All three enforced builds reject with `program broker exceeds two code
pages`. Separate measurement-only linker copies omit only that code-size assertion;
entry/writable-static assertions remain. Measurement binaries are not booted or
accepted. The kernel/profile/producer link script remains unchanged.

Earlier plain-handle measurements were8832/8816/8896 bytes. The first attempt
failed because rust-lld lacked its libLLVM search path; the corrected environment
uses the installed compiler's lib directory. Initial function-factoring selection
also failed an exact-text assertion; the corrected private variants still exceed
the real limit. Size-oriented compiler checks also fail that limit. Attempts and
logs are retained, not rewritten as passing validation.

The staged adapter preserves signed native errors, treats unexpected success
values as unknown, and conservatively closes against close/reclaim error replay.
Nonzero handles use Rust's optional-handle representation without changing wire
values. The candidate is not yet a qualified native boundary or a product error
reporter. Fixture assertion failures still terminate the experiment. Stop/partial
launch/recovery witnesses remain required when it fits.

Sources are derived from the exact intake packet's 196-member source archive;
raw application artifacts and startup are reused only for this bounded link study.
The current native command adapter sources are under source/. Existing native
entry points and released/runtime pins remain unchanged. Compiler commands and
measurement inputs are retained; host full checks follow. BG-068 records the
capacity/design decision, with no sibling edit or request delivery implied.

All ten local gates pass in run-8y9u_yfp with checked sources unchanged.
`git diff --check` passes. The actual compiler matches the earlier pinned
Rust1.98.0 identity; host-qualified owner sources and released locks are unchanged.
No native success or stack high-water claim follows from these checks.
sha256.json seals this new bundle and excludes only itself.
