# UL-066 bracket/range interpretation

Follow up the supplementary ROT13 failure without changing its historical oracle.
Pinned BusyBox tr.c explicitly treats ordinary brackets as literal characters;
only class/equivalence syntax has special bracket meaning. Compare both pinned
providers using bracketed and unbracketed expressions on the original phrase and
all256 input bytes. Eight cases, C locale, exact stdout, empty stderr and exit0.

Expected arrays are explicit ASCII bytes: [abcdefghijklmnopqrstuvwxyz] maps to
[nopqrstuvwxyz][abcdefghijklm], while abcdefghijklmnopqrstuvwxyz maps to
nopqrstuvwxyzabcdefghijklm. A simple positional byte table supplies the independent
oracle; the original phrase's unbracketed result must also equal the literal
squeamish ossifrage plus newline. The earlier ROT13 expectation for the bracketed
expression must disagree. This characterizes pinned implementations, not POSIX
conformance or every locale. No upstream or historical evidence modification.

Reuse LEGACY-PLAN's unchanged process/container helpers, exact runtime/candidate
pins, licenses,15-second children/180-second container, read-only inputs and
private scratch. Retain all eight command records and cleanup, source archive
identity and extracted tr.c. Run syntax, actual cases and quality gate. Review of
this new helper remains pending. Document the supplementary test assumption as
incorrect if all observations support it; retain real prior provider differences.
