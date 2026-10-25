# 0133 — Native consumer report fields

BG-056 host slice, 2026-09-07. Validate consumer results.json fields/types before
semantic auditing or linked receipt reads. Cover I/O and init report/case variants,
command argv/exit fields, optional paired worker pins and supported build profiles.
Require exact known fields and lowercase SHA-256 strings, proper booleans/integers,
bounded text, 1–1,000 cases, 1–3,004 commands and 1–1,000 argv elements per command.
Keep existing case membership, command ordering and artifact/serial oracles.

Maintained evidence has five I/O reports and 45 init reports; max argv is 195
items/328 characters. Recorded image/ISO digests are structurally checked, not newly claimed to have artifact correspondence. Original report bytes
and pins stay fixed. Test malformed records before receipt traversal and current
variants; run focused/full checks. E-01–08 host scope; no native/sibling changes.
Producer summaries, producer reports and worker/build receipt schemas remain
separate BG-056 work. Independent review and filesystem race limits stay open.

Validation: 57 native-harness tests and all ten gates pass in run-k02c23ut.
All 50 retained report variants pass; malformed field/type/bound controls reject,
including before linked receipt parsing. Native audit stdout, catalog, 24 native
inputs and release pins remain fixed. Four final mandoc checks pass after source
line reflow; the initial lint style failure is retained. No native execution.
Evidence: ../evidence/native-consumer-report-fields-2026-09-07/.
