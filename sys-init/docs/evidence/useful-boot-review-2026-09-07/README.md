# Useful boot input review — 2026-09-07

BG-066 source review only. inputs/ retains the exact selected companion documents,
source and reported userland receipt inspected for compatibility. This is not a
complete producer source archive or an executable intake. Companion test outcomes
are reported evidence, not fresh sys-init consuming runs. Individual source reads
were compared after capture; the selection is not an atomic sibling checkout.
Released/runtime pins and historical bundles remain unchanged.

See [findings](../../research/USEFUL-BOOT-INPUTS.md). reviewed-files.json records
source locations and content hashes. Final local check results are retained after
validation; sha256.json seals this bundle, excluding itself.

Validation: `python3 scripts/check-all.py` passed all ten gates in
run-192jzn08 on macOS arm64, with checked sources unchanged. `git diff --check`
passed. All 18 captured input hashes and review links verified; inspected local
runtime files and the three released locks are unchanged. No fresh target run or
independent approval is claimed. BG-066 review is complete; BG-067 integration
remains blocked. No sibling repository was modified.
