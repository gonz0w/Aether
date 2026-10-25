# Native binding busy rejection — 2026-09-06

Decision 0068 passes 67 native cases. Received creation busy retains empty
inventory; launch busy retains both endpoints. Exact errors and consumed tokens
remain while provisional slot claims release. Another issued service launches
in the released slot after fixture disposal; rejected tokens stay denied.
Controls hit 1018/0 and 1019/0. All 178 frozen inputs unchanged; 44 of 63 prior
raw clients match and changed clients pass prior oracles. The two busy paths use
explicitly inventoried fixture interference, not unknown inventory adoption.
Next: NB-06 expected target/received result qualification. Other errors, remaining
NB cases, ND-02–05 and BG-033 recovery stay open; no complete driver claim.

Three failed compile-only size versions are retained. Shared fixture helpers
bring all final probes within 4 KiB. No native execution failed. See witness/README.md
for exact command, source/input identity and scoped outcomes.
