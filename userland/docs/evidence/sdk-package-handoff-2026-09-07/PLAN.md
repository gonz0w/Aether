# UL-005 SDK/package handoff review plan

Scope: local documentation proposal and read-only verification of the existing
native SDK against its retained native-stdio-files pin. No recipes, package-state
machinery, sibling writes, staging, dependency fetch or runtime changes.
Foundations O/I/E, candidate PS, Distribution TR/B/SV and quality TD/TE/CP/DW/DS
apply. Preserve source licenses and immutable pins. Record consumer contract
hashes and current SDK modes/types, source/compiler identity and mismatch results.

Acceptance for this slice: exact pinned SDK regular files match; document
build/host/target distinctions, static rebuild closure, modes/link limitations,
owner questions and concrete positive/negative staging tests. Existing pkg-mgr
host package/bounded boot evidence is inspected, not rerun or generalized.
Run local quality and whitespace checks. Independent owner review and actual
pkg-mgr staging remain required for UL-005 completion. No runtime claims.

## Review-bundle preparation extension

Prepare an inert owner-review directory under a new private build root: verified
231 SDK inputs, pinned musl archive/COPYRIGHT and original build/patch/command
receipts. This is source/material copying, not package staging or registration.
Verify before and after copy, require regular non-hardlinked inputs, preserve
ordinary modes, and retain a sorted manifest of every copied file. Source drift
must abort. Include exact reviewed pkg-mgr contracts, snapshot this proposal and
hash the preparation script. No binaries execute and no sibling writes occur.
The directory is not a pkg-mgr binary bundle; SDK-01–08 remain NOT RUN.
