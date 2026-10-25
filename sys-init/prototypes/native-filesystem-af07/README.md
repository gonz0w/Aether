# Separate ABI29 AF07 filesystem activation candidate

Current2026-10-21: [Decision0193](../../docs/decisions/0193-af07-native-consumption.md)
consumes Aether's exact eight-guest native activation/readback/five-peer witness.
All876 input hashes and eight bounded selected oracles check locally. Sources,
original preparation and defaults are unchanged. The preparation/intake procedure
below remains historical; its native gate is now closed for this bounded slice.
Next [ABI29 client correction](../../docs/research/ABI29-BOOT-PARENT.md): the delivered
object candidate rejects the actual boot supervisor PID7. Full linked client,
AF07 FD/path/exec, matching dispatcher and real shell remain separate.


[Decision0192](../../docs/decisions/0192-af07-filesystem-owner.md) prepares the
existing small activation policy for the separately delivered AF07 engine.
This explicit compatibility copy preserves every byte of the accepted AF06
source/delivery. No runtime negotiation, metadata workload or framework is added.
Only policy wire selection changes from AFSRPC06 to AFSRPC07; the native wrapper,
linker and bootstrap/roles/region/budgets/ownership algorithm remain identical.
The four extra fault scenarios reject old/future greetings before dependent
admission and old/future disconnect replies before engine settlement/reclaim.

The engine is pinned in inputs.json to Aether's
fs-launch-af07-2026-10-21-v3 manifest
`e28d249b97d2e0a94c376190ec3f3839d50b6c1426cf788bab8f303fdb4084ac`,
ELF `9039e7b1d9a488076e3f8329b3666f39d85385f294d89954dd03df7c2df1753a`.
All30 dependency members were verified before/after preparation. METADATA16/root31
are the service's explicit selection, not new native grants from init. Init still
launches only the small selected c002 `p` process after live generation-bound root
readiness; it sends no filesystem mutations or metadata requests. That process
is not a shell, runner or loader. Import/export can change pool metadata.

Reproduce using the [original local preparation commands](../native-filesystem/README.md#reproduce-local-preparation),
substituting native-filesystem-af07 for native-filesystem and a fresh output root.
Use the same pinned Rust1.98.0/2024 and compiler-only adjacent library environment.
The [sealed preparation](../../docs/evidence/filesystem-af07-owner-2026-10-21/README.md)
records exact commands/tools, four compiling omissions, source/engine hashes,
strict lints/format and read-only structural inspection. Local preparation passes:
raw2072/ELF9080 bytes, scoped1096/4088 stack; no writable statics or indirect calls.

## Original Aether intake handoff (consumed by decision0193)

Consume preparation.json, inputs.json, four source files and owner.elf/owner.raw
from the new sealed evidence directory. Verify sha256.json and exact source/tool
closure; retain the original AF06 intake/defaults. Raw SHA256
`620939e5218df104586ff38ce843776696c70814efdd2180c0244e7defae08a7`;
ELF SHA256 `87598149c7a33307fffd3dc393f4cb87a04f635b40276f079943f93a904ebc03`.

Aether's current --metadata-engine selector intentionally rejects sys-init:
Aether must add explicit matching AENFS003/ABI29 composition/intake with this
exact AF07 engine, owner6, engine0, process1–5 and original block/endpoint grants.
Require fresh actual-owner positive activation/disconnect/export/ordered native
settlement and failed-peer controls (startup exit, malformed/version/generation
reply, failed terminal and reply closure). Preserve complete bounded oracles;
no inferred cleanup, replay or auto-restart after unknown outcomes. The current
engine-only three-guest approval authorizes no additional native campaign here.
No guest has been run, and producer engine success is not owner acceptance.

Following that witness sys-init must perform its own exact consumer review.
The [ABI29 shell/client/PID/FD/TTY and filesystem-backed boot handoff](../../docs/FILESYSTEM-BOOT-HANDOFF.md)
remains open. Old serial/AF06 recipes and all released standard pins are unchanged.
