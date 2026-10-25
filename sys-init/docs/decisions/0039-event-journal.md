# 0039 — Isolated event occurrence journal

Accepted for BG-057 on 2026-09-06 after decision 0038's source review. Implement
an isolated trusted Python journal before composing it with Model.batch. This is
not a durable journal, native driver or lifecycle cause inference implementation.
Foundations I-01/04–06 and E-04–08 apply through STANDARDS.md.

Reserve twenty logical credits for one whole cut, only when no earlier unresolved
obligations or reservation remain. A monotonic uint64 cut serial is consumed even
on cancellation or empty capture. An opaque reservation ticket is local to its
journal. cancel is legal only before begin; begin marks possible model mutation.
After begin, loss retains all credits because the number of effects may be unknown.
These logical reservations do not preallocate memory or make Python crash-atomic.

capture accepts zero to twenty immutable records: (kind, service, generation,
cause-kind, cause-id). Kinds include launch/stop/force/reclaim. Cause-kind is
activation or stop; cause-id is a uint64 originating operation identity supplied
by a trusted owner, not inferred from the current active operation. The tuple
retains cause independently of operation history. The later lifecycle adapter must
maintain and validate that provenance; these values confer no authority.

Tokens have ten fields: event-effect-v1, epoch, revision, cut serial, zero-based
occurrence index, service, generation, kind, cause-kind, cause-id. Equal force
records produce distinct occurrence tokens. This preserves requests without
approving native duplicate invocation. Per-service generation high-water rejects
older generations; no seen-kind deduplication is applied to separate occurrences.
Capture validates the entire batch before publishing tokens. Any capture error
after begin closes the journal and retains the reservation; valid bounded raw
records are retained before token publication for failure diagnosis. Invalid
input need not be retained. No cancel/retry can turn uncertain capture into success.

Tokens transition reserved -> issued exactly once. Only rejected-before-effects
can finish an unissued token. Issued work accepts executed, rejected-before-effects
or unknown. Terminal results move to a 64-record history; unknown remains live.
Repeated identical acknowledgments replay, conflicts reject. Evicted token
identities return retired without execution or payload identity assurance. Future
cut tokens reject. driver_lost closes mutations: reserved tokens become rejected,
issued tokens become unknown; a begun uncaptured cut retains its twenty credits.
Observation of retained tokens remains available. No acknowledgment mutates Model.

The conservative gate deliberately blocks new cuts behind unknown obligations.
It therefore does not claim production observation progress or recovery. BG-057
remains active for lifecycle cause retention, validation before mutation, retained
input on denial, capture-failure ownership and unknown/terminal observation policy.
BG-032/BG-033 retain exact producer results and consuming native witnesses.
Existing EffectLedger and AccountedDelivery interfaces/bounds remain unchanged.

Test capacity, cancellation versus begun cuts, twenty/twelve-effect captures,
duplicate force occurrences, caller-supplied cause independent of operation history,
stale/wrong tokens, capture failure, generation retirement, acknowledgments,
driver loss and serial/history exhaustion. Add a reservation gate omission control;
run model/full checks and retain evidence. No dependencies beyond the standard
library, unsafe code, wire/CLI changes, shared pin changes or native invocation.

Validation passes: 146 model tests, thirteen distinct mutation controls, 48 host
tests, 37 harness tests and every offline adoption/quality/evidence gate.
[Retained evidence](../evidence/event-journal-2026-09-06/README.md) includes all
three model attempts; the first two accidentally ran the same new control twice,
corrected before the final run. No native code or lifecycle behavior changed.
