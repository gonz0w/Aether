# 0121 — Standards input consistency around execution

BG-056 host verifier slice, 2026-09-07. Capture lock and manifest bytes and listed
payload digests, then recheck paths, complete membership and captured identities
immediately before and after a successful reference child. Reject controlled
mutations instead of reporting success for different inputs. Keep existing read
and traversal budgets, release bytes/pins, successful stdout and child environment.

E-01–08 require scoped identity evidence. Test late lock/manifest/payload and
membership changes before invocation and during a mocked child, plus unchanged
real pinned checks. Run focused tests and all repository gates. No sibling/native
or shared interface change. No new dependencies; retain standalone wrappers.

This detects persistent changes at comparison points, not atomic verify/execute,
changes restored before comparison, mutation after the final check or interpreter
closure. A child may already emit success text before a post-check failure;
callers must inspect the wrapper exit status. Isolated execution from verified
copies and interpreter/environment policy remain follow-ups, not claims here.

Validation: fifteen focused tests pass, including 39 new mutation subcases.
All ten repository gates pass in out/checks/run-4ijd1_d1; three released-standard
stdout streams match decision 0120. Locks and 24 native inputs stay unchanged.
Twelve manual lint/render commands pass. Evidence and scoped wrapper diffs:
../evidence/standards-input-rechecks-2026-09-07/README.md.
