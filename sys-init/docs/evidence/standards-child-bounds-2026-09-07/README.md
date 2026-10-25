# Standards child bounds — 2026-09-07

Decision 0123 / BG-056. Commands: python3 -m unittest discover -s tests -p
`test_harness_standard*.py` (17 tests) and `test_harness_offline_locks.py` (4).
Earlier passing run before capture controls is retained. All ten gates pass with
`python3 scripts/check-all.py` in run-wo5ygk7e. Exact commands and source hashes
are in validation/results.json. All focused attempts passed.

Three new real-process tests exercise each wrapper: raw stdout/stderr including
non-UTF8/NUL/CRLF and exit 0/7; timeout, overflow and a live child with both pipes
closed; and timed-out staged-tree cleanup. Small test deadlines/caps accelerate
controls. Direct children are reaped and pipes closed; accepted prefixes stay
within the combined cap. Existing tests mock the named run_reference boundary
instead of subprocess.run; actual isolated child and mutation controls remain.

The self-contained capture follows the existing POSIX selector/group pattern.
The child deadline covers draining/exit; on capture exceptions the owned group
is killed and direct child reaped before temporary-directory unwinding. Raw
prefixes replay on success/failure. Cross-stream ordering and live delivery are
not promised. No blocked-output-sink deadline, escaped-descendant containment,
SIGKILL/SIGTERM cleanup or filesystem-I/O deadline is established. The parent
interpreter/stdlib remain trusted. No external dependency or native change.

Real standard stdout matches decision 0122 exactly, all lock bytes match, and 24
native inputs match the boundary snapshot. RC1 remains unpublished. No new target
execution was needed. Initial manual lint found sentence-line formatting warnings;
corrected manuals pass all twelve commands, with both attempts retained. The
Experience output-timing note was added after the aggregate; its standalone check
passes. Independent reader/HTML visual/narrow-layout publication review remains
pending. Source copies and scoped diffs describe this slice in a larger dirty tree.
