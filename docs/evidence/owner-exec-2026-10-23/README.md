# Guarded owner exec/readiness checkpoint —2026-10-23

[Decision0213](../../../sys-init/docs/decisions/0213-owner-stack-exec-readiness.md),
[contract](../../native-fs-owner-stack-v1.json), [results](results.json).
Original sources BSD-2-Clause; third-party pins/notices unchanged.

The separate AENFS005/AENMX010/ABI31 owner has8192 guarded stack bytes and49152 RX
code allowance, within the same128-page partition. Measured complete bounded owner:
39376 code (9776 headroom),3408 Runtime+4096 workspace of8192, conservative whole
call-path8000 of8184 usable. All existing time/authority/workload/cleanup bounds
remain. Actual immutable-helper commit receipt precedes CLOEXEC/rebind/publish;
startup requires actual live readiness. Unknown/partial progress stays closed.

Passing focused checks:57 prior+four private exec tests/seven schedules, three new
compiling exec omissions, eight prior controls/two borrow denials, actual C608-byte
frame decoded by Rust. C80 exec/readiness cases/two omissions; stage1010/nine
controls, frame5847/libc78 each. Complete shell/helper static links and unchanged
ELF/TLS/WX parser pass. Actual selected geometry, Debug and direct ReleaseSafe
kernels build. Mapping/guards/zeroing/old-profile/parser/selector controls pass.
All nine current sys-init offline stages pass across initial aggregate and focused
continuation after inventory correction; userland quality and workflow pass.

The broad checkpoint is **not passing**:162 Zig tests pass;924 Python tests finish
with seven failures/four errors. Eighteen focused tests subsequently pass after
correcting option classification, an extracted-body scaffold and component-file
copying in the workflow fixture. Four old AF07 intake methods remain blocked by
prior live-source hashes (owner_stack.py/native_fs_session.zig); wrong-wire denial
is intercepted by that earlier drift. No old seal/pin or intake guard was changed. The base HEAD already differs
from those two historical source pins; this drift predates the current stack/exec
batch, as verified from Git blobs without running old source.
All failed stack/decoder/C-header/invocation/inventory attempts remain recorded.

No guest or native persistence qualification ran. Prepare a fresh matching input
chain and selected native harness, then obtain fresh runtime disposition under
OPENZFS-FEASIBILITY's existing rule. Host doubles and static links do not establish
native authority/permissions, export/recovery or independent acceptance. Persistent
ELF loading, writable public descriptors, packages, Zsh/TTY and ISO remain R1 work.

Results retain top-level commands, exact build argv, source/tool/artifact digests,
child outcomes and short failure diagnostics. No binary, SDK, source-tree, disk or
archive bundle is retained. Historical image-acceptance inputs remain dependencies,
not newly generated evidence. Source manifests and final compiled raw identities
were checked before disposal. Root STATE owns next action.
