# Effect acknowledgment ledger evidence — 2026-09-06

Isolated trusted Python ledger on macOS arm64. It neither invokes native effects
nor guards Delivery.take_effects. Tokens are accounting identity, not authority;
acknowledgment has no lifecycle observation or cleanup side effect.

Commands from repository root:

- `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-effects-final-20260906.json`
  passes 119 tests and eleven mutation controls. model.json contains verbose cases,
  source hashes, host identity and caught assertions; model.log records stdout.
- `python3 scripts/check-all.py` passes 119 model/eleven controls, 48 host and 37
  harness cases and all offline gates. validation/ retains exact reports/raw logs.
  Native audit checks 215 historical outcomes, not new target execution.
- `git diff --check` passed for tracked changes.

Nine cases cover issue/ack separation, token mismatch, atomic validation rejection,
capacity and serial bounds, unknown retention, history/generation retirement,
driver-loss closure and separate lifecycle ownership. The reclaim case keeps the
worker owned after executed acknowledgment until a distinct cleaned observation.
Removing the unissued-execution guard must cause one assertion failure without
errors. The tests do not establish crash-atomic allocation or truthful driver input.

initial-model.json/log preserve the passing 119-test/ten-control run before the
issued-state mutation. No failed implementation run was observed. source/ retains
final source/docs; model hashes match retained code. Result-only Markdown notes
were added after full checks. SHA256SUMS.json binds all files except itself.
Existing pins/bundles remain unchanged; no independent owner sign-off is claimed.
Next work is capacity-gated delivery integration and producer-result mapping;
unknown reconciliation and replacement-driver authority remain open.
