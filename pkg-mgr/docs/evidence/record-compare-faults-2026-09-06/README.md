# Record comparison error review — 2026-09-06

HR-02/HR-04 found cmp errors treated as ordinary differences in preflight and
replacement branching. The pre-fix regression injected exit 2 into the exact
old/proposed comparison and observed preflight success. before-test.log records
the failing assertion; before-binary.sh, before-replacement.sh and the before-input
manifest identify the tested implementation. This demonstrates a false-success
preflight, not an observed payload mutation.

The local same_record helper in binary.sh and replacement.sh accepts status 0 as
equal and 1 as different. Every other result aborts with the existing helper error
prefix and 'cannot compare package records'. Prepare cannot treat a read/tool error
as authorization to build a replacement, and finish cannot fall through to another
record-state branch after such an error. Existing equality guards that already
reject every nonzero result remain unchanged. No format, pin, runtime dependency
or successful-output change.

Six controls inject statuses 2 and 73 in preflight, prepare's own post-preflight
comparison, and finish's old-record comparison. The wrapper counts only the exact
selected input pair, so preparation exercises its second comparison independently
of required preflight. Each case must reach its marker, fail without stdout, and
preserve the target's complete file/hash/mode snapshot; failed preparation must
leave no pending transaction. The existing successful replacement, retry and
retained-stage cases exercise normal equal/different decisions.

All sixteen fixtures and all three pinned standards gates pass, including six
comparison-error cases and existing normal/recovery paths. tools.json records the
host and relevant tool identities. input-sha256.json binds final source/test inputs. The selected checks are scoped
lint, the normal sixteen-fixture suite with these controls, and final development,
standards/experience and whitespace checks. Failed regression evidence remains
separate from the accepted full-suite log/result. Later tracking/documentation
edits do not change the recorded runtime inputs.

These are ordinary comparison-tool failure controls, not hostile filesystem-race,
concurrency, physical full-storage or durability qualification. The previously
assembled public archive predates this fix and needs refreshed qualification.
Independent review, pinned setup, the actual monitored security contact and
publication approval remain outstanding.
