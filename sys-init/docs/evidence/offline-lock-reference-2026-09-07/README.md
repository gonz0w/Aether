# Offline lock reference — 2026-09-07

Decision 0119 / BG-056. Documentation and synthetic host-test coverage only.
Four new tests exercise 45 subcases across Foundations, Experience and Distribution:
accepted row ordering/LF/CRLF/final-newline variations (9), malformed fields (30),
manifest identity before ASCII parsing (3), and changed payloads before invocation
(3). Child execution is mocked. The tests use private temporary trees and do not
alter vendored releases. Existing tests and actual released reference checkers
are separately included in the successful ten-gate aggregate run.

Focused command: `python3 -m unittest discover -s tests -p 'test_harness_offline_locks.py'`.
The first run failed nine expected-path comparisons because macOS resolves /var
through /private/var; the expected checker path was corrected with resolve().
Both logs are retained. Aggregate command: `python3 scripts/check-all.py`.
All ten gates pass in out/checks/run-j58r3r5b; command details and source hashes
are in validation/results.json. No new native behavior or target run is claimed.

All three wrappers match their prior retained source snapshots (Foundations:
standards-manuals-2026-09-06; other two: standards-wrapper-validation-2026-09-06).
All lock bytes match standards-manuals-2026-09-06 and 24 native inputs match the
local-boundary-review snapshot. Released standard gates pass unchanged; RC1 remains
unpublished. Source copies record this slice within the existing dirty checkout.

The reference records actual permissive parser details and remaining unbounded
read/tree traversal, special-file, verification-to-execution and interpreter
closure gaps. It neither approves those gaps nor establishes independent review.
No manual renderer change was made; this is a Markdown configuration reference.
