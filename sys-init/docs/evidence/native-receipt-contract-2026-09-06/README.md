# Native receipt ownership contract evidence

2026-09-06, decision 0071. Documentation and acceptance-plan review only.
`source/` retains ten reviewed local sources with `reviewed-files.json` digests.
The binding contract copy records the basis before this decision's appended note.
`native-source-comparison.json` lists seven current consumer hashes verified
against `../native-generation-exhaustion-2026-09-06/witness/sources.json`.
No native code changed or new target execution occurred; decision 0070's 75-case
witness remains the implementation checkpoint.

`validation/` contains the exact `python3 scripts/check-all.py` command output
and all eight passing reports from `out/checks/run-jxyxd88h` on macOS arm64.
The model passes 228 tests, 23 negative controls and 1000 traces; host passes
48 tests, harness 37. The catalog verifies 1040 historical outcomes in 35 bundles.
These are historical outcomes, not 1040 distinct current native tests.

`adoption/` preserves the contract, decision, scoped standards record, quality gap
and next work. Validation notes and evidence copies were added after the checks;
no implementation, pin, inventory or contract changed afterward. Link review and
`git diff --check` pass. No independent sign-off, receipt implementation,
missing-kernel-reply recovery or new native conformance is claimed.

`SHA256SUMS.json` inventories all files except itself. Hashes establish byte
identity, not authority. Historical bundles and shared release bytes are unchanged.
