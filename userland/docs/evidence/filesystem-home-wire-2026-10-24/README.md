# Two-grant service/client evidence — 2026-10-24

[FS-HOME-WIRE](../../proposals/FS-HOME-WIRE.md) owns requirements, status and
continuation. These are actual Rust owner/service/client host executions over
synthetic storage and no_std builds. No guest, native transport/readiness or
complete executable/persistence acceptance was performed.

Final command, from `userland/`:
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-home-wire.py`.
[Run context](run-context.json) binds that exact caller environment to
[attempt07](attempt-07.json). Its135 child receipts record pinned Rust1.98.0,
strict warnings/Clippy/Owner-service-client unsafe denial, actual commands, source
and tool/native-library identities, deadlines, outputs and process cleanup.
The source freeze includes the existing sealed AF07 producer and its manifest;
neither the seal nor current native dependency selection was refreshed.

## Attempts and triage

| Attempt | Outcome |
| --- | --- |
| [01](attempt-01.json) | Planned tests-before-code red: missing run_home/connect_home APIs. Compiler result, not a semantic runtime failure. |
| [02](attempt-02.json) | Implementation compile failure: shared loop visibility and an over-restricted old private constructor. Corrected internal visibility and retained the constructor used by the private old bulk helper. No guest. |
| [03](attempt-03.json) | New interoperability tests pass; harness incorrectly compiles legacy service tests under unsupported runtime/wait/namespace flags. Select their actual legacy profile; exercise AF07/08 through their actual client tests. No product pass inferred from the failed suite. |
| [04](attempt-04.json) | Behavior/build/layout/compatibility checks pass, and the first mutant fails its named semantic marker. Checker incorrectly requires the literal word “assertion”; corrected to require each explicit semantic marker. Attempt remains failed. |
| [05](attempt-05.json) | Initial complete pass: eight integration tests and six compiling semantic controls, with selected/default/sealed compatibility and layout checks. |
| [06](attempt-06.json) | Expanded affected profile/consumer checks pass, including AF05/06 compilation, both mismatch directions and the missing-home prerequisite. |
| [07](attempt-07.json) | Final pass after peer review replaces Python assert-based oracles with explicit checks. Runs under PYTHONOPTIMIZE=1,135 children and six semantic controls. |

No failed observation is reset or discarded. Qualified attempts preserve compact
results and short diagnostics; all owned generated build/source/mutant trees and
CLI/process-check roots are removed. No SDK, full run archive or binary retained.

## Acceptance mapping

Eight new tests cover actual two-grant client reads/lookups, physical home paths,
borrowed dot/root-parent and attenuated nested-parent aliases; malformed/lost first
or second greetings; refusal by old constructors; service greeting-loss readiness;
wrong provisioning; actual raw home create/write versus root/read-alias denial;
malformed body/reply-loss retirement; and the tested12-free-owner-handle capacity
without token advancement on Full. Both local close results remain observable and
normal client/service/backend cleanup occurs exactly once.

Six compiling controls remove home-kind validation, accept the wrong home token,
publish readiness after a failed second greeting, widen root rights, bind home to
root, or reuse token2 for a new handle. Each fails its named test and required
marker; timeout/generic failure cannot qualify a control.

There are65 additional host regression executions: AF08 and AF07 each run1 policy
and13 actual client cases, legacy policy13/service11, and current client13 against
the exact sealed AF07 service. These unchanged suites supply existing foreign/
stale-handle, malformed response, cleanup and retirement coverage. They are not
new native AF09 authority tests. AF05/06 and selected/AF07/08 host and target
library builds pass; matching old activation/remote consumers still build, while
AF09 dependencies and both mismatched client/service directions reject on host
and target. The old service run entry is unavailable under AF09.

Client remains680 bytes/alignment8; host/target equality against AF08 passes.
Owner's prior1080/8 result is reused from unchanged FS-HOME inputs, not freshly
measured here. Source inspection confirms no new Owner/Client/Binding fields.
Whole-owner code/stack/resident sizing is pending native consumer integration.
Current Python3.14.7 is tested; minimum Python3.10 execution is not established.

[CLI controls](cli-controls.json) pass help/version, escaped usage64,
missing/mismatched-prerequisite2, syntax and a deliberate failing oracle under
`python -O`. [Process checks](process-checks.json) verify root standards and
method/simplicity pins. [Separate peer review](peer-review-checks.json) reports no
unresolved findings and retains final workflow/quality/link gates and owned-output
cleanup. Its actual scope is recorded in the owning record.
