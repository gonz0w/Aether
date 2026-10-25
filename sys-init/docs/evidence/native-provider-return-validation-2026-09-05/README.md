# Provider-return development validation — 2026-09-05

`python3 scripts/check-all.py` passes on macOS arm64: 48 host tests, 34 model
cases/three mutation controls, 32 harness tests, all three standards checks and
the 80-outcome offline native audit. The catalog covers 12 bundles and 2,323
listed files. Two new inert harness tests reject changed worker receipts, ELF or
build inputs and escaping input paths.

Target execution and worker-build evidence are retained separately under
`../native-provider-return-2026-09-05`. Its 17 cases pass with 178 unchanged
consumer inputs, and all fourteen preceding clients remain byte-identical. This
separate validation bundle avoids a catalog/manifest cycle. No Linux, SMP,
physical-hardware or prior ABI-2 target execution is claimed.
