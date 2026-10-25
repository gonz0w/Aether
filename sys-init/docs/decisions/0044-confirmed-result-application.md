# 0044 — Serialized application of qualified returns

Accepted for BG-058 on 2026-09-06. Add one trusted ResultApplier per JournalRuntime
lifetime, configured with an opaque original owner and producer hash. Construction
claims the runtime once; another applier cannot reset its binding history. This
is an in-process model coordinator, not thread synchronization, native authority,
a transport or owner replacement. Existing unguarded APIs remain trusted fixtures.

bind constructs and retains at most twenty BoundCall contexts for exact issued
tokens. Reject duplicate binding, foreign owner, unsupported call/target and closed
owner. The expected native target remains trusted adapter bookkeeping input; this
change does not implement actual slot ownership. apply requires the exact retained
context object, not an equivalent or newly fabricated BoundCall. The caller must
supply the raw exact reply, not an earlier verdict. Qualification runs again under
an application guard immediately before journal acknowledgment.

The guard also sets runtime.running, blocking ordinary lifecycle/queued intake
operations and reentrant bind/apply during application. This is serialized trusted
execution only; callers must not mutate the journal through bypass APIs or other
threads. A validation failure before acknowledgment changes no journal/lifecycle
state and retains the context. Once acknowledgment begins, any exception or result
other than recorded closes the runtime through driver_lost. This preserves unknown
issued obligations and known terminal acknowledgments without rollback or retry.
Retain the bounded context set and last attempt/verdict for diagnosis.

On success, remove the context, retain one last applied record, and return the
already-qualified immutable verdict. Repeated apply rejects rather than executing
or acknowledging twice. If the caller loses that result, the journal's existing
bounded observation history remains the accounting record; there is no new wire
replay protocol. Unknown or externally completed obligations cannot be applied.
The applier never changes Model state, starts a queued cut or synthesizes terminal,
launch or cleanup observations. A confirmed rejection likewise does not imply
cleanup of independently allocated resources.

Test end-to-end qualification/acknowledgment followed by separately supplied
observations, repeated/forged/foreign contexts, stale verdicts after unknown,
invalid replies, reentrant application, failure before/after acknowledgment, and
single coordinator ownership. Add a retained-binding omission control. Full
model/development checks and source-bound retained evidence are required.

BG-058 remains active for exact terminal-kind/cleanup observation mapping,
authoritative live native target bookkeeping and fresh consuming witnesses.
BG-057 control composition and BG-033 unknown recovery remain open. No native
source, shared pin, existing wire/token schema or CLI behavior changes. This uses
only standard-library Python under Foundations O-01/04, I-03–06 and E-04–08.

Validation: 181 model tests, seventeen distinct mutation controls, 48 host tests,
37 harness tests and all offline adoption/quality/evidence gates pass.
[Retained evidence](../evidence/result-applier-2026-09-06/README.md) binds the new
coordinator, tests and runner. No existing lifecycle/journal/qualifier or native
source changed, and no native execution was rerun.
