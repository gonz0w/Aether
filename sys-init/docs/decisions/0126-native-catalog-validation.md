# 0126 — Strict native catalog validation

BG-056 host slice, 2026-09-07. Validate the complete catalog before any bundle
read: exact fields, supported schemas/profiles, scalar types, normalized paths,
digests and unique bundle/case names. Catalog JSON is UTF-8, at most 4 MiB and
32 levels deep, with duplicate keys/non-finite values rejected. Bound bundles
and cases per bundle to 1,000 and total cases to 10,000; text to 4,096 characters.
Use the captured catalog bytes for parsing and reported SHA-256. Preserve current
catalog/evidence bytes, result schema and native behavior. No sibling edits.

Tests cover invalid fields/types/paths/profiles and JSON controls before bundle
access, plus compatibility with the maintained catalog and full aggregate.
Receipt schemas, ordinary-file policy, large artifact bounds and final filesystem
consistency remain follow-ons. E-01–08 apply to host audit only; no native witness
is replaced by these checks. Independent review stays open.

Validation: 33 native-harness tests and all ten gates pass in run-7bbbia9g.
Initial aggregate run-e20qyqiw had ten passing gates but failed source identity
because collection-budget tests were added during its execution. Both runs are
retained. Native audit stdout, catalog bytes and 24 native inputs are unchanged.
Four manual commands pass. Evidence:
../evidence/native-catalog-validation-2026-09-07/README.md.
