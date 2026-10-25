# Native taskq bridge contract and object review

The proposed [native contract](../../NATIVE-TASKQ.md) resolves the next fixture's
bootstrap, allocator, synchronization, admission and stop/reap requirements. This
turn defines and checks the contract; it does not implement or boot a native bridge.
No upstream, kernel, sibling, release pin or runtime source was changed.

Fresh llvm-nm inspection finds 27 undefined symbols in the retained Linux/x86_64
taskq object. closure.json classifies every symbol exactly once and binds the
object, tools and original engine baseline. llvm-ar extraction verifies that this
object is byte-identical to its member in the linked libzpool archive. All 4063
original upstream files and static link archives still match the prior digest
inventory. object-header.log identifies this as an x86_64 relocatable object,
not a native Aether executable or full transitive symbol closure.

Commands use /opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-nm --undefined-only and
llvm-readelf -h on the retained lib/libzpool/libzpool_la-taskq.o; llvm-ar p extracts
that member from .libs/libzpool.a for byte comparison. The exact retained engine
root is zig-out/openzfs-x86-2026-09-06/work/zfs-71a9f9578616a90c3c14bb59629fb4d31bfd68d1.
The baseline source archive and tool closure remain in the preceding OpenZFS
receipts; this review installs nothing and does not run Linux or native target code.

Decisions: isolate TSD bootstrap with a recorded helper fragment instead of
starting/changing 64+4 system workers; propose a single-page taskq-only slot arena
subject to native layout proof; distinguish nonblocking rejection from required
allocation failure; use the parent as drainer to stay within two live children;
keep queue destruction separate from exact native stop/unmap/retire. The native
object/stack quota and four-admission limit remain unchanged. No generic allocator,
clock, scheduler or capability operation is added.

Current validation is import coverage/member/source identity plus host/inventory/
pin checks and local documentation links. Native compilation, layout assertions,
adapted CDDL-source review, runtime cases and consumer acceptance remain missing.
Older Linux and native pthread evidence is referenced, not rerun or relabeled as
bridge acceptance. The proposed C helpers/header must preserve upstream terms;
original bridge code remains BSD-2-Clause.

Validation passes: all 98 Python tests, Zig host checks, three immutable pins,
22-reference/28-group workflow inventory, new local links and diff checks.
runtime-identity.json verifies no runtime/build inputs changed since the preceding
taskq witness. review-inputs.tar.gz retains the exact proposed contract and inventory.
