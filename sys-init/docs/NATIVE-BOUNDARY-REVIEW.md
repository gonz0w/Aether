# Native boundary review

2026-09-06; BG-056 / decision 0096. This source review inventories first-party
Rust unsafe/entry sites and C assembly boundaries. It is not an independent audit,
a proof of soundness or a POSIX compatibility claim. No native bytes change.

The machine inventory is `docs/native-boundaries.json`. Each source is bound by
SHA-256, with exact site text and line. Revisit a record when its source, producer,
compiler/flags, architecture or lifecycle contract changes. Historical evidence
must not be rewritten to satisfy a new review.

| Boundary | Obligations and inspected evidence | Disposition |
| --- | --- | --- |
| adapter.rs trap | x86-64 register contract; RAX/RDX/R8 results and RCX clobber; integer handles confer no authority. The retained protection.S entry saves general registers, restores r11 and returns through iretq. No nomem/readonly/pure assertion is made. nostack relies on the privilege transition using the kernel stack, not client stack scratch. | Source-level review; full instruction/frame-handler and compiler audit remains required before broader ABI claims |
| adapter.rs launch | repr(C) Startup has two u64 counts and eight 32-byte text fields; initialized storage lives through the synchronous trap. Mode length <32 leaves NUL space. Kernel must validate/copy startup and consume the writer only on success; counters change after decoded success. | Existing native launch/denial witnesses support the bounded contract; pointer validity must not be inferred from a numeric address |
| adapter.rs read | A live mutable one-byte local is passed for length 1; initialized before trap and inspected afterward. No escaping pointer or asynchronous ownership is accepted. Pending/EOF/one-byte outcomes remain distinct. | Existing read/EOF/denial cases; kernel copy-boundary proof remains producer-owned |
| adapter.rs handles and cleanup | Copy wrappers are references to kernel identities, not independent ownership. Counts are bookkeeping under the single-owner fixture and kernel duplicate/stale rejection. Failed operations preserve counts; release clears only after success; stop is not reclaim. No Drop invents completion. | Bounded fixture assumptions, not a reusable thread-safe ownership API; widening callers/reuse requires review |
| init.rs entry attributes | Unique exported _start in the separately linked init image, .text.entry selected by owning linker, six integer bootstrap arguments, no_std and abort/no unwind. Profile gate distinguishes ABI6/15. | Build/loader contracts are prerequisites, not supplied by an extern C annotation |
| service_worker.c native | Fixed-register operands and memory clobber; initialized one-byte ready buffer remains live for synchronous copy. argv strings and auxiliary writer originate from the pinned startup contract; C11 TLS is tested by its tag. | Exact worker ELF and native cases are retained; GNU register/asm and uintptr_t conversion are x86-64-specific, not generic POSIX C |
| Intentional ud2 and completion loops | Fault probes deliberately terminate the worker/owner. Non-returning paths require the pinned fatal/trap behavior. They test kernel containment and cleanup, not recovery performed by the dying process. | Fixture-only; never repurpose as ordinary input error handling |
| Older lifecycle/I/O Rust and C probes | Inventory preserves every textual unsafe, entry and assembly occurrence. Each separate profile has its own loader, register and producer history. | Inventory coverage only; do not extend the ABI6/15 source review to older profiles without their exact producer/target audit |

The current adapter's public Rust wrappers still rely on trusted caller discipline
and kernel enforcement. Mutable method access alone does not make copied handle
values affine or establish ownership after another caller uses one. Generation
exhaustion and partial cleanup stay with the existing domain algorithms; this
review introduces no replacement handle type or resource-reset API.

No `allow(...)`, `noqa`, `Wno-*` or `cap-lints` suppression was found by the recorded
search of active first-party native/model/tool/test source. This is a textual
inventory, not a complete compiler-option or generated-source suppression audit.
The host history harness's `dead_code` warning for shared methods not used in that
crate remains visible; no blanket suppression is added. It is not a failed Clippy
rule or evidence that those methods are absent from other consumers.

