# 0221: Explicit root-path owner selection

2026-10-23. Implementation plan before changing owner/build behavior. Root STATE
owns integration; existing AENFS005/AENMX010/ABI31 bounds remain authoritative.

Requirement: consume the tested read-only AEFP0001 path candidate through the
actual owner and linked shell, with matching explicitly selected producer/protocol/
router/C codec. Default AEFD0001 remains exact; never auto-detect or negotiate a
variant. Dispatcher uses the same compile-time magic as its bound FILE handler;
foreign magic fails the existing unknown-protocol/fail-stop path before effects.
Library selection mismatches must reject before a composed image can be admitted.

C libc opt-in allows canonical root paths only under AEFD_PATH_WIRE; its existing
component calls retain delegated-root semantics. This does not claim POSIX CWD,
normalization, symlinks or change getcwd ENOSYS. Keep O_RDONLY/O_CLOEXEC and explicit
write/create/append rejection. Context/native exclusivity, pointer range, workspace
and complete-frame cleanup obligations remain unchanged. No new unsafe/native ABI.

Use --paths only on separately selected host/build profiles. Record it in producer,
provider and owner reports; require exact agreement before linking. Do not select
such a shell with a component handler or claim previous whole-owner measurements
for it. No runtime fallback, additional service/channel/worker/FD/handle or memory.
Keep owner49152 code/8192 stack/data,35MiB/seven domains/twelve channels, storage
9 mutations/96 requests, writer60s6000/readers30s3000 and64KiB capture unchanged.
The interactive writable-home policy is separate; do not grant system-root writes.

Focused checks: actual producer inheritance/retirement/initialization controls and
native library; actual C libc bindings default vs selected path acceptance/error
and unchanged fork/exec/readiness; compiled dispatcher identity/framing/partial
transfer/drop/unknown controls; real complete owner code/data/stack measurement.
The historical same-wire byte differential remains default-only; it cannot assert
AEFD0001/AEFP0001 byte equivalence. Selected protocol compatibility is instead
covered by exact C/Rust/C and opposite-version denials in userland evidence.
Any missing required profile check or actual fit remains blocked coverage; no
native guest runs under this plan or the consumed three-case approval. Fresh
matching inputs/exact workload and explicit persistence disposition precede native
qualification. Preserve failures; no automatic retry or relaxed bounds.

Simplicity/security: carry one explicit protocol identity through the existing
client/owner chain instead of another path service or magic autodetection. The
protected state is each authenticated process/file binding and intermediate AF07
handles; untrusted pathname/version cannot create authority. Existing cleanup/
source retirement owns partial outcomes. This adds no fields or new trusted
process. No broad refactoring, new dependency, standards pin or ownership change.
Technical review is by the implementation agent; independent/native acceptance
remains pending. Keep compact results/commands/hashes and remove owned outputs.

Commands (from system root): current fresh-input recipe and qualifier in NATIVE-C;
new path-specific host/build flags are documented alongside their affected tools
before execution. This plan does not add execution authority or claim release fit.

## Native read probe, before implementation

A separate --path-probe helper body requires --exec --paths. Preserve the default
helper and script. The existing fixed exec-wait script executes the selected immutable helper
with the existing status argument; its body opens /zstd O_RDONLY|O_CLOEXEC, reads
exactly16 bytes, seeks to original780248-byte EOF, observes two zero-byte EOF reads,
closes and writes AF07-READ:ok plus newline (13 bytes) before returning7. Errors
return distinct non7 status and stop qualification. This tests real path/read/FD
and context routing, not full content correctness; independent pristine/recovery
readers still verify the whole original file/hash/media. No bytes are executed
from disk. The separate helper retains initialized TLS/application-ready entry,
ELF/WX/parser/resource checks and the current immutable exec-image authority.

Host checks execute this exact body against bounded callbacks for complete and
failed/partial outcomes/order/cleanup before target linkage. Target helper/shell
admission pages must be measured, bound to input receipts and checked exactly;
do not relax resource limits or assume old measurements. Kernel code unchanged.
Prepare only pristine reader → selected writer → recovery after strict success,
with existing watchdog/capture/resource/media/cleanup rules. The consumed9-guest
approval is insufficient for this changed composition; explicit fresh disposition
precedes the prepared --run. No automatic retry or replacement trial.

## Host/build outcome

Complete selected owner40640 code/7504 resident/8000 conservative stack fits the
unchanged49152/8192/8184 limits; default owner39376/7504/8000 remains exact.
Selected producer38/15 controls, owner56 tests plus actual controls, C fork1010/
nine controls/exec/readiness,78 libc cases and ten read-probe outcomes pass.
Default producer37/owner57 including old same-wire differential pass in the fresh
input rebuild. Two initial C mock failures remain retained, not native defects.
All30 focused input/qualifier methods pass; current Python only, minimum runner
and independent review pending. Exact candidate images are
[prepared](../../../docs/evidence/af07-root-read-2026-10-23/README.md); zero new
VMs. No CWD/dup2/home writes/persistent ELF/Zsh/ISO acceptance.

## Approved native outcome

The explicit one-sequence disposition now passes all three guests at unchanged
limits: helper7/parent0/engine0, actual read marker,21 cleanup rows,302 paired waits
and halt2020. Both readers verify all780248 original bytes; recovery preserves
stopped writer media/canaries; all VMs stopped. Zero FS mutation requests, metadata
import/export writes possible, no retry/extra guest. Compact result replaces
passing generated output retention. This is bounded native path/read/count/cleanup
evidence, not independent durability/Zsh/ISO acceptance. Approval is consumed.
[Exact results](../../../docs/evidence/af07-root-read-2026-10-23/README.md).
