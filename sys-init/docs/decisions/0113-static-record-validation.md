# 0113 — Strict static record validation

BG-056 implementation slice. Validate both static settings and boundary records
before tool lookup. Read at most 1 MiB plus one byte per JSON input; reject
invalid UTF-8/JSON, duplicate keys, non-finite values and excessive recursion.
Require exact schema/fields and field types, bounded strings/lists, lowercase
SHA-256, normalized relative paths and positive non-boolean site line numbers.
Metadata is syntactically checked, not authenticated. Existing maintained record
bytes, tool arguments, native inputs and published release pins stay unchanged.

Malformed records become ValueError and the existing structured fail/exit 1
contract. Test actual reader rejection before any command call, including
missing/wrong fields, duplicate keys, deep/large JSON, malformed sites/paths,
and metadata errors. Update minimal synthetic boundary fixtures to the now
required complete shape. Full static and aggregate gates must pass.

Ordinary-file/parent-symlink policy, atomic reads/settings identity, semantic
argument authorization and transitive tool closure remain BG-056 work. This is
trusted local configuration validation, not an external ingestion API or shared
standard change. No sibling or native execution change is authorized.

Validation: all 22 focused static cases and all ten gates pass in
out/checks/run-d8akh8py. The retained initial depth failure prompted an explicit
32-level bound rather than relying on Python parser recursion behavior. Current
settings/boundary bytes and all 24 native inputs remain unchanged. Manual lint
is clean after one retained blank-line formatting correction.
