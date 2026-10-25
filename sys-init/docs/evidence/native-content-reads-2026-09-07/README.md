# Native semantic content reads — 2026-09-07

Decision 0129 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 44 tests. Three new tests cover host-default
text/newline compatibility; late JSON, envelope and serial replacement with FIFO,
symlink or oversized files during actual copied-bundle auditing; and descriptor
cleanup on read error. Late replacements happen at the semantic reader after
initial hashing, proving that content reads apply their own file/type/size checks.
Both earlier and final focused attempts pass.

`python3 scripts/check-all.py` passes all ten gates in run-hdspju8m. Exact commands
and source hashes are in validation/results.json. Four manual lint/render commands
pass. No failed test/render attempts occurred. IO TextIOWrapper is standard-library
support for preserving default text decoding and universal newline semantics.

Every semantic read uses a captured buffer bounded at 4 MiB with ordinary-file,
component and descriptor identity checks. Digest-only archive/firmware reads retain
the 64 MiB streaming path. Hashes and semantic reads still capture independently;
strict receipt JSON and verified-byte parsing/final consistency remain open. No
atomic snapshot, I/O deadline or new native execution follows from this change.

Native audit stdout exactly matches run-wl7174yz; catalog and 24 native input
hashes remain unchanged. Released standard gates pass with existing pins; RC1 is
unpublished. No sibling or retained evidence changes. Independent reader/HTML
visual/narrow-layout review stays pending. Source copies/diff record this slice
within the pre-existing dirty checkout.
