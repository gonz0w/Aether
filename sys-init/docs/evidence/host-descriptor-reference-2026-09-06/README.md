# Host descriptor reference evidence

Decision 0106 documents all thirteen local descriptor fields and the separate
parse, prepare, activate and explicit start stages. It records model-level
restrictions, raw-byte pins, environment precedence, error propagation, mutable
caller objects, trusted regular-file requirements and unsupported reload,
concurrency and production-policy claims. The canonical reference is
docs/HOST-DESCRIPTORS.md; it is not an installed API/configuration manual.

Six new contract tests pass, with raw-byte/UTF-8/scalar boundaries, syntax-valid
but unpreparable inputs, no-launch construction and repeated activation,
whitespace staleness, graph bounds/fixed budgets, actual environment override
and the executable temporary oneshot example. The first test-development run
also discovered the imported legacy test class, duplicating its six cases; the
import was changed to a module reference. The retained final focused run has
exactly six new cases, and aggregate discovery retains the original suite once.

The example launches a real trusted Python child in a temporary workspace,
uses a five-second observation limit and finally cleanup, and returns the exact
expected output. It is explicitly executed by the host gate, not discovered by
running arbitrary Markdown blocks. Command, host/Python identity and results
are retained in review.json and adjacent streams.

All ten aggregate gates pass in out/checks/run-qdahttz9, retained in validation/.
Reviewed descriptors/runtime/model bytes are unchanged from the decision-0101
source snapshot. No runtime implementation, native source, shared pin, sibling
repository or historical evidence changed. Current source copies bind the
reference, example, tests and exact reviewed contracts.

Independent technical/reader review, installed configuration/API manuals and
target lookup remain pending. Other API/record families and legacy subprocess
bounds remain open. Named tests are scoped evidence, not exhaustive parser,
filesystem, concurrency or all-platform conformance.
