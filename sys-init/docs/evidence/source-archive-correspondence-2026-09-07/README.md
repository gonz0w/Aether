# Source archive correspondence — 2026-09-07

Decision 0140 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 76 tests. New controls cover every retained
archive, wrong hashes, duplicate/extra/missing/escaping names, link/directory/FIFO
members, malformed/truncated encodings, expansion overflow and oversized members.
All attempts passed. No filesystem extraction or execution occurs.

All ten `python3 scripts/check-all.py` gates pass in run-pgv6t__v with tested
sources unchanged. Exact commands/hashes are in validation/results.json. Four
mandoc lint/ASCII 78/ASCII 60/HTML commands pass. Independent reader/HTML visual
and narrow-layout review remains pending.

Audit stdout equals decision 0139; catalog, 24 native inputs and release locks
match the baseline. All 45 archives exactly match 8,307 summary entries. Maximums:
401 entries/archive, 3,528,344 compressed bytes, 9,737,622 member-content bytes,
3,653,632 bytes/file. The 32 MiB expansion limit includes tar metadata/padding;
regular nonsparse files are bounded at 4 MiB each and 10,000 members. Member
hashing uses 64 KiB chunks. Standard tar parsing semantics remain authoritative,
including historical PAX timestamps; no canonical tar-byte-format claim is made.

Of 3,430 producer source references, 3,420 match; ten .DS_Store references are
absent from five normalized archives. This slice verifies full summary input
maps, not full producer-source maps. Missing artifacts, source authenticity and
build provenance, filesystem deadlines/races and independent review remain limits.
No native/sibling/release-pin/historical-evidence changes; RC1 remains unpublished.
Source copies/diff identify this slice; only planning/decision validation notes
and evidence followed aggregate checks.
