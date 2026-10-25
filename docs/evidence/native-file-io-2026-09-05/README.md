# Native bounded file I/O — 2026-09-05

Producer-only evidence for [the file-I/O contract](../../NATIVE-FILE-IO.md).
Five new target cases pass: two-round positive plus frozen-offset, zero-consumes,
wide-rights and skipped-storage controls. The positive finishes with six reclaims;
negative cases require their exact ordered context and designated panic.

Thirty-eight affected regression cases pass: inherited-launch 9, shared-files 6,
connections 6, program 6, coexist 6 and writable-files 5. `zig build test` passes
kernel/host checks, 56 Python tests and all three offline standards checks.
Python compilation, Rust formatting and CLI help/mutual-mode rejection also pass.
Memory/SMP/default boot suites were not rerun; kernel sources are unchanged.

`summary.json` records suite paths, report hashes, tool pins, host and all 172
archived source hashes. `producer-sources.tar.gz` retains those source bytes.
Each suite directory includes its results, ELF helpers, raw broker variants,
envelopes, build logs and serial evidence. ISO hashes are recorded in the reports;
the large ISO files remain in the local suite output paths rather than this bundle.
The accepted file-I/O broker is 5512 bytes within the unchanged 8192-byte bound.

Reproduce with the command in the contract and the strict musl SDK/tool-lock pins
recorded in the suite results. No sibling code, immutable consumer pin or release
was modified. These results do not establish independent userland adoption,
public libc read/write/close, CR-01 command execution, shell support, persistent
storage or shared standards approval.
