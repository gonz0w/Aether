# Native receipt JSON parsing — 2026-09-07

Decision 0132 / BG-056. `python3 -m unittest discover -s tests -p
'test_harness_native*.py'` passes 53 tests. Three new tests cover duplicate keys,
non-finite literals/numeric overflow, depth/byte limits, invalid UTF-8 and non-object
roots; finite values/quoted-bracket compatibility; and routing at all five receipt
read sites. Routing controls inject malformed bytes at the parser boundary during
real retained auditing without modifying retained files. No native content executes.

`python3 scripts/check-all.py` passes all ten gates in run-zw1mn0x6; exact commands
and source hashes are in validation/results.json. Four manual lint/render commands
pass. All test and renderer attempts passed. Finite-float checking also applies
to the shared catalog/manifest parser, with their existing strict field checks.

Verified receipt buffers now decode as UTF-8 and use bounded strict JSON parsing,
requiring object roots. Serial text retains host-default decoding/newlines.
Per-schema fields/types/extension policy are not fully validated by this slice;
sequential filesystem checks are not atomic snapshots. Independent review and
I/O deadlines remain open. No external dependency or shared ABI is introduced.

Native audit stdout matches run-djhnko6x exactly; catalog and 24 tracked native
inputs remain unchanged. Released standard gates pass with existing pins; RC1 is
unpublished. No sibling or retained evidence mutation. Independent reader/HTML
visual/narrow-layout review remains pending. Source copies/diff describe this slice
within the pre-existing dirty checkout.
