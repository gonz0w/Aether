# Private standards execution — 2026-09-07

Decision 0122 / BG-056, macOS arm64 host scope. Eighteen focused tests pass:
`python3 -m unittest discover -s tests -p 'test_harness_standard*.py'` (14)
and the same command with `test_harness_offline_locks.py` (4). Earlier passing
runs before new private-execution controls are retained. All ten gates pass with
`python3 scripts/check-all.py` in run-celvo_l3; exact commands/source hashes are
in validation/results.json. No failed test or renderer attempts occurred.

Three new tests span all three wrappers: real staged execution under conflicting
PYTHONPATH/PYTHONOPTIMIZE settings with explicit isolated/no-site/no-bytecode/
assertion checks; original-source replacement immediately before dispatch;
cleanup after a mocked child failure; and staging-budget rejection (the budget
constant is lowered for the synthetic fixture). The real child records its staged
__file__; original replacement rejects in the post-check without executing the
replacement. Existing real-child self-mutation controls now exercise staged-file
postchecks. Updated lock tests require isolated flags and removed temporary paths.

Only hash-verified captured bytes are staged. Each file remains bounded at 1 MiB,
payload total at 64 MiB and traversal at 2,000 entries. Temporary roots are private
and removed on ordinary unwinding; this is not a same-user/OS sandbox, immutable
filesystem, pinned interpreter/stdlib closure or SIGKILL cleanup guarantee.
The child has no standalone deadline/output cap yet. Parent Python startup and
non-Python environment remain trusted. No external dependency was introduced.

Real Foundations, Experience and Distribution stdout matches decision 0121 exactly.
Their pins and 24 native inputs remain unchanged; no new native behavior or target
run is claimed. RC1 remains unpublished. Twelve manual lint/terminal/HTML commands
pass; final environment-description edits follow the aggregate and were linted.
Independent reader/HTML visual and narrow-layout publication review remain open.
Source copies/diffs cover this slice within the pre-existing dirty checkout.
