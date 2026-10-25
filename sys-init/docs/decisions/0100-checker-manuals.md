# 0100 — Offline checker manuals

Accepted local documentation work, 2026-09-06; BG-056 follow-up to decision 0099.
Add canonical mdoc manuals for check-static.py, check-quality-process.py and
check-native-evidence.py. Record actual options, prerequisites, environment,
files, temporary/retained output, streams, error distinctions and scope. Preserve
all implementation bytes, release pins and machine contracts. Correct the older
static guide's superseded Clippy-selection wording without rewriting evidence.

Review each manual against the exact source; probe help/version/invalid usage
and the normal check. Existing required harness controls exercise operational
failures. Lint and render every new manual at 78/60 columns and HTML. Retain
initial lint warnings and resolve them. Explicit experimental OS metadata keeps
the decision-0099 scoped STYLE notice, not a zero-exit lint claim. Independent
technical/reader review and target installation remain publication work.

Evidence: docs/evidence/checker-manuals-2026-09-06/README.md. No native build or
execution is required for documentation-only changes. No sibling is modified.
