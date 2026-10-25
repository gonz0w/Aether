# 0103 — Offline wrapper validation and assertion mode

Accepted local verification fix, 2026-09-06; BG-056 findings from decision 0102.
Bring the Experience wrapper's pre-execution checks into the existing local
Foundations/Distribution pattern: exact lock fields, source/format/version/digest,
duplicate-field rejection, symlink rejection, strict manifest paths/digests and
complete inventory containing the checker. Reuse the small standalone pattern;
do not introduce an unrecorded helper or alter the vendored release.

Experience and Distribution launch their reference checker with PYTHONOPTIMIZE=0
while preserving the remaining environment. This explicitly selects assertions
in the child even when its parent runs with -O/-OO or inherits optimization.
The original environment and parent process are unchanged. Foundations already
uses explicit rejection paths and is unchanged. Success text, ignored arguments,
release pins and offline input locations stay the same. Experience malformed
input now follows the stricter short-diagnostic rejection paths; this is an
intentional developer-diagnostic compatibility change, not a new operator CLI.

Tests use synthetic private releases and execution markers: malformed pins,
changed/missing/extra files, malformed/unsafe/duplicate manifests, missing checker
and symlink roots/files must reject before invoking the checker. Positive and
deliberately failing assertion checkers run across normal, inherited 1/2 and
parent -O/-OO modes for both wrappers. Preserve real pinned-release stdout and
verify all release bytes before/after. Run the aggregate gates. No target witness
is needed for this host verification-only change; no sibling/native edits.

This is static filesystem validation, not protection against concurrent hostile
mutation between verification and execution. Standalone tool duration/output
bounds and other legacy CLI conventions remain separate gaps. Independent
review, complete tool closure and remaining manuals/API work remain BG-056.
Evidence: docs/evidence/standards-wrapper-validation-2026-09-06/README.md.
