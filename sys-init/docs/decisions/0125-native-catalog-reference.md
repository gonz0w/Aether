# 0125 — Native evidence catalog reference

BG-056 documentation/host-test slice, 2026-09-07. Document catalog, bundle and
case fields; I/O versus init report dispatch; required receipt/artifact links;
serial/envelope rules; output and input lifetime. Distinguish actual validations
from intended record shape. Add controls for top-level rejection before bundle
access and required evidence membership. Keep checker/catalog/evidence bytes fixed.

Foundations E-01–08 and reviewed Documentation/Testing topics apply to historical
host auditing, not new native acceptance. Run focused and full checks. Track strict
JSON/field validation, bounded ordinary-file reads, complete tree membership and
same-byte identity as follow-ons before claiming those properties. No sibling,
native, released-pin or immutable evidence changes. Independent review stays open.

Validation: 28 native-harness tests pass, including three new catalog controls.
All ten gates pass in out/checks/run-fnv8xqqe. Audit stdout, checker/catalog hashes
and 24 native inputs match the previous checkpoint. Evidence:
../evidence/native-catalog-reference-2026-09-07/README.md.
