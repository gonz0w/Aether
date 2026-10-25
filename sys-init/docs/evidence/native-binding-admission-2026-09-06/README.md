# Native binding admission — 2026-09-06

Decision 0066 passes 61 native cases. Two generation-one services bind complete
issued tokens to actual retained workers/readers; preflight denial preserves
reservation and acquisition count, and consumed tokens remain denied after
fixture cleanup. Controls hit 1014/0 and 1015/0. All 178 frozen inputs unchanged;
44 of 57 prior raw clients match and changed clients pass prior oracles.
This is synthetic issuance and read-only launched qualification, not a pending
event queue or journal. Next: NB-04 post-acquisition failure retention with an
omission control. Remaining ND-01 cases, ND-02–05 and BG-033 recovery stay open.

Seven failed size versions with source/logs/maps are retained; all final probes
fit the unchanged 4 KiB bound. See witness/README.md for the exact command and
limits. No native execution failed; no production or complete contract claim.
