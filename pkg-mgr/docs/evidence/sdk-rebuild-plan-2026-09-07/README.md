# SDK read-only planner implementation evidence

2026-09-07. [Contract](../../SDK-REBUILD-PLAN.md). Host development evidence only;
no native execution, SDK admission, rebuild or release qualification.

## Attempts retained

- [Attempt 1](attempt-1-registration-failure.json): fixture setup failed because
  multiple synthetic packages claimed the same artifact/inputs paths. The fixture
  now gives each package distinct paths. No planner case passed in this attempt.
- [Attempt 2](attempt-2-nul-diagnostic.json): fourteen controls passed before the
  NUL diagnostic assertion failed. The host AWK discarded NUL; the canonical-byte
  comparison rejected the binding as noncanonical, while the test expected a
  grammar rejection. There was no acceptance of the invalid binding. An explicit
  byte filter now gives consistent grammar rejection before AWK.
- [Attempt 3](attempt-3-40-controls.json): forty controls passed with metadata
  limit failures and receipt-size boundary coverage.
- [Attempt 4](attempt-4-46-controls.json): forty-six controls passed after adding
  world drift, failed delivery, interruption, plausible failed header output,
  root paths with spaces and a candidate containing consumers.

Each JSON records actual command arguments, results and source hashes. Working
roots are retained under the paths in those commands. SDK receipts and artifact
bytes are synthetic; opaque receipts and fixture build metadata establish no
complete SBOM, actual link-input closure, original provenance or native authority.
Fixture re-registration and graph edits construct test inputs; the planner itself
never registers, edits or removes a record/payload.

Early scoped lint identified SC2154 for a trap variable and SC2015 for two boolean
checks. Explicit initialization and grouped conditionals resolved these without
suppression. Review also moved header/count reads into checked assignments so a
failed provider cannot pass through successful-looking output. The final header
failure control covers that path.

## Full gate

[Full command log](full-check.log) and [source identities/result](full-check.json)
record the normal suite run. This checkout includes pre-existing Origins changes;
exact dirty runtime/fixture inputs are recorded, rather than treating HEAD alone
as the test identity. See the result's status and input comparison for completion.
The suite's own private log/receipt and the planner run directory remain retained.
The full gate returned 0 in 317.449 seconds with its recorded inputs unchanged:
all sixteen shell fixtures and the [46 planner controls](full-sdk-controls.json)
passed, alongside the existing SDK/profile/Origins/CLI and standards checks.
The final fixture also creates its work parent when absent in a fresh checkout.
[Final checks](final-checks.json) retain the passing documentation/standards/lint
commands and confirm runtime inputs still match the completed full gate.

## Limits

The tests compare exact reports and selected diagnostics, root entry types/modes/
file hashes and root-local sentinels. They check receipt size at 1 MiB and one byte
above, and rejection above package/edge/world/per-record/aggregate bounds. They do
not prove every valid maximum-size graph or record, physical disk exhaustion,
SIGKILL cleanup, hostile concurrent writers, all host shells/AWK implementations,
external-sentinel preservation under races or native execution. Injected world
drift is left intact by the planner; only the test restores its own edit before
checking for collateral effects. Failed delivery and TERM are controlled provider
injections, not power-loss or terminal certification. A plan is never apply or
service authority. Complete input receipts remain the producer's responsibility.
