# Preflight receipt hash failures — 2026-09-06

HR-02/HR-04 review found final preflight record hashes embedded in printf arguments.
When the selected old-record hash helper returned failure, preflight still returned
success. before-test.log retains the regression assertion and before-result.json
its 300-second process-group deadline. before-binary.sh, before-binary-package.sh
and before-inputs.json bind the exact pre-fix bytes. This is a false-success report,
not package mutation or evidence that replacement finish accepted an invalid plan.

Both final old/new record hashes are now assigned and checked before the report
header. A failed helper cannot produce an incomplete or falsely successful report.
Successful fields/order, error stream, standards pins and dependencies are unchanged.
No new diagnostic vocabulary or shared policy is introduced.

Oracle and forbidden outcomes: inject a failed hash-file request for the final old
or new record pin. For each, test empty stdout and a correct digest followed by
exit 73. Require the marker, nonzero status, no report bytes and unchanged target
file/hash/mode snapshots. The wrapper counts only the exact chosen helper/file:
old record's first direct request, proposed record's second (after its descriptor
validation request). Other invocations delegate to recorded host sh. Four cases
must reach the final-report seam; an earlier validation failure is not a pass.
The positive check compares the first four report lines against the fixed schema,
package identity and hashes of the actual old/proposed records. Existing drift,
reverse-dependent and three-way comparison cases retain their oracles.

Selected checks: scoped ShellCheck and the normal sixteen-fixture suite, including
all three pinned standards gates, under its 600-second process-group watchdog.
Final runtime/test hashes and host tools are retained in input-sha256.json and
tools.json. Failures remain in separate logs; no timing is a performance claim.
The contract and existing subsystem inventory are updated; no new driver is added.

The public candidate predates this correction and needs refreshed qualification.
These deterministic command failures do not establish full-storage behavior,
concurrency safety, power-loss durability or publisher authentication. Captured
builder setup, independent reviews, a monitored security contact and publication
approval remain separate release gates.

All sixteen fixtures, three pinned standards gates and whole-shell/scoped lint
pass. All four report-hash faults and the successful exact-header check pass,
alongside prior export/replacement/recovery controls. Runtime/test hashes remain
unchanged after the run; suite-result.txt records its duration and deadline.
