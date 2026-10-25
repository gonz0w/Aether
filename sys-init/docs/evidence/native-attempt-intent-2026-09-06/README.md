# Native attempt deadline and service intent — 2026-09-06

[Decision 0054](../../decisions/0054-native-attempt-intent.md) has a
[fresh 27-case native witness](witness/README.md). Deadline/revision precedence and
retained completions are tested separately from service-cancelled intent, which
blocks retry and preserves ownership through observed stop and cleanup.

Twenty-one earlier binaries match; two changed Attempt clients pass their original
oracles. All 177 inputs are unchanged. An initial missing-brace compile failure
(no native case ran) is retained in attempts/compile-01/; acceptance uses a fresh
run. Passing source/artifacts/logs are catalog-pinned under witness/; repository
validation is separately retained in validation/. Broader driver/error policy remains open.

All eight development gates pass: 228 model tests, 23 mutation controls, 48 host
and 37 harness tests. sources_unchanged is true. The catalog audits 302 outcomes
across 21 bundles and 5,970 files. Current consumer sources match the executed
snapshot. Final decision/planning validation notes were appended afterward; no
native code changed. The only failed attempt was the retained initial compile;
all target cases in the corrected run and the full repository check passed.
