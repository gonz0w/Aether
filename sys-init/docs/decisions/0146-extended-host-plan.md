# 0146 — Bounded extended host qualification plan

BG-054 planning slice, 2026-09-07, coordinated with BG-056. Adopt the local plan
in EXTENDED-HOST-TESTS.md and the versioned corpus in extended-host-plan.json.
Foundations E-01–08 and reviewed Testing TD/TC/TE practices apply in host scope;
no draft standard is published or release pin changed. Existing native witnesses
remain independent. This checkpoint plans work, not executed extended coverage.

Choose repeated deterministic order variation of the existing 54 trusted-host
cases before adding new event generators. Eight fixed seeds give 432 planned
case executions in eight fresh workers. Hash-based ordering avoids Python random
implementation drift; keep classes contiguous for unittest fixture semantics.
Pin exact IDs and existing corpus/runtime source bytes. Reject discovery drift,
empty/skipped/incomplete suites or source drift. Bounds: 60 seconds/4 MiB per
worker, 600-second whole run, one-second cooperative cleanup then forced owned
group cleanup, at most eight workers sequentially. No host services or native VM.

Retain attempts and exact order/count/outcome/cleanup/source evidence in private
run directories. No automatic retry or scheduling. Maintainer owns triage;
independent/platform/release qualification needs actual evidence. The next slice
implements the runner and controls, then executes this plan locally. Validate the
corpus identities/hashes/order uniqueness and run all repository gates now; do not
label the planned 432 executions as completed or close G-EXTENDED.

Validation: 54 unique IDs, eight distinct complete orders and all 16 corpus input
hashes verify. All ten gates pass in run-tz9n5yw7. Final dependency review added
the executed descriptor example to the plan manifest after aggregate checks;
its source bytes were already covered/executed by that run, and the completed
manifest was revalidated. No extended executions are claimed. Evidence:
../evidence/extended-host-plan-2026-09-07/.
