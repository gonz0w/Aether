# Snapshot hash-tool failure review — 2026-09-06

HR-02/HR-04 found a lost exit status in snapshot_digest: reading $? after a failed
if-without-else compound returned the compound's zero status. A failed hash tool
therefore appeared to produce an empty digest and reported snapshot-hash-mismatch.
The existing snapshot-hash-unavailable result was not reached. The fix captures
the failure inside else, cleans its temporary file and returns the captured status.
No schema, pin, trust policy or successful verification output changed. Failure
still returns nonzero; its existing diagnostic category is now accurate.

The regression was added before the fix. before-test.log records the reproduced
mismatch, before-verifier.sh the prior implementation, and before-input-sha256.json
the exact test inputs. Eight cases inject failed, empty, malformed and plausible
but failed digest output at self-hash and index-hash stages. Each must reject with
the appropriate hash-unavailable label, preserve both input files, clean temporary
hash files and never invoke the signer. A separate controlled-digest case proves
the signer marker is reachable. Controlled hash/signer commands are fault fixtures,
not cryptographic validation; the normal live minisign test remains separate.

Focused validation passes, including the live signature fixture. The first scoped
lint found SC2100 on two unquoted test-label assignments; quoting the literal labels
fixes those findings without suppression. initial-lint.log, initial-suite.log and
initial-test.sh preserve the failed gate and inputs. The corrected files pass lint.
The first full-suite attempt stopped at that lint gate; it is not runtime evidence.

input-sha256.json binds final runtime/test inputs; initial-lint-input-sha256.json
identifies the fixed helper with the pre-quote test. All sixteen fixtures and three pinned standards gates pass in the corrected
full-suite run, including the eight faults and live minisign fixture. Final suite and follow-up
standards/development/whitespace logs are retained alongside these attempts.
Later documentation/checkpoint edits do not change the recorded runtime inputs.

The review establishes correct ordinary hash-tool failure reporting and ordering,
not full parser fuzzing, real full-storage recovery, durability, signer authority
or remote eligibility. The earlier public source candidate predates this runtime
fix and must be rebuilt and qualified before release. Independent review, pinned
setup and the monitored security contact remain open gates.
