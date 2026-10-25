# UL-067 process-mask host candidate

Implement process-local state only, no public/native umask replacement or file
creation policy. Caller supplies reviewed initial mask and nonzero generation;
one initialization attempt per zeroed context. Reject invalid initialization,
stale generations, uninitialized/retired state and null result without mutation
or fabricated success. Exchange returns the old mask and stores requested low nine
bits. Retire clears live mask, preserving history; a later process requires a new
context and owner-selected generation. These labels are not capabilities.

Test all512 initial masks x512 requested low masks x4 high-bit patterns, exact
save/restore, separate-process isolation, failed/repeated initialization, stale
access, retirement and fresh-context reset. Independent modulo/value oracles and
three compiled semantic mutants. Strict C17/UBSan/format, CLI/grammar and quality;
owned60s commands/private outputs and source/tool/plan retention. O/I/E, CE/CC/TD/TE
apply. No native ABI, shared standard, global state, concurrency or grant implied.
BSD-2-Clause original source; independent/owner review pending. CAT-04 NOT RUN.
