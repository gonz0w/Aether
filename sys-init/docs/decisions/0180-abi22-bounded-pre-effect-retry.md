# ABI22 bounded pre-effect command retry

2026-10-03; BG-067; local experimental supervision policy.

Requirement: one bounded automatic replacement for a failed command in the useful
ABI22 table path, with exact cleanup before fresh admission, finite exhaustion and
no replay of uncertain effects. Backend/runner failures and unknown cleanup still
stop admission; no general recovery coordinator is introduced.

Select an explicit supervised composition, preserving the default and table-only
images. Command retry budget is one; backend and runner automatic retries remain
zero. Only a terminal command failure before any dispatched command backend read
or write is eligible. Completed reads also disqualify replay. Unknown transport,
reply, reference or cleanup outcomes cannot reach the retry branch. Retire the
command's logical aliases only after its observed terminal, finish the runner's
result/EOF protocol, close all logical backend file references and paired owners,
observe provider EOF/terminal/reclaim and verify empty owned resources. Only then
spend one retry and admit the fresh entire cohort under a new epoch. This scope
assumes the frozen bytecount command has no effect outside its mediated backend;
it is not a policy for arbitrary commands/devices or opaque side effects.

One request may use at most two command attempts. Normal completion returns to
the request boundary and resets the budget for a new request. Exhaustion or
failure after I/O produces a distinct failed-state diagnostic; requests cannot
admit further workers. Halt is still allowed after known cleanup. Failed is not
successful completion. Epoch exhaustion remains separately fail-closed.

Simpler alternatives are never retrying or retrying every observed failure. The
first does not meet bounded replacement; the second cannot establish safe replay.
Choose a small counter inside the existing sequential owner and a conservative
pre-effect flag, borrowing the current paired cleanup and finite epoch machinery.
No parser, dependency graph, backoff service, durable journal or general recovery
state machine is needed. Existing retained profiles and test drivers remain; this
adds no shelved lifecycle machinery.

Acceptance: native normal success; first actual command exit64 before I/O then
fresh successful replacement; two such failures exhaust; actual stopped command
after a read blocks replacement; unknown cleanup blocks replacement. Exact normal
output/status, ordered cleanup before new launches, no completion after failure,
finite budget, failed-state halt and image/stack bounds; preserved baseline/table
images; relevant host controls and all repository gates. Retain failed attempts.
Shared pins, ABIs, userland payloads and sibling repositories stay unchanged.
Foundations O/I/E and scoped Distribution/Experience obligations apply; this is
local technical review, not full SI-07 or independent release acceptance.


Qualification exposed two compatibility facts: the actual payload closes some
aliases on early exit, and the kernel stop path does not emit a UART terminal
line. Accept only the valid command-alias subset at an observed terminal, then
retire remaining references; the stop control asserts the observed143/kind3
result explicitly. Early known terminals receive no bootstrap publication.
Partial/uncertain publication still rejects without retry. Initial failed cases
and diagnostic1403 are retained. The old compiler outputs also changed under
source reshaping; baseline/table select their exact pinned module snapshots while
supervision selects current modules. No historical packet or released pin changed.
