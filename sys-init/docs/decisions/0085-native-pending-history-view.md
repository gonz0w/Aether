# 0085 — Bound terminal-history views

Accepted bounded implementation, 2026-09-06; BG-058 PH-01/02, decision 0084.

Implement a private immutable view minted from the bound Sampling session only
when its sample is sealed Terminal and its retained fact matches. The view borrows
the session's owner, token and raw Sample and carries attempt index and actual
Worker. The borrow prevents driver mutation and sample reset while the view lives.
An exact identity query replays that same retained view as Duplicate; wrong owner,
index, any token field or worker returns Denied without mutation. The immutable
owner reference fixes profile/producer identity. No arbitrary candidate offer,
conflict storage, history reset, journal acknowledgment or resource retirement is
introduced. Storage beyond the session lifetime remains future PH-03–07 work.

Use a private nested pure module shared with host tests. Its constructor is visible
only to the parent binding module; synthetic host fixtures establish comparison
logic, not native origin. Native probes use real O1/S/O2 from the existing bound
fixture admission. Preserve the existing 143 native oracles and 4096-byte bound.
No new dependency, unsafe code, allocation, kernel ABI or shared pin change.

Before execution, expected new cases:

- history-replay: repeated Duplicate and identical three raw receipts/fact, with
  unchanged reads, pending, generation, issuance and worker/reader; result 100/3.
- history-identity: wrong owner/index, every token field, and actual other worker
  deny, including equal-generation cross-service token; result 100/3.
- history-skip-token: omission control must fail identity assertion 1050/0.

Host tests cover terminal-only construction, all identity fields and retained
content. The omission control must fail the named identity assertion, not fail
compilation. Full development checks and a fresh consuming native run are required.
Review footprint before full execution; retain unsuccessful revisions. This is a
trusted in-process boundary, not authentication against code bypassing Driver.


Preflight revision: split the identity checks into history-identity (each token
field and equal-generation cross-service token) and history-target (owner/index
and actual other worker); each retains the duplicate and resource assertions and
finishes 100/3. A separate history-unsealed checks empty-session view denial before
reads, retains pending/open state and finishes 100/3 after known fixture cleanup.
The three initial images exceeded the strict link bound; an inline view factory
made replay fit exactly 4096 bytes but identity still exceeded it. Those artifacts
are retained. These are probe/layout changes, not weaker acceptance rules.


Final preflight plan: seven positive probes (history-replay, history-identity,
history-context, history-index, history-service, history-target, history-unsealed)
and one history-skip-token control, for 151 native cases. Context checks wrong
owner; index checks both other and out-of-range indices; service checks the other
service's equal-generation token. Every terminal probe retains full state before
and after queries and exact raw prefix afterward. Shared pure predicates reduce
code duplication; index denial iterates a two-element bounded array. Positive
oracles remain 100/3 and the control 1050/0. Eleven source/build revisions are
retained; no linker limit or compiler profile was widened.


Technical review: the nested view constructor is visible only to its parent
binding module. The public-to-parent surface has no mutator, arbitrary candidate
argument or native effect access. Its native caller binds values from the same
live session after matching the sealed sample to the retained fact. The returned
borrow prevents changing Driver or resetting Sample while a view exists. Context
has immutable strings and is not zero-sized; owner pointer comparison is only a
local identity check. Host fixtures deliberately use synthetic owner/token/worker
values and cannot establish native capture. No unsafe code, FFI or dependency was
added. Failure to mint returns None; closed/partial/nonterminal sessions grant no
view. This slice does not implement an independent-candidate store or internal
conflict disposition. No independent reviewer sign-off is claimed.

Host validation: three named view tests pass (duplicate retention, every identity
field, terminal-only minting), and omitting token equality fails the exact identity
assertion with Rust test exit 101. All nine existing sample tests and both earlier
omission controls also pass. Source snapshots, compiler identity, commands and
outputs are retained under host-checks. Full development and native results follow.


## Native acceptance

Decision 0085 passes 151 native cases, preserving all 143 previous oracles.
Seven positives qualify private bound terminal views, duplicate replay, every token
field, owner/index, equal-generation cross-service token, actual other worker and
empty-session denial. Every terminal probe checks retained state before/after
queries and exact raw history afterward. Positives finish 100/reclaimed=3 after
known fixture cleanup; the token-omission control fails exactly at 1050/0.

All 184 frozen inputs remain unchanged; 87 of 143 prior
images match byte-for-byte. Every changed image has fresh target execution.
Maximum image is 4096 bytes under the unchanged 4 KiB limit. Eleven
size/layout preflights are retained. Shared pure predicates and split probes keep
all assertions; no compiler profile, linker bound or worker change was needed.

This implements PH-01/02 origin and replay within a borrowed sampling session.
The view cannot mutate Driver or Sample and exposes no arbitrary candidate API.
It does not implement independent-candidate equality/conflict, fixed diagnostic
storage, retention across session destruction or journal acknowledgment/retirement.
Next BG-058 PH-03/04 qualifies a separately labelled synthetic conflicting sample
while retaining both histories and closing admission; PH-05/06 capacity and sealing
and BG-057 PH-07 whole-cut retirement remain open. Full launch composition,
additional NT-04 O1 injections and BG-033 unknown-owner recovery remain open.


The first full development run (`out/checks/run-v47pv0mh`) rejected the
sample-receipts gate after all five wrapper cases passed: its completeness guard
still expected three cases. Updated that guard to five without weakening missing,
skipped or failed-suite rejection. The failed run and its original runner are
retained in `validation-attempt-1/`; native sources and their witness are unchanged.

Validation: all nine development gates pass in `out/checks/run-6ci2bl01`, with
no skipped gates and unchanged checked sources. The offline audit now covers
2209 historical native outcomes across 45 bundles, separate from the fresh
151-case native witness. All 38 harness tests, nine existing sample tests and
three pending-view host tests pass; three omission controls fail their exact
assertions. Eleven current consumer inputs and both worker/builder inputs match
the retained execution/build snapshots. Full logs and adoption records are retained.
