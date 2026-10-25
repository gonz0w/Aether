# Native SDK error guards — UL-003 / UL-015 / UL-081

Scope: correct two reproduced musl1.2.6 native error paths in the maintained
native-C build recipe. Preserve upstream style/terms, native interrupt transport,
existing SDK pins and immutable prior deliveries. No kernel/sibling edits.

Applicable O/I/E and approved TD/TC/TE/CP rules require honest error identity,
source-pinned experiments and distinct object/link/native evidence. The caller
retains its buffer on an actual rejected clock call; sysconf must return-1 with
provider errno before reading a rejected sysinfo result. Unsupported providers
remain unsupported. Other sysconf branches and real time/capacity semantics are
outside this correction. No authority, recovery or ambient host resource added.

Plan: anchored source patches with exact upstream identities; fresh source build,
optimized replacement-source controls for denied and successful raw providers,
then actual native ENOSYS probes and baseline-broken semantic controls. Record
commands/tool hashes/deadlines/cleanup under build/. Keep every failed attempt.
Use the existing bounded process helper unchanged. Run quality gate and syntax.
Documentation: native-C README, STATE/BACKLOG and this review/evidence packet.
Independent reviewer and reader walkthrough remain pending; no SDK promotion.

This is a routine error-guard fix: direct return checking is the smallest change.
Zero-initialization alone would conceal a failed provider and is insufficient.
No existing compatibility path is removed. A matched candidate may be consumed
by Aether, but does not authorize engine execution or supply time/entropy/storage.

Actual implementation review: agent inspected both upstream paths, errno conventions,
exact anchored patches and optimized native/semantic controls. Only two of the
archive members changed. Independent technical/reader review remains pending.
Quality gate (including all three standards checks), syntax and whitespace pass.
Candidate seal: f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc.
