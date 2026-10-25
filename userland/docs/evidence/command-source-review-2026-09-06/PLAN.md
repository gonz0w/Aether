# UL-063 command-runner audit and mechanical formatting

Scope: read runner/adapter/entry/bytecount/control C and three Python build/runtime
helpers; review current producer startup/result and sys-init/package boundaries
for UL-059. No protocol, C edition, compiler flags or behavior change in this
slice. Record findings and required corrections before future implementation.

Pin Clang-format 21.1.8 plus local style. Snapshot six C/header files, run the
non-mutating format check and record its expected failure, then apply only that
formatter. Rebuild five native client ELFs with unchanged existing builder flags
and compare exact bytes with source-matching UL-057 baseline. Run all 21 host/
control cases and native object inspection. Exact binary equality scopes reuse
of native behavior evidence; no new native runtime execution is claimed.

Python cleanup/environment gaps are reviewed, not fixed in the formatting change.
Missing reviewed fixes and dedicated failure controls keep UL-063 active and block
public-runner behavior changes. Retain all sources, attempts and tool identities.
Apply approved CC/CP, CE/CD, TD/TE, Foundations E and local quality workflow.
