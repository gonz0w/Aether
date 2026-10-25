# UL-067 shared uncertainty/finalization plan

Compose unchanged host vector/finalizer candidates in a private session wrapper.
Write and finalization share one poison state. Pre-existing uncertainty abandons
all local roles without any close/diagnostic callbacks; prior nonzero status is
preserved. Unknown close or diagnostic results poison later writes. Finalization
started means no new public write, including callback re-entry. Finalization during
an active write poisons that in-flight outcome and abandons roles, never pretending
remote cleanup. Completed finalization is repeatable without effects.

No native wiring or libc patch. Synchronous callbacks/private zeroed state, explicit
borrowed lifetimes. Test Cartesian write/close/diagnostic outcomes/status plus write
and finish re-entry, exact call order and no later callbacks. Reuse unchanged
component evidence only after hash verification. Strict C17/UBSan/format, semantic
mutants, CLI/grammar and quality gates; private outputs and owned60s command bounds.
O/I/E and CE/CC/TD/TE apply. All native CAT cases remain NOT RUN; independent review
pending. Original source BSD-2-Clause. Retain every attempt and exact hashes/logs.
