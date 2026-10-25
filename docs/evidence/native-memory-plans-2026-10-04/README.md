# Constant-size native memory plans

Status: bounded qualification passes,2026-10-04. [Before-code scope](contract.md)
removes quota-sized stack snapshots while preserving complete preflight, owner
serialization and old mapping/thread semantics. Existing128/2048-page quotas and
public contracts remain unchanged.

Run the existing planner/memory/thread commands in [NATIVE-BACKING](../../NATIVE-BACKING.md).
The one-off receipts here are scoped evidence recipes, not a new SDK or supported
public entry point. No sibling or released standards pin changes are part of this
step. Larger physical backing, table/metadata geometry and full engine lifecycle
remain local work. Production entropy, SDK adoption, independent review and R1
assembly gates remain separate.

All10 planner tests and137 Python host cases plus Zig/Rust/offline pins pass.
Fresh target coverage totals181:25 default/large memory,112 pair/pthread lifecycle,
11 hardware entropy, seven hardware block, five native block, five origin, five
lifetime reuse, four native entropy and seven two-core cases. Old fault/permission/
FP/context/pin/quota/stop/replacement oracles remain. Plans occupy16bytes and the
free cursor32bytes on x86_64 at both supported quotas; no larger quota or latency
guarantee follows. [Implementation review](review.md) corrects the initial stack
rationale and describes the metadata-borrow obligation.

The nonadvancing first host control stalled and is retained as failed coverage;
the skipping cursor fails exact expected1/found2 TestExpectedEqual. The first
orchestrator counted the independently owned M4 root and is retained as a runner
failure. Its12/13-case memory receipts pass on final source bytes and are recovered
by the corrected ownership filter before the remaining suites run. No failed
attempt is removed or accepted merely because it exited nonzero.

Sealed SDK/source intake verifies1979+5037 archive members. Legacy maintained
suites use a private byte-identical evidence.json alias of build-evidence.json
and the pinned adjacent musl source archive; sealed SDK originals are unchanged.
Clang/LLD21.1.8, Rust1.98.0, Zig0.16.0, Python3.14.7, QEMU11.1.1/q35/qemu64/TCG
and exact commands/artifacts/source hashes/times are recorded. Native builds
180seconds, VMs30seconds and owned teardown3seconds; forced teardown fails.
Every owned archive member is read back before verified duplicate cleanup.

Next prove physical/RW-NX/readonly/supervisor/detach aliases under actual fresh
roots before binding external RAM to one native service. Default/large arenas
remain128/2048 pages. Full engine worker/backing admission, identity/configuration,
feature closure and startup/fini/restart still precede R1 filesystem/package
composition. These are local prerequisites, not an external companion block.
