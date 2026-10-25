# 0104 — Builder manuals

Accepted documentation work, 2026-09-06; BG-056 follow-up to decision 0103.
Add canonical manuals for all four standalone builders. Describe exact operands,
variants, prerequisites, output reuse, receipt differences, environment, per-tool
bounds and failure paths. Do not invent common worker schemas, imply compiler
success equals final acceptance, or treat envelope assembly as runtime proof.

Read current scripts and retained 0097/0098 build evidence. Probe help/version
and missing arguments on each builder. Perform one fresh default build per
builder from the reviewed offline inputs; require retained lifecycle/supervisor
and I/O worker byte equality and the service builder's structural acceptance.
This is build-only evidence. Native runtime/source and all release pins stay
unchanged; no sibling or historical evidence is edited.

Lint/render all four manuals at 78/60 columns and HTML, then run required checks.
Retain the decision-0099 exact experimental-OS STYLE notice, not a zero-exit lint
claim. Independent/HTML visual review and target lookup remain pending. Fourteen
of eighteen commands now have manuals; native runners and API detail are next.
Evidence: docs/evidence/builder-manuals-2026-09-06/README.md.
