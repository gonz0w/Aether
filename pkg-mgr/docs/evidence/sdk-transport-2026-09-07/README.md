# SDK transport checkpoint

2026-09-07. [Contract](../../SDK-TRANSPORT.md) adds explicit private SDK branches
without changing host-v2 admission or public CLI commands. Oracle: exact synthetic
record/payload/mode equality, independently pinned full profiles, no publication
on validation failure, unchanged unrelated data, and exact retained-stage recovery.
Selected checks: profile/transport controls, changed-shell lint, standards and full
sh tests/check.sh. No real SDK, compiler, native execution or sibling write.

attempt-1.json records the initial 23 passing synthetic controls. The additional
plausible-output/failed-hash case in attempt-2.json exposed acceptance because a
command substitution inside test discarded the hash command status. The fix
separates checked hash assignment from digest comparison. Both original attempts
and their source/test hashes are retained. Subsequent focused/full evidence binds
the final dirty executable inputs; unrelated Origins work is excluded from the
commit, not falsely excluded from the tested source tree.

lint-before.json retains SC2209 on an unquoted literal command assignment. Quoting
the literal resolves it; changed-shell lint then passes. attempt-3.json records
24 passing controls after the hash-status correction. Final full-suite inputs
include that quote-only correction and are recorded separately in inputs.json.

Final full suite: exit 0 in 243.812 seconds; watchdog result=pass, all sixteen
active fixtures complete, 65 profile and 24 transport controls pass. Runtime input
path/hash/size/mode inventory stayed unchanged during the run. Final standards,
development, changed-shell lint and whitespace checks pass. Full suite includes
ShellCheck across all 39 active shell files. No native SDK consumer was run.
