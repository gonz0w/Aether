# UL-059 mapped-path uncertainty host plan

Compile actual runner.c/mapped-runner.h and real parser/result decoder against
scripted exchange/I/O/bootstrap/channel seams. The test controls one exchange
boundary, not kernel transport; earlier adapter and native witnesses remain
separate. Exercise lost/malformed admission and collection, explicit rejection,
pending then success/loss, exact100000 pending budget, abnormal/wide terminal,
input/output-close and EOF failures, and raw facts preserved across cleanup.
Assert exact serialized launch/collection, event order, no calls after ambiguous
or malformed replies, exact status/counters and policy facts. Unknown abort1 is
not public precondition mapping or recovery. Each scenario is a fresh process.

Four private mapped-header mutations: retry a lost collection, exceed budget by
one, skip input close, erase raw terminal detail. Each must compile and reject
at a named semantic oracle, not compiler failure. Keep production sources intact
unless tests expose a defect, then retain failure before fixing under review.

C17 strict pilot diagnostics; pinned Clang21.1.8, explicit UBSan (ASan remains
incomplete); Python3.10+ standard library and owned commands30s/16MiB, clean env,
source/tool/runtime/plan hashes and snapshots before consumption. Run parser,
result and21 command host regressions plus format/grammar/quality gate. No native
rerun for test-only changes; do not claim native unknown-state recovery. Domain
O/I/E, approved CE/CC/CP and TD/TC/TE apply, original source BSD-2-Clause. Record
actual current-task review; independent/owner review and RL local outcomes pending.
