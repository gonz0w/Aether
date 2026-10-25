# Native catalog validation — 2026-09-07

Decision 0126 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 33 tests. Five new tests cover invalid fields
before bundle access; duplicate/non-finite/deep/oversized JSON; maintained catalog
compatibility and I/O exit types; reported hash from parsed bytes; collection/text
limits including total case budget. Synthetic hash-identity test changes a private
catalog during mocked auditing; this proves reporting identity, not end consistency.

`python3 scripts/check-all.py` passes all ten gates in run-7bbbia9g. The first run
(run-e20qyqiw) had passing gates but sources_unchanged=false because the collection
budget test was added while it ran. The failed attempt and successful rerun are
both retained, with exact commands/source hashes. A separate actual native audit
also passed. Four manual lint/render commands pass; no renderer retry was needed.

Current catalog is below 4 MiB and satisfies all supported schemas/fields without
byte changes. Existing low-level audit helpers keep their historical semantic
checks; strict catalog validation occurs at the CLI before bundle reads. Unknown
receipt fields, manifest parsing, ordinary-file policy, large-artifact reads and
final consistency remain explicit follow-ons. This is not an atomic file snapshot
or native execution witness. No external dependency or sibling change.

Native audit stdout matches run-fnv8xqqe exactly; catalog bytes and 24 native input
hashes remain unchanged. Released standard gates pass with existing pins; RC1 is
unpublished. Independent reader/HTML visual/narrow-layout review remains pending.
Source copies and scoped diff describe this slice in a larger dirty checkout.
