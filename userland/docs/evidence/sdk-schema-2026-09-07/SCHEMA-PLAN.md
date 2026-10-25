# SDK consumed-field validation — UL-005 / UL-063

Validate the JSON fields this local startup harness consumes before using paths,
copying SDK payloads or running tools. Require objects, nonempty SDK inventory,
canonical relative stage/usr paths, absolute tool/import paths and lowercase
SHA-256 digests. Validate receipt probe/I/O/memory digests after receipt identity
verification. Unknown owner fields remain allowed; this is not a new package schema.

Risk/authority: malformed fields currently escape as TypeError/KeyError; SDK
inventory names are also used to form output paths. Reject absolute/traversal and
noncanonical components before any SDK copy. Do not infer trust from shape checks.
Retain current receipt/hash identities, private staging, command bounds and native
oracles. No shared format, sibling change, dependency or runtime implementation.
Applicable: Foundations I-01/02/E-01/05/06, quality CP-01/02 and TD/TE. Preserve
existing operational error stream/exit 1; no new public CLI contract.

Controls: table-driven invalid consumed types/fields/digests/paths at the actual
main entry point; require exact field-specific failure, incomplete summary, zero
process and copy calls. Include valid unknown owner fields and libc receipt
field controls. Prior harness must fail a structural regression. Rerun missing-file/
JSON and staged-copy controls, complete startup link and local quality gate.
Python 3.10+ syntax; actual interpreter only is qualified. Controls budget 60s,
link budget 5 minutes with existing 30-second process deadlines. All outputs under
build; preserve every attempt and source in docs/evidence/sdk-schema-2026-09-07.

Documentation: SDK README/coverage, backlog and STATE; independent review pending.
Resource limits for JSON reads, duplicate-key policy, hostile parent symlinks,
post-validation concurrent mutation and unavailable report storage remain outside
this bounded field-validation slice. No complete hostile-input or native claim.
