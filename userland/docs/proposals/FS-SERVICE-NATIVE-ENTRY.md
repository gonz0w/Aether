> Historical2026-10-18 proposal: current Aether Rust-write/recovery results clear
> its timeout/callback gate. The separate new [transport handoff](FS-SERVICE-TRANSPORT.md)
> supplies a bounded service entry and the current writable+IPC integration gate.
> The sealed old delivery and historical evidence below remain unchanged.

# UL-082 private filesystem native entry proposal

Status: concrete producer integration proposal, not adopted. Owner: Aether for
engine/build selection, Aether-userland for Rust policy/bridge/callback. No sibling
files/messages, public opcode, shared standard, SDK pin or quota is changed here.

## Current gate and review inputs

The Rust bridge/policy/callback now compile for x86_64-unknown-none and partially
link with the actual private zpl-write.c implementation. Six C bindings resolve;
ABI drift and omitted write symbol reject. This is not an engine ELF/ISO/guest.
[Current evidence](../evidence/filesystem-bridge-2026-10-18/README.md) includes a
pinned private Rust-object delivery and [callback header](../../experiments/filesystem-service/native-probe.h).

Aether's current repeated-write guest fails its30s watchdog before either write's
progress/terminal/cleanup is known. The reader never started. Its newer probe
source also differs from the historical single-write pair source base; a moving
probe must not be treated as matching old acceptance. [Captured blocker](../evidence/filesystem-bridge-2026-10-18/owner-blocker.json).
No new persistence guest, retry, watchdog increase or second transaction is
requested/authorized by this proposal. Renewed owner human disposition is required.

## Proposed owner selection

Add an explicit build-only opt-in selection for this exact private delivery.
Preserve default reader/writer objects and readonly wire/rights byte for byte.
Do not link the old C one-write body and invoke it as well as the Rust writer.
Verify the delivery manifest/members, target tool/core identities, original six
C origins, UTC-v3 archive, actual code/controller/ISO readback before execution.
The opt-in selection owns all modified builder/origin/fixture controls in Aether;
userland does not duplicate its whole engine/kernel/boot harness here.

Callback: `int aether_fs_policy_write_probe(struct spa *, aether_fs_probe_result *)`.
The proposed header's three u64 words are TXG, staged bytes and progress state:
0 unassigned,1 committed,2 synced,3 uncertain/malformed. Positive errno can accompany
committed or synced progress. State2 is not a public durability acknowledgment.
Callback initializes valid output before rejection, retains committed progress and
preserves successful write progress if subsequent readback fails. No replay.

Before callback: register original accounting before import, retain one exclusive
writable SPA and live shared UTC anchor, and an unused one-transaction observation
slot. The configured dataset/file remain the known bounded fixture; client requests
cannot provide pointers, object IDs, endpoint labels, dataset or UTC fields.
The Rust callback opens/closes its own single context; no other C context or
borrowed SA mapping may coexist across it. No import/export/property mutation,
reentry, thread transfer or code unload occurs before context close and full drain.

Preserve the original independent pre/post full-file SHA/metadata oracle and
fresh READ1 VM recovery. C owner pre-scan must close its context before Rust opens
its own; post-scan opens only after Rust context close. Preserve ordered transaction/
provider completion, context close/drain/export, all21 cleanup checkpoints, three
terminal0 owners/live0/reclaims3, outer media guards and confirmed QEMU stop before
media inspection. A16-byte local alias read is not a substitute for these oracles.

Workload remains one overwrite at offset37, length16, byte(i)=i*17+91 modulo256,
file780248 bytes. Fixed test peer labels71/72 are internal policy controls, not
native endpoint authentication. This does not implement/qualify operational WRITE
IPC or sustained service. One nonempty provider call per context stays enforced.

## Acceptance and disposition

First build-only: exact source closure/current producer receipt, six C and actual
Rust/UTC origins, omission/duplicate/ABI/type/borrow controls, structural loader,
unchanged default artifact comparison and new Rust/full C stack/resource review.
The local C write frame4456 is only a compiler frame, not full native stack fit.
Current delivery objects are relocatable and still require the original engine,
matching runtime/UTC/core and owner panic-abort boundary. Do not boot them alone.

After resolving the owner failure gate and explicit disposition, one guarded
fresh writer/fresh readonly recovery pair with the exact reviewed composition.
Stop/report any missing marker, unexpected exit/stall, partial/unknown progress or
uncertain cleanup; never retry, reset retired identities or widen limits. Retain
all failures and media/retirement known/unknown. Independent consumer acceptance,
authenticated transport/reply-loss retirement, sustained writes and remaining
filesystem mutations/runner/packages/sys-init assembly remain UL-082/M3/R1 work.
