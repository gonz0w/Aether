# Standards input bounds — 2026-09-07

Decision 0120 / BG-056. Host input verification only; no native/shared ABI changes.
Commands: python3 -m unittest discover -s tests -p PATTERN, for patterns
`test_harness_standard_wrappers.py`, `test_harness_offline_locks.py` and
`test_harness_standard_inputs.py`; then `python3 scripts/check-all.py`.
Twelve focused tests and all ten aggregate gates pass in run-fq54cl5_.
Exact aggregate commands/source hashes are in validation/results.json.

New controls span all three wrappers: lock/manifest/payload FIFO and symlink
rejection before open or child invocation, oversized reads before execution,
exact 1 MiB read and 2,000-entry acceptance, overflow rejection, controlled
replacement and growth with descriptor closure. Private synthetic trees and
mocked child invocation do not establish atomic concurrent-filesystem safety.
The initial input suite passed eight cases because it imported another test class;
module import limits discovery to the four intended tests. The growth hook was
also shortened to one mutation. Both passing attempts are retained.

Readers are deliberately self-contained in each wrapper to preserve copied-script
operation. No external dependency is introduced. Locks now decode ASCII; current
ASCII pins and LF/CRLF layouts remain supported. Filesystem deadlines, directory
replacement races, restored changes and verify-to-execute identity remain open.
Child environment/behavior is unchanged, including Foundations inheritance.

All three released reference stdout streams match run-j58r3r5b exactly, released
lock bytes match decision 0119, and 24 native inputs match the boundary snapshot.
No native runtime changed or new target witness was needed. RC1 is unpublished.

Initial mandoc lint flagged blank fill-mode lines and long source lines in the
added caveats. Corrected source passes all twelve final lint/78-column/60-column/
HTML commands; both render attempts are retained. Long literal identifiers may
exceed narrow terminal widths; independent reader and HTML visual review remain
pending. Final manual-only corrections follow the aggregate run and were checked
with mandoc. Source copies represent this slice within a larger dirty checkout.
