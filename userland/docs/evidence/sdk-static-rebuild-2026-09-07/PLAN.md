# SDK-07 bounded static input/relink witness

Scope: experimental consumer input receipts only, no package-state registry,
recipe/update implementation or native execution. Verify SDK-05 final sources and
rerun its source-pinned startup link/denial controls. Capture baseline explicit
link inputs and commands. Add an unused member to a private copy of imported
libc.a; never alter the imported package or production adapters.

Expected: archive hash changes, old consumer input binding is stale before relink,
while an unrelated consumer with a disjoint input set stays current. A same-byte
copy is unchanged. Relink from the changed archive and rerun ELF/no-undefined
checks; link output should stay identical because the added member is unused.
Fresh input/command/artifact binding records the archive change despite equal ELF
bytes. Restoring baseline bytes restores its original fingerprint, not an implicit
package rollback. Preserve old/new receipts and command evidence. Negative control:
a checker using only artifact hashes misses the stale-input condition.

This is SDK-07 local static consumer evidence, not automatic package updates or
a full package reverse-dependency scheduler. Exact package-record changes and
selection remain pkg-mgr-owned. No new native compatibility or ASan claim.
Reuse pinned compiler/linker/ar/readelf/nm, clean env, private build root and
30-second owned-command bounds. All attempts retained; quality/whitespace checks.
Foundations O/E and quality TD/TC/TE/CC/CP apply; original BSD-2-Clause. Independent
review, package-update integration and SDK-08 native execution remain open.
