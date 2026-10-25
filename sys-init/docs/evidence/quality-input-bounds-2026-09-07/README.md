# Quality input bounds — 2026-09-07

Decision 0118; BG-056 host-only verification on macOS arm64.

Commands: `python3 -m unittest discover -s tests -p 'test_harness_quality*.py'`
and `python3 scripts/check-all.py`. The first focused run found three missing-file
exception regressions. They were corrected by preserving the previous ValueError
contract; both logs are retained. The retry passes 21 tests; all ten aggregate
gates pass in out/checks/run-xuuqhhmn. Exact aggregate commands and source digests
are in validation/results.json. Manual commands and raw output are retained.

Four new tests cover record/reference FIFO, directory and link rejection before
open; parent links; large allowed existence-only references versus rejected large
payload reads; exact 1 MiB reads; replacement between stat/open; and growth during
read. Replacement/growth use controlled hooks around real file operations.
They are not exhaustive concurrent-filesystem or platform qualification.

Read memory is bounded per file, descriptors close in finally, and current path
components are checked at/below the supplied root. No filesystem I/O deadline,
atomic traversal, transitive reference identity, or independent approval follows.
The helpers follow the existing static reader pattern without adding dependencies.

Success quality stdout matches decision 0117. Snapshot manifest pin and 24 native
input hashes are unchanged; no native runtime behavior changed or target run was
needed. All three released-standard gates pass without pin changes. RC1 remains
unpublished. General referenced contents are not executed or authenticated.

Manual lint and terminal/HTML rendering exit zero. The 60-column rendering keeps
the existing long literal path/command lines; HTML visual review and independent
reader review remain pending. Source copies reflect this slice in a larger dirty
checkout, not an assertion that other uncommitted work belongs to this change.
