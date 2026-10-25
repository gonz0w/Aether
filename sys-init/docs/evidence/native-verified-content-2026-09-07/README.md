# Native verified semantic content — 2026-09-07

Decision 0130 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 47 tests. Three new tests cover changed captured
JSON/summary/envelope/serial bytes before parsing, parsing from the verified buffer
despite a later physical file change, and secondary receipt digests remaining tied
to the pinned manifest. The verified-capture test deliberately still passes after
post-capture file mutation, documenting the lack of final tree consistency.
Earlier and final focused attempts pass.

`python3 scripts/check-all.py` passes all ten gates in run-718_ig3c; exact commands
and source hashes are in validation/results.json. Four manual lint/render commands
pass. No failed test/render attempts occurred. Semantic buffers remain per-read,
not a whole-bundle cache. Their existing 4 MiB/type/path/descriptor checks remain.

Each semantic buffer is hashed against the retained manifest before decoding or
parsing. Secondary receipt-correspondence digest reads must also equal the manifest
map. This prevents a new buffer from being parsed under an earlier digest, but
does not establish atomic tree identity, complete membership, final consistency,
strict receipt schemas or blocked-I/O deadlines. No native execution or new target
qualification follows. No external dependency or shared ABI changed.

Native audit stdout exactly matches run-hdspju8m; catalog and 24 native inputs
remain unchanged. Released standard gates pass with existing pins; RC1 remains
unpublished. No sibling or retained evidence modifications. Independent reader/
HTML visual/narrow-layout review remains pending. Source copies/diff describe this
slice within the pre-existing dirty checkout.
