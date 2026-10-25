# 0106 — Host descriptor reference and contract evidence

Accepted documentation/test work, 2026-09-06; BG-056 configuration/API follow-up.
Document all thirteen descriptor fields, narrower model constraints, absence of
field defaults, environment precedence, error stages and preparation/activation
ownership. Preserve the distinction between parsing bytes, preparing a complete
graph, activating an idle runtime and explicitly starting trusted children.

Source review covers descriptors.py, runtime.py and runtime_model/model.py with
the pinned Distribution service clauses. No production service-format decision,
native API or shared revision is introduced. Record filesystem race, mutable
caller object, interpreter provenance and concurrency limits without claiming
that content pins are authentication or sandboxing.

Add six contract tests for size/Unicode/scalars, staged validation, no-launch and
byte-stale selection, graph bounds/fixed budgets, actual environment precedence
and a runnable temporary oneshot example. Do not change runtime source. The
example is documentation support, not an additional supported operator command.
Require the aggregate gate so future host changes exercise these contracts.

Retain example/test results and exact reviewed source identities. No new native
execution is required for this host documentation/test slice. Independent review,
installed configuration/API manuals, complete boundary cases and target lookup
remain open. Next: remaining API/record families and legacy subprocess bounds.
Evidence: docs/evidence/host-descriptor-reference-2026-09-06/README.md.
