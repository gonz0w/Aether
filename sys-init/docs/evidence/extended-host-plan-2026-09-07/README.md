# Extended-host plan — 2026-09-07

Decision 0146 / BG-054. Planning-only checkpoint. EHT-01 pins 54 existing test IDs,
16 corpus/runtime/example inputs and eight fixed seeds. plan-check.json records
54 unique cases, eight distinct complete class-contiguous orders and 432 planned
executions. Hashes match retained manifest source identities. No extended worker
or campaign was implemented, executed or scheduled by this checkpoint.

All ten `python3 scripts/check-all.py` gates pass in run-tz9n5yw7 with tested
sources unchanged. Exact commands/hashes are in validation/results.json. This
includes the ordinary 54-case host gate, not the planned 432 executions. Guide
links resolve and git diff --check passes. No new command/manual behavior exists,
so no renderer or new behavior tests were required. All checks passed.

The final dependency review added docs/examples/host-descriptor.py to the plan
manifest after aggregate checks. Its bytes were already in the aggregate source
map and its execution was already covered by the descriptor test. The completed
manifest and all 16 hashes were revalidated separately; no source implementation
changed. Planning/decision validation notes and evidence also followed checks.

Native audit stdout equals decision 0145; catalog, 24 native inputs and release
locks remain fixed. RC1 remains unpublished. Plan budgets are 60 seconds/4 MiB
per worker, 600 seconds/campaign, eight sequential workers and scoped cleanup.
Replay, failure retention, maintainer triage and seven-day same-input development
freshness are specified without claiming a hosted scheduler or release policy.

Next: implement the local supervisor/worker and negative controls, then execute
all eight seeds. Platform/independent review/native qualification remain separate.
No sibling, native source, release pin or historical evidence changes.
