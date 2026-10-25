# ABI-6 offline audit validation — 2026-09-05

Command: `python3 scripts/check-all.py`; retained full report in
[validation/results.json](validation/results.json). All checks pass on macOS
arm64: 48 host tests, 34 model cases/three mutation controls, 30 harness tests,
three standards checks and 29 audited native outcomes across 1,494 listed files.

The audit adds seven ABI-6 cases to five existing ABI-2 bundles. Five new test
methods exercise completeness, command failures, exact ordered serial assertions,
bounded envelopes and re-pinned artifact mutations. Historical bundles are
unchanged. This is offline evidence validation, not a new QEMU or Linux run.
Producer source archives are hashed without extraction/execution; receipt hashes
do not establish publisher authenticity or validate unretained ISO bytes.

The source snapshot includes the catalog, checker, regression tests and adapter
decision. Decision 0018 specifies subsequent work; no native adapter extraction
or new service/dependent workload is implemented by this checkpoint.
