# Scoped technical review

Current-task review traced cat read/xwrite/loopfiles against the pinned source.
The original object bytes are pinned before relink; exact control ELF equality
binds their consumed closure to the earlier candidate. No retained upstream input
changed. Injection markers use the real stderr write and fail closed with status90
if the witness cannot be emitted. The prefix-error case requires exactly two bytes
and status1; filename close injection calls real close once before EIO. The host
controls independently check counts, one-time faults and errno under UBSan.

All seven QEMU Linux cases and named cleanup pass. Two negative oracle checks,
six host sanitizer controls, three CLI stream/status checks, C17 warning/format,
Python3.12 grammar on the actual recorded interpreter and quality gate pass.
Actual minimum-Python runtime testing remains unprovisioned. No native sanitizer
claim follows. Current-task review only; independent technical/reader review is
pending. Locale, buffered stdout, real signals and native lifetimes remain open.
The tested failures are findings to preserve, not fixes or conformance acceptance.
