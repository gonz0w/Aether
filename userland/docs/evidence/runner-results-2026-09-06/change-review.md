# UL-059 pure result decoding plan

Before implementation: decode exact 32-byte admission and collection replies
from the selected command-I/O producer. Validate bounded generation/receipt,
result word, error payload zeros, success reserved bytes and terminal kinds
1 exit / 2 fault / 3 stop. Preserve full uint32 detail and signed errno without
implementation-defined unsigned-to-signed casts. Unknown kind, positive result,
out-of-range errno, wrong receipt and malformed length reject atomically.

Pure functions own no transport, receipt lifecycle or authority. Separate pending
collection EAGAIN from error, admission and collected result. Decoder success does
not prove authenticity, perform collection or authorize replay. Invalid replies
leave output unchanged; callers must branch on the decoder outcome. Missing or
malformed delivery means unknown, not denied admission or a dead child. Numeric
terminal policy requires validated collected facts and explicit cleanup complete:
normal0..255 preserved; fault/stop/wide detail/unknown cleanup return1 without
erasing raw fields. Zero-admission precondition mapping remains separate.

Tests: both generations; all errno1..4095; collection-only pending; all normal
statuses0..255; fault/stop and wide detail boundaries; all short lengths and an
oversize; every padding byte; receipt/kind/context corruption; null pointers;
unchanged outputs and owned copies. Four compiled semantic mutants must reject
at exact oracles: ignored receipt, error padding, terminal kind and cleanup.
Use C17 strict pilot diagnostics, pinned Clang/SDK and explicit UBSan (ASan still
incomplete), native x86-64 object/import inspection, parser and21 host command
regressions. No native link/boot: the new helper remains unwired this slice.

Python3.10+ standard library, owned clean-environment commands with30s deadlines
and16MiB per-output-file bounds. Record source/plan/tool/runtime hashes before
consumption, exact flags/logs/cleanup and every attempt. Run format/grammar and
quality gate. Foundations O/I/E, approved CE/CC/CP and TD/TC/TE apply; original
code BSD-2-Clause. Current-task technical review; independent technical/reader
and affected-owner acceptance remain pending. Next: explicit native mapped
results while preserving finite parent29, default pins and raw result evidence.
