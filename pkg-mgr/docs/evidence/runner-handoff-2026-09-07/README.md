# Runner handoff and source-policy regression

2026-09-07 UTC. The development source snapshot omitted SECURITY.md even though
README/CONTRIBUTING and the development checker now require it. The fix adds that
required source input; it does not change a released archive or release pin.

Oracle: the security policy's exact bytes are included in the source manifest and
extracted tree; omission fails assembly. A miniature isolated regression must fail
against the old source list and pass against the corrected list. The real snapshot
must repeat byte-for-byte, verify host-tar extraction, and execute the full normal
host suite from its relocated tree. Missing policy, broken source closure, skipped
required checks or false target/remote claims are forbidden outcomes.

The snapshot result and input manifest identify the large source archive retained
outside Git. The handoff is private development material, including exact existing
uncommitted Origins inputs and historical evidence, not a public release artifact.
No source/tree cleanup, sibling edit, release-pin update or remote transfer occurs.

This directory retains regression results, actual snapshot/relocated-suite outputs
and final checks. The source list change, runner handoff and evidence are scoped
locally. Linux/VM qualification, Forgejo configuration, scheduling, evidence upload
and actual operator review remain pending until performed on a supplied destination.

Attempt 01 assembled successfully but the relocated suite failed: README links
.githooks/README.md, whose tree was absent from the archive. Its original receipts
and failed log are retained in attempt-01; its “prepared” receipt predates that
failure and does not qualify that archive. The corrected oracle also requires the
hook tree and exact documentation bytes; a missing hook tree must reject assembly.
Hook installation remains explicit and outside snapshot assembly.

Attempt 02 passed: 6,317 source files, identical repeated archives, exact extracted
bytes/modes and the full normal suite (exit 0, 212.5 seconds).
The post-suite input inventory remained identical. The watchdog receipt is retained.
The hook omission regression fails against the security-only fix and passes with
both required inputs. See handoff.json for the locally retained archive and digest.
Final planning/results documentation was added after assembly; the archive identity
is its recorded manifest, not the eventual commit. No executable input changed
after qualification. This is a relocated witness on the existing host, not a new
VM witness or scheduled run. All three release pins remain unchanged.
