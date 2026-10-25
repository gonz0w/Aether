# UL-007/081/082 tagged startup binding proposal

Pre-code scope: sys-init decision0196 prepares actual file exchange but still
needs the shell's explicit startup/file/pipe/console binding contract. Legacy pipe
selectors3–6 overlap AF07 private file FD3–15. Add a separate opt-in AEFDT001
startup snapshot decoder and class-preserving lookup. Do not modify old AEFSH001,
installed-table bytes, linked shell/SDK or sys-init policy. New snapshot is a local
candidate for affected-owner review, not an accepted native startup API.

One128-byte snapshot:64-byte header with magic, exact externally trusted nonzero
file-channel generation, count16 and five reserved zero words; then16 four-byte
records {kind,selector,cloexec,reserved}. Kind0 empty requires all zeros; console1
selector0–2; pipe2 selector3–6 matching existing bounded pipe profile; file3 selector
3–15. Flags0/1; reserved0. Logical FD is record index0–15, independent of selector.
Stream aliases may share selector; file selectors are unique per process view,
requiring actual remote dup for a second local binding. No remote handle can be
silently lost into a second local alias. Shapes/labels confer no native authority.

Decode into temporary bounded state; publish only after exact length/version/
generation/count/reserved/entry and uniqueness validation. Bad snapshot leaves
output unchanged; bootstrap caller must stop rather than continue a prior map.
Lookup binds expected generation again and preserves the tag. Absent FD differs
from malformed/stale snapshot. No allocation, close/dup/flag mutation, I/O, native
cleanup or successful unsupported operations; consuming owner must validate actual
endpoint/process/selector rights/lifetime and replace, not duplicate, old table.
No automatic4KiB storage. No whole native fit claim or cross-project acceptance.

Simpler alternative: classify by integer range. Invalid because pipe3/file3 overlap.
Reuse existing little-endian codec helpers and fixed sixteen-slot startup geometry,
not a generic handle framework or new service. Remove no accepted old wire now;
this specifies a replacement table for an explicit future profile. Full lifecycle/
routing/failed-exec/immutable exec and native resource placement remain follow-ons.

Pin exact C-client9 source dependency/codec, compiler/formatter/resource/SDK headers,
UBSan runtime and owned helper before use. Host C17 strict diagnostics/format/UBSan,
actual minimum/current Python, owned60s compilation/30s tests/16MiB streams and
clean environment. Tests cover all incomplete lengths, legacy/mixed frames, reserved/
flags/kinds/ranges/generation, duplicate file vs permitted stream alias, output
nonpublication, logical-vs-source collision and stale lookup. Compiling omissions
must fail specific assertions; retain every attempt. Run local quality/syntax/
whitespace; independent reader/owner and native gates stay open.

## Implementing-agent assessment and outcome

The candidate distinguishes logical descriptors, source selector and class before
any consuming dispatch. Decode rejects exact-length/version/generation/count/
reserved/flag/range failures and file-selector duplication before publishing its
fixed bounded temporary. Console/pipe alias labels remain permissible; no local
file alias can be mistaken for an independently owned remote descriptor. Output
on failure is untouched, and the consuming bootstrap must stop on required decode
failure. No automatic fallback/resynchronization, source calls or state mutation.

Lookup checks exact nonzero expected channel generation, FD bounds, presence and
selected record shape, then returns the class intact. Success is exactly1, absent0,
malformed/stale -1; consumers must not treat nonzero as success. The map must be
successfully decoded and immutable under serialized C access. Arbitrary mutation
of caller-owned C state is outside its validation guarantee. Pointer ranges are
valid/disjoint. The bytes do not prove admitted process identity, actual remote
FD existence, stream refs/generations/rights, immutable exec or native authority.

Both actual interpreters qualify identical source/checker inputs:65951 host cases
and five assertion-specific compiling omissions. Strict C17 diagnostics/format/
UBSan pass. Complete pinned client/codec/tool/resource/runtime and66-header host
SDK closure verify before consumption and recheck afterward. Raw commands/limits/
environment/source/binary/log/owned-cleanup evidence retained; no suppressions.
No baseline/setup failures occurred; intentional semantic failures remain visible.
No host IPC/service, native object/link/fit/runtime or selected shell profile.
Existing facade/live-service evidence is unchanged and reused in original scope.

Both exact owned roots were archived and every regular file hash/size streamed
back before removal:973797 logical bytes removed,44112 archive bytes retained.
Physical reclamation not measured. Candidate/previous dependency/evidence seals
and member hashes verify; selected source/contract equal maintained files. No
unrelated roots, immutable releases/pins/wires, native limits, sibling files or
source deliveries were removed/changed. Local quality/syntax/whitespace pass;
full runtime/audit/reader/publication remains NOT RUN.

Updated contract/architecture/acceptance/backlog/current evidence and contributor
coverage/review/output exception. Intent unchanged. This is implementing-agent
review of a local proposal, not sys-init API acceptance or independent sign-off.
Remaining: consuming-owner reconciliation, explicit shell startup/table replacement
and routing/mutations without duplicate live ledger, actual native binding/copy/
failed-exec preservation, immutable executable admission, complete fit/dispatcher
and native commands/errors/cleanup/fresh boot. Full UL-007/081/082/M3/R1 stay open.
