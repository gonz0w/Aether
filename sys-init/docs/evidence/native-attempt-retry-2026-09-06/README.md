# Native owned attempt retry — 2026-09-06

[Decision 0052](../../decisions/0052-native-attempt-retry.md) has a
[fresh 20-case native witness](witness/README.md). Adapter-returned launch EBUSY
is retained with its endpoints; cleanup precedes one replacement. Both omission
controls hit exact assertions. All 17 earlier binaries and 177 frozen inputs match.

The pinned witness retains sources, artifacts, command logs and reproduction steps.
Full repository validation is recorded separately in validation/. This is a bounded
native attempt policy, not complete service restart or unknown-effect recovery.

All eight development gates pass (228 model tests, 23 mutation controls, 48 host,
37 harness tests). sources_unchanged is true. The native catalog audits 252 outcomes
across 19 bundles and 5,220 files. Current native consumer sources match the executed
snapshot. Final decision/planning validation notes were appended after checks;
no native code changed afterward. No native/full-check failures occurred.
