# Native adapter development validation — 2026-09-05

`python3 scripts/check-all.py` passes on macOS arm64: 48 host tests, 34 model
cases/three mutation controls, 30 harness tests, all three standards and the
38-outcome offline native audit. The catalog pins seven bundles/1,693 listed
files. Target execution is retained separately under `../native-adapter-2026-09-05`;
its nine primary cases pass, while the minimal sequential-reuse probe remains
failed and gates broader lifecycle orders. No new Linux execution is claimed.

The primary evidence and catalog were finalized before this full check. This
separate validation bundle avoids a catalog/manifest reference cycle. The source
snapshot records the checkpoint and decision. `size-diagnostic` retains a private
relaxed-link measurement of the rejected initial implementation (5,232 bytes):
this diagnostic artifact was never booted and does not satisfy the 4 KiB bound.
All accepted native cases use the unchanged original linker map.
