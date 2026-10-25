# Retry budget development validation — 2026-09-06

`python3 scripts/check-all.py` passes on macOS arm64: three pinned standards,
quality inventory, 149 historical native outcomes, 37 harness tests, 34 model tests
with three negative controls and 48 host tests. The historical audit reads
15 pinned bundles/3,582 files and does not execute the target.

The separate [target bundle](../native-retry-budget-2026-09-06/README.md) retains
27 passing QEMU cases. Silent/malformed exhaustion each finishes three cleanups
and refuses a fourth reservation. Excess admission rejects at 931 after three
reclaims; early termination rejects at 934 after two. Twenty-three prior raw
supervisors remain unchanged, and all 178 frozen consumer inputs remain stable.

The positive clients are 1,200/1,216 bytes within the existing 4 KiB bound. This
is bounded policy evidence, not a production retry default or new target timing
claim. No kernel, shared pin, sibling file or historical evidence changed.
Current source/planning snapshots and full development logs are retained here
separately from the target catalog to avoid a manifest cycle.
