# UL-062 retained parser replay and reduction plan

Before behavior work: extend only the host parser workload and its driver. Keep
runner-parse.c, native interfaces, sibling repositories and released pins unchanged.
This continues TC-02 fuzz failure retention; it does not finish UL-062.

Applicable requirements: Foundations E-01–08, I-03; approved Testing TD-01–05,
TC-01–03, TE-01–05; Coding CE-02–09, CC-01–04, CP-01–03; Documentation DW/DS/DP.
Aether-userland owns this fixture. Original code is BSD-2-Clause; reuse pinned
Clang 21.1.8, Apple SDK, Python standard library and existing process ownership.
No dependencies are fetched. Use the existing strict C17 diagnostics and UBSan
selection; default ASan remains required and its known host timeout stays open.

PXR-01: semantic failure retains exact bytes, length, must-accept expectation and
oracle name in exclusively created files within the owned work directory. Replay
must reproduce the same oracle/exit 90. Original parser must pass that input.
PXR-02: deterministic byte deletion and zero substitution retain only the same
oracle. Preserve original and all candidate inputs, exact command/cleanup receipts,
source/tool/plan hashes, reduced bytes and reduction trace. Confirm the final input
replays and a full final pass finds no single deletion or nonzero-to-zero reduction.
This is local minimality for those operations, not a globally smallest input.
PXR-03: empty and oversized replay files, missing files and invalid expectation
arguments; missing/invalid input must not look like a parser failure. Existing
output files must not be overwritten. Internal fixture errors use exit 91.
PXR-04: budget exhaustion must fail rather than claim minimization; synthetic
controls exercise deletion, zero reduction, non-reproducing input and exhaustion.
PXR-05: unchanged 172038-case sweep, parser controls and UBSan canary regressions;
actual Python 3.10.21 and 3.14.7 execution, pinned format check and local quality gate.

Each candidate is at most 225 bytes. At most 1024 reduction oracle invocations and
180 seconds between invocations; each child also has a 30-second timeout and
existing bounded cleanup/output caps. Deadline is checked between calls and does
not interrupt active cleanup. This is not a total-suite deadline or RSS guarantee.
No VM or network needed. Sanitizer-only sweep crashes still require separate input
isolation; this slice retains semantic failures, with every replay input persisted
before execution. Interrupted/failed reduction leaves its trace and original intact.

Technical self-review will cover file exclusivity, short/error I/O, pointer lifetime,
replay bounds, exact oracle matching, process ownership and budget behavior.
Independent technical/reader review remains pending; no approval is inferred.
Retain failed and successful attempts; source/plan changes invalidate affected
reuse. Update EXTENDED, coverage, BACKLOG and STATE with actual evidence and
remaining ASan, broader exploration, transport/static/resource and review gaps.