Outstanding before full CR-02/CE-02–07 acceptance: complete the older-profile
producer checks, per-call native register/frame preservation and copy validation,
C/libc failure paths, Python path/process/descendant audits, and actual independent
technical review. BG-033/048 own unresolved parent/session/recovery contracts.
No critical defect is waived by listing these gaps. This is a local review record,
not permission to broaden runtime authority or an assertion of full compliance.

Decision 0112 adds the [field-level record reference](STATIC-RECORDS.md) for
static tools, boundary inventory and results. It separates enforced checks
from descriptive metadata and records strict parsing/identity/ordinary-file
gaps under BG-056. Five additional record-contract tests cover source scope,
byte accounting, path rejection and textual/duplicate boundary behavior.
The implementation and current settings/inventory bytes are unchanged.


## ABI29 filesystem owner — decision0190 / 2026-10-20

`prototypes/native-filesystem/init.rs` is new original opt-in code. The unique
static `_start` validates six scalar bootstrap arguments before effects, with
no_std/panic-abort/no writable statics and its owning RX linker. The interrupt
wrapper uses explicit rax/rdx/r8 results, rcx/r11 clobbers, fixed scalar inputs and
no nomem/preserves_flags claim. Region24-byte, argv272-byte and <=16-byte transfer
buffers are live synchronous typed borrows; no pointer may escape. No external
caller can invoke this as a safe general native API. The kernel still checks
holder, direction, generation, role and actual bounds.

Source review matches engine admission0x20008, region delegation0x27005, reserved
channel factory0xd002 and process0x23000/program0xc002/slot1 to the producer
contract. Crucially0x20001 returns terminal exit_status+1 in rax, retained readiness
in rdx, and terminal kind in r8. Exit0/kind1 is accepted even when engine ready1
remains set; ready1 with terminal/stale status never admits work. The initial
host model incorrectly treated rdx as terminal detail; it was corrected from the
kernel source before any guest. Tests now represent both actual terminal tuples.

Intentional UD2 retains unknown resources on any failed or returned halt. This
is bounded fail-stop preparation, not operator error recovery. Host doubles,
compiled raw/ELF inspection and conservative stack bounds do not qualify native
assembly, trap correctness, media quiescence or independent review. BG-067 retains
those gates; no production/service API, default pin or old ABI24 path changes.


Decision0191 consumes Aether's exact native witness for the unchanged ABI29 wrapper.
The five retained failed-peer kernel spans trap at the linked UD2/0x400028 with
correct stop-versus-reclaim distinctions. Positive producer results are bound to
this exact source/ELF/raw; retained tails cannot independently replay the complete
positive oracle. This review changes no unsafe code or broader soundness claim.

## Separate AF07 wrapper — decision0192

The new native-filesystem-af07/init.rs is byte-identical to the AF06 wrapper.
Scalar trap register constraints, synchronous exclusive buffer lifetimes, lack
of nomem/preserves_flags and fail-stop on returned halt remain unchanged. Only
the separate policy wire magic changes. Inventory covers all five sites/hash;
no new native grant, pointer retention, concurrency or device claim. Host policy
and structural fit pass; fresh matching Aether witness and consumer review pending.

## AF07 consumer checkpoint — 2026-10-21

Decision0193 now consumes fresh exact AF07 native owner witnesses without
changing its wrapper/source hash. All eight bounded selected oracles replay;
raw UART and timer schedules do not. Fixed-peer fail-stop is not device recovery.
The separate ABI29 client correction is host decoder/native-source evidence,
not a new trap boundary or native shell claim.

## AF07 endpoint adapter — 2026-10-21

The separate af07_native.rs wrapper passes a synchronous initialized exclusive
slice or scalar arguments only. ABI29 rax operation/result, rdi endpoint, rsi
pointer and rdx count have explicit outputs; r10/r8/r9 are zero, rcx/r11 clobbered,
no nomem/preserves_flags. Object disassembly has int0x81 with24001/24002/24004/24003
and zero unused scalar arguments. Host tests exercise the actual sealed client
over typed doubles, not the trap or kernel authority. Native panic=abort, no host
unwinding cleanup qualification. Final code/stack/heap, live holder/direction,
wait scheduling and full engine cleanup need fresh matched native witnesses.


