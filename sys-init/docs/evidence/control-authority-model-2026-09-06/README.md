# Trusted control authority model — 2026-09-06

Python policy model on macOS arm64, not native authentication or a protection
boundary against direct object access. The binding is one opaque fixture object.
Unguarded Model/Delivery/Stream APIs remain trusted experiment tools.

Commands from repository root:

- `python3 scripts/check-runtime-model.py --output /private/tmp/sys-init-authority-final-20260906.json`
  passes 110 tests and ten controls. model.json retains verbose cases, mutation
  assertions, source hashes and host identity; model.log records stdout.
- `python3 scripts/check-all.py` passes 110 model/ten controls, 48 host and 37
  harness cases and all offline gates. validation/ retains reports and raw logs.
  Native audit checks 215 historical outcomes, not new target execution.
- `git diff --check` passed for tracked changes.

Eleven cases cover invalid bootstrap, foreign/missing binding, payload impersonation,
dependency/stop/shutdown scope, separate disclosure rights, conflicting private
operation details, cached rejection replay, revocation across partial input/output,
same-binding reconnect, stale configuration, unknown lookup and copied scopes.
The conflict test injects a separate active operation through the trusted model
owner. It demonstrates disclosure policy, not concurrent-client native execution.
Removing binding comparison must cause one assertion failure without test errors.

initial-model.json/log preserve the passing 110-test/nine-control run before the
binding mutation. No failed implementation run was observed. source/ contains
final implementation and documents. Execution source hashes match retained code;
result-only Markdown notes were added after full checks. SHA256SUMS.json covers
all files except itself. Shared pins and earlier evidence remain unchanged.
Native binding/revocation, effect execution acknowledgment and recovery remain
BG-032/BG-033 gates. No independent owner sign-off or real endpoint is claimed.
