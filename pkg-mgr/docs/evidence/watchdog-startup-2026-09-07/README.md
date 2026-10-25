# Watchdog startup-failure receipt

2026-09-07 UTC. The development suite runner returned 125 after a spawn error
before writing result.txt. Add a semantic regression using a genuinely missing
executable in a private writable run directory. It must return 125, retain an empty
suite.log and failed result.txt with the deadline, keep its infrastructure diagnostic
and print a failure summary without a pass claim. Missing receipt or false success
is forbidden. The regression must fail before the fix and pass afterward.

Selected checks: focused watchdog controls, development/coverage/pinned standards
and fresh full sh tests/check.sh. The underlying group cleanup and package runtime
are unchanged. No guarantee of retaining a receipt on an unwritable/full filesystem
is added; this fixes executable-startup failure when the run directory is writable.
All failure evidence and exact dirty input hashes are retained. No sibling or pin
changes, native support or complete arbitrary-phase cancellation claim.

## Attempts retained

- before-fix.log/json: new control failed because result.txt was absent; hashes
  bind the original runner and added fixture.
- attempt-1-after-fix.log/json: receipt was written, but the direct fixture failed
  its unresolved-versus-resolved temporary path assertion.
- attempt-1-suite.log/result and inputs: full suite passed under its resolved TMPDIR;
  executable input hashes were unchanged during the run. This invocation began
  before handling the direct fixture failure and does not replace that failed evidence.
- The final fixture resolves its expected path just as main does. after-fix.log/json
  retain the passing direct control. The final suite has a separate input identity
  and receipts; no earlier attempts were discarded.

The development inventory already lists the watchdog control under the development
subsystem; its oracle is now explicit about failed startup receipts. Existing critical
case mappings remain 68 groups; no broader package coverage claim is added.

Final full suite: exit 0 in 229.481 seconds; watchdog result=pass.
Executable/fixture path, mode, size and SHA-256 inventory was unchanged during both
full runs. Final standards, development, coverage controls and whitespace checks
passed; full suite includes required ShellCheck for all 38 active shell files.
