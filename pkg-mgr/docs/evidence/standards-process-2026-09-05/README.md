# Standards process review — 2026-09-05

The updated canonical catalog/requirements were reviewed in the pkg-mgr owning task.
The three immutable release pins match; new coding, testing and documentation
profiles remain drafts. No standards repo or published release was modified.

`review.json` binds the local process inputs and observed check scope. `development.log`
and `releases.log` retain checks. `shellcheck-initial.log` preserves 112 initial
legacy diagnostics, including the CDPATH warning subsequently corrected in the
changed tests/check.sh. This is not a suppression baseline or reviewer approval.
The complete fixture run is recorded separately in `macos-fixtures.log`.

Four deliberate development-check failures were exercised in disposable copies:
empty inventory, new untracked-by-inventory source, invalid shell syntax and absent
reference. Each failed for its named reason; no runtime fixtures were mutated.

Initial lint triage: lifecycle byte decoding deliberately splits od's numeric output
(SC2086); state result labels are strings rather than arithmetic (SC2100); several
SC2094 observations arise inside read loops and require call-path review before
suppression. No whole-file exceptions were added. Remaining warnings are unresolved;
review touched code and run the required changed-file lint gate before merge.

This work establishes contributor/check selection and records missing release gates.
It does not establish whole-repo coding conformance, manual completeness, reader
review, scheduled CI, broad host portability or supported-product release readiness.
See [the local process](../../DEVELOPMENT.md) for owner and revisit conditions.

The drift check rejected a changed canonical README during this review. The owner
was recording maintainer approval of all four drafts. After reading the approval
and updated status/defaults, the local review snapshot was refreshed; its initial
snapshot is retained. No immutable pin changed. The linked machine-readable approval
receipt was not yet present; verifying it remains part of future release adoption.
