# Quality record validation evidence

Decision 0116 adds bounded strict inventory/manifest parsing. Exact required
fields, existing optional gap reference/review_evidence fields, strings, arrays,
paths, digests, statuses and IDs reject malformed values before traversal.
Each JSON input is limited to 1 MiB and 32 levels; duplicate keys, non-finite
constants and invalid Unicode/JSON reject. The manifest is captured once for
both hash verification and parsing. Optional gap references must exist locally.

All eleven quality tests pass: six existing tests with required scope added to
minimal fixtures, plus five new tests. New coverage includes eleven malformed
inventory variants with no-traversal assertions, eight malformed JSON inputs
plus depth/string positives, matching-pin malformed manifests, optional gap
references and a real copied-checker CLI failure (empty stdout, stderr, exit 1).
No failed test/check attempt occurred.

All ten gates pass in out/checks/run-ulshq9dr, retained in validation/. Quality
success stdout matches the prior run byte-for-byte. Reviewed snapshot location
and pin and all 24 native inputs are unchanged. No sibling, native implementation,
release pin, retained snapshot or vendored bytes changed. No native execution or
independent reviewer approval is claimed.

Manual lint and 78/60-column/HTML generation pass. Final evidence assembly's
width assertion found two existing literal lines at 62 and 61 columns in the
60-column rendering (snapshot path and example command); width-review.txt retains
that failure/limitation. No 78-column overflow. Identifiers remain complete;
publication layout and independent/HTML/target review stay open.

Full snapshot closure, ordinary-file/symlink policy and end-of-run identity remain
BG-056 work. One captured manifest removes hash/parse rereading but does not make
the whole snapshot atomic. Referenced tests are not executed by this checker;
owner and review metadata are syntactic, not authenticated approvals.
