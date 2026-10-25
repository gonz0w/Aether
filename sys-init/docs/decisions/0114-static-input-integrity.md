# 0114 — Static input file and metadata integrity

BG-056 host tooling slice. Read selected sources and JSON records only from
ordinary files beneath the supplied root, rejecting symlink components within
that root. Open nonblocking to avoid FIFO-open hangs after replacement; use
O_NOFOLLOW where available, then compare fstat identity/type with pre-open lstat.
Bound reads and compare file identity/size/mtime after reading. This is portable
POSIX host tooling with optional O_NOFOLLOW reinforcement, not an atomic snapshot
or protection against a hostile concurrent directory replacer.

Capture exact settings and boundary-record bytes before parsing or tools. Parse
those captured bytes; reread safely and require identical bytes before success,
including metadata unused by the semantic boundary comparison. Retain existing
result fields, tools, arguments and pins. Update prior tests where missing-field
fixtures relied on bypassing boundary reads. Add real FIFO/symlink/oversize cases
and controlled record mutation tests; run all gates. Native bytes/siblings and
published pins remain unchanged. Full tool dependency closure and other record
families remain open. Evidence: docs/evidence/static-input-integrity-2026-09-06/README.md.

Validation: all 27 focused static tests and all ten gates pass in
out/checks/run-rzjuf8cz. FIFO, symlink, controlled replacement/growth and valid
metadata mutation controls pass. Maintained record and native bytes remain
unchanged. Manual lint is clean; limitations are retained in the field reference.
