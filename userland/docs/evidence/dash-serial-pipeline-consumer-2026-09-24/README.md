# UL-007 independent serial pipeline qualification

All **898 native cases pass**:105 capacity,358 connections,431 command-runner,
two console handoff and two console/connections cases.105 Python host tests plus
required Zig/Rust checks pass. All native suites passed on their first execution.
Twenty-nine independent lifecycle/control comparisons pass, with a retained
collector correction described below. [Acceptance](acceptance.json) binds receipts.

Actual dash receives a pipeline at its serial prompt, returns a prompt after its
three children terminate, then executes `echo after; exit 0`. Across three fresh
shell generations the local trace contains six exact command events/prompts,
three exact `pipe data` and `after` lines,15 successful terminals,12 image
admissions and15 reclaims. The copied builtin is not an image admission.
[Raw prompt offsets](serial-prompt-order.json) additionally confirm the returned
prompt follows all three child terminals in each generation. Owner output checks
require exact16-byte stdout and four prompt bytes per generation.

Changed output rejects2743/0; wrong UART selector rejects2795/0; disabled006
rejects before admission. Parent/copy direct UART denial, short-count progress,
blocking empty reads and owner close/post-close denial remain native predicates.
This is bounded AENMX006/ABI20 consumer evidence, not general UART/TTY behavior.
Local serial owner bytes match the producer's18616-byte linked audit, whose scoped
critical depth is4000/4088 with88 bytes margin. This is not an all-path stack proof.

## Inputs and verification

Consumed the sealed Aether pipeline-serial-2026-09-24 packet, SHA256SUMS digest
`8cef3c5723e687a6513d1348028dd3bbaf71312e5c83154f64d313c08c79016e`.
Entire producer and prior consumer seals were verified before restoring source.
All287 runtime hashes match across five suites. Console reports additionally
match all their nonmetadata support/test inputs. Legacy Finder metadata differs
from producer records; per-suite metadata dictionaries explicitly retain this
difference. There is no claim of identical full legacy source dictionaries.
All657 restored source/support/metadata files and4311 SDK files remain unchanged.
Original twelve-script inputs and prior evidence are preserved.

Reused the verified parent-consumer scaffold, including its pinned corrected
build-policy test; overlaid final287 runtime sources and11 review inputs. The
producer-packet copy omits large artifacts archives; the original producer packet
retains them and every exploratory failure. Copied source archives, reports,
review inputs, audits and their original seal are retained here. Tools, SDK,
Python, process helper, driver and plan identities are in preparation.json and
the referenced tool receipt. No sibling implementation or released pin changed.

| Local suite | Cases | Elapsed seconds |
| --- | ---: | ---: |
| Capacity |105|361.45|
| Connections |358|1131.06|
| Command-runner |431|1538.85|
| Console handoff |2|6.00|
| Console/connections |2|5.80|

Every suite remains below its1800-second review ceiling. Owned outer limits are
3600 seconds for native suites,300 for host checks,512 MiB per output stream;
guest watchdogs are unchanged. All owned process cleanup is complete. These are
test durations, not shell performance claims.

## Retained collector correction

The first extra console/connections collector demanded the producer's scheduling
order and an optional parent terminal before rejection. It failed after native
tests had passed. Source review established an exact positive terminal multiset
and a negative requiring peer74 with optional parent80, followed by941/reclaims0.
The corrected collector passes without a native rerun. Preserve original source,
failure log, producer traces and [correction](console-retention-correction.md).
A subsequent explanatory source-reference correction is also retained explicitly;
it did not change predicates. No native or host failure was erased.

## Retention and continuation

run.py prepares and runs host/capacity/connections/command-runner modes; console.py
runs the two console modes. Use a new packet/work root for replay; the drivers
refuse to overwrite existing mode timing records. retain.py, retain-console.py
and accept.py validate completed evidence. Native serial/QEMU logs and exchange
events are retained under cases/. compaction.json and compaction-selection.json
record verified archives and exact generated directories selected for cleanup.
Archive every file, read back hash/size/mode and recheck unchanged originals before
removing duplicates and this build's cache. Preserve SDK, source and prior archives.

Cleanup completed for all five suites and their compiler cache, reclaiming
7,075,536,896 allocated bytes (6.59 GiB). Final archive/index hashes, original
source/SDK and prior evidence pins verify. The local quality gate, six Python
syntax checks and git diff --check pass; see [final validation](final-validation.json).

This closes independent acceptance of the first serial pipeline profile. The
twelve-script matrix stays12/12 across private profiles. SESSION-01–06, shared SDK,
independent reviews, general signals/TTY, persistence, packages and sys-init/R1
assembly remain open. Aether advanced during this replay: its current STATE reports
a sealed shell-streams-2026-09-24 successor and a prospective session-lifetime
review. Those are next inputs, not accepted by this packet. Do not substitute this
pipeline-plus-builtin run for the entire composed.sh workload.
