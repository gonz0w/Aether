# Development source closure — 2026-09-06

Scope: HR-06 local development snapshot, not a public release candidate. The oracle
is exact input file bytes/modes plus existing host fixture and compiler/manual
semantics. Generated roots must not enter the archive; changed content, missing
inputs, links and extraction differences must not pass.

The accepted archive contains 3,207 files. Two assemblies produced SHA-256
`94d7d3a2b64459d22fbd897158bf3a5723ca191b4cdc19ec7fd9d2fae78529c2`.
Host tar extracted all files with matching bytes and modes. The retained archive
and extracted tree are under
`/private/var/folders/2k/hbwvd2qn4cb988kpjk1wcn800000gn/T/pkg-source-snapshot-2se07t40`.
input-files.json binds the exact dirty-checkout inputs; result.json identifies the
platform, scope and archive. tools.json records installed tool versions where
available and executable hashes. No tool installation was performed.

From extracted/pkg-mgr, `sh tests/check.sh` passed all sixteen fixtures, all three
pinned standards checks, whole-shell lint and watchdog controls in 143.207 seconds
under the 600-second deadline. Live minisign fixture verification ran and passed.
suite.log and result.txt retain this observation. The separate
`python3 tests/check-manuals.py --render-required --binary-example` passed all three
manuals, host lookup and actual bytecount build/register/export/import/execution.
manual-check.log, manual-result.json and manual-binary-example.log identify that run.
The selected extracted source inputs remained unchanged after both checks.

negative-controls.py records eight small controls in negative-controls.json:
changed content, changed source before assembly, changed mode, an extra file,
a missing file, source/extracted symlinks and a missing source directory all reject.
These controls test the verifier independently of the round-trip success path.
The first assembly used USTAR and failed on a historical path exceeding its name
limit. initial-ustar-failure.log and initial-input-files.json preserve that attempt;
PAX supports the actual paths without renaming historical files.

This is the owning task's relocated host witness. Sibling projects are not required
by these command paths, but network denial and hostile-process/filesystem confinement
were not tested. It is not an independent review, a pinned tool installation recipe,
a native package-manager test or a publication approval. Documentation history and
optional recipe content still require selection/license review for public release.
The tar is retained locally and was not tagged, uploaded or signed.

The snapshot predates this evidence bundle and the final tracking/documentation
updates; their later development/standards/whitespace checks are retained separately.
Do not present this archive's hash as the identity of the subsequent whole checkout.
