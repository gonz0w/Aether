# Native catalog reference — 2026-09-07

Decision 0125 / BG-056, documentation and host controls only. Command:
`python3 -m unittest discover -s tests -p 'test_harness_native*.py'` passes 28 tests.
Three new tests require unsupported/empty/duplicate catalogs to reject before
bundle access, existing-but-unlisted results.json to reject, and matching-pin
empty manifests to reject. Synthetic files are private and never executed.
`python3 scripts/check-all.py` passes all ten gates in run-fnv8xqqe; exact commands
and source digests are in validation/results.json. All attempts passed.

The reference distinguishes current permissive catalog/JSON parsing from actual
semantic and identity checks. It documents I/O versus init case/command rules,
receipt paths, bounded init envelopes, serial outcome differences and native=not-run
summary semantics. Follow-ons retain strict records, bounded reads, complete
membership and same-byte/end identity. No checker/catalog implementation changed.

Native audit stdout exactly matches run-81w8wpg7, as do checker and catalog source
hashes. All 24 tracked native input hashes remain unchanged. Released standard
gates pass; no release pin or historical evidence changed. RC1 is unpublished.
No new native execution is claimed. Markdown reference links were checked locally;
manual sources were not changed, so rendering was not repeated. Independent
technical/reader review remains pending. Source copies reflect this slice within
the existing larger dirty checkout, not an assertion that all changes are ours.
