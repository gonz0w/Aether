# 0029 — Bounded control request decoding

Accepted for a local BG-050 prototype, 2026-09-06. Implement B01/B02 of
[Control boundary v0](../specs/CONTROL-BOUNDARY-V0.md) as a pure decoder followed
by existing facade validation. No socket, authentication or response API is added.

`decode_request(frame)` accepts exact immutable bytes, validates the four-byte
length envelope and 4096-byte body cap before copying/decoding the body, checks
container depth before recursive JSON parsing, and returns an inert root dict.
It rejects BOM/invalid UTF-8, duplicate decoded keys, surrogate strings, fractional
or exponent numbers, non-finite constants and integer tokens over 20 digits.
The facade remains the sole logical payload validator: pass the candidate to
`Control.submit` for exact fields/types/version, identity, service and value bounds.
Decoder success alone is not request admission or authority. No duplicate schema
validator is introduced; no convenience dispatch API implies authenticated delivery.

Use the Python standard JSON parser after a bounded quote/escape-aware depth
scan. A custom JSON grammar would add unnecessary maintenance; an unrestricted
parser would not satisfy the pre-parse depth and numeric conversion limits.
Existing Python host-tool portability rationale applies; no dependency is added.
The pure decoder owns only bounded temporary values, performs no I/O and touches
no manager state. Input already exists in caller memory; stream allocation,
deadlines and backpressure remain unimplemented. No performance claim follows.

Errors use `InvalidFrame(ValueError)` with fixed categories: frame-type,
frame-length, utf8, depth, json, duplicate-key, number, unicode, root.
Do not interpolate source bytes or parser diagnostics into exception text.
Malformed syntax is not distinguished beyond these local categories; unexpected
host failures such as MemoryError are not converted into successful decoding.

Test hand-authored frames, exact length/depth limits, pre-parser rejection,
quoted delimiters/escapes, UTF-8 and escaped Unicode, duplicate escaped keys,
numeric conversion limits and logical schema rejection without state/sequence
changes. Equivalent bytes must replay the original receipt with no effects;
changed logical payload must reject. Run model and full development checks and
retain source/report identity. Native sources and shared pins stay unchanged.

Next define bounded response projection/encoding, keeping internal effects out of
client replies. B04–B06 authority, stream delivery and restart recovery remain
separate gates; BG-050 stays active.

Result: [retained evidence](../evidence/control-codec-2026-09-06/README.md) passes
61 model tests and five mutation controls, plus full development checks: 48 host,
37 harness and all offline standards/quality/native-evidence gates. The native
audit covers 215 historical outcomes; no fresh native execution was required.
The runner's formerly hard-coded control count now reports the actual list size;
report fields, output layout and exit contracts are unchanged.
