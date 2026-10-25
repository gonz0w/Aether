# 0116 — Strict quality inventory and manifest parsing

BG-056 host tooling slice. Bound inventory/manifest JSON to 1 MiB and 32 levels;
reject duplicate keys, non-finite constants and invalid UTF-8. Require exact
inventory/surface fields and gap fields with the existing optional reference and
review_evidence paths. Validate strings, list sizes, unique reference lists,
normalized relative paths and lowercase SHA-256 before reference traversal.
Retain experimental/open vocabulary and cross-list ID uniqueness. Validate
optional gap references as local files. Capture manifest bytes once for both
hash and parse. Keep snapshot/release bytes and successful result fields fixed.

Malformed input follows existing stderr-only failure/exit 1, not new JSON failure
output. Add controls for shapes, metadata, duplicate JSON, bounds, manifest pins
and optional references; update minimal test inventories with required scope.
Run all gates. Full snapshot closure, file/symlink policy and end-of-run input
identity remain separate work. No native runtime or sibling changes.

Validation: eleven quality tests and all ten gates pass in
out/checks/run-ulshq9dr; success stdout is byte-identical to the prior run.
Snapshot pin and 24 native inputs are unchanged. Manual lint passes; the
60-column rendering retains two existing overlong literal lines for review.
