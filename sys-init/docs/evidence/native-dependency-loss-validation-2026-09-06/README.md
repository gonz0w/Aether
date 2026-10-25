# Dependency loss validation — 2026-09-06

`python3 scripts/check-all.py` passes on macOS arm64: three pinned standards,
quality records, 215 historical native outcomes, 37 harness tests, 34 model
tests/three controls and 48 host tests. Historical audit covers 17 bundles and
4,563 listed files without executing the target.

The separate [target bundle](../native-dependency-loss-2026-09-06/README.md)
retains 35 passing QEMU cases. Both provider-loss schedules retain the admitted
dependent alive until explicit stop; controls reject at 940/941 with zero reclaims.
Thirty-one older raw supervisors remain unchanged; all 178 frozen inputs remain
stable. Positive clients are 2,416/2,528 bytes under the existing 4 KiB bound.

This is bounded R-07 alignment, not a full native model port or operator event
stream. Current policy/quality/planning snapshots and full check logs are retained
separately to avoid a native catalog/manifest cycle. Earlier stop-on-loss fixtures
remain unchanged historical profiles. No shared pin, ABI or sibling file changed.
