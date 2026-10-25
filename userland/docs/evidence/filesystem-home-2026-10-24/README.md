# Home delegation library evidence — 2026-10-24

[FS-HOME](../../proposals/FS-HOME.md) owns scope, acceptance and continuation.
These are actual Rust owner-policy host tests and no_std builds with synthetic
storage. No VM, live service transport, complete executable fit or persistence
qualification was performed. Native sources, sealed deliveries and pins stay fixed.

Command from `userland/`:
`python3 -B experiments/filesystem-service/check-home.py`.
The checker records exact argv, tool/library/source hashes, host/interpreter,
timestamps, child cleanup and bounded diagnostics in each attempt. Pinned Rust
1.98.0, rustfmt1.9.0 and Clippy0.1.98 run offline; compiler/format edition2021 is
the existing fixture convention. Current Python execution is scoped to the
recorded interpreter; Python3.10 minimum execution is not established here.

## Attempts

| Attempt | Actual result |
| --- | --- |
| [01](attempt-01.json) | Harness failure: unsafe-code denial was incorrectly applied to existing metadata FFI. Narrowed the ban to the changed Owner/library while retaining existing unsafe-operation diagnostics for metadata. No product result. |
| [02](attempt-02.json) | Planned tests-before-implementation red: selected owner tests fail with missing `attach_home` (E0599). This is an unavailable-API compiler result, not a semantic runtime failure. |
| [03](attempt-03.json) | Implementation tests/builds pass, but the shortened-serial-reservation mutant fails through overflow rather than the named semantic assertion. The checker rejects the attempt; it is not a passing control. |
| [04](attempt-04.json) | Final pass:14 selected tests (13 new home plus1 existing runtime),1 unselected AF08 runtime regression,13 legacy owner tests and five compiling semantic omissions. |

Final controls remove source-right checks, widen root rights, substitute the root
object for home, publish despite exhausted serials, or reuse the single free
handle slot. Each compiles and fails its named assertion/test. The corrected
serial control demonstrates wrongful publication on exhaustion; the prior generic
overflow remains a failed attempt. Strict rustfmt, Clippy and Owner unsafe denial
pass. Selected home, AF08 and legacy libraries compile on host and
x86_64-unknown-none; missing directory-context selection rejects on both targets.

The measured zero-sized-provider Owner stays1080 bytes/alignment8 on the host;
target compile-time size/alignment equality also passes. This is a library layout
comparison, not full-service resident/stack/code sizing. All final input/tool/native
library hashes recheck, every child cleanup completes, and owned generated trees
are removed. No whole run archive, copied SDK or binaries are retained.

[CLI controls](cli-controls.json) pass help/version, escaped usage64 and
missing/mismatched-prerequisite2, plus syntax on final checker bytes. The only
post-attempt04 checker edit puts purpose before usage in help; the receipt records
that exact impact check and reuses unaffected behavior evidence. The final checker
SHA256 is `794b2bbccdc54d1a95b63259b0cfa316f91639612fdf459fbcffc71f18ccf80a`.

[Process checks](process-checks.json) retain standards/workflow/userland quality
checks and owned reference-process cleanup. The [separate peer review](peer-review-checks.json)
found no unresolved findings and repeats final inventory/link gates; its scope is
recorded in the owning record. Host tests do not replace future authenticated provisioning,
public write/CWD semantics or native recovery gates.
