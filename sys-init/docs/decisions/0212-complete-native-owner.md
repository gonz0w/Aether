# 0212: Compose and measure the native owner before budgeting code

2026-10-22 / BG-070. Maintainer-directed pre-code review.

Apply the pinned Foundations ownership/interface/evidence rules, local adopted
CE/CD/CA and Rust unsafe/FFI guidance, TD/TC/TE risk-based focused checks, and
SE-01–05 simplicity review. Keep service policy in the actual sys-init/userland
owners, kernel capability enforcement unchanged, and native/independent/R1 claims
separate. This is a local experiment contract, not a new shared standard or pin.

Complete native ownership takes priority over satisfying the experimental16KiB
code cap. That cap rounded the old15120-byte init image to four pages; it is not
a capability or isolation property. New offline full-owner measurements may
exceed it. Keep historical profiles/pins exact, choose no new admitted allowance
until the coherent executable is measured, and preserve all other fixed bounds.

Required composition: ABI30 entry capture and single mapped initialization; one
AF07 service client/greeting; engine/block provisioning; process launch; full
FILE/fork/stream routing; actual pipe and console holders; native copy/refusal/
child-ready/parent publication; terminal/wait/transport settlement; readiness and
ordered drain/disconnect/export/channel proof/reclaim/serial closure/halt. The
selected actual userland codecs/native provider and syscall contracts are inputs,
not guessed operations. Missing immutable-exec/provider behavior must stay explicit
and cannot be replaced by success, an old framing fallback or a fake shell.

The existing route requires stream replies to complete synchronously. Add an
explicit polling result for initial idle/EOF and side-effect-free Pending requests.
Preserve the old synchronous API exactly. A Pending frame is retained once in the
existing per-process owner slot and only retried under admission when its handler
guarantees no effects. Completed partial replies never replay. EOF requires a
fresh matching native terminal observation before any clean settlement. No extra
queue, worker, endpoint, ledger or kernel-global mutable state.

Actual stream state owns parent/child console holdings plus two existing SESSION
pipe cores. Validate native identity/generation/rights/reference/source history
before effects. Normalize only a fully checked tagged pipe route to the existing
local core, and translate only validated successful factory output back. Stage
both pipe holdings atomically before copy, activate only after context-ready,
rollback only after a known no-child refusal, retain unknowns, and clear holders
only after confirmed terminal. Pending requests prevent pipe-generation reuse.

Native ownership must observe freeze tokens separately from application sequence,
record actual copy and supervisor0 cancellation results, and preserve original
copy errno. Either process may run after successful copy; the owner gate remains
closed through complete child/parent publication. Endpoint closure, process
terminal, native reclaim, FILE settlement and wait delivery remain distinct.

Keep exactly one exclusive initialized mapped owner and4096 workspace. Add no
writable image statics or dynamic owner allocator. Any new field projection is
from aligned MaybeUninit storage with no enclosing invalid reference; publish
only after every field and the sole greeting succeed. Returned failure and abort
must not invent reclamation. Borrowed buffers remain synchronous; traps retain
explicit clobbers and no nomem/preserves_flags assumptions.

Tests: existing focused producer/consumer tests and semantic controls; actual
pending pipe/console/wait continuation, idle peers/EOF-terminal races, stale/forged
sources, full queues, stage/refusal/unknown/child-ready order, wait/reclaim and
shutdown failures. Build complete target entry/control paths, inspect code/data/
stack/call graph, and preserve missing/unresolved coverage. Native qualification
requires matching admission and fresh scoped disposition under the persistence
recurrence rule. Retain compact commands/hashes/results/short failures and remove
owned generated outputs, with no archives, SDK copies or source bundles.

Simplicity: keep the existing capability kernel and actual service/FILE/pipe cores,
compose their ownership once in a direct owner loop. Shrinking partial link roots
cannot complete these transitions. Reuse the per-process slot for Pending rather
than adding an asynchronous broker or cache; remove redundant integration wrappers
only after their consumers move. No new shared standard, broad runtime refactor,
quota-driven code golf or speculative framework. No independent or ISO acceptance.

The current Client disconnect closes endpoints immediately after receiving its
acknowledgment, before native engine/export/EOF/EPIPE proof can occur. Add a scoped
checked-disconnect callback after the exact ack is validated and before either
close; propagate its failure and actual close results, never replay. Preserve the
old API. ProcessFiles requires every view settled before invoking the callback.
The native callback must observe the actual engine terminal/kind, EOF and EPIPE
on those same endpoints; then close/reclaim stay separate. Callback borrow cannot
escape, missing/error verification cannot report success. Test callback ordering,
malformed ack, live-view rejection, failure/close-result preservation and no retry.

The first concrete link is34992 bytes with3376 resident bytes plus4096 workspace.
This is not a complete-owner measurement: immutable exec and initial readiness
remain. Default compiler jump tables prevent the existing direct-edge stack
checker from proving a bound. Select direct branches (-Cjump-tables=no) only for
the new offline composition, including its target libraries, to make that check
inspectable; retain exact flags and report its code cost. This is for stack
verification, not fitting a smaller code quota, and changes no old admission.
Resolve a RIP-relative linkage call only by verifying actual FF15/FF25 bytes,
the pointer in one immutable RX file-backed ELF segment, no writable alias and
an exact defined function target. Do not trust disassembler comments or accept
register/table/dynamic/unknown targets. Test writable, opcode, pointer, target,
recursive and segment corruptions; keep the4088-byte stack gate. A successful
link or unresolved inspection must never become native acceptance.

### Proposed stack disposition — decision required

The direct-branch owner is34560 code bytes; it still needs immutable exec and
initial readiness, so no complete-owner code budget is selected. Its3376-byte
resident object plus4096 workspace fits8192, leaving720 bytes. Separating boot,
dispatch and lifecycle call boundaries reduces the conservative stack bound
7352 to6360, still beyond4088 usable. The exact longest compiled path is retained
with the result. This is a conservative bound, not an observed overflow or formal
peak-stack proof; do not lower/remove its safety margin merely to pass.

Before admitting this composition, propose a separately selected owner with an
8192-byte RW/NX stack at[0x800000,0x802000), initial RSP0x802000-8, and unmapped
guards at0x7ff000 and0x802000. Existing owner backing128 pages,8192-byte mapped
data at0x900000,35MiB total,sevendomains/twelvechannels,worker/authority/I/O/poll/
watchdog/workload/cleanup limits stay fixed. The extra stack page comes from the
same owner partition: current9 code+2 stack+2 data pages use13/128 pages, before
the final code budget is selected. Do not enlarge an existing seal/profile or
silently reuse ABI30 admission: a versioned envelope/startup selection, loader/
intake/entry and stack-check consumers must agree. Keep guard, W^X/NX, zeroing,
peer isolation, backing and rejection checks; qualify fresh before native use.
8192 gives1824 bytes above the current conservative6360 bound, but completion
and final executable measurement must still pass8184 usable; no guaranteed
future fit or native acceptance follows. This is not implemented or approved.
