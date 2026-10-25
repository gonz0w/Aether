# Native acquisition and cleanup — 2026-09-06

[Decision 0051](../../decisions/0051-native-acquisition-cleanup.md) now has a
[fresh 17-case target witness](witness/README.md). The new positive sequence and
two cleanup omission controls pass their exact oracles. Fourteen compatibility
binaries are unchanged; all 176 frozen build inputs remain unchanged.

The catalog-pinned witness contains source/artifacts/logs and exact reproduction
commands. Full development validation is retained separately in validation/.
This is selected native sequence coverage, not the complete Python driver port.

Full validation: all eight gates pass (228 model tests, 23 mutation controls,
48 host tests, 37 harness tests), with sources_unchanged true. The offline native
catalog now audits 232 outcomes across 18 bundles and 4,880 listed files. Current
native consumer sources were compared with the executed snapshot and match.
Final decision/planning validation notes were appended after the checks; no native
code changed afterward. No native or full-check failures occurred in this attempt.
