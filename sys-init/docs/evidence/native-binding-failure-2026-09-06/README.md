# Native binding failure retention — 2026-09-06

Decision 0067 passes 63 native cases. Local binding failure after actual channel
success retains both endpoints, original token/slot and consumed/pending state;
separate binding_failed closes admission without inventing native errno. Repeated
calls deny without new acquisition. Writer-loss control hits 1017/0. All 178
frozen inputs unchanged; 44 of 61 prior raw clients match and changed clients
pass prior oracles. Fixture disposal clears Adapter accounting but leaves the
driver failed and reservation retained; no recovery or journal cleanup is claimed.
Next: NB-05 selected creation/launch rejection within an explicitly scoped fixture.
Remaining ND-01, ND-02–05 and BG-033 recovery stay open.

Initial compile-only type error is retained in build-attempt-1. The corrected
source uses typed close_writer; all final clients fit 4 KiB. No native execution
failed. See witness/README.md for exact command, evidence and limits.
