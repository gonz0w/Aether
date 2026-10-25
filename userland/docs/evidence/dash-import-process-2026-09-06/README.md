# UL-075 — dash import process hardening

Source review found an unbounded, environment-inheriting nm invocation and assert
checks that Python optimization could disable. The revised auditor uses explicit
pin/empty-input errors and the existing owned process helper. PLAN.md defines scope,
clauses, risks, controls and limitations. No shared pins or upstream files changed.

Four test methods exercise six controls: exact symbol subtraction/environment,
wrong pin before execution, empty input, nonzero exit, timeout with descendant and
output exhaustion. All pass on Python 3.14.7 and 3.10.21; the complete suite also
passes on 3.10.21 with -O, retaining the explicit pin check. Each started failed
process group is absent after cleanup. Failure leaves a preexisting report untouched;
it cannot be consumed as success for this attempt. Raw logs identify retained build
fixtures and receipts. Copies of all execution receipts/streams are retained here.

Commands (repository root):

```
python3 -B experiments/dash-reference/test-audit-imports.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-audit-imports.py
build/python-qualification/Python-3.10.21/python.exe -B -O experiments/dash-reference/test-audit-imports.py
python3 -B build/dash-import-review/compare.py
python3 -B docs/quality/check.py
```

comparison.json binds platform/tool/runtime and the original report hash. The
retained compare.py copies the original objects to a new build directory and
compares scope, keys, all object digests and all symbols against the original
report. All 32 objects and 99 symbols match. Only script identity changes in the
report. No compilation, guest execution or native acceptance is inferred.

sources.json records current auditor, tests and unchanged helper hashes. The
UL-074 census remains a historical snapshot: its audit-imports.py digest is now
superseded by this record, and test-audit-imports.py is newly maintained source.
The new test belongs to the dash-reference subsystem and its README/coverage route.
No rewrite of historical evidence is required to hide this intentional drift.

Author review and host controls are complete; independent technical review remains
pending and UL-075 stays active. The earlier user approval covered UL-072, not this
change. No release exception is requested. Remaining UL-061/063 work includes dash
CLI documentation and build/container-run lifecycle audits. Per-process limits do
not bound total object traversal or all invocations; trusted local trees, no concurrent
mutation and non-detached children remain assumptions, not confinement guarantees.
