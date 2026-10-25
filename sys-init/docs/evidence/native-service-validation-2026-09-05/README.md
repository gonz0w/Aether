# Native service development validation — 2026-09-05

`python3 scripts/check-all.py` passes on macOS arm64: 48 host tests, 34 model
cases/three mutation controls, 30 harness tests, all three standards checks and
the 63-outcome offline audit. Target evidence is retained separately in
`../native-service-2026-09-05`: fourteen cases pass with unchanged frozen inputs
and nine unchanged legacy adapter binaries. The separate validation bundle avoids
a catalog/manifest reference cycle. No Linux rerun or older ABI-2 target execution
is claimed. The production service graph and spontaneous failure schedules remain
unimplemented by this bounded forced-stop workload.