## ABI30 entry and owner placement — decision0206

The seven producer source hashes and exact AENFS004 contract are checked before
selection. Numeric entry validation does not supply authority: unsafe claim
requires the actual unique boot mapping, once, until VM termination. Zero bytes
are inspected before typed writes. Backing remains MaybeUninit<u8>, because T's
padding can become uninitialized; safe callers cannot subsequently read it as
u8. Exclusive splitting provides one aligned MaybeUninit<T> slot and disjoint
initialized workspace/spare. No reference to T exists until a valid T is written.
Fieldwise gate initialization writes every field before assume_init_mut and avoids
the measured full-gate stack temporary. No destructor/settlement is implied.

Naked entry copies initial r10/r11 to C stack arguments before a normal call,
preserves the six existing argument registers and aligns RSP by subtracting24.
A returned diverging body traps. Compiled object and disassembly are evidence of
construction only; no executable owner_main body or native entry/permission/
zeroing/isolation witness is claimed. Actual parent/child obligations, caller
frames and complete fit remain BG-070. No independent review is invented.
## Mapped constructor and comparison follow-up —decisions0207/0208/0209

The current aggregate static check exposed an active inventory entry still bound
to0206's by-value gate initializer. Review0207's already committed constructor
before updating this active entry: exclusive aligned MaybeUninit<Owner> supplies
the sole FILE field projection, without creating an uninitialized Owner reference.
Producer owns its nested layouts and returns only after full initialization and
the sole greeting; on returned failure it records once-only actual closes/drop
and the unconsumed streams value drops normally. On success streams/phase/sequence
move once without fallible callbacks before assume_init_mut. No second valid Owner,
opaque cast or zero-as-valid representation. The35 producer/34 consuming tests and
actual native build hashes cover this unchanged source; peak-stack/native execution
and independent review remain open. This is an active index correction after source
review, not a rewrite of0206's evidence or a released pin.

0209's publication/refusal code is safe Rust over the existing synchronous Kernel
trait. It adds no pointer/assembly boundary; actual endpoint/grant authentication
and native obligations remain caller-owned.0208's explicit C memcmp leaf uses only
compiler-supplied readable ranges, unsigned byte loads, no retained state/allocator/
unwind or hidden symbols; source/header/license/tool hashes and guard/UBSan tests
are recorded. Its41-byte x86_64 object uses one8-byte RBP push, no other stack
reservation, calls, red-zone access or wider loads in the inspected
assembly. This does not prove the complete owner's stack or native execution.
## Mixed owner routing —decision0210

New routing, prefix handling and received-header dispatch are safe Rust; no new
assembly/FFI/unsafe sites or native authority. The existing0207 constructor functions
are byte-identical to the prior reviewed source (chunk SHA256
7f176d630809853da5cfc5d27fea67f3999479a8ec92758ecb192762e500446f).
Adding the safe Routed type shifts their textual site lines; update only that
active boundary record after this identity comparison. Preserve the old review,
all release bytes and sealed source snapshots. Scoped channel escape and owner
reentry are actual compile-denied attempts. Shape validation still does not supply
native endpoint authority. Whole-owner resource/native and independent review stay
open; safe Rust alone does not prove caller authentication or protocol correctness.

## Compact FILE layout and native cancellation —decision0211

Descriptor indices are private u8 with compile-time SLOTS bound and explicit
widening at checked array indexing. Typed Option writes in the producer initializer
retain their actual element extent/alignment and no zero-as-None assumption;
there is no opaque sys-init cast. Target gate shrinks2968 to2240. Gate constructor
unsafe functions remain byte-identical to4e32ff296; native reconciliation is safe
Rust over the same phase/sequence checks. Wrong result/error/unwind stays closed.

