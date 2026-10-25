# Native metadata inputs — 2026-09-07

Decision 0127 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 37 tests. Four new tests cover catalog/manifest
FIFO and symlink rejection before open; malformed matching-pin manifests before
payload hashing; parser input matching captured hashed bytes; and oversized,
replaced or growing metadata with descriptor closure. The same-byte parser test
changes a private manifest after capture; this demonstrates captured-byte identity,
not a final consistency check. Earlier and final focused attempts both passed.

`python3 scripts/check-all.py` passes all ten gates in run-5_9vk5jd; exact commands
and source hashes are in validation/results.json. Four manual lint/render commands
pass without retry. Current retained manifest maxima are 167,504 bytes and 1,510
entries, below the new 4 MiB/10,000-entry limits. Largest listed artifact is
3,653,632 bytes (retained firmware code.fd); payload reads remain separate work.

Catalog/manifest paths are checked at/below the supplied root. Bounded nonblocking
reads verify descriptor identity and metadata, and close on failure. Hostile
concurrent directory replacement, restored mutations, final consistency, payload
file policy/bounds and strict receipt schemas remain open. No atomic snapshot or
new native execution follows. The parser uses one captured buffer for hash/parse.

Native audit stdout matches run-7bbbia9g exactly; catalog and 24 tracked native
inputs are unchanged. Released standard gates pass with existing pins; RC1 remains
unpublished. No sibling or historical evidence changes. Independent reader/HTML
visual/narrow-layout review stays pending. Source copies/diff reflect this slice
within the pre-existing dirty checkout.
