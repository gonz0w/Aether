# Launched journal adapter — 2026-09-07

Decision 0160 connects Launched cuts to the actual JournalRuntime, Model.batch
and EventJournal. A prepared journal ticket is reserved before application; other
commands deny until consumption/cancellation. LaunchedAdapter revalidates exact
executed launch-token binding and starting state, checks the applied transition,
and verifies all generated effect obligations before returning the cut receipt.
Provider launch produces the real dependent launch obligation with its original
cause. Empty-effect cuts still retain their actual journal serial. Exact replay
changes neither lifecycle state nor journal. Queued/derived runtimes explicitly
deny the new reservation API so intake cannot masquerade as application.

All 263 model tests pass, including nine new adapter tests with two source omission
controls for missing transition and capture. All ten local gates pass in
`run-i4iynltv` with unchanged checked inputs. All twelve native consumer sources,
three release locks and catalog bytes remain unchanged. This is actual integration
of policy-model/journal code; native source origin and launch execution are still
injected model facts. No new QEMU or production-conformance claim is made.

Next BG-057: exact Terminal mapping and subsequent cleanup/Cleaned admission through
the actual lifecycle/journal adapter. Native source/worker provenance and consuming
integration remain BG-058/BG-057; BG-060 reuse and BG-033 recovery stay open. The
185-case native checkpoint and BG-056 producer source-closure limitation remain
unchanged. No native effects, reset or shared ABI are added.

source/ and sources.json retain final adapter/runtime/model/test/runner inputs.
validation/ is the final local-check snapshot. The previous passing run and its
changed runtime/test sources are retained separately; review then added explicit
queued-runtime profile denial before final acceptance. Negative controls execute
modified adapter source against the real model/journal call path and require named
assertion failures. The adapter boundary is tested independently of the outer
coordinator's additional transition checks. No native call or arbitrary service
code executes in these fixtures.