The native scalar cancellation method reuses the same reviewed trap bridge: source
rdi/token rsi, opcode23005, rdx/r10/r8/r9 zero, explicit rax/rcx/r11 clobbers and
no nomem/preserves_flags claim. No pointer is supplied for cancellation. Actual
measurement root disassembly confirms one trap and raw0 success test. The0 return
is supervisor-side; parent-11 is separately set by kernel and is not fabricated
as an observed callback value. No native execution, holder/endpoint/child/backing
settlement, parent acknowledgment, whole stack or independent review is implied.

## Concrete owner composition —decision0212

The native owner now has a real8-scalar owner_main body linked to the existing
entry bridge. It validates binding, claims the unique mapped region once, checks
Runtime layout and uses exclusive final-slot construction. Nested FILE/gate success
precedes infallible elementwise moves of every remaining valid field; no enclosing
invalid reference, aggregate owner temporary, writable image static or heap.
Failed construction does not expose Runtime or invent native cleanup. Original
gate constructor unsafe chunks are unchanged; the new projection has a distinct
active inventory/review. Source/format changes refresh exact active hashes only.

The new Control bridge passes exact op/arguments and typed synchronous initialized
buffers, with explicit rax/rdx/r8 outputs and rcx/r11 clobbers, no retained pointer
or nomem/preserves_flags assumption. Numeric grant labels are not authority; the
current kernel caller/grant checks remain. Cloning the zero-sized Native adapter
adds no endpoint-close owner: Endpoints/Peer remain sole transport obligations.
Owner error or impossible returned halt traps; no partial transaction/reply may
replay, and no owner fault is called engine export or child reclamation. Current
copy preflight/exhaustion/fault fail-stop is not graceful parked-parent recovery.

Checked disconnect validates ack before an exclusive verification callback, then
closes both endpoints once. Full owner callback requires actual engine terminal/
kind plus same-endpoint EOF/EPIPE before close; reclaim/staleness remains separate.
Host tests use actual protocol cores and injected native results, not real trap/
permissions/engine acceptance. The compiled direct-edge stack6360 exceeds4088;
no native admission or full exec/readiness/independent review is claimed. New code
budget waits for complete measurement, and the separate guarded-stack proposal
requires disposition. Old profiles/seals/released pins stay exact.

## Selected guarded owner, exec and readiness —decision0213

The same eight-scalar assembly entry now supports exact separately selectedABI31
with initialRSP0x802000-8; register capture/call alignment is unchanged. The mapped
region claim remains once-only, zeroed, exclusively owned and alive until VM end.
Binding metadata does not itself establish authority. ABI31 validates actuale002
cleanup rather than c003 image. Initialization/projection unsafe bodies remain
unchanged; refreshed records include exact active source hashes and shifted lines.

The typed synchronous exec borrow covers272 readable initialized bytes through
23007, with fixed factory/process/image/freeze and zero unused operand. Receipt
23008 and publish23009 are scalar calls through the same explicit output/clobber
bridge. No retained pointer, ambient grant, allocator or new unsafe mechanism.
Actual kernel checks establish provenance; host doubles do not. C calls use the
existing reviewed masked/native provider and real startup binding. Errors after
commit cannot reopen the gate or imply rollback. The exact image receipt precedes
CLOEXEC and rebinding; full new startup and live-ready observation precede success.

Compiled code/resident/stack checks pass under the separate measured profile;
this is not native permission/interrupt/peak proof or independent sign-off.
Old profiles and immutable pins remain distinct. Fail-stop preflight/exhaustion
still does not provide graceful parked-parent recovery. See0213 and root STATE.

## ABI31 entry correction — decision0214 /2026-10-23

The producer's actual SESSION frame selects image c003 in r9 because it excludes
storage-lifetime. Correct the owner's e002 expectation to c003 before region
construction or effects. Explicit event operations still select e002 separately.
No assembly/unsafe site or authority is added; the region source inventory is
refreshed. The new root test compiles the real producer expression and validates
its scalars with the actual Rust consumer, rejecting each changed scalar, e002 and
old ABI30. Prior synthetic-frame coverage did not expose this mismatch; historical
evidence remains unchanged. Fresh current chain/native qualification is separate.
