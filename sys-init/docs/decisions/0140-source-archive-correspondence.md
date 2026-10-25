# 0140 — Bounded source archive correspondence

BG-056 host evidence slice, 2026-09-07; Foundations E-01–08 applies. Verify each
producer source archive against the complete summary inputs map without filesystem
extraction. Consume the existing verified compressed buffer (4 MiB ceiling),
expand gzip to at most 32 MiB plus one sentinel byte, parse tar in memory, accept
only regular nonsparse files with normalized names, reject duplicate names and
require exact map membership/digests. At most 10,000 members and 4 MiB per file;
read/hash members in 64 KiB chunks. Tar metadata may carry historical PAX mtime;
all parsing remains bounded by the expanded buffer. No paths are opened from tar.

Inventory: 45 archives, 8,307 regular entries, max 401 entries/archive, 3,528,344
compressed bytes, 9,737,622 file-content bytes and 3,653,632 bytes/file. All summary
maps match exactly. Source archive tar headers/padding count toward expansion
limit. Bad gzip/tar, special/sparse members, duplicate/escaping names, missing or
extra files and wrong hashes reject. Test resource bounds and retained variants;
run focused/full checks. Preserve native inputs, historical evidence and pins.

Producer report sources have 3,430 entries: 3,420 match archive members; ten
.DS_Store references (kernel/.DS_Store and kernel/arch/.DS_Store in five normalized
bundles) are absent. This slice proves complete summary input correspondence only,
not full producer-report source coverage. Preserve these omissions as explicit
limits. No extraction, commands, dependencies or shared ABI are introduced.
Missing artifacts, filesystem deadline/race limits and independent review remain
BG-056 work. Archive authenticity and build provenance are not proved by hashes.

Validation: 76 focused tests and ten gates pass in run-pgv6t__v.
Four manual lint/render commands pass; all attempts passed. Audit output, catalog,
24 native inputs and release pins remain unchanged. Evidence:
../evidence/source-archive-correspondence-2026-09-07/.
