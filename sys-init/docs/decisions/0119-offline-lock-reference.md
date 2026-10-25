# 0119 — Offline standards lock reference

BG-056 documentation and host-test slice, 2026-09-07. Describe the five local
lock fields, release path derivation, verification order, manifest grammar,
streams/exits, input lifetime and unsupported guarantees for all three wrappers.
Add synthetic cross-wrapper controls for valid lock order/line endings, malformed
fields and verification before child invocation. Do not change wrapper behavior,
lock bytes, released standards, sibling repositories or native inputs.

Applicable Foundations E-01–08 and reviewed Documentation/Testing topics require
exact identity and scoped evidence; a matching digest is not publication authority.
Run focused tests and all repository checks. Record unbounded reads/traversal,
ordinary-file policy, verification-to-execution races and tool/environment closure
as BG-056 follow-ups. Independent technical/reader review remains pending.

Validation: four new tests (45 subcases) pass; all ten repository gates pass in
out/checks/run-j58r3r5b. The initial valid-invocation expectations used unresolved
macOS temporary paths; expected paths were corrected to match script resolution.
Both attempts are retained. Wrappers match their previous retained sources;
locks and 24 native input hashes are unchanged. See
../evidence/offline-lock-reference-2026-09-07/README.md.
