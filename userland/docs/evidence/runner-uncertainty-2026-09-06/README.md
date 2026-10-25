# UL-059 mapped-path uncertainty host evidence

Actual runner.c and mapped-runner.h execute with real parser/result code, while
bootstrap/exchange/channel/read/close are scripted host seams. Admission and
collection frames are compared against independently assembled complete expected
bytes. Every scenario is a fresh owned process. This test does not substitute a
new implementation of mapped_run or its decoders.

25 UBSan scenarios pass: normal0/64/255, fault, stop, wide detail, pending once,
success at poll100000, exhaustion after100000 pending replies, pending then lost,
lost/foreign/padded/positive/error admission, lost/foreign/padded/invalid-kind/error
collection, malformed pending, input/output close failure, read failure and
unexpected non-EOF. Counters enforce exactly one launch, proper close/collection/
read/policy ordering and no later effect after unknown, malformed or rejected
exchange in this bounded abort profile. Decoded raw receipt/kind/detail and cleanup
facts reach the real policy through an independent witness callback.

Four private mapped-header mutants compile and reject at their exact oracle:
retry lost collection -> no-after-unknown-or-malformed; poll100001 -> collection-budget;
skip input close -> collection-after-input-close; overwrite detail -> raw-terminal-facts.
The original header and other production sources are unchanged. There were no
failed attempts or production fixes in this slice. The eight production source
identities match the prior native mapped witness. Result28159/four mutations,
parser1293/two mutations and21 command host cases also pass.

Strict C17 diagnostics, Clang-format21.1.8 and Python3.10 grammar (actual3.14.7)
pass; the quality/three-standards gate passes. Pinned compiler, source/plan/runtime
identities and snapshots precede consumption. Host commands use explicit clean
environments,30-second owned deadlines and16MiB output-file bounds; quality60s.
UBSan is explicitly selected; ASan remains incomplete from previous prerequisites.
No new runtime package, source profile or standards pin changed. Original files
are BSD-2-Clause, with Python standard library only.

Current-task technical review by Codex checked scenario independence, exact frames,
callback guards, bounded pending, raw facts and cleanup ordering. Independent
technical/reader and owner reviews remain pending. This is a complete-exchange
host seam: partial native transfer, real FD closure, supervisor abort/resource
retention and native recovery have not been newly exercised. No native run was
necessary for test-only changes. Existing adapter/native evidence remains separate,
not a substitute for the next native mapped-path lost/malformed-reply witnesses.
Aborting1 does not resolve unknown ownership or implement local public diagnostics.

Run summaries/raw logs, each mutant header/client and exact consumed source
snapshots are retained in host directories; final source and tracking documents
are separate. Foundations O/I/E and approved CE/CC/CP, TD/TC/TE apply. Affecting
changes invalidate reuse. Next UL-059 is native mapped uncertainty controls under
the existing deliberate-rejection mode. RL local outcomes still need owner review
and an explicit extension; no general project wait, release or recovery acceptance.
