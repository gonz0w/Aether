# 0101 — Model, host and measurement manuals

Accepted local documentation work, 2026-09-06; BG-056 follow-up to decision 0100.
Add canonical source manuals for the model checker, real-child host checker and
measurement runner. Preserve source and machine contracts, including the host
runner's ignored arguments and absence of help/version, the model's argparse
exit 2 and output-file overwrite behavior, and measurement's retained samples,
censored timeout control and limited memory/timing scope.

Read implementation and existing guides before writing. Validate selected CLI
outcomes, a complete exploratory measurement attempt, manual lint/rendering and
all required gates. Record exact sources and output. This is documentation/host
validation, not a new native or comparative-performance claim. Do not change
published pins, sibling repositories, runtime algorithms or historical evidence.

Seven of eighteen inventoried commands now have source manuals. Remaining
manuals/API detail and actual independent/target review remain BG-056 work.
Explicit experimental OS lint notices retain decision 0099's scoped disposition.
Evidence: docs/evidence/runtime-manuals-2026-09-06/README.md.
