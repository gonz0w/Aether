# Readiness retry validation — 2026-09-05

`python3 scripts/check-all.py` passes on macOS arm64: three pinned standards,
quality inventory, offline native audit, 37 harness tests, 34 model tests with
three negative controls and 48 host tests. The offline audit verifies 122 recorded
outcomes in 14 bundles and 3,134 listed files; it does not execute Aether.

The separate [target bundle](../native-readiness-retry-2026-09-05/README.md)
retains 23 passing QEMU cases with exact producer/worker/source pins. Both retry
paths finish with three reclaims; omitted cleanup/fresh readiness rejects at
927/929 after one reclaim. All nineteen prior supervisor binaries are unchanged;
178 frozen inputs remain stable. Positive clients are 2,272 bytes each.

This bundle retains current documentation/process snapshots and full development
logs separately to avoid a catalog/manifest cycle. The new work covers one retry,
not unbounded restart, production backoff or all interleavings. No shared pin,
kernel ABI, sibling repository or historical evidence was changed.
