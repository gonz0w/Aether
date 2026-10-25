# OC-H3 declared closure evidence

2026-09-06. This is a local host-review format proposal, not origins/userland/shared
acceptance. See [the contract](../../ORIGINS-CLOSURE.md). No sibling code, network,
recipe, package state or trust authority was invoked or modified.

Attempt 01 passes 38 cases. Engineering review then added cached-subgraph height
accounting and three explicit graph/object budget cases. Attempt 02 passes 41 cases.
The initial run was not a failed suite; it lacked that additional coverage. Original
results and exact input identities remain retained. Each result identifies its
private run root through command paths; large budget blobs remain there, while
canonical selection, logs and small complete-case inputs are copied here.

The oracle is exact report bytes for positive cases and expected rejection status/
identifier with empty stdout for negatives. Input names/types/modes/hashes and private
sentinel state must remain unchanged. A recipe contains a command-looking marker
instruction; no execution occurs. Cyclic graphs use an inconsistent closing reference,
with cycle rejection preceding map comparison. These are synthetic records and raw
SDK/review placeholders, not complete real compiler closure or owner approvals.

Selected checks: python3 tests/origins-closure-cases.py (10 seconds per child),
sh tests/check.sh, scoped ShellCheck for changed shell gate and Experience integrity.
The normal gate retains its whole-suite process-group timeout. Exact full-suite
outcomes are added after completion. No native/TUF/physical-storage test is claimed.

Attempt 03 adds multiple-root and unselected-catalog controls: 43 cases pass.
Shared objects/SDK count once and unselected missing records are not traversed.
The report claims only the selected declared set.

Final resource review added a separate 64 MiB cumulative read budget. Repeated
references can otherwise cause excessive work while satisfying the 32 MiB unique
object limit. Attempt 04 passes 44 cases including repeated-read exhaustion. This
was a reviewed additional boundary, not a silently discarded test failure. The
full gate started before this change is an earlier-input witness; a new full run
is required for the final consumer. Large read-budget blobs remain in the private
run root identified by result.json.


Final full gate passes: sh tests/check.sh exits 0 with all sixteen shell fixtures,
13 byte-handoff, 96 source-record and 44 closure cases, required standards/lint and
manual/watchdog checks. Attempt 05 contains the final integrated closure results;
suite.log/result.txt retain the gate. The earlier full-suite pass remains separately
labelled before cumulative-read enforcement. Compiler manual example/native/TUF/
physical-storage checks are not selected and no such claims follow.
