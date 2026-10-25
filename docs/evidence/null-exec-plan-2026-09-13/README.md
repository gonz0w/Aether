# Scoped null descriptor: exec preparation — 2026-09-13

Requirement: establish the smallest descriptor extension needed for unchanged
wait.sh. Dash backgrounds its child, closes FD0, opens /dev/null read-only, then
executes the helper. The parent's original input must remain separate. Add pure
four-binding exec preparation using the existing canonical sixteen-FD table.
This step does not wire an open route, publish a new bootstrap or run wait.sh.

Selection before code: retain the existing three-binding and five-binding pipe
entry points unchanged; add prepare_null using the same checked implementation.
Binding3 denotes a separately authorized null object only in the future null
profile. Table bytes are not authority. The owner must validate its actual handle,
caller connection, lifetime and holder counts before consuming the plan.

Forbidden: substituting original stdin for null, broadening the old three-binding
profile, authorizing objects from descriptor bytes, dropping a parent's holder,
mutating live aliases on denied exec, preserving CLOEXEC aliases, accepting invalid
flags/counts, or claiming host preparation proves native null I/O or consumer wait.

Aether owns the bounded fixture and enforcement; userland owns facade acceptance;
sys-init/package policies remain untouched. No kernel/ABI/SDK/pin/dependency/quota,
unsafe/FFI/assembly or runtime routing changes. All existing entry-point bodies and
call sites remain unchanged. Foundations E-01–E-08, local DEVELOPMENT and scoped
simplicity apply. Reusing the existing generic checked table transformation avoids
another descriptor representation; a broad descriptor/service refactor is not
needed. No consumed path is retired.

Tests: exhaust all null-alias descriptor pairs and CLOEXEC combinations; check
mixed original-input/null ownership, canonical record and count rejection, and
release of last aliases without mutation. Run existing host checks, Rust format,
a freestanding x86_64 no_std compile and semantic mutants proving the assertions
reject broken alias retention/release. No native profile consumes prepare_null yet;
no new QEMU acceptance or new matched phase-one source set is claimed. The prior
290-case native packet remains immutable. Next wire owner admission, open/EOF,
bootstrap and exec publication together in a bounded native profile with real
positive/denial/stale/rollback evidence before running unchanged background wait.

Additional compatibility check selected before execution: recompile all 88 prior
connection-owner recipes that import exec_fds and compare their raw image hashes
with the sealed 290-case qualification. Use new owned output paths and the same
Rust target/options. Identical images retain the prior native execution evidence
for those old paths; they do not test prepare_null, which has no native caller.
Keep every compiler log and compare against the sealed artifact index, not mutable
unpacked output. No target run or broad build is inferred from host success.

The first host run passed the Rust tests but failed the Python pipe wrapper's expected count: adding four descriptor tests raises its included total from23 to27. Preserve the complete failed receipt, old wrapper and failed pipe artifacts; update only that exact count and repeat host checks. This changes no runtime source or oracle semantics.

## Result

PASS: 11 descriptor tests, including 960 null-alias/flag combinations; all four
semantic mutants fail their exact named assertion. Freestanding x86_64 no_std
compilation and Rust formatting pass. The final host run passes all 100 Python
tests plus Zig and offline standards/workflow checks. The pipe wrapper includes
27 Rust tests; these overlap the descriptor tests and are not additional independent
coverage. The first stale-count host failure and its artifacts remain preserved.
The simplicity manifest and four members verify.

All 88 affected existing native-owner recipes rebuild to byte-identical raw images
against the sealed 290-case artifact index. Every log and comparison is retained.
No existing native execution behavior changed; no new QEMU run is claimed.
prepare_null itself is host-tested and target-compiled, not natively consumed.
The only source changes are its entry point/four tests and the pipe wrapper's count.

Reproduce descriptor tests through the existing `zig build test` command. The
captured check and compatibility scripts record exact tool commands and private
output paths; do not rerun them into this sealed packet. Current sources, the prior
input identities, failed host artifacts and raw comparison images are retained.
Missing native open/EOF/authority/rollback/bootstrap tests remain required coverage.

Next implement the dedicated null-owner and bootstrap/descriptor route, preserving
separate parent input and child null ownership, then qualify actual background
wait with its unchanged helper status7 and wait ok output. Independent userland
acceptance, writable /scratch, OpenZFS and R1 assembly remain open. No sibling,
kernel ABI, released standard pin or SDK was changed.
