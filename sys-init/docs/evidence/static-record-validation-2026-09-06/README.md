# Strict static record validation evidence

Decision 0113 validates static-tool settings and native-boundary records before
tool lookup. Exact schema/fields/types, normalized relative paths, lowercase
hashes and bounded collections/strings reject malformed values. JSON reads are
limited to 1 MiB plus one byte; excess input, invalid UTF-8/JSON, duplicate keys,
non-finite constants and nesting beyond 32 levels reject. Ordinary malformed
records now follow the existing failed JSON/diagnostic/exit-1 path. Maintained
record bytes and successful output schema remain unchanged.

All 22 focused static tests pass: eleven existing tool/static cases, five prior
record cases and six new validation tests. New cases exercise maintained-record
acceptance, eleven malformed settings variants, eight malformed JSON inputs,
nine boundary variants, structured missing-field failure, and depth/quoted-
bracket boundaries. Invalid reader paths assert no command invocation. The
settings-only tests stub boundary checking to isolate validation; boundary
cases use the real boundary reader. They do not claim malicious-tool confinement.

The initial depth test found that this Python accepts a 2,000-level JSON value
without RecursionError. That failed attempt is retained. An explicit 32-level
scan now supplies a host-independent bound; quoted/escaped string characters
are excluded and 32/33-level cases pass. Existing minimal synthetic boundary
fixtures were updated to the complete required schema. Empty inventory rejection
now occurs during validation, before source-membership comparison.

All ten repository gates pass in out/checks/run-d8akh8py, retained in validation/.
The real static gate uses unchanged maintained settings/boundary bytes and the
same tools/arguments. All 24 native inputs remain unchanged. No native, sibling,
release pin, vendored bytes or historical evidence changed; no new native
execution is claimed. Toolchain/native compatibility is unchanged in this scope.

Updated manual lint and 78/60-column/HTML rendering pass. The initial blank-line
warning is retained under manual-initial/; only that manual formatting was fixed
after full checks. Independent technical/reader review, HTML visual review and
installed target reference lookup remain open.

Metadata is syntactically validated, not authenticated. Compiler arguments remain
trusted maintainer policy. Ordinary-file/parent-symlink policy, blocking read
behavior, standalone settings/inventory identity and transitive tool closure
remain BG-056 follow-ups. Bounded parsing does not create an external ingestion
API or an atomic filesystem snapshot. Published release pins remain fixed.
