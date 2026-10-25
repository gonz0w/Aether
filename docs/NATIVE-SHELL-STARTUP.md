# Native shell startup prerequisite

Current assembly direction,2026-10-03: the [source-backed sys-init/serial-shell
review](evidence/serial-boot-contract-2026-10-03/README.md) records the selected
bounded composition and next kernel lifecycle experiment. ABI22 command init and
ABI23 SESSION are incompatible closures; no new profile or runtime is implemented
by the review. SI-07’s bounded kernel dependency is complete; full protocol/SDK and
assembled boot acceptance remain separate. Earlier dated missing-input notes below
retain their historical scope.


## Delivered bounded runtime candidate — 2026-09-29

Userland records agreed ownership and delivers an extracted private008 runtime/
application bundle. [Aether-side technical review](evidence/session-runtime-review-2026-09-29/README.md)
verifies its571 inputs and fresh isolated whole-ELF equality with native-tested
parent/helper artifacts. The start guard rejects repeated bootstrap before traffic;
a copied image inherits state, and a failed first attempt requires termination.
The application narrows helper policy while native owner grants remain authoritative.
All49 native completion receipts are verified, with11 serial owner bindings matching
producer images. Existing mask/rebind/memory/FD/cleanup source mechanisms remain.
No new kernel behavior or public SDK API is adopted by this intake.

The ownership/bundle prerequisites below are now supplied; their remaining gates
are actual independent technical/reader findings and scoped SSDK-01–06 disposition.
See the packet's REVIEW.md for requirement-by-requirement limits and retained intake
corrections. Full160-case, broad runner/connections, all-path stack/concurrency and
physical/TTY/storage coverage are not claimed by the49-case extraction. SI-07's
sustained transport/runner payload remains a separate missing delivery.

## Session SDK integration boundary intake — 2026-09-29

The [verified UL-081 handoff](evidence/session-sdk-intake-2026-09-29/README.md)
selects the exact accepted AENMX008/ABI23 component closure as the experimental
reference. Its static baseline reproduces the accepted serial parent ELF; missing
startup facade/process components and duplicate facade fail linking. Missing
memory adaptation still links using musl providers and yields an unqualified ELF.
The runtime bundle must reject missing, stale, duplicate or wrong-profile components
before build/admission, including a missing memory adapter even when symbols resolve.
No successful link substitutes for native authority or memory-protection evidence.

Next delivery requires an explicitly agreed libc/POSIX runtime implementation owner.
Aether owns ABI/grants and the fixture owner; userland owns SDK experiments and
consumer replay. Separate application main/helper/namespace policy from one
per-process bootstrap and process/FD/mask state. Retain strict memory adaptation,
musl CRT/allocator/sigaction and shared public/internal mask state. Preserve exact
copy/rebind/exec/CLOEXEC identity, descriptor positions, EOF, poisoned-transport and
terminal/reclaim semantics. UART stays owner-only;007 remains without UART access.
The fixed fixture must remain visibly scoped rather than become a general runtime
by archival packaging. No global POSIX server or generic VFS is introduced.

The owner-agreed sealed bundle needs source/object/archive/header and symbol-provider
inventories, pinned SDK/CRT/libc/tool/flags/patch/license inputs, bootstrap/profile/
grant/identity/quota closure, interrupted-transport exclusions and an isolated build
recipe. Reject absent, wrong or repeated bootstrap before effects. Qualify SSDK-01–06:
component closure, independent bootstrap, shared masks/rebind/exec, truthful FD/memory/
error behavior, all accepted composed workloads and actual independent review.
The consumer handoff and reader checklist are snapshotted in the intake packet;
no runtime bundle or reviewer approval is supplied by that static audit.
SI-07's complete versioned transport and rebuilt runner/bytecount remain separate.

## Real serial SESSION experiment — 2026-09-29

[Integration evidence](evidence/serial-session-2026-09-29/README.md) combines the
accepted scripted session and UART components under explicit private AENMX008/ABI23.
007/ABI21 remains without UART authority;006/ABI20 retains its original bounds.
The008 owner alone accesses UART; parents and copied children receive scoped
stdio references and fail direct UART read/close. Empty reads retain the request
on EAGAIN; no synthetic EOF is supplied. The existing pinned native input object
selects upstream's one-byte fallback; the scripted input object would consume an
extra internal pipe before the command. No termios success is fabricated.

Producer qualification passes three parents, nine prompt-driven commands and all11
serial controls with matching regressions.
[Verified independent acceptance](evidence/serial-acceptance-review-2026-09-29/README.md)
now closes SERIAL-SESSION-01–06 with169 fresh native cases and151 checker controls. Run the pipeline-capacity
command with `--case serial-session-composed`; omit `--case` for all controls.
`python3 -m unittest discover -s tests -p test_serial_session.py -v` checks the
host oracle only. Physical hangup, general TTY/job control, SDK and R1 remain open.

## Scratch session producer — 2026-09-29

The unchanged SESSION-SCRATCH composition and semantic controls have producer
qualification in [the scratch packet](evidence/scratch-session-2026-09-29/README.md).
[Verified userland acceptance](evidence/scratch-acceptance-review-2026-09-29/README.md)
now closes SCRATCH-SESSION-01–06 for this private volatile profile. Shared SDK
adoption and the real serial-session composition remain open. This private
AENMX007/ABI21 profile adds bindings7/8 after standard streams0–2 and pipe pairs3–6;
it leaves the16-descriptor snapshot and all kernel limits unchanged. Each fresh
parent receives an explicit namespace record after its binding records. Copied
children inherit that grant only through the existing admitted owner connection.

Opcode86 carries the namespace selector, zero reserved word, bounded mode and
16-byte canonical pathname. It permits only the frozen volatile scratch path;
protected writes return owner-backed EACCES without a handle. Typed description
selectors bind namespace, non-wrapping allocation sequence and binding index.
Reads/writes/closes use existing32-byte frames and16-byte payloads. The owner
tracks shared offsets and authenticated per-peer holders; client aliases collapse
to one holder, and confirmed terminal releases remaining peer references. Full
nine-binding snapshots are validated before scratch entries are excluded from
pipe lifecycle operations. Native exec preserves or drops holders according to
the same CLOEXEC plan, before publishing the replacement.

Two descriptions,32 bytes of volatile data, immutable protected seed bytes and
15 allocations per namespace bound this experiment. It is not a persistent
filesystem or general filesystem API. No path grants image authority. Run the
existing pipeline-capacity command with `--case scratch-composed` for focused
coverage, or omit `--case` for all controls and regressions. Host checks use
`python3 -m unittest discover -s tests -p test_scratch_smoke.py -v`; the existing
pipe-owner host wrapper also tests the scratch core and no_std compilation.

## Current bounded SESSION integration

The AENMX007 persistent-parent implementation now has a
[qualified producer packet](evidence/session-native-2026-09-25/README.md): unchanged
composed.sh, all eight semantic cases and matching full regressions. [Independent userland SESSION-01–06 acceptance](evidence/session-acceptance-review-2026-09-25/README.md)
now covers this private scripted profile. The next composition needs new consumer inputs. Shared SDK/runtime adoption and R1
assembly remain separate. The original profile below and dated prospective reviews
retain their scoped contracts/history; they do not describe every later profile.

## Original startup profile — 2026-09-07

Status: experimental producer candidate, 2026-09-07. Qualification is recorded
in STATE; this reference alone is not a passing result or SDK-owner acceptance.

The opt-in startup adapter uses the existing AENMX001 connections envelope,
`-Dnative-runner-local=true`, and AECAT001 capability-bound role bootstrap.
No version, resource limit or inherited-role wire format is changed. Its public
C functions are linked from startup-client.c/startup-adapter.h alongside the
captured strict native musl SDK; the stock SDK alone does not supply them.

Kernel operation 0x10027 queries the actual caller identity only in this profile.
All six argument registers must be zero (otherwise EINVAL); other profiles return
ENOSYS. Identity is generation * 4 + slot + 1, stable for an admitted lifetime,
distinct across slots and the three nonwrapping generations. It is bookkeeping,
never authority. No current exec operation promises to retain it.

The adapter is single-threaded and has no signal delivery or exec. Before complete
role validation no descriptors or signal interface is published. Sixteen local
descriptor entries share three underlying inherited bindings. F_GETFD/F_SETFD,
F_DUPFD/F_DUPFD_CLOEXEC and scalar read/write/close are supported. Duplication
selects the lowest free index >= minimum in 0..15; invalid minimum/flags produce
EINVAL, full table EMFILE, closed source EBADF, unsupported commands ENOTSUP.
Each alias has separate CLOEXEC flags; only final local close consumes the remote
binding. I/O uses the original remote FD and grant, retaining access rights,
shared stream position, partial transfers and existing poisoned-connection rules.
Atomic flag publication relies on the explicit single-context/no-handler bound.
No claim of exec-time CLOEXEC enforcement or forked tables is made.

Signal query/set supports signals 1..64 excluding libc-reserved 32..34. Mutating
SIGKILL/SIGSTOP rejects EINVAL. Dispositions accept DFL/IGN and zero flags;
custom handlers/flags return ENOTSUP without mutation. All 64 mask bits are stored
except unmaskable signals 9/19; query/block/unblock/replace are real transitions.
Other sigset_t storage is zero on output. Invalid mutating how returns EINVAL;
query ignores how. Each fresh image starts with default dispositions and empty
mask. Raw action/delivery calls remain unsupported. The mask bridge below now shares
the native context with musl internal masking; dispositions remain public C overrides.
As with other C facade calls, application pointers must be valid; a bad pointer
can terminate its isolated domain. No kernel pointer/authority validation is bypassed.

Run the complete affected profile with the captured SDK and lock:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build SDK --tools-lock LOCK
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The original nine startup cases include the unchanged copied UL-007 consumer,
four exact-stage producer mutants, four malformed role bootstraps and supplemental
alias/flags/exhaustion/rights/I/O/signal checks. The owner independently checks
stream contents, terminal kind/status, final closes and four reclaims across two
fresh generations. This remains producer-side execution of the consumer, not its
independent acceptance. Custom signal handlers, actual dash initialization,
UID/GID, fork/vfork/exec/wait, pipes and interactive shell assembly remain open.

[Preimplementation review](evidence/shell-startup-2026-09-07/review.md) records
ownership, applicable standards, forbidden outcomes and test selection.

## Descriptor replacement for the shell path — 2026-09-07

The same opt-in facade adds `dup2(source, target)` within its 16-entry table.
Invalid source/target returns EBADF before mutation. A valid self-dup preserves
flags and binding; distinct replacement clears target CLOEXEC and works with a
full table. Source and target share the original offset/rights. Replacing the last
alias consumes its remote binding once; replacing a nonfinal alias is local.
A complete remote close EIO already confirms consumption under AECAT001 and is
discarded. Unknown/malformed close poisons the connection and rejects replacement
without publishing it. This fail-closed profile does not promise transparent
recovery or ordinary POSIX behavior after transport uncertainty.

There are still no handlers, threads or exec peers in this facade: mutation is
serialized by that bound. Future handler delivery must review descriptor and
transport reentrancy before reuse. No new kernel operation, inherited wire format,
SDK archive or authority is introduced. `dup2` does not implement cross-process
inheritance, exec-time CLOEXEC, file creation or pipes.

The complete command-runner suite now includes four `cat-roles-startup-dup*`
cases: positive two-generation save/replace/restore, self-dup flag corruption,
replacement flag corruption and leaked displaced references. Exact terminal
70/71 and owner1501 or leaked-close owner1503 distinguish semantic failures.
The standalone close-boundary probe uses copied functions and a mocked transport;
it is host evidence only for consumed-EIO/unknown-close behavior. Qualification
and the unchanged twelve-workload consumer intake are retained in the
[descriptor replacement packet](evidence/shell-dup2-2026-09-07/README.md).
Full dash initialization/signal delivery, child exec/wait and pipeline acceptance
remain open; this packet is a prerequisite, not the full-dash handoff.

## One authoritative shell mask — 2026-09-07

The runner-local connections profile now accepts the existing SDK's four-argument
native transport for rt_sigprocmask (0x1000e): rdi=how, rsi=set, rdx=old, r10=8.
R8/R9 are unspecified by musl's actual four-argument inline transport and ignored.
This is a scoped native adaptation, not Linux binary compatibility. Other profiles
retain ENOSYS. Before descriptor admission, libc may change only its own context
mask; this does not publish descriptor or signal-send authority.

Both that call and the existing grant-bound 0x28009 thread call use the same checked
copy/transition helper and Execution.signal_mask. The public startup sigprocmask
facade delegates to it; its former independent startup_mask is removed. Public
facade calls still require complete startup admission. The original thread entry
retains its own grant/argument checks, inheritance and reset behavior.

Size must be eight. Non-null set requires how 0/1/2; null-set query ignores how.
The kernel snapshots eight input bytes and validates every output byte before
writing old state or committing the new mask. Aliased input/output is supported.
Bad size/how returns EINVAL; inaccessible or overflowing input/output returns
EFAULT without state mutation. Bits for SIGKILL/SIGSTOP remain clear. No user
pointer is retained, no caller can target another context, and no allocation occurs.
The C facade snapshots input before clearing the full output sigset_t, and zeroes
its tail only on successful completion. Invalid application pointers still remain
subject to existing domain isolation; raw kernel copies validate native mappings.

The expanded startup witness calls actual linked musl __block_all_sigs,
__block_app_sigs and __restore_sigs, checks raw/public state in both directions,
rejects malformed size/how and invalid/overflow pointers, and checks aliasing and
two-generation reset. The omitted-internal-block control must terminate at73 and
owner1501. These calls prove mask transitions, not deferred-signal delivery.
The [producer packet](evidence/shell-mask-2026-09-07/README.md) records source and
SDK identity, selected regressions, failures and remaining coverage. Custom
handlers, pending delivery, handler return, actual dash and exec/wait remain open.

## Handler boundary review — 2026-09-07

**Proposed; no handler ABI or delivery is implemented by this review.**
The [retained source review](evidence/shell-signal-review-2026-09-07/README.md)
identifies two prerequisites that must precede enabling custom `sigaction`.
The current startup facade continues to reject custom handlers with ENOTSUP.

The requirement is actual dash initialization and signal handling on the existing
single-context, capability-scoped shell path. Aether owns native pending state,
validated user entry/return and lifetime enforcement. Userland owns libc signal
translation and shell behavior; its matching-build acceptance remains required.
Sys-init supervision and pkg-mgr installation gain no signal authority. Applicable
rules are Foundations O-01–05, I-01/03/05/06 and E-01–08, proposed Distribution
NC-04/PX-01–03, and the locally adopted SE-01–05 process. This review changes no
released pin, existing terminal kind, syscall allocation or supported profile.

### Findings and selected direction

1. **A handler need not return.** Pinned dash `onsig(SIGINT)` can call `onint`,
   clear its mask, and reach `exraise`/`longjmp`. Its trap handler also fills the
   action mask, uses flags zero and records SIGCHLD for later processing. A single
   kernel-owned saved frame with an `active` flag cleared only by `sigreturn`
   would remain occupied after a nonlocal exit. Reject that design. Do not infer
   handler completion from stack-pointer comparisons or from a mask update.
2. **Libc already defines the entry seam.** Pinned musl converts public sigaction
   into a 32-byte x86_64 record: handler, flags, restorer and eight mask bytes.
   It supplies SA_RESTORER; its adapted restorer issues native trap `0x1000f`.
   That trap is currently unsupported. A successful custom setter cannot precede
   working entry and return. Public and internal callers must ultimately share
   one disposition owner, just as they now share one mask owner.
3. **The I/O adapter cannot tolerate arbitrary interruption.** `exchange` sends
   and receives frames in pieces on one request/reply channel. `startup_io`,
   fcntl and dup2 modify related descriptor/refcount state. A handler that calls
   I/O can interleave another request; a nonlocal exit can abandon an outstanding
   reply or partly changed state. Dash's ordinary USR1 handler records a pending
   trap for later evaluation, but that observation does not make the generic
   adapter reentrant or fix the SIGINT escape path.

Select a user-stack return-frame direction for the next experiment. It avoids
kernel allocations or a persistent active-handler slot that must be unwound by
libc. It is **not yet an agreed frame layout** or permission to trust a copied
CPU context. First prove a checked frame round trip with the pinned musl restorer;
only then connect pending signals and replace the local disposition table.
A fixed kernel frame stack merely moves the nonlocal-exit leak to a quota boundary.
An opaque return token would also need explicit abandonment semantics.

The frame implementation must specify exact offsets, size and alignment; preserve
the x86_64 red zone and FP/SIMD state; and validate every user copy, executable
handler/restorer/return address and writable stack range. Return must force valid
user selectors and permitted flags, reject privileged flags and invalid MXCSR,
and preserve kernel ownership of FS/TLS, page tables and capabilities. Snapshot
and validate before changing live execution. Mapping removal/protection changes
between registration, delivery and return require fresh validation. A forged,
replayed or abandoned frame must never recover authority or kernel CPU state;
user-controlled resumption within the same granted domain needs a documented
policy. A raw FXRSTOR of unchecked user bytes is forbidden.

Use per-domain dispositions and a bounded standard-signal pending bitset, with the
existing per-context mask, for the single-context experiment. Signal numbers,
accepted flags, default actions, coalescing, selection order, delivery points,
exhaustion and fatal-frame behavior must be enumerated before dispatch code.
Do not silently accept SA_SIGINFO, alternate stacks, real-time queuing or restart
flags without implementing their contracts. Self-directed delivery is sufficient
for the first witness; a numeric PID alone must never authorize another target.
Remote sends and SIGCHLD require generation-bound authority and process-lifetime
integration. Do not reinterpret normal exit status as a signal terminal record.

For existing bounded synchronous I/O, mask catchable signals before descriptor
mutation or a complete request/reply transaction; restore only after state and
reply ownership are settled. Use the authoritative mask, preserve errno and
nested prior masks, and retain existing unknown-result poisoning. Masking just
one channel trap or the request send is insufficient. An invalid restore must
fail closed. Nonreturning fatal signals may still terminate the entire domain,
whose existing cleanup must remain sufficient. This approach is a prerequisite
for a bounded probe, **not an interruptible shell-read design**: indefinite reads,
waits and pipes need cancellation/completion and EINTR rules before enabling
interactive SIGINT. They cannot hold signals masked indefinitely or retry an
ambiguous side effect. No new kernel "transport busy" policy is proposed.

### Simplicity assessment

- **Simpler alternative:** retain the existing startup facade and defer handlers.
  It remains appropriate until checked entry/return exists, but cannot satisfy
  actual dash. A callback-only demo or successful custom setter is insufficient.
- **Chosen cost:** validated user-stack context plus local pending state adds
  copy/validation and scheduling work, but avoids a second service, return-token
  lifecycle, or kernel unwinding protocol for dash's nonlocal exit. Borrow the
  pinned musl record/restorer seam; do not infer a complete Linux signal ABI.
  Exact frame compatibility is the next executable question.
- **Removable complexity:** replace the C action table when the native owner is
  qualified; retain the current tests until the replacement passes. None is
  removed in this documentation-only change. No profile/quota expansion or broad
  native dispatcher refactor is justified by this review.

### Acceptance before advertising handler support

The next frame experiment must exercise the actual restorer, GPR/FP/red-zone/mask
preservation, malformed and cross-page frames, RX/RW/NX/guard rejection, privileged
return attempts, invalid FP control state, changed mappings, nonlocal escape and
repeated delivery after escape. Deliberately broken validation and restoration
must fail for their named reason; timeout/crash does not count as rejection.

The subsequent pending/delivery slice must add blocked/coalesced and unblocked
self delivery, DFL/IGN policy, action-mask application, independent domains,
termination/reuse cleanup, and raw-musl/public agreement. Inject interruption
between descriptor updates and partial request/reply transfers; verify no crossed
replies, lost close, duplicate effect or stuck mask. Include failed and unknown
close outcomes. Select complete command-runner, affected native mask/pthread and
M4 regressions for changes at these boundaries. Keep exact owner terminal/reclaim
oracles. No native regression is required for this source-review-only step.

The twelve userland scripts still require process creation/exec/wait, redirection,
pipes and matching consumer qualification. In particular, `signal-table.sh` uses
command substitution before trapping USR1, so a self-signal probe cannot satisfy
that script. OpenZFS follows this shell producer path; persistent storage remains
required for R1.

## CPU-frame codec prerequisite — 2026-09-07

[Implementation and test evidence](evidence/shell-signal-frame-2026-09-07/README.md)
covers `kernel/arch/x86_64/native_signal.zig`, currently imported only by the
native execution host tests. It does not enable a trap or signal handler.

The private experimental payload is 720 bytes: identity/reserved words at 0/8,
normalized 176-byte CPU frame at 16, signal mask at 192, zero padding at 200,
and 512 FXSAVE bytes at 208. An eight-byte return address immediately precedes
it. Stack placement aligns the payload to 16 and entry RSP to 8 modulo 16,
leaving the interrupted 128-byte red zone intact. This borrows only the pinned
restorer's RET-then-trap convention; no Linux ucontext, SA_SIGINFO or published
native ABI compatibility is claimed. Actual restorer execution is still pending.

`decodeCpu` consumes a kernel-owned byte snapshot and returns a candidate; it
never touches Execution. It requires CS=0x23, SS=0x1b, flags=0x202 plus only
CF/PF/AF/ZF/SF/DF/OF, zero vector/error metadata, nonzero lower-half canonical
RIP/RSP and matching private metadata. It strips SIGKILL/SIGSTOP mask bits and
validates MXCSR against a trusted nonzero 16-bit hardware-supported mask. The
payload's MXCSR-mask field cannot relax validation. Reserved FP bytes are cleared
and the mask field is replaced from trusted input. FS/TLS, waits, mappings and
capabilities have no fields in the candidate.

This is structural validation only. The runtime caller must obtain the hardware
MXCSR mask (including the architecture's zero-mask fallback), validate complete
readable/writable ranges and executable targets under owner-local serialization,
and only then publish the candidate into aligned CPU/FP storage. Handler entry
must clear DF even though interrupted DF is preserved for return. Input/output
copy failure must leave the interrupted context unchanged. A candidate alone is
not safe to pass to IRET or FXRSTOR. Stack geometry is not mapping validation.
There is no active-handler slot, allocation or kernel resource to strand after
nonlocal escape; exercising escape and repeated native delivery remains pending.

Four codec tests pass in Debug and ReleaseSafe. Deliberately removing flags or
MXCSR validation causes the corresponding named test to fail with TestExpectedError.
The existing 98 Python host tests and Zig/pin/workflow checks also pass. Mapping
permissions, cross-page copy, actual FP restore, musl return and signal delivery
are not established by these host tests. The next step remains runtime mapping/
copy integration and the native entry/return witness before custom sigaction.

## Owner-local frame copies — 2026-09-07

[Memory preparation evidence](evidence/shell-signal-memory-2026-09-07/README.md)
extends the codec with `prepareEntry` and `readReturn`. Both remain test-only
imports; no native syscall dispatch or handler support is enabled.

The helpers borrow parallel owner-local page metadata/backing arrays, requiring
equal lengths and mapping/execution serialization across validation and copying.
They never dereference user virtual pointers. Code must be present/user, readable,
non-writable and executable; stack must be present/user, writable and NX. Complete
ranges are validated before copying, including overflow and holes. The owner must
supply aligned, unique page metadata from its authoritative mapping table.

Entry validates the interrupted target, handler, restorer and complete stack
span through the original red zone before writing a return slot and sanitized
payload. It returns an entry candidate with signal number in RDI, clear DF and
the union of prior/action/signal masks minus unmaskable bits. This helper accepts
ordinary signals 1–31 except SIGKILL/SIGSTOP; it defines no default or pending
signal policy. Errors leave backing unchanged. No active-handler token is added.

Return requires aligned RW/NX payload storage, copies the whole payload to a
local snapshot, decodes CPU state, and freshly checks RX return RIP and the 128
bytes below restored RSP as RW/NX. It writes neither user backing nor Execution.
The eventual runtime owner must publish a successful candidate atomically while
still excluding mapping mutation. Same-domain replay conveys no additional
mapping or capability authority; these checks do not authenticate signal origin.

Eight host tests pass in Debug and ReleaseSafe, including cross-page transfer,
red-zone preservation, changed permissions, missing pages, bad entry targets,
corrupt frames and unchanged backing on failure. A permission-bypass mutant fails
with TestExpectedError. The full host command also passes. These synthetic page
fixtures do not prove native page-table enforcement or actual CPU restoration.
Hardware MXCSR-mask discovery, runtime publication, the pinned musl restorer,
nonlocal escape/repeated delivery and QEMU negative controls remain next work.

## Synchronous native entry/return — 2026-09-07

The [native frame experiment](evidence/shell-signal-native-2026-09-07/README.md)
connects the helpers to native owner state. This supersedes the earlier test-only
status for those helpers. Public sigaction still rejects custom handlers. No
pending/asynchronous signals, interruptible I/O or complete dash support follows.

In `native_runner_local` connections with native threads disabled, experimental
self-upcall `0x29000` takes RX handler/restorer in RDI/RSI, ordinary signal number
in RDX and action mask in R10; R8/R9 must be zero. It addresses only the caller.
The fixed loader stack [0x08000000,0x08010000) bounds entry. It saves a continuation
with RAX=0 and enters the handler through the checked frame. The actual pinned
musl `__restore_rt` issues `0x1000f`; that operation reads the frame at RSP and
restores the continuation. Its argument registers are unspecified and ignored.
Unsupported profiles return ENOSYS; invalid entry/return returns EINVAL without
publishing the candidate. If a restorer cannot handle that error and faults, the
normal fault/lifecycle path applies. Neither operation confers remote authority.

The current exception executes FXSAVE into trusted owner storage. Its MXCSR mask,
with 0xffbf fallback for zero, bounds decoding. The runtime supplies disjoint
candidate scratch; decode/copy helpers may alter scratch on failure, so callers
must discard it. On success, IF=0 and owner-local serialization cover complete
validation, stack writes and publication of frame/FP/mask. FS/TLS, wait state,
mappings and capabilities are never copied from the payload. There is no active
return token for longjmp to strand. This experiment is synchronous, so it does
not interrupt a partly completed descriptor or transport operation.

Native integration exposed a Debug-build stack cost hidden by host tests. The
initial value-returning call chain reserved over 16 KiB and the probe timed out.
Caller-owned output buffers and borrowed frame/request inputs remove the large
copies. The inspected principal entry chain now reserves 0x130 + 0x4f0 + 0xc80 +
0xeb0 + 0x3b0 = 9472 bytes before smaller callees, pushes and interrupt frame,
versus 25608 bytes in those principal frames previously. These are compiled frame
reservations, not a measured high-water bound. The 16 KiB quota is unchanged.
Native callers use decodeCpuInto, prepareEntryInto and readReturnInto.
Value-returning conveniences are private host-test helpers only. Their removal
from the native call chain changes no payload bytes or validation rules.

The new command cases are `cat-roles-startup-frame` and
`cat-roles-startup-frame-skip`. The positive invokes the actual restorer, checks
XMM15 and mask restoration, escapes with actual musl longjmp, then enters again.
It rejects bad entry/restorer pointers, SIGKILL entry and malformed direct return.
The control omits the handler counter update and must produce terminal detail75
and owner result1501. Existing normal lifecycle evidence requires two generations
and four reclaimed domains. Full-suite results and failed attempts are retained
in the packet; these checks do not cover every malformed native CPU frame.

Run the existing complete command-runner command in this reference and M4
regression for this integration, plus the full host suite and ReleaseSafe codec
checks. Adversarial native FP/flags frames, mapped-page changes, nested entry,
full-register/red-zone assembly witnesses and independent consumer review remain
open before general signal adoption. Replace or retire the synchronous probe
operation when the real pending/disposition path has equivalent tested coverage.

## Native forged-frame rejection — 2026-09-07

The [adversarial fixture](evidence/shell-signal-adversarial-2026-09-07/README.md)
adds two command cases without changing the kernel or its ABI. A handler copies
its actual payload to aligned private RW/NX storage and submits modified copies
through `0x1000f`. A naked user-space helper temporarily places that pointer in
RSP and retains the original stack pointer in R11; rejection restores the helper's
context with RAX=EINVAL's negative value. Actual emitted assembly confirms the
helper has no prologue and the handler establishes RBP before locating its payload.
The helper never calls C while using the artificial stack. Acceptance instead
resumes the frame's saved continuation, so it cannot masquerade as rejection.

| Attempt | Required native outcome |
| --- | --- |
| Wrong identity or nonzero reserved header | EINVAL |
| Kernel CS or SS selectors | EINVAL |
| IOPL, TF, VM or missing IF in saved flags | EINVAL |
| Return RIP in the NX staging buffer | EINVAL |
| Noncanonical saved RSP | EINVAL |
| Reserved MXCSR bit31 with forged all-ones payload MXCSR mask | EINVAL; the payload mask cannot authorize FP state |
| Otherwise-valid payload at an unaligned address | EINVAL |

There are twelve attempts per positive generation. Every rejection checks that
payload bytes and the handler's signal mask remain unchanged. The original frame
then returns through musl, and the existing lifecycle oracle requires two normal
generations and four reclaims. The fixture uses 1456 bytes of fixed writable
frame buffers plus a counter; the existing image/memory bounds are unchanged.

`cat-roles-startup-frame-uncorrupted` deliberately omits the first corruption.
The kernel must accept that valid copied frame and resume the saved continuation;
the missing rejection count then yields exact terminal78/owner1501. This control
rejects an always-EINVAL implementation as well as a fixture that fails to observe
successful restoration. Faults, hangs and unsupported operations never pass it.
Run both cases through the complete command-runner invocation above; no separate
runner or kernel mutation flag is introduced.

This covers CPU/header rejection and a mapped NX return target. It does not cover
permission changes between entry and return, nested entry, all-register/native
red-zone restoration or asynchronous transport interruption. Those remain before
general pending/disposition adoption. Public custom sigaction and full dash remain
unsupported. Exact execution results and retained initial attempts are in the
linked packet; earlier evidence and standards pins remain immutable.

## Nested entry and register witness — 2026-09-07

The [native state fixture](evidence/shell-signal-state-2026-09-07/README.md)
uses the existing synchronous operation without kernel, grant or quota changes.
It does not add pending delivery. The existing shell fixture has no memory grant;
permission transitions still require an explicitly granted memory experiment.

Nested C handlers check the outer mask (4|8|512), inner mask
(4|8|512|16|2048), restoration to the outer mask, and restoration to caller mask4.
Two nested calls per generation must preserve the entire outer 720-byte payload
and advance both inner/outer counters. A skipped inner counter must yield exact
terminal79/owner1501. These are synchronous LIFO calls, not asynchronous nested
POSIX delivery or SA_NODEFER semantics.

`user/native-command/frame-registers.S` is a single-context user-space witness.
It saves caller FP state and callee-saved GPRs, sets independent 64-bit GPR values
where the operation permits them, all-ones values in all sixteen XMM registers,
x87 ST0=1 and MXCSR=0x1f80. RAX/argument registers retain the operation's required
values; restored RAX must be zero and RSP must match its recorded address. The
handler destroys live GPR/XMM values, empties x87 and changes MXCSR to 0x3f80;
return must reconstruct the interrupted state through actual musl restoration.

The witness sets status flags 0xed7 and all sixteen qwords of the 128-byte red zone.
Handler entry must observe flags 0xad7 (DF clear); return must restore 0xed7. After
return it stores GPRs without a call, captures flags below the tested red zone,
and checks the snapshots plus every red-zone qword. Cleanup clears DF and restores
caller FP/callee state. Emitted assembly is retained to verify this sequence.
Fixed assembly scratch uses 1176 bytes, plus eight read-only MXCSR bytes; the
nested handler uses a 720-byte local snapshot. All remain within existing bounds.
This samples x87 ST0, not every x87 stack configuration or exception state.

Controls deliberately overwrite saved R12 or one interrupted red-zone word.
Both must yield exact terminal80/owner1501; normal restoration is required for
those controls to reach their C oracle. The positive combines these witnesses
with the prior normal/longjmp checks across two generations and four reclaims.
Cases are `cat-roles-startup-frame-state` and its `-nested`, `-reg` and `-redzone`
controls. The existing full command-runner invocation compiles the assembly with
the pinned Clang target and links it only into these four cases. No new runner or
profile is added. Native permission changes and pending/disposition handling
remain open; full dash and public custom sigaction are not claimed.

## Return payload mapping transitions — 2026-09-08

The command-runner cases `cat-roles-startup-frame-memory` and
`cat-roles-startup-frame-memory-writable` compose the existing `native-memory`
grant with runner-local self-upcalls. Only these cases enable that build option;
no new memory operation, kernel validation switch or quota is introduced.

The handler copies its valid 720-byte return payload into one granted anonymous
page. It attempts return after read-only protection, no-access protection and
unmap. EINVAL must preserve the active mask; restoring access must expose the
same payload bytes. Reallocation after unmap must return zeroed backing. The
positive releases the page and returns through musl. The writable control skips
the transitions: the valid copied frame resumes its saved continuation and must
fail at terminal 81/owner 1501 because the three rejections did not occur.

The existing full command-runner invocation qualifies these cases. This covers
return-payload permissions, not changed mappings of saved RIP/RSP, asynchronous
signals or public custom sigaction. Current results belong in STATE and the
linked evidence packet.

The earlier XMM15/frame loop now reports entry failure as 82, handler-mask
mismatch as 83, XMM mismatch as 84, mask-query failure as 85 and restored-mask
mismatch as 86. Handler-count failure retains 75 for the existing skip control.
These diagnostics preserve the predicates and distinguish a previously combined
75 failure; they do not fix the unexplained intermittent failure retained in the
2026-09-08 evidence packet.

## CPU resume flag normalization — 2026-09-08

A forced scheduler handoff reproduced entry status 82 with captured RFLAGS
0x10293: RF was set in an otherwise valid CPU trap image. Entry now clears RF
in the kernel-owned payload before strict decoding. User-provided return frames
still reject RF; selector, privileged flag, FP and mapping checks are unchanged.
Ordinary scheduler restoration is unchanged. This does not implement debugging.

The full command suite adds `cat-roles-startup-frame-preempt`: 10,000 checked
entries per generation, yielding before entry and inside the handler. It retains
the mask/XMM and longjmp checks and completes two generations/four reclaims.
An isolated version fails before the fix and passes afterward with the same
user payload. Nine host codec tests include the trusted-entry/hostile-return
RF distinction; removing normalization fails that exact test.

The original uninstrumented terminal 75 did not identify its failing predicate.
The amplified reproduction establishes an RF rejection defect in that entry
path; it does not retrospectively add telemetry to the original failure.
[Diagnosis evidence](evidence/shell-signal-diagnosis-2026-09-08/README.md) retains
all attempts and the temporary kernel diagnostic, which is removed from sources.

## Saved return target mappings — 2026-09-08

The `cat-roles-startup-frame-memory-targets` case checks six saved-target
rejections with a valid static payload: saved RSP into a page made read-only,
inaccessible or unmapped; saved RIP into non-executable, inaccessible or unmapped
storage. Each EINVAL must preserve the payload and current signal mask. The
existing memory grant must also deny protect/unmap on fixed code and live stack.

The `-stack-valid` and `-code-valid` controls leave the respective target valid.
They must resume the saved continuation and produce terminal 87/owner 1501 for
the missing rejection count. The alternate-stack continuation consists only of
loading the original RSP and jumping to original RIP; it makes no C call or stack
access before restoring the original stack. Scratch is private to this synchronous
fixture. Positive cleanup unmaps the owned page; control cleanup uses teardown.
The existing full command-runner invocation includes all three cases.

Anonymous pages cannot become executable with this grant, so these tests do not
claim a live RX-to-NX/unmap transition. Fixed executable mappings remain immutable
to this caller. General executable mapping mutation requires a future authorized
contract, not a test-only shortcut. Pending delivery and public sigaction remain
separate work. Results and frozen evidence are recorded in STATE.

## Pending/disposition owner component — 2026-09-08

`kernel/arch/x86_64/native_pending.zig` defines host-qualified domain state for
ordinary signals 1–31 excluding 9/19. It is imported only by the execution host
tests; no native domain contains this table yet. The active facade remains the
only current disposition owner. There is no new syscall or handler-support claim.

One fixed action table and pending bitset require at most 1 KiB, with no heap.
Posts coalesce, IGN discards queued/new occurrences, and replacing a pending
action changes the eventual selected disposition. DFL remains an explicit action
for dispatch to interpret; this component neither executes it nor acknowledges it
as handled. Invalid signal numbers or structurally invalid handler addresses leave
state unchanged. RX mapping checks remain required in the runtime caller.

`peek(mask)` selects the lowest unmasked signal without removing it. The owner
must hold serialization from selection through fresh mapping/frame checks and
publication; only then may `commit(signal)` remove the bit. No retained selection
is valid across a yield, post or action update. Failed frame preparation preserves
the pending occurrence. A later occurrence can be posted while the handler mask
blocks it and becomes selectable after mask restoration. Domain reset clears all
actions/pending bits after stop; no handler-active token requires longjmp cleanup.
The execution mask remains context-owned and is supplied to selection explicitly.

Five owner tests cover coalescing/order/masks, failed preparation, IGN/replacement,
invalid atomicity, isolation/reset and actual frame preparation/return composition.
The import also runs nine existing frame tests. Run:

```sh
zig test kernel/arch/x86_64/native_pending.zig --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig test kernel/arch/x86_64/native_pending.zig -O ReleaseSafe --cache-dir .zig-cache --global-cache-dir .zig-cache/global
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Before native integration, enumerate accepted syscall flags and DFL effects,
protect complete descriptor/transport transactions with the authoritative mask,
and define pending consumption/publication and fatal-frame handling. Remote sends,
SIGCHLD authority, indefinite-wait cancellation/EINTR and consumer acceptance
remain separate requirements. No asynchronous handler may enter the current
unprotected transport merely because this state component passes host tests.

## Default effects and transaction boundary plan — 2026-09-08

The host-only pending component now distinguishes these proposed bounded effects;
it does not dispatch any of them into a running domain:

| Signal numbers | Default effect in the component |
| --- | --- |
| 17 (CHLD), 23 (URG), 28 (WINCH) | Discard new and queued occurrences when DFL is installed |
| 18 (CONT) | Explicit continue effect; unsupported in the first self-delivery admission |
| 20–22 (TSTP/TTIN/TTOU) | Explicit stop effect; unsupported in the first self-delivery admission |
| Other supported 1–31 | Terminate domain; no core-file service implied |
| 9, 19; outside 1–31 | Rejected by this component; no self-send admission added |

Installing a handler on a default-ignored signal does not recover discarded posts;
subsequent posts select that handler normally. Explicit IGN also discards pending
occurrences. Termination must eventually produce an explicit signal/lifetime
result, not a forged normal exit or CPU exception. Its record encoding is not
allocated here. Continue/stop side effects (including interacting pending signals)
and process-group/job control are not implemented by an enum label. Admission
must reject these sends until their lifecycle semantics are implemented.

### Action flags before native wiring

For the first one-argument handler contract, accept public flags zero only. The
pinned musl translation adds raw `SA_RESTORER` (0x04000000), including for DFL/IGN.
The raw custom-handler setter will require that flag and a freshly validated RX
restorer; public zero flags are therefore not raw zero flags. Other raw bits must
reject ENOTSUP before changing dispositions or writing old-action output:
NOCLDSTOP (1), NOCLDWAIT (2), SIGINFO (4), ONSTACK (0x08000000), RESTART
(0x10000000), NODEFER (0x40000000), RESETHAND (0x80000000), and unknown bits.
DFL/IGN raw zero or RESTORER-only records can be represented without calling a
restorer; old-action queries must preserve the accepted record, including mask
and flag fields. The present semantic Action union does **not** yet retain all
those query fields and must not be used as a lossy syscall codec.

This is a proposed setter contract, not enabled acceptance. The current public
startup facade supports DFL/IGN for additional signals through 64 (excluding
libc-reserved 32–34), while this pending component supports 1–31 except 9/19.
Before replacing that facade, resolve this range/query compatibility explicitly;
do not silently narrow existing successful queries or claim real-time delivery.
Mapping changes require validation again at delivery. Neither flags validation
nor a successful setter may advertise handlers before complete entry/delivery.

### Exact bounded I/O guard placement

The next guard must use raw native mask operation `0x1000e` (block all catchable
bits and capture prior mask atomically), with a stack-local prior mask for nesting.
It cannot call the facade's readiness-gated `sigprocmask` during bootstrap. A
failed acquisition permits no mutation or request. An impossible restore fails
closed by terminating the domain; it must never return with an unknown mask.
Restore only after all operation-owned state and output have settled. Preserve
operation results/errno across mask syscalls. Restoring can immediately deliver a
handler that never returns, so nothing essential can remain after that boundary.

| Entry boundary | State that must settle before unmasking |
| --- | --- |
| `startup_begin` | Entire bootstrap receive, binding validation and all descriptor/user-count/readiness publication |
| `fcntl` | Lookup through GETFD read, SETFD update, or duplicate reference increment and descriptor publication |
| `dup2` | Source snapshot, target close (including its full reply), error/poison decision and replacement publication |
| `__aether_io` → `startup_io` → `file_io` | Descriptor lookup/removal, alias decrement, complete request/reply, reply validation, copied read output and poison decision |

A nested `startup_io` inside dup2 must remain under the outer mask. Guarding just
`exchange` leaves the preceding close/alias mutation exposed. Guarding just `move`
allows interruption between sending a request and receiving its reply. On an
unknown close outcome, retain existing poison and consumed-local-alias behavior;
do not retry a possibly applied close. Complete EIO close remains distinguishable
from malformed/unknown reply. Masking does not make a thread-shared FD table safe;
this is still a single-context profile.

Qualification must inject a queued occurrence between alias updates and between
partial transfers, then show delivery only after the outer restore, including
nested dup2/close, rejected operations, known EIO, ambiguous replies and poisoning.
A handler that reads/duplicates or escapes nonlocally must not see partial state.
Indefinite read/wait/pipe transactions require cancellation/EINTR and cannot reuse
this bounded masking strategy indefinitely. These guards and native delivery are
still the next work, not evidence provided by the host default tests.

## Bounded mask guards implemented — 2026-09-08

`startup_begin`, fcntl, dup2 and startup_io now wrap their complete operations in
native block/save and restore calls. The masked bodies preserve existing validation,
reference accounting and poison decisions. Nested startup_io during dup2 restores
the already-blocked outer mask; only the outer completion restores the caller's
mask. A failed acquisition returns without entering the body. Errno is preserved
by the public wrappers and existing __aether_io boundary. The guard uses only
stack-local eight-byte masks and the existing memory-clobbering raw trap.

Restore error exits the entire fixture with normal exit 125, followed by a trap
if the exit unexpectedly returns. This is an internal fail-closed guard failure,
not a signal terminal encoding, graceful cleanup claim or public shell status.
The restore-failure control forces the error branch after an actual successful
restore; it qualifies refusal to resume, not kernel corruption of a mask pointer.
The acquisition control supplies EFAULT before the trap and verifies unchanged
FD/user-count snapshots, transfer count and caller mask.

The native guard probe observes the authoritative mask before every partial
bootstrap/request/reply transfer; checks nested calls, a nonzero caller mask and
errno; and verifies the final mask is restored. The broken-block control rejects
at terminal 88/owner 1501; forced restore error rejects at terminal 125/owner 1501.
Existing duplicate/close, malformed bootstrap and protocol-negative cases remain
part of the complete command suite. These controls do not yet inject queued
asynchronous handlers between stores. Known/ambiguous close outcomes retain their
existing protocol tests; combining those outcomes with live handler/nonlocal-exit
injection remains required before advertising delivery safety. Runtime masks are
now present, but public custom sigaction and asynchronous delivery remain disabled.

## Retained action records — 2026-09-08

The host-only owner now stores one 32-byte record per signal: entry, flags,
restorer and mask at offsets 0/8/16/24. A semantic action is derived from that
record; there is no independently mutable disposition table. The fixed table is
2,048 bytes and State is bounded to 3 KiB including pending bits/alignment. This
replaces the earlier 1 KiB component budget, justified by retaining existing
query fields and range. It allocates nothing in the native runtime yet.

`query` supports 1–64 except 32–34, including immutable initial DFL queries for
9/19. `installRecord` rejects setters for 9/19. Signals 35–64 accept only DFL/IGN;
custom handlers there reject NotSupported. This preserves existing configuration
behavior without enabling queued real-time or reserved-signal delivery. Post and
commit remain limited to 1–31 except 9/19. All masks clear only KILL/STOP bits.

Accepted DFL/IGN records retain zero or RESTORER-only flags, mask and restorer
bytes; the unused restorer is never interpreted as a callable address. Custom
handlers require RESTORER-only flags and nonzero low-half handler/restorer targets
(entry must exceed the DFL/IGN sentinels). Every other flag bit rejects, including
high bits. Validation precedes table or pending-bit mutation. Installing DFL on
CHLD/URG/WINCH or explicit IGN discards queued occurrences as before. Reset clears
the retained records and pending bits together. The old semantic experiment helper
uses this same storage and does not preserve query-only fields when replacing an
action; it is not a syscall setter.

Ten owner tests plus nine frame tests pass in Debug and ReleaseSafe, including
all unsupported flag bits, public query ranges, rejected-update atomicity and
retained query fields. A deliberate mask-loss mutant fails the exact query test.
This closes the host representation gap only: native mapped-RX validation, user
record copy/old-output atomicity, public/raw adapter routing and measured native
placement remain required. No syscall, terminal kind, handler delivery or published
ABI was enabled. Explicit signal terminal encoding and its owner/consumer contract
must precede native self-delivery. Complete guarded I/O and nonlocal-handler
injection remain delivery acceptance requirements.

## Signal terminal candidate — 2026-09-08

**Candidate, not an allocated/published terminal extension.** Existing launch
profiles retain kind 1 normal exit (detail low eight exit bits), kind 2 CPU fault
(detail 128 + exception vector), and kind 3 authorized stop (detail 143). Existing
observe returns detail + 1 for terminal, zero for running, with kind separately
in R8; readiness and yield fields remain independent. Re-observation is retained,
and generation-bound handles plus terminal-before-reclaim remain authoritative.

For a separately qualified signal-capable profile, propose kind 4 with detail the
actual signal number, not 128 + signal. The host-only `defaultTermination` helper
constructs this candidate only for the bounded default-terminate set. It rejects
ignored, stop/continue, unmaskable and unsupported signals. Example distinctions:

| Cause | Kind | Detail |
| --- | --- | --- |
| Application exits 130 | 1 | 130 |
| CPU #UD (vector 6) | 2 | 134 |
| Supervisor requests stop | 3 | 143 |
| Proposed default SIGINT death | 4 | 2 |

A later shell wait/status adapter may present signal 2 as status 130 after its
own defined wait encoding. That presentation must not overwrite the retained
cause. No core-dump bit/file, stop/resume event, process group or POSIX wait word
is implied. Failed handler-frame preparation should terminate with a specified
signal cause (proposed SIGSEGV/11) without recursively attempting another handler;
this fatal path is separate from the default-action constructor and is not enabled.

Before emission, native finish must stop all contexts, settle channel ownership,
retain the cause and increment the observation revision once using existing
quiescence/reclaim rules. Repeated observe/stop must preserve the first terminal
cause; reuse must reset it. No normal-exit helper or CPU-fault tag may stand in for
signal death. The private signal qualification profile must explicitly select
an owner accepting the candidate and must not route it through legacy result
parsers. No build option/profile number or protocol version is allocated here.

### Consumer compatibility and adoption gates

The captured userland runner-result decoder rejects kind outside 1–3, preserving
output on rejection. Its normal exit 130 remains 130; fault/stop map to failure 1
only after accepted collection and complete cleanup. The compiled host witness
checks those existing cases and kind-4 rejection for details 1–31. The captured
sys-init native-command lifecycle adapter also rejects outside 1–3 as an unknown
boundary result; this was source-inspected, not independently executed here.
See the [frozen inputs and evidence](evidence/shell-signal-terminal-2026-09-08/README.md).

Therefore do not emit kind 4 on existing ABI9 profiles, use an overloaded old tag,
or silently widen the legacy decoder. First qualify a private native signal owner,
then coordinate an explicitly selected profile and versioned command-result
extension with both consumers. Sys-init must retain signal cause while applying
its own lifecycle/restart policy; userland owns runner mapping and future wait
semantics. Required cases include exact signal kind/detail, normal exit with the
same eventual shell status, CPU fault and stop controls, retained observation,
stop-after-terminal, cleanup/reclaim/reuse and legacy-profile rejection. Consumer
source compatibility does not confer independent acceptance.

This host contract is a prerequisite for native wiring, not proof of signal
termination or an unblock for either consumer. Native record copies, delivery,
guarded close/error and nonlocal-exit injection remain required before dash.

## Private native action-copy operation — 2026-09-08

`-Dnative-signal-actions=true` selects action-copy qualification and requires the
existing runner-local native image. The operation rejects ENOSYS unless selected
in the connection profile with native threads disabled. It is not public
sigaction, is not forwarded by the C facade, and does not deliver signals or emit
candidate terminal kind 4. No legacy producer selects the option implicitly.

Private trap `0x29001` uses RDI signal, RSI optional input record, RDX optional old
record output, R10=8, R8/R9=0. Records are the retained 32-byte x86_64 layout above.
The operation accesses only the caller's domain; a numeric signal or pointer grants
no access to peers. Query restrictions, setter flags, masks and range rules follow
the retained-record owner. ENOTSUP is -95, invalid shape/target/record is -22 and
invalid input/output memory is -14. With multiple simultaneous invalid arguments,
no relative error-priority contract is offered.

Input is fully snapshotted before output validation, permitting exact overlap and
cross-page records. Every old-output byte must be caller writable before record
mutation. Custom handler/restorer pages must be present user RX and not writable;
DFL/IGN retain the unused restorer without calling it. Record validation then
commits, and old bytes are copied under the same IF=0 owner serialization. There
is no yielding or mapping mutation in that interval. Input/output buffers are
owned stack snapshots, never retained user pointers. Future delivery must check
mappings again; registration is not a permanent executable grant.

The opted-in build adds one fixed State per native domain (64 records plus pending
bits, currently 2,056 bytes each). The disabled build uses a zero-sized field.
Reclaim clears the state after terminal/quiescence and mapping detachment; pending
state is never selected by this operation. A worker leaves an installed handler
behind so the next generation must observe all-zero DFL. Existing instance grants,
user memory bounds, termination tags and reclaim counts remain unchanged.

The native copy probe exercises an in-place record spanning two pages, returned
old bytes, retained flags/restorer/mask, unsupported flags without output mutation,
input/output overflow, read-only code as output, NX data as a handler, valid RX
handler/restorer registration, and two-generation reset. The identical operation
in a disabled build must return ENOSYS. Both clients continue the existing shell
startup and I/O fixture; they do not execute the installed handler. Broader missing
page/protection-transition cases, pending delivery and a signal-capable owner still
precede consumer adoption. Evidence and failed build attempts are retained in the
[private copy packet](evidence/shell-signal-action-copy-2026-09-08/README.md).

## Private action-copy mapping transitions — 2026-09-08

The action-copy memory variant uses the existing explicit anonymous-memory grant
and places its 32-byte record across two pages. Its second page is successively
read-only, inaccessible and unmapped. Old-output copies reject EFAULT in all
three states before changing the installed action or writable 16-byte prefix.
Input copies reject EFAULT for inaccessible/unmapped tails and leave old-output
storage untouched. Read-only input succeeds, returning the previous action; the
probe restores the baseline and verifies the displaced record.

Restoring protection preserves the entire record. Remapping the missing page
returns zeroed backing while preserving the live first-page prefix. Both pages
are then unmapped. Inaccessible/unmapped handler and restorer targets reject
EINVAL without changing the old-output or installed action. These checks do not
grant executable anonymous mappings or change fixed code/stack protections.

The writable-output control skips the permission/removal changes: the copy succeeds
and must fail the expected-rejection check at terminal 90/owner 1501. The positive
still runs the existing startup/I/O path across two generations and four reclaims.
No kernel runtime logic changed; the stale pending-state header now distinguishes
native opt-in record copies from host-only pending delivery. Native peer isolation,
self-delivery and signal-capable terminal observation remain next qualification.
See the [mapping evidence](evidence/shell-signal-action-mappings-2026-09-08/README.md).

## Native action-record peer isolation — 2026-09-08

The private peer case installs signal10 IGN with mask16 and an unused restorer
value29 in the supervisor before launching either client generation. Each client
must independently observe initial DFL, then install its RX handler/mask4 using
the existing action-copy probe. The supervisor checks its exact retained record
during complete client I/O requests, after terminal observation, and after client
reclaim. Thus client writes and generation reset must not affect the live peer.
The supervisor's own record remains installed across both client generations.
No cross-domain selector or additional signal authority is introduced.

`-Dnative-signal-actions-shared=true` is an explicit negative option: it routes
record storage to worker0 for this isolation rejection test, while user-memory
validation still uses the caller. Worker admission resets that shared table, and client action updates also target
it. The supervisor's exact record query then rejects at owner1591/reclaimed0.
The separate initialization check is owner1590; no client terminal is required
for this retained peer-record failure. The option is classified negative and
rejected by `-Drelease-artifact=true`; it is not a supported ownership mode.
Default builds and all ordinary private action operations still select caller
storage. No terminal kind4 or handler delivery is enabled by this experiment.

The positive retains the existing two generations/four reclaims and normal file
protocol. This qualifies supervisor/client record separation and reclaim isolation,
not a remote-signal API or thread-shared dispositions. Pending self-delivery and
signal-capable terminal retention remain the next work. See the
[peer-isolation evidence](evidence/shell-signal-peers-2026-09-08/README.md).

## Private explicit self-delivery — 2026-09-08

In the native-signal-actions runner-local non-thread experiment, trap 0x29002
posts RDI to the caller only, or polls when zero; all other arguments must be
zero. Signals 1–31 except 9/19 are bounded coalesced posts. Invalid arguments
return EINVAL; default non-ignored actions return ENOTSUP before posting.
At most one unmasked handler enters per call using the existing checked frame
and authoritative mask. Failed preparation retains pending state. A disposition
changed to default while pending returns ENOTSUP without dequeue. Ignore drops
posts. No mask operation, timer, handler return or I/O boundary auto-delivers.
Legacy builds return ENOSYS. Pending state resets with domain reclaim.

This private integration does not enable public kill/sigaction or terminal kind4.
See [qualification](evidence/shell-signal-self-2026-09-08/README.md).

### Pending self-delivery retry qualification

The native retry fixture polls with null, insufficient, out-of-bounds and high
stack positions. Each must reject with EINVAL while preserving the installed
record, mask and pending occurrence. Retrying on the normal stack without another
post must deliver once; a second poll must not duplicate delivery. A deliberate
ignore/reinstall between failure and retry must fail client92/owner1501.
This exercises existing frame bounds without changing immutable executable
mappings. See [evidence](evidence/shell-signal-retry-2026-09-08/README.md).

## Private retained signal termination — 2026-09-08

The separately selected native-signal-termination experiment requires private
actions and a matching Rust owner. Default terminating self-posts may queue while
masked; an explicit poll with an eligible signal commits kind4/detail signal
through existing terminal publication. The supervisor and unsupported stop/continue
effects reject with ENOTSUP. Existing action-only builds retain their rejection.
Repeated observe and stop preserve the cause; reclaim invalidates the handle.
This is not an extension adopted by ABI9 consumers or a public signal API.
See [evidence](evidence/shell-signal-termination-2026-09-08/README.md).

### Signal termination with live resources

The private live-resource fixture self-terminates with signal15 before copying,
after an 11-byte copy or after a 16-byte diagnostic prefix, with descriptors still
live. The existing owner verifies retained cause, exact bytes, backend retirement,
channel closure and stale-handle rejection across two generations. Deliberately
corrupted output and skipped backend close must reject separately. These are
between-operation hooks, not asynchronous interruption of a partial IPC request.
See [evidence](evidence/shell-signal-live-2026-09-08/README.md).

## Private successful-mask return delivery — 2026-09-08

Separately selected native-signal-mask-delivery requires private actions. After
a successful native mask call, the kernel prepares at most one eligible custom
handler using the committed syscall frame and mask. Failed mask calls do not
deliver; failed preparation preserves the successful syscall result and pending
occurrence. Default termination is excluded from this automatic boundary.
Existing explicit post/poll and frame return remain unchanged; no timer, I/O or
handler-return injection is enabled. This is a private guard-boundary experiment,
not public sigaction adoption or full guarded/nonlocal-handler qualification.
See [evidence](evidence/shell-signal-mask-return-2026-09-08/README.md).

### Automatic preparation failure and retry

At four invalid stack positions, the automatic-entry fixture requires successful
unmask to return zero and copy the old mask, then a query to report the committed
zero mask without handler execution. The action record must remain unchanged.
A normal-stack query then delivers once without reposting; deliberate discard
rejects at client94/owner1501. See [evidence](evidence/shell-signal-auto-retry-2026-09-08/README.md).

### Guarded I/O handler reentry

A fixture hook queues signal10 at the end of a masked read. The handler must wait
for mask restoration, then duplicate/close a descriptor and write D-newline through
the same guarded transport. The original read and copy must complete with exact
backend bytes and cleanup. Skip-restoration rejects client95/owner1501. This is
post-operation reentry, not interruption of partial IPC or a nonlocal exit.
See [evidence](evidence/shell-signal-guard-live-2026-09-08/README.md).

### Nonlocal exit at the guarded return boundary

The private fixture uses pinned musl sigsetjmp/siglongjmp to leave a handler after
its descriptor and diagnostic operations. It verifies the restored zero mask,
forwards the completed 11-byte read from static storage and resumes normal copy
and cleanup. Saving no mask must fail client96/owner1501. No kernel handler-active
slot or new return protocol is introduced. This is a completed-read witness, not
general partial IPC cancellation. See [evidence](evidence/shell-signal-nonlocal-2026-09-08/README.md).

### Guarded known-error handler entry

The fixture injects a pending handler at failed fcntl (EBADF) and denied alias
write (EACCES) return boundaries. The handler deliberately changes errno; each
wrapper must report its original error and preserve usable descriptor state,
then finish exact copy and cleanup. Skipping fcntl errno restoration rejects
client97/owner1501. Ambiguous replies and nonlocal error exits remain separate.
See [evidence](evidence/shell-signal-errors-2026-09-08/README.md).

### Handler entry after ambiguous replies

Malformed and truncated first-read replies must poison before handler entry.
Handler write/close calls return EIO with no further channel traps. The caller's
read buffer stays unchanged; local descriptor retirement and owner backend cleanup
complete across two generations. Skipped injection rejects client98/owner1501.
This is post-reply handling, not arbitrary partial-request cancellation.
See [evidence](evidence/shell-signal-poison-2026-09-08/README.md).

### Nonlocal exit after an ambiguous reply

The combined fixture leaves the poisoned-read handler via musl siglongjmp. It
checks restored mask, unchanged static buffer, retained poison and no post-poison
channel calls during remaining local cleanup. The abandoned read supplies no
return/errno result. Saving no mask rejects client99/owner1501.
See [evidence](evidence/shell-signal-poison-jump-2026-09-08/README.md).

### Ambiguous close with handler/nonlocal entry

The early-close fixture checks fd10/input binding retirement before handler entry
on malformed/truncated close replies. Returning and siglongjmp handlers preserve
poison and local cleanup; repeated close returns EBADF without channel traffic.
The owner checks zero copied/read bytes and backend cleanup. Deliberate alias
resurrection rejects client100/owner1501.
See [evidence](evidence/shell-signal-close-2026-09-08/README.md).


## Public signal routing review — 2026-09-08

This source review follows the 284-case private close qualification. It selects
implementation work; it does not qualify public signals or accept full dash.
The exact reviewed inputs are hashed in
[evidence](evidence/shell-signal-public-review-2026-09-08/inputs.sha256).

| Boundary | Existing coverage and compatibility issue | Required work |
| --- | --- | --- |
| Public disposition | Startup facade keeps a separate C action table and accepts only DFL/IGN with flags zero. Private 0x29001 owns checked native records, including handlers. | Route an opt-in real-musl sigaction witness to that native owner; do not advertise the facade table as kernel agreement. |
| Raw calling convention | Pinned musl sigaction uses four arguments at 0x1000d. Its x86_64 transport does not initialize R8/R9; private 0x29001 requires both zero. | Validate the four public arguments without imposing private reserved-register rules. Preserve the private rejection contract. |
| Wrapper flags | Musl adds SA_RESTORER even for DFL/IGN; its signal() adds SA_RESTART and calls __sigaction. Dash ignores some signal setup errors and uses signal() for ignores. | Test actual wrapper records and errors. Keep SA_RESTART unsupported in the first agreement witness; do not silently accept restart semantics or treat a prompt as successful setup. Resolve dash's signal() path before its handoff. |
| Signal production | Private self-post/poll and mask-return delivery pass. Musl raise() instead invokes tkill using its thread ID. | No public raise/kill success until identity, authority and supported targeting are explicit. SIGCHLD needs a lifecycle-owned producer; a numeric PID is insufficient authority. |
| Delivery | Checked stack/restorer, nesting, nonlocal return, guarded I/O, errno and poisoned close combinations pass privately. Automatic delivery is limited to a successful mask operation. Failed automatic frame preparation retains pending state. | Define broader safe delivery points, indefinite-I/O interruption and fatal frame-failure behavior before expanding advertised semantics. No timer or arbitrary partial-request cancellation claim. |
| Terminal consumer | Private signal terminal kind4 is qualified with its selected fixture owner. The reviewed sys-init native-command decoder accepts only kinds1–3. | Preserve legacy profiles; obtain matching consumer implementation and acceptance before handing off signal termination. |

### Next bounded implementation and acceptance

Requirement: prove actual pinned musl public sigaction and raw action operations
observe one native-owned disposition in a separately selected experiment. Disable
the startup C sigaction override only in that selection; keep the existing
consumer profile intact. Reuse the checked record operation with explicit public
arity handling. No second action table, callback registry or new service is needed.

Acceptance must include DFL/IGN and flags-zero custom registration through musl,
public/raw old-action and mask agreement, nonzero unused R8/R9, actual restorer
entry/return and nonlocal exit after public registration. Include unsupported
flags (including signal()'s SA_RESTART), bad pointers/permissions and atomic
failure, plus a deliberate broken routing control. Preserve disabled-profile
ENOSYS and private reserved-register rejection. Select the complete command suite,
host/pin/workflow checks and affected architecture regressions on frozen sources;
retain every attempt. Actual dash and affected-owner acceptance remain separate.

Authority and resource review: existing per-domain records, mapping checks, stack
ownership, quotas and reclaim remain authoritative. The revised assembly/FFI
boundary must distinguish public and private arity without relaxing pointer,
RX-restorer, overlap or transactional copy checks. No sibling, release pin or
public default changes are authorized by this review. Update this reference,
STATE and the existing workflow inventory when adding the selection.

Simplicity (SE-01–SE-05): directly reusing the existing native owner is simpler than
synchronizing two disposition tables. Keeping the C facade alone cannot demonstrate
real libc/kernel agreement. The temporary opt-in selection protects current
consumers; retire the old table only after replacement qualification and consumer
adoption. No runtime complexity is removed in this documentation-only review.
Public signal routing is the next step; child notification, exec/wait, pipes and
consumer integration still precede full-dash acceptance and the OpenZFS audit.


### Experimental public action selection

`-Dnative-signal-public=true` requires the existing private action selection and
runner-local profile. It routes four-argument 0x1000d through the existing checked
record operation; R8/R9 are unused here, but remain reserved-zero for 0x29001.
The selected C fixture omits its sigaction override and disposition table, linking
actual pinned musl sigaction/signal/restorer code. Custom handlers accept only
SA_RESTORER; DFL/IGN also retain inert SA_RESTART under the follow-up review below. Public signal production and legacy terminal profiles are unchanged.

The `cat-roles-startup-public` command case checks public/private record agreement,
DFL/IGN/custom actions, musl-added restorer, unsupported custom signal() flags, failed-copy
atomicity, RW/NX handler and read-only output rejection, private reserved-register
rejection, handler return and siglongjmp mask restoration. It then completes the
existing descriptor/copy/reclaim protocol. The disabled-routing control must fail
client101/owner1501; older startup selections require raw 0x1000d ENOSYS.
Run the existing complete command-runner invocation above, `zig build test` and
`scripts/regression.py` on frozen sources before qualifying this selection.

### Dash default/ignore flag review — 2026-09-08

Requirement: pinned dash trap.c uses signal(signo, SIG_IGN); redir.c also uses
signal(SIGPIPE, SIG_DFL). Its setsignal custom handlers use flags zero. Pinned
musl signal() adds SA_RESTART and calls __sigaction. In the experimental public
route, retain SA_RESTART only for DFL/IGN records: these dispositions never enter
a handler, so no interrupted handler return requires syscall restart. Reject
SA_RESTART for custom handlers and every other unsupported flag, atomically.
Keep private 0x29001 setter validation unchanged, including when an old public
record is queried through it. This is flag storage for non-handler dispositions,
not an implementation of interrupted syscall restart or public signal delivery.

Before implementation: reuse the native owner's checked record mutation with an
explicit allowed-flags argument internally; public/private entry points choose
their fixed masks. No new option, service, record field, resource, authority or
borrowed pointer. Existing IF=0 serialization, mapping checks and cleanup apply.
A wrapper shim would hide actual musl behavior; accepting restart for all actions
would promise missing semantics. The shared validator avoids duplicated mutation;
no consumed compatibility path is removed (SE-01–SE-05).

Select host tests for public/default/ignore flag retention, all unsupported flag
bits, custom restart rejection, pending discard and unchanged private rejection.
Extend the real-musl native witness to check signal() return values, retained
flags, ignored pending/future posts, DFL restoration, invalid SIGKILL and failed
custom replacement. A skipped ignore update must reject at client101/owner1501.
Run the complete command suite, host/pin/workflow checks and M4 regressions on
frozen sources. Update this reference, workflow and STATE; preserve evidence and
release pins. Actual dash setup and affected-owner acceptance remain separate.

### Actual dash signal setup experiment — 2026-09-08

Pre-code requirement: execute pinned dash setsignal/ignoresig/onsig code against
experimental public dispositions. Import the 32 unchanged userland reference
objects with their hash receipt and COPYING, and verify every object before link.
Wrap main at link time to enter the bounded conformance client; dash main/init,
command execution and job control are not exercised. No successful syscall stubs
or replaced dash signal functions. The fixture sets existing dash option state
for a root interactive shell with job control disabled, invokes SIGCHLD setup and
SIGINT/QUIT/TERM setup, then queries actual native records and calls ignoresig.
Deliver SIGCHLD through private self-post to verify dash's real onsig path.

Expected: SIGCHLD/INT use onsig with musl restorer; QUIT/TERM and ignoresig use
IGN, with checked masks/flags. A skipped SIGCHLD setup must fail client102/owner1501.
Reset dispositions before existing descriptor/copy/reclaim checks. No new kernel
primitive, quota, authority, public delivery or signal terminal profile. Preserve
third-party terms and source provenance; captured Linux configuration remains an
explicit fixture limitation. Run host/pin/workflow and complete command suite.
M4 runtime is unchanged from the immediately prior qualified source revision.

Simplicity: reuse actual objects instead of extracting or imitating signal policy.
Only the entry point is wrapped; retained dash functions resolve normally. This
adds a bounded integration input, no runtime service or compatibility shim. It
cannot qualify all of dash init or replace consumer acceptance. Record exact ELF
and source evidence, and preserve any failed build/admission attempts.


### Actual main/init prerequisites review — 2026-09-08

This is a source review, not a new native execution claim. The preceding 289-case
packet ran real signal routines through wrapped main. Reading the pinned generated
init.c shows why that result cannot establish complete shell initialization.

| Startup operation | Current contract and failure mode | Next required evidence |
| --- | --- | --- |
| main sets mypid/rootpid using getpid | Caller identity is supported in the selected native profile. | Enter real main, verify shell identity agrees with the generation-bound native identity. |
| initvar calls geteuid for PS1 | No effective-user metadata contract exists in this profile. Musl returns the raw syscall value, with no errno conversion; ENOSYS becomes a nonzero uid_t. | Define explicit informational user metadata and provenance before exposing this call; never infer capabilities or privilege from UID zero. |
| generated init sets PPID using getppid | No parent identity query is routed. Musl returns raw -38, which generated init formats as a parent number without checking. | Define the logical parent and lifetime contract with the launcher; a supervisor or connection owner is not automatically a POSIX parent. Query metadata must confer no target authority. |
| generated init validates inherited PWD with stat64, then setpwd calls getcwd when needed | Current named-file service explicitly has no cwd or directory traversal. getcwd fails; dash warns and can continue with an empty directory string. | Add a capability-scoped directory/working-directory contract in userland, with validated startup grant and honest getcwd/stat behavior. A literal slash or trusting environment PWD is insufficient. |
| setvareq/setpwd and later parsing allocate | Native memory primitives and SDK adapter exist, but the signal selection did not require heap allocation. | Select the existing memory grant and qualify real initialization allocation, denial and cleanup; do not raise quotas without measured need. |
| procargs calls optschanged and may detect terminals or enable job control | Signal setup is bounded-qualified; interactive terminal/job-control behavior is not. | First select explicit non-login, noninteractive -c with empty controlled environment and job control off. Serial interactive startup remains a later acceptance case. |

Next executable experiment: invoke the real generated init with the existing
scoped memory grant and a controlled environment; capture actual PPID, PWD and
installed CHLD state. Treat invalid metadata or missing directory semantics as
expected diagnostic evidence, never successful startup. Then implement the
smallest truthful parent/user-metadata and directory contracts before a positive
real-main command case. Full shell acceptance must inspect these initialized
values as well as command output, exit status and cleanup. Add semantic negative
controls for fabricated/missing metadata and directory grants.

Ownership: kernel retains local process identity/lifetime and capability checks;
launcher supplies explicitly defined relationship metadata; user-space namespace
service owns directory meaning. No ambient UID privilege, PID-based signaling,
global cwd or fabricated successful stat/getcwd. Shared normative changes require
the canonical standards owner; local experiments do not silently extend sibling
contracts. No implementation or sibling acceptance is asserted here.

Simplicity (SE-01–SE-05): the simpler initial test is a controlled noninteractive
command with no profiles or external programs. That reduces startup inputs but
cannot remove generated init's unconditional metadata/directory work. Success
stubs would conceal missing contracts. Reuse existing memory and service grants;
no new service or abstraction is selected by this review. No runtime complexity
is removed yet. This review changes documentation only, so host/pin/workflow and
snapshot verification are selected; no fresh QEMU result is claimed.

### Generated-init diagnostic execution — 2026-09-08

Before code: select the existing native memory grant for a new dash-init fixture,
link the unchanged pinned objects and call generated init with an empty environment.
Require initialized IFS/OPTIND, CHLD handler, PPID=-38 and empty PWD under today's
unsupported metadata/directory calls; check geteuid's raw unsupported result.
The owner must observe the exact upstream getcwd warning, followed by ordinary
copy and two-generation cleanup. A skipped initializer rejects client103/owner1501.
These are diagnostic expectations of known missing behavior, never positive shell
startup criteria. Replace the expectations when truthful contracts are implemented.

No new kernel API, option, authority or allocation policy: reuse the existing
memory selection. Preserve upstream diagnostic text and current machine markers.
Use the full command suite, host/pin/workflow checks and exact source/artifact
receipts; preserve all attempts. Kernel bytes are unchanged from prior M4 evidence.
This fixture may reveal further prerequisites; do not hide a failed init with a
success stub or relax its oracle. Full main and consumer acceptance remain open.

### Bounded startup identity contract review — 2026-09-08

Requirement: replace the observed invalid PPID and effective UID with truthful
metadata, while keeping capability authority independent. Apply Foundations
O-01–O-04 and proposed Distribution ID-01/02. This is a local experimental contract
review; it neither updates released pins nor assigns authentication policy to the
kernel. No new runtime behavior is claimed by this section.

The next implementation is parent identity alone, in a separately selected
runner-local, single-context profile. For this profile, define the logical parent
as the direct authorized native launcher. All admitted workers are created by the
fixed supervisor through control/launch operations. The root supervisor is loaded
by the kernel, has no user-process parent, and cannot be replaced while workers
remain running. Thus the root query returns zero; a worker query returns the
supervisor's existing generation/slot identity. In the current AENMX001 profile
that is 4 (generation zero, slot three), but implementation computes it using the
same identity formula as getpid, rather than storing a magic PID.

Public getppid is a zero-argument musl syscall (0x1006e). All argument registers
are unused, not reserved-zero. Gate it to the selected connections/runner-local
profile without native threads; disabled and other profiles retain ENOSYS. The
result is information only: it cannot be used as a launch, stop, channel, memory
or signal capability. No new parent table, mutable slot, resource pool or orphan
policy is needed within this fixed lifetime. Reparenting, detached children,
parent replacement, fork/exec identity and general process trees need a later
explicit contract before extending this bound.

Acceptance: actual musl getppid must agree with the supervisor's independently
queried getpid across two worker generations and both worker slots; the root
must query parent zero. Dirty unused argument registers must work. Substitute a
worker/self or stale identity and require rejection. Preserve existing capability
denial and exact-stop/reclaim tests. Generated init must now produce the actual
parent string, while still reporting the separate UID/CWD gaps. Keep the old
unsupported diagnostic selected separately so no legacy default silently changes.
Run host/pin/workflow, full command and M4 regressions on frozen sources.

User/group identity is a separate next contract. Its compatibility values must
come from a validated launcher/session record whose provenance and lifetime are
explicit, with real/effective UID and GID distinguished. The current AECAT001
bootstrap contains descriptor roles, not principal metadata; neither those roles,
PID, nor ownership of a launch capability determines a Unix account. Do not
return a convenient zero/1000 or copy an environment value to make init pass.
The developer-only profile may declare a fixed unauthenticated compatibility
principal in user-space launch policy, but that record and its admission path
must be specified and tested before public identity calls succeed. UID zero
cannot enlarge capabilities. No login/authentication or ID-02 adoption follows
from such an experimental record. Sys-init/userland retain policy and SDK roles;
affected-owner acceptance remains separate from producer qualification.

Simplicity (SE-01–SE-05): computing the bounded direct-launcher parent is sufficient
because replacement/orphaning cannot occur in this profile. A general process
hierarchy would add unsupported policy and cleanup now. User metadata cannot be
inferred from that relation, so keep its admission contract separate rather than
adding arbitrary kernel account constants. No existing compatibility code is
removed by this review; future broader parent semantics must replace this bound
explicitly, with consumer and lifetime evidence.

### Parent-query selection

`-Dnative-parent-identity=true` requires runner-local and rejects native threads.
In the connections profile, raw 0x1006e returns zero for the kernel-loaded root
supervisor and its computed generation/slot identity for direct-launched workers.
Unused registers are ignored per musl's zero-argument call. Disabled profiles
continue returning ENOSYS. No parent table, new authority or wire field is added.

The dash-init-parent cases check actual musl and raw query agreement, generated
PPID=4, supervisor getpid=4/getppid=0, and both worker slots across two generations.
The swapped-slot case changes the test placement, not launch permissions. The
existing identity check still validates each client's actual generation/slot.
Disabled routing and self-PID substitution reject client104/owner1501. Ordinary
copy and four reclaims must complete. Existing init diagnostics still require
PPID=-38 outside this selection; effective-user and CWD gaps remain unchanged.
Run the complete command suite, host/pin/workflow checks and M4 regressions as
selected by the pre-code identity contract above.

### Launcher-supplied user/group metadata review — 2026-09-08

Requirement: give the selected dash initializer truthful compatibility identity
without inventing kernel account policy. The current role bootstrap has no user
metadata. This review selects an experimental AECAT002 record and C startup
adapter integration, not a new kernel credential service or shared release.
Foundations O-01–O-04 and proposed Distribution ID-01/02 apply: the Rust launcher
owns the declared compatibility view; existing kernel capabilities enforce all
access. UID/GID values, including zero, never authenticate a principal or confer
native rights. No setuid/setgid, supplemental groups, login or authentication
profile is implemented by this proposal.

The separately compiled selection accepts exactly 160 bytes: the existing
128-byte descriptor bootstrap with magic AECAT002, followed by this 32-byte
little-endian metadata record. Legacy AECAT001 bytes remain unchanged. Each
selection rejects the other version; no implicit fallback or reinterpretation
of reserved v1 bytes.

| Absolute offset | Field | Validation |
| --- | --- | --- |
| 128 | real UID, u32 | Reject UINT32_MAX, reserved as the failure/sentinel value. |
| 132 | effective UID, u32 | Same; distinct from real UID, including zero. |
| 136 | real GID, u32 | Same; no supplementary group implication. |
| 140 | effective GID, u32 | Same; distinct from real GID. |
| 144 | source kind, u32 | Exactly 1: explicitly declared developer-only compatibility view, unauthenticated. |
| 148 | flags, u32 | Zero. |
| 152 | reserved, eight bytes | All zero. |

Read the fixed 32-byte header first and reject an unsupported version before
waiting for its body; otherwise a v1 sender can wait indefinitely while a v2
receiver expects another 32 bytes. Stage the selected body before publication.
The existing header generation binds the complete record to the admitted worker.
The delegated startup endpoint supplies its provenance; environment variables,
PID arithmetic, role numbers and caller text do not. Stage and validate all
160 bytes, including every descriptor and metadata field, before publishing any
binding or getter value. A short/malformed/stale record publishes nothing. The
existing transport poison and lifetime cleanup rules still apply; version mismatch
with unread bytes must be accounted for by owner teardown, not silently retried.
Fixed local costs are 32 additional startup bytes and four cached u32 values;
no new kernel object, grant, queue or resource pool is selected.

The selected adapter supplies getuid/geteuid/getgid/getegid from the validated
record once startup_ready is committed. Before admission, return the reserved
all-ones value with errno=EAGAIN. These are genuine metadata lookups, not constants
chosen to conceal unsupported syscalls. Raw SDK/kernel UID/GID operations remain
ENOSYS and must be documented as such; no raw/public agreement is claimed. The
cache is advisory process-local data: other services must never accept it as
proof of principal identity. Kernel policy does not read it. Future SDK adoption
must explicitly select this startup contract and retain its provenance rules.

The Rust conformance owner will explicitly declare different tuples across two
fresh launches (including distinct real/effective and user/group values), proving
that replacement does not reuse an old cache. A separate zero-UID case must keep
read-only input writes and foreign capability operations denied. Actual dash
initvar must choose PS1 according to the supplied effective UID; PPID still comes
from the already-qualified native parent query. PWD/getcwd remain an independent
known gap. Do not label these results authenticated or full-shell startup.

Before implementation, select these controls in the existing complete command
suite: valid tuples, zero effective UID, generation reuse, before-ready queries,
truncated record, wrong source kind, nonzero flags/reserved, sentinel fields,
stale generation, mismatched versions, and a skipped metadata-publication mutant.
Invalid inputs must leave every descriptor and metadata getter unpublished and
preserve owner cleanup, including unread transport bytes. Update the existing
malformed-bootstrap oracle for the public-signal selection: own-domain raw
sigaction is independent of descriptor admission and cannot be used as a proxy
for startup_ready. Check readiness through descriptors and metadata getters.
Retain exact output, terminal and cleanup evidence. Run host/pin/workflow and the
complete affected native suite on frozen sources before qualification.

Simplicity (SE-01–SE-05): one extra fixed bootstrap record reuses the existing
launcher and validation boundary; no account server or kernel UID policy is
needed for this requirement. Reusing v1 reserved bytes or deriving IDs from roles
would conceal the changed meaning. Preserve v1 for current consumers; remove it
only after replacement qualification/adoption. No implementation is removed or
new runtime behavior enabled by this review. Sys-init/userland acceptance and any
future cross-project normative standard remain separate work.

### Selected metadata fixture

The dash-init-parent-identity cases compile STARTUP_IDENTITY and send AECAT002.
The declared owner policy supplies real UID=1000+generation, effective UID=real+10,
real GID=real+20 and effective GID=real+30; a separate zero-effective-UID case
checks dash's root prompt selection while input writes and PID-based stop remain
denied. The decoder reads the version header before the selected body; legacy
AECAT001 layout and metadata-free getters remain unchanged. Invalid metadata
must return client110 with four reclaims; skipped publication rejects at 105/1501.
Source/flags/reserved, each sentinel ID, stale generation, truncation and both
version directions are selected controls. Header-only mismatch and truncated
senders close their writer explicitly; owner cleanup accounts for that consumed
endpoint. This is developer compatibility metadata, not authentication.

### Scoped directory/CWD contract review — 2026-09-08

Requirement: the next generated-init experiment must obtain its working-directory
name from a delegated directory object and validate inherited PWD against that
object. It must not return a guessed slash, accept environment text as authority,
or claim the existing stream backend is a persistent directory tree. This is a
local conformance contract, proposed for implementation; no new runtime behavior
or SDK default is enabled by this review.

The inspected pinned generated init imports environment variables, then compares
stat64(PWD) and stat64(".") by device/inode before retaining an absolute PWD.
Otherwise setpwd calls getcwd with a caller-owned PATH_MAX buffer. The first
positive witness must exercise both paths, not merely provide an empty environment
to avoid stat. Keep real upstream init/cd objects unchanged.

Ownership and applicable clauses: Foundations O-01–O-05 and I-01–I-06 require
explicit delegation, owner enforcement, bounded messages and cleanup. Proposed
Distribution PX-01/03 keeps POSIX translation in user space and consumer acceptance
separate. Aether owns this fixture's native endpoints and Rust conformance owner;
userland owns SDK integration and shell acceptance; sys-init retains session and
bootstrap policy. This does not assign the production filesystem service. Shared
normative changes remain Aether-standards work; released pins stay fixed.

#### Selected bounded namespace

Add one immutable directory object to the existing Rust conformance owner for
this selection, with the visible name `/work`. This represents a private fixture
namespace, not a mount in a machine-global tree. Its service instance and object
identity are distinct from the client generation. The owner binds a fresh query
reference to the admitted client's connection and generation. The directory does
not alias a stream descriptor; fd 0/1/2, their offsets and backend handles retain
their existing meanings. Directory queries are read-only and allocate no open
records. Neither UID zero, path text nor a copied reference from another connection
can create a binding. The server checks the binding even if C validation is bypassed.

The owner supplies `/work` and a matching directory identity for `.` and `/work`.
Ordinary absent names return ENOENT. Parent traversal and absolute paths outside
that scope return EACCES. For this bounded selection reject other multi-component
or noncanonical spellings explicitly; no symlinks, mount traversal or normalization
algorithm is implied. Empty names return ENOENT; overlong names return
ENAMETOOLONG. Queries do not mutate cwd. chdir/fchdir, readdir, directory creation,
rename, permission modification, file lookup through this grant and persistence
remain unsupported. These exclusions must remain visible in the eventual handoff.

#### Bootstrap and wire boundary

Select a new AECAT003 carrier: 192 bytes, with the AECAT002 descriptor and identity
fields unchanged except for the version magic, followed by a 32-byte directory
binding. Keep descriptor count three. At absolute offsets 160/164/168/172 place
query reference u32, rights u32 (exactly 1, metadata query), object kind u32
(exactly 1, directory), and current client generation u32; offsets 176–191 are
zero. Reference must be nonzero and distinct from the three descriptor references.
Its actual owner binding, not its numeric shape, enforces authority. The C decoder
stages all 192 bytes before publishing any descriptor, metadata or directory state.
AECAT001/002 remain separately selected; all mismatches reject after the header.
No old reserved bytes or descriptor flags acquire new meaning.

Reuse the existing 32-byte, one-request-at-a-time transport. For this selection,
operation 4 queries cwd and operation 5 queries directory identity. Requests use
u32 operation/reference/selector/length at offsets 0/4/8/12 and data[16] at 16.
Selector is exactly 3 for the directory object, outside the three stream slots.
Cwd query requires length zero and zero data. Identity query carries 1–15 pathname
bytes followed by zero padding; embedded NULs are rejected. All fields must be
validated before a response or state effect. Missing rights or a foreign binding
returns EACCES; a retired binding returns EBADF; malformed fields return EINVAL;
unknown operations return ENOSYS. Responses are signed i32 result at 0, zero
reserved bytes 4–15, and a 16-byte data area. Errors have zero data. Cwd success
returns the byte count including NUL (six for `/work`), with zero tail bytes.
Identity success returns zero and data containing four LE u32 fields: service
identity, directory identity, type/mode and zero reserved. Supply actual stable
fixture identities, S_IFDIR|0500, and compare both identity fields in the facade.
No structure layout, pointer or native struct stat crosses the wire.

The identity response is only enough for the selected generated-init comparison.
It is not a general successful stat implementation: document this adaptation and
the supported struct fields before implementation; do not silently present zero
sizes/timestamps/ownership as full filesystem metadata. The adapter fills a staged
native struct for this selected directory witness, with deterministic zero values
for the explicitly unavailable fields. General stat consumers remain unqualified.
A future filesystem-backed replacement must provide their semantics before adoption.

#### Facade, lifetime and failures

The selected C getcwd uses the live directory grant for every query. With a valid
caller buffer, copy only after a complete validated response and sufficient room
including NUL; insufficient room returns ERANGE without changing the buffer.
Before admission return EAGAIN; transport truncation or malformed response returns
EIO and poisons the shared connection under the existing transport rule. Do not
retry a poisoned connection or fall back to a cached/environment path. Define the
selected null-buffer allocation variant using the existing allocator (NULL,0
allocates the exact required bytes; a positive insufficient size returns ERANGE).
Allocation failure returns ENOMEM without publishing a partial result. Caller
pointers must be valid C objects; this facade is not a native pointer-validation
boundary and must not claim safe probing of arbitrary addresses.

Directory/stat response translation lives beside the existing startup adapter.
It preserves errno on successful internal cleanup and the startup signal guard
across exchange/publication. Shared transport ownership and its poison state
remain authoritative. No new queue, thread, kernel syscall, global cwd, service
process or kernel resource limit is required. Added fixed state is one owner
binding and one client reference, plus the 32 startup bytes and bounded request,
reply and staged stat storage; null-buffer getcwd explicitly uses heap memory.
Stop/exit invalidates the connection and directory binding before worker reuse.
No directory descriptor needs close, but terminal cleanup must clear the binding
and account for unread bytes. Old references cannot revive in the next generation.

#### Qualification selection and implementation order

Implement the owner/adapter in the existing complete command suite, then qualify
unchanged generated init with supplied identity and: empty PWD; matching `/work`;
relative PWD; missing PWD target; and a mismatched directory-identity response.
Expected fallback still resolves to owner-supplied `/work`. Require no getcwd
warning on successful cases and exact unchanged copy/output/terminal cleanup.
Test buffer sizes zero/one/exact/large, NULL allocation/free, guard bytes, and
unchanged output on error. Test before-ready, missing/foreign/stale grant, wrong
rights/type/generation/reserved bootstrap fields, both version directions and
truncation. Raw requests must independently prove owner enforcement; wrapper-only
denials are insufficient. Close/reuse must complete across two generations/four
reclaims. A malformed/truncated reply must poison subsequent traffic and still
allow owner-confirmed teardown. Mutants that invent `/`, trust PWD without stat,
substitute inode/device identity or skip grant publication must fail named semantic
oracles; assign their numeric stages before code. Preserve all old profiles.

First implement this bounded namespace/query witness, then evaluate actual main
and exec/wait composition. The inspected userland metadata review also records
that the pinned Linux-target main omits a UID/GID equality guard for interactive
ENV. Resolve the native configuration/secure-environment contract with actual-main
controls before claiming full-shell acceptance; advisory IDs do not solve it.
OpenZFS integration and general paths remain subsequent release work.

Run `zig build test` plus the complete command suite with the pinned SDK/tool lock
on frozen implementation bytes. No kernel change is selected; add M4 regressions
if implementation changes kernel/interrupt/transport code. Retain all failed
attempts, exact traffic, status and cleanup receipts. This documentation step runs
host/pin/workflow and snapshot/link checks only; runtime qualification and consumer
review remain open. Update STATE and this reference, preserving existing workflow
suite/entry points. Existing C formatting migration remains separate; use Rust
2024 formatting for touched owner code and current C11/GNU warning checks.

Simplicity (SE-01–SE-05): the simpler constant getcwd or trusted PWD cannot establish
directory identity or delegated authority. Choose one immutable directory and two
queries on the existing connection; a full VFS, account service or new filesystem
engine is unnecessary for this initializer witness. Borrow directory-relative
authority and identity comparison without adding mounts, traversal or mutation.
None of the still-consumed legacy fixtures can be removed now. The additional
version, owner binding and rejection paths are necessary costs; keep directory
handling cohesive rather than expanding stream operation branches throughout the
owner. This is a bounded precursor, not the final filesystem interface.

### Directory implementation qualification plan — 2026-09-08

Implement the selected facade and owner without kernel changes. Client stage106
identifies directory query, buffer, identity and initializer mismatches; owner1501
must reject that terminal status for deliberate skipped publication. Bootstrap
mutants keep client110/four-reclaim cleanup. Retain C's existing local formatting
and Rust edition2024 formatting. The initial implementation selection qualifies
ordinary queries, raw authority denial, bounded buffers/allocation, inherited PWD,
and malformed binding admission; reply corruption/truncation and every version
pair remain required follow-on controls until separately recorded. Do not mark the
whole directory acceptance matrix complete from this initial selection.


### Initial directory implementation result

The [retained initial qualification](evidence/shell-cwd-2026-09-08/README.md)
passes 319 command cases. Selected getcwd queries use the current connection's
reference; stat fills only st_dev, st_ino and st_mode, zeroing unavailable fields
as the declared initializer adaptation. The fixed directory identity is 1, with
service identity 100+fixture generation. It remains stable for that service/client
lifetime and changes on replacement. Environment PWD=/missing is out of scope
(EACCES), so actual init falls back to the granted `/work` path. No persistent
namespace, general stat or full-main acceptance follows from this witness.

Ten added cases select cwd, matching/relative/absent PWD, skipped publication,
and missing/rights/kind/stale/reserved bootstrap fields. Positive cases exercise
raw foreign/stale reference and malformed-selector/unknown-op/reserved-byte
rejection, caller and allocated buffers, exact fit, errno and unchanged stat/output
on errors. Bootstrap rejection remains client110 with four reclaims; skipped
publication rejects client106/owner1501. Other planned version, truncation,
response-poison, directory-identity mismatch and alias controls remain open in
STATE. No completed directory handoff is implied by this initial selection.

### Directory bootstrap rejection selection — 2026-09-09

Requirement: qualify the current decoder against a directory reference aliased to
stdin, a 16-byte final directory record followed by EOF, and both AECAT002/003
version directions. Forbidden outcomes are partial descriptor/ID/directory
publication, successful fallback, a sender waiting for an unconsumed body, or
resource leakage. Reuse client110 and the owner's zero-I/O/four-reclaim oracle.
Version senders supply only the header and close; short senders close after the
partial record. The owner must account for its already-consumed writer during
cleanup. This changes only conformance sender selections and the existing harness;
no decoder, kernel, SDK default, sibling contract or release pin change.

Run the full command suite and host/pin/workflow checks on frozen inputs. Reuse the
bounded half-frame sender for both metadata and directory truncation; stack bytes
remain borrowed only through synchronous copy calls, EAGAIN yields, and the fixed
iteration limit fails rather than claiming a successful short transfer. Rust
edition2024 formatting applies; no broad harness formatting or new tool entry.
Update this reference, workflow and STATE with actual evidence. Reply-poison,
other version pairs and identity/PWD controls remain separate missing coverage.
This is a routine extension of the adopted directory review and its authority,
compatibility and simplicity assessment, not a new abstraction or protocol.


The [2026-09-09 bootstrap evidence](evidence/shell-cwd-bootstrap-2026-09-09/README.md)
qualifies the four selected alias/short-final-record/v2-v3 cases with client110
and four reclaims, within a passing 323-case suite. No decoder fix was needed.
V1/V3 pairs and other truncation boundaries are not inferred from this selection;
response-poison and directory-identity/PWD controls remain open in STATE.

### Directory reply-poison selection — 2026-09-09

Requirement: inject reserved reply data, invalid cwd length, invalid stat mode,
and EOF after half a reply. The selected client must observe EIO, unchanged output
and restored signal mask; subsequent cwd/stat/read/write must fail and the owner
must accept no further request bytes. It exits1 after verifying the rejection;
owner cleanup expects untouched streams and four reclaims. Client107/owner1501
rejects a mutant omitting semantic-reply poison publication. Assign owner1593 to
unexpected traffic after injection. Reuse the existing bounded half-frame sender
and explicit writer-close accounting. No general retry, kernel or ABI addition.

This extends the existing directory authority and simplicity review. The Rust
conformance owner remains authoritative for transport observation and teardown;
C's cached poison state is not an authority boundary. Stack buffers stay owned
through synchronous exchange, invalid output is never copied to the caller, and
native mask restoration remains required. No dependency, resource quota or sibling
change. Preserve Rust edition2024 and existing local C style. Run host/pin/workflow
and the full command suite on frozen inputs, retaining all attempts. Update STATE,
this reference and the existing workflow oracle. Identity/PWD and remaining version
or truncation boundaries remain separate coverage, not inferred acceptance.


The [reply-poison evidence](evidence/shell-cwd-poison-2026-09-09/README.md) qualifies
these four injected failure responses and the missing-poison mutant in a passing
328-case suite. Error-output/mask checks precede additional cwd/stat/read/write
rejections; owner1593 rejects any accepted request after injection and its terminal
check rejects partial queued bytes. Successful failure-handling cases exit1 with
four reclaims; the mutation rejects client107/owner1501 with no reclaim claim.
No complete directory response-validation matrix or full-shell handoff is implied.

### Inherited-PWD identity selection — 2026-09-09

Requirement: prove unchanged generated init compares both device and inode when
validating inherited PWD, rather than accepting text or collapsed identity fields.
All selected cases supply PWD=/work. A dedicated fixture skips the already-qualified
pre-init directory probes so the Rust owner can observe init's exact requests:
stat(/work), stat(.), and getcwd only when an identity field differs. Inject one
well-formed inconsistent field in the /work stat reply (device or inode separately).
This is an adversarial fixture response, not a new directory or production namespace
feature. All outcomes still yield PWD=/work, so string equality alone is insufficient.

The owner checks query ordering and terminal counts at1594, plus unchanged copy,
output and two-generation/four-reclaim cleanup. Mutants collapse the received device
or inode to the current-directory identity; actual init then incorrectly omits the
fallback query. Require normal client0 followed by owner1594/reclaimed0, not a timeout
or unrelated client failure. No native authority comes from either identity field.
Existing adapter behavior, grants, raw operations, pins and upstream objects remain
unchanged except for explicitly compiled mutation controls. No sibling changes.

Reuse the existing suite and owner, adding only one bounded per-generation query
counter. Stack/local ownership and existing synchronous guarded exchange remain
unchanged; no new resource allocation, thread, kernel code or service. Retain Rust
edition2024 and local C style. Run host/pin/workflow and the complete command suite
on frozen sources. Update STATE, this reference and the existing workflow oracle.
This scoped test extends the directory review's simplicity assessment; it avoids
adding a synthetic filesystem tree merely to exercise the comparison. Remaining
version/truncation coverage and actual consumer/full-main acceptance stay separate.


The [inherited-PWD evidence](evidence/shell-cwd-pwd-2026-09-09/README.md) qualifies
the match, device-mismatch and inode-mismatch cases with exact owner-observed
query sequences and four reclaims. Each collapsed-identity mutant exits client0
but is rejected at owner1594 because the required fallback query is missing.
All 333 command cases pass. These are generated-init controls using unchanged
upstream objects; full main and independent consumer acceptance remain separate.

### Remaining bootstrap boundary selection — 2026-09-09

Qualify V1 sender/V3 receiver and V3 sender/V1 receiver, plus EOF at byte offsets
0, 16, 48, 144 and 191 of the 192-byte V3 carrier. These cover no header, partial
header, partial descriptor, partial metadata and the missing final reserved byte;
previous evidence covers the half directory record and both V2/V3 directions.
Every accepted rejection must remain client110, with unpublished startup state,
untouched streams and four reclaims. No successful fallback, partial binding or
sender waiting after EOF is allowed. Reuse explicit writer closure and its owner
cleanup accounting. These selected boundaries are not exhaustive parser fuzzing.

Use one bounded bootstrap-send helper that tracks the remaining selected byte
budget and sends nothing after it reaches zero. Preserve ordinary full-frame
transfer behavior and the existing half-frame helper via a bounded prefix helper;
borrowed frame bytes are copied synchronously, EAGAIN yields, and bounds/watchdog
failure is not success. This only changes the conformance sender/harness. No C
adapter, kernel, package, sibling, dependency or pin change. Rust edition2024 and
existing Python style apply. Extend the existing workflow oracle, run host and
complete command qualification on frozen sources, retain all attempts, and update
STATE/reference with results before reviewing consumer readiness. This reuses the
existing authority/simplicity assessment without creating another harness or API.


The [boundary evidence](evidence/shell-cwd-boundaries-2026-09-09/README.md) qualifies
all seven selected V1/V3 and EOF cases within a passing340-case suite. Each rejects
client110 and completes four reclaims. The decoder is unchanged. The byte-budget
sender stops sending at the selected offset, then closes; cleanup accounts for the
consumed writer. This is selected boundary coverage, not exhaustive truncation fuzzing.

### Directory and metadata intake review — 2026-09-09

Read-only userland records report independent reproduction of the initial319-case
directory profile. Their [captured inputs](evidence/shell-cwd-boundaries-2026-09-09/consumer-review-inputs/inputs.json)
are retained with hashes; this review did not rerun that consumer or approve its
acceptance on its behalf. Current340-case producer qualification is newer and must
be consumed at matching revisions before extending independent acceptance.

| Consumer observation | Current producer evidence / remaining work |
| --- | --- |
| Corrupt/truncated directory replies, poison and teardown | Selected reserved/length/mode/half-reply cases and missing-poison mutant pass in the328-case packet. No complete malformed-reply Cartesian product claim. |
| V3 version and header/body truncation | V2/V3 pairs plus V1/V3 pairs and selected offsets0/16/48/144/176/191 now pass. Mismatched-version senders are header-only; this does not prove queued wrong-version body disposal. |
| Directory reference aliases each stream | All three stream aliases now pass in the allocation/alias qualification linked below. |
| Directory identity/PWD fallback | Matching, device-mismatch and inode-mismatch exact init query sequences and collapse mutants pass in the333-case packet. |
| Forced getcwd allocation failure | Successful allocation/free and ERANGE pass; one injected allocation failure now checks ENOMEM, mask restoration and subsequent allocation. System-wide exhaustion is not claimed. |
| Metadata03 per-getter errno | Independent resets/checks now run before and after failed admission; four targeted missing-errno mutants reject105/1501 in the metadata packet linked below. |
| Metadata05 V2 descriptor composition | V2 rights, FD, stale-reference and descriptor-count combinations now reject110 with four reclaims in the metadata packet below. |
| Metadata06 additional truncations | V2 offsets0/16/48/144/159 now reject110 with four reclaims; these are selected boundaries, not exhaustive fuzzing. |
| Metadata07 queued wrong-version body | Both V1/V2 directions now reject with15 body bytes unread, terminal110 and four reclaims; a wrong-marker witness rejects108/1501. See the queued-body qualification below. |
| Metadata11 all raw getters | All four raw getter calls now require ENOSYS while public getters retain the admitted tuple, using the pinned SDK constants. |

These are concrete coverage gaps, not newly established runtime defects or waived
requirements. The aliases/ENOMEM follow-up below is now producer-qualified. All five metadata observations are now producer-qualified below, including queued
wrong-version body disposal. Matching consumer reproduction remains pending. Do not
create another decoder or relax consumer oracles.
The selected stat facade still supplies only three initializer fields, and paths,
chdir/persistence remain unsupported. Full-main secure-ENV configuration and the
consumer's actual exec/wait/redirection/pipeline workloads remain separate gates.

### Directory alias and allocation-failure selection — 2026-09-09

Complete the consumer-requested aliases to stdout and stderr using the existing
late directory validation. Both must reject client110 with all startup state
unpublished and four reclaims. The existing stdin-alias case remains selected.
Force the first eligible getcwd(NULL,0) allocation to fail in a separately compiled
fixture. Require NULL/ENOMEM, restored signal mask, intact connection/readiness,
and a subsequent real allocation/free and ordinary init/copy/cleanup across both
generations. This is fault injection at the facade allocation boundary, not proof
of kernel-wide heap-exhaustion behavior. Do not poison or retire a valid directory
grant on a known local allocation failure.

A mutant omits ENOMEM assignment; reset errno to77 immediately before the call so
stale errno cannot satisfy the check. Require client106/owner1501 rejection. No
new allocation framework or global allocator replacement: one fixture-only counter
selects a single NULL result, and later allocation uses the unchanged allocator.
The normal path and capacity limits remain unchanged. Synchronous guarded query,
buffer ownership and cleanup follow the existing contract; no pointers escape on
failure. No kernel, sibling, upstream, dependency or pin change. Preserve local C
style and Rust edition2024, update the existing workflow oracle/reference/STATE,
and run host/pin/workflow plus the full native suite on frozen sources. Retain all
attempts. This scoped extension reuses the directory review's authority/simplicity
assessment. Remaining metadata rows and consumer adoption are separate work.


The [allocation/alias evidence](evidence/shell-cwd-allocation-2026-09-09/README.md)
qualifies both remaining stream aliases and one forced getcwd allocation failure
within a passing 344-case suite. Allocation failure leaves the connection usable;
a subsequent real allocation/free and generated init pass. The omitted-ENOMEM
mutant rejects client106/owner1501. Each non-mutant case completes four reclaims.
Normal allocator behavior is unchanged. The five metadata rows and matching
consumer reproduction remain open; no full-main or persistent-filesystem claim.

### Metadata observation completion selection — 2026-09-09

Address consumer rows03/05/06/11 in the existing suite. Reset errno to77 before
each public getter, independently before admission and after failed admission;
check its sentinel/EAGAIN and unpublished cached field. Four mutants suppress
errno for one getter each only after the selected malformed-source bootstrap is
fully received and rejected. Require client105/owner1501, preserving the original
before-admission checks and avoiding a sender-blocked early exit.

Probe all four raw getter numbers from the pinned SDK's SYS_getuid/geteuid/getgid/
getegid macros through the native syscall prefix; each must remain ENOSYS while
public getters expose admitted metadata. This does not assign credential authority
or change raw syscall semantics. Select V2 records with malformed descriptor rights,
FD, reference generation and descriptor count but otherwise valid metadata. Require
whole-record rejection, client110, zero published state/traffic and four reclaims.
Add V2 EOF offsets0/16/48/144/159 using the bounded byte-budget sender; close the
writer and verify consumed-endpoint cleanup. These are selected boundaries, not
exhaustive parser fuzzing. The malformed-descriptor and truncation cases each use
two generations. Preserve all old V1/V2/V3 selections.

No kernel/decoder, sibling, dependency or pin change. Getter mutation controls are
fixture-only; normal adapter behavior remains unchanged. Existing local C style
and Rust edition2024 apply. Reuse fixed getter arrays and the existing bounded
sender/owner, with no extra service or framework. Update reference, workflow and
STATE; run host/pin/workflow and the complete native suite on frozen sources and
retain all attempts. This extends the existing metadata authority/simplicity review.
Consumer row07 (queued mismatched-body disposal) still requires a coordinated
bounded witness; header-only rejection must not be presented as that result.


The [metadata observation evidence](evidence/shell-metadata-observations-2026-09-09/README.md)
records all 357 command cases passing. Thirteen added cases comprise four targeted
missing-errno mutants, four V2 descriptor combinations and five V2 truncations.
Raw syscall probes use 0x10000 plus pinned SYS_getuid/geteuid/getgid/getegid and
run alongside admitted public getters. The erroneous getter mutants activate only
after complete malformed-source rejection, preserving before-admission checks and
allowing the owner to observe client105/owner1501. Non-mutant rejection cases finish
four reclaims. No kernel credential implementation or new identity authority.
The queued mismatched-body observation and matching consumer review remain open.

### Queued wrong-version body selection — 2026-09-09

Requirement: consumer metadata row07 needs actual unread body bytes at version
rejection. Add V1-to-V2 and V2-to-V1 fixture selections using the existing channels.
After reading the header, a test-only decoder hook acknowledges it with a fixed
32-byte record. The owner verifies that record and performs one exact 16-byte
body write into the now-empty queue. The hook consumes one generation-tagged
marker byte, then the unchanged version check rejects; 15 bytes remain unread.
The owner closes its writer, requires client110 with unpublished descriptors/IDs,
no subsequent client traffic, untouched backend streams and four reclaims across
two generations. This witnesses disposal and reuse, not arbitrary parser fuzzing
or direct inspection of physical queue zeroing. Existing host channel zeroing tests
remain complementary evidence. A wrong-marker control must produce client108 and
owner1501, proving a failed witness cannot count as ordinary version rejection.

Forbidden outcomes: successful admission, publication, body interpretation as
requests, stale bytes entering the next generation, or treating handshake failure
as version rejection. The only new client state is a fixture-only witness flag.
The hook uses existing bounded synchronous transfers; the owner's one-write buffer
is a live local 16-byte array, immutable during the trap, with no retained pointer.
No authority, kernel ABI, SDK default, upstream object or released pin changes.
Aether owns this producer test; userland intake remains separate.

The simpler header-only test cannot establish queued body disposal. An uncoordinated
write risks a scheduler-dependent partial write or already-closed receiver, so the
bounded hook is necessary. No service or generalized synchronization framework is
added; no existing compatibility control is removed. Retain current C formatting
and Rust edition2024. Update this reference, STATE and the existing workflow oracle.
Select host/pin/workflow checks, Rust formatting and the complete command suite,
including the malformed witness control. Freeze runtime inputs for qualification;
no fresh M4 selection for fixture-only changes.

Preflight correction: native channel calls cap each transfer at16 bytes, separately
from queue capacity32. The initial 32-byte write assertion failed at owner1595;
retain that attempt and its frozen sources. The corrected witness writes16 and
leaves15 unread bytes, without changing the kernel transfer limit.

The [queued-body qualification](evidence/shell-queued-body-2026-09-09/README.md)
passes all360 command cases and host/pin/workflow checks (98 Python tests). Both
version directions complete four reclaims; wrong-marker injection yields108/1501.
The retained first attempt failed owner1595 because of its oversized write assertion.
All five requested metadata observations now have bounded producer evidence;
matching consumer acceptance and actual-main/secure-ENV work remain separate.

### Actual-main ENV configuration selection — 2026-09-09

Requirement: stop using the Linux-reference main object's omitted identity guard
as the basis for native interactive ENV behavior. First retain an isolated build
comparison from the pinned dash source, generated headers/config and native SDK.
Select a one-line portability condition in main.c:
`#if !defined(linux) || defined(AETHER_NATIVE_ENV_GUARD)` replaces its sole
`#ifndef linux`. Enabling the define preserves the upstream real/effective UID
and GID equality check before interactive ENV loading. Preserve all platform
macros, the original32 reference objects, generated configuration and upstream
notices. This is a candidate main-object build, not active harness adoption.

Forbidden outcomes: global Linux macro removal, silently replacing pinned objects,
claiming privilege from UID0, allowing unadmitted metadata, or counting object
imports as native execution/security acceptance. Compare original, patched-disabled
and patched-enabled objects: only enabled must import all four getters. Record
preprocessed source, tool/SDK/input hashes, exact flags, logs and disassembly.
Existing source authentication limitations remain; no fresh configure/generator or
whole-dash source-build claim. Run host/pin/workflow checks and snapshot verification;
no QEMU selection because the candidate does not enter any runtime profile yet.

Simplicity: global macro changes are broader than the specific missing guard and
can affect SDK headers. A single named native compile condition preserves proven
upstream control flow without a second ENV policy engine. No obsolete active path
can be removed before native execution and consumer intake. No new service, object
capability, unsafe boundary or resource pool is introduced by the object experiment.
Aether owns native launcher authority; userland owns shell compatibility/intake.

Native execution acceptance must use actual main and an observable ENV script:
equal UID/GID plus interactive flag loads it; unequal UID or GID suppresses it;
noninteractive, absent ENV and empty ENV do not load it. Check script side effects,
stdout, terminal status, exact descriptor closure and all-child cleanup. An omitted
guard control must demonstrably execute the forbidden script and fail the oracle.
Launcher metadata must already be admitted; equality remains informational and
must never authorize opens. This narrow guard does not control login profiles.
Initial selection is non-login; /etc/profile and HOME profile handling, trusted
launch environment and authenticated/secure execution remain separately specified.

The pinned options table has no privileged `-p` option: do not invent its support
or silently ignore it. Actual-main qualification must check its existing illegal-
option rejection. No set-ID execution is supported by the current metadata carrier.
This build step does not settle privileged launch policy or establish complete ENV
security. Then run the existing argv/signal/syntax cases before exec/wait, native
children, redirection and pipelines; do not expand the bounded /work fixture into
a synthetic general filesystem merely to pass them.

### Actual-main first execution selection — 2026-09-09

Before adding ENV file access, execute the selected main object with admitted V3
startup, PWD=/work, no ENV, and `sh -c "printf 'dash-main\\n'; exit 7"`. The wrapper
only admits startup and calls real main; it must not call init or the old startup
probe first. Dash owns parsing, initialization, builtin execution and exitshell.
Wrap its final _exit boundary to retire each present facade descriptor, preserving
status7 unless cleanup fails (112). This explicit adapter cleanup is necessary
because native endpoint teardown alone does not retire owner service aliases.
Do not add a general atexit facility or override dash's trap/flush logic.

Require exact stdout dash-main plus newline, empty diagnostic/input, client7,
backend17 and four reclaims across two generations. A skipped-main control returns0
and must fail owner1501; an omitted-close control still exits7 but must fail
owner1503 with unreclaimed aliases. Generic panic/timeouts cannot satisfy either.
The final _exit uses existing native termination after synchronous bounded closes;
no stack pointer escapes and no new capability or kernel API is added.

Use the hash-pinned enabled main object from the isolated build comparison and
retain the other31 original objects, including their notices. Pin the replacement
independently and verify its bytes before linking; do not overwrite original main.o.
This first execution does not test ENV loading or implement opens, exec, wait,
pipes, login, TTY or a general filesystem. It is the smallest actual-main path
needed to discover execution gaps without fabricating a file service. No existing
probe or compatibility case is removed. Retain existing C style and Rust2024;
select host/pin/workflow checks and the full command suite, all failed attempts
and exact source/artifact receipts. No kernel changes or fresh M4 selection planned.

The [first actual-main qualification](evidence/shell-main-execution-2026-09-09/README.md)
passes all363 command cases and host/pin/workflow checks (98 Python tests), with
no failed target attempt. Real main emits dash-main/newline and exits7 across two
generations with four reclaims. Skipped-main and skipped-close controls reject
0/1501 and7/1503 respectively. The selected candidate is now used only by these
three explicit fixture links; original main.o remains unchanged. ENV file access,
actual ENV suppression, unsupported -p execution and external commands remain open.

### Existing file-service composition selection — 2026-09-09

Requirement: reuse the existing Rust read-only file service for shell file access.
Before exposing a new root/FD carrier, compose it in worker slot2 alongside actual
dash slot0 and its stream backend slot1. The existing six-channel/three-worker
limits suffice: each worker receives its own endpoint pair. Keep all name/content/
open-record policy in the existing service, with no kernel or CWD stub expansion.

The owner alone retains the file-service connection/root. Verify the exact hello,
open hello.sh read-only, read its actual immutable bytes in <=16-byte chunks, EOF,
write denial, consuming close and stale-handle rejection. Reject a stream handle
as file root, write-open rights and a missing name. Perform this before dash and
again after its terminal observation, requiring successive file-handle generations
within that connection. Both rounds use the unchanged service protocol. Shut down
the file service through request EOF, observe17, close reply, then reclaim it.
Repeat with a fresh service/domain pair: six total reclaims and exact ordered
client7/stream17/file17 terminals. Shell still has no open call or file root grant.
This validates composition, not ENV execution or general pathname behavior.

Negative selections: compiling the service with the existing command_runner
payload selection substitutes abcdef for the script and must fail owner1596;
omitting the remote file close must fail the stale-read assertion at1597. Neither
may count as normal cleanup or require an invented child terminal. Preserve exact
failure logs and all attempts. No ambient root, parser duplication, filesystem
backend rewrite or persistent storage is introduced. Service request data is a
bounded owned stack record copied synchronously, with no retained raw pointer.

Simplicity: a local fake open would bypass the real owner and create a second file
implementation. Reusing the existing server costs one already-supported domain and
two channels and exercises its actual lifecycle. No extra pool, framework or
compatibility path is needed; older profiles retain their image choices. The next
root/descriptor bridge must be explicitly granted and versioned, with publication,
masking, shared offsets, error/poison and cleanup contracts before implementation.
Userland owns consumer acceptance; sys-init retains supervision policy. Select
host/pin/workflow and complete command regressions; existing Rust2024 conventions,
no C/runtime/kernel changes or fresh M4 selection. Update STATE and this reference.

Composition preflight correction: the first owner completed all six reclaims, but
the inherited native-runner-local build selection still required four at final
kernel validation. Retain the failed attempt; select the existing default six-
reclaim connections mode for only the three main-files cases. This changes harness
profile selection, not kernel limits or checks. Re-run on frozen final sources.

Second preflight correction: runner-local also gates parent/action interfaces, so
turning it off is invalid for actual dash. The second attempt was interrupted
during compilation before target cases, with sources/report retained. Keep local
mode and add positive selector native-runner-files, valid only with runner-local,
which selects exact6 instead of4 at final result validation. Authority, pool limits,
all-channel cleanup and existing profile results remain unchanged. Classify the
selector in the existing build-policy test; exercise invalid profile combinations
and one valid help selection, then host, full command and fresh M4 regressions.
This scoped build/evidence change applies existing O-04/I-04/E-06 cleanup rules;
it is not a new syscall, resource allowance or permissive completion check.

Final oracle correction: the valid native six-reclaim result also needs the old
blanket slot2 ban scoped to the older cases. Allow only the named positive file
composition and still require exact0/1/2 terminal order and six reclaims. File
precondition negatives must have no terminals. Retain this failed oracle attempt
and the successful pre-correction M4 run; qualify final sources with both suites.

The [completed composition](evidence/shell-file-composition-2026-09-09/README.md)
passes all366 command cases, seven fresh M4 regressions,98 Python host checks and
four build-selector cases. Owner-side file access works across dash termination;
exact0/1/2 terminals and six reclaims pass across two generations. Wrong content
and skipped file close reject1596/1597. All failed/interrupted and intermediate
passing attempts are retained. This does not expose shell open or an ENV file root;
the explicit versioned grant/descriptor bridge remains the next implementation.

### Read-only shell root and descriptor bridge selection — 2026-09-09

This is the pre-implementation contract for the next bounded experiment, not an
implemented carrier or consumer handoff. Requirement: actual dash must source
`hello.sh` through the existing read-only Rust service, including its real
open/read/descriptor-duplication/close path. Aether owns this fixture's launcher,
proxy and adapter; userland retains SDK and matching consumer acceptance, sys-init
retains supervision policy, and pkg-mgr retains installation policy. Apply
Foundations O-01–05, I-01–06, E-01–08 and locally adopted SE-01–05. No shared
standard, released pin, sibling, upstream object or kernel ABI changes are selected.

#### Admission and authority

Select AECAT004 explicitly: 224 bytes, with the first192 bytes retaining V3's
fields except the version magic. Header role count remains3. Append this record;
all integers are little-endian u32:

| Byte offset | Required value |
| --- | --- |
| 192 | Root reference `0x76040000 + native_generation` |
| 196 | Rights1: read-only named-file lookup |
| 200 | Kind1: bounded named-file service root |
| 204 | Current native generation |
| 208–223 | Zero reserved bytes |

Validate every field, old role/identity/directory record and root nonaliasing
before publishing any descriptor, identity, directory or root. Reject unknown
versions at the header, without downgrade. A V3 grant confers no lookup right;
`PWD`, UID0, directory stat identity and the service's numeric root0xf001 do not
confer file access. The Rust owner binds the root to this client's actual channel
and current file-service instance; token-shaped request bytes alone are insufficient.
The shell never receives the owner's native file-service endpoints.

#### Request and reply boundaries

Reuse the client's existing synchronous32-byte owner connection. Keep stream
ops1–3 and directory ops4–5 unchanged. Dispatch new file ops by opcode before
the existing directory selector range check; neither an arbitrary selector nor a
file reference may redirect a request into stream/directory authority.

| Op | Request fields after opcode at0 |
| --- | --- |
| 6 open | root reference@4, selector4@8, rights1@12, zero-padded NUL-terminated basename@16 |
| 7 read | issued open reference@4, binding selector3 or4@8, count0–16@12, zeros@16 |
| 8 close | issued open reference@4, binding selector3 or4@8, zeros@12–31 |

Only nonempty basenames of at most15 bytes are admitted. Slash, `.` and `..`
reject EINVAL; no traversal, absolute paths, symlinks, PATH search or CWD-relative
namespace translation is implied. An admitted missing name returns ENOENT. Wrong
root or lookup rights returns EACCES. Wrong/stale open reference or binding pairing
returns EBADF; malformed fields return EINVAL after authority validation. Unknown
opcodes reject ENOSYS. These errors have zero reply bytes4–31 and cause no effects.

Open success has result0@0, issued reference@4, binding selector@8 and zeros@12–31.
Read success has count@0, zeros@4–15, exact data@16 and zero trailing padding;
count must not exceed the request. EOF is a fully zero reply. Close success is
fully zero. No raw backend handle or backend file size is published to the shell.
The owner checks the unchanged backend reply's handle, size, reserved bytes and
operation-specific bounds before producing a client reply. Unexpected backend
errors or malformed replies are failures, not fabricated EOF or successful close.

#### Open records, aliases and bounded reuse

Keep three stream bindings and add exactly two file bindings in the opt-in
adapter; the facade still has16 descriptor slots. Open first reserves a free
descriptor under the existing signal mask, and returns EMFILE without traffic if
none is available. The owner chooses a free file binding, independently enforcing
its two-record limit. Only a complete valid success publishes the adapter binding,
one alias count and the lowest available descriptor. Flags supported initially
are O_RDONLY with optional O_CLOEXEC; other flags reject ENOTSUP before transport.
NULL path rejects EFAULT; an unterminated/overlong bounded name rejects
ENAMETOOLONG. The adapter does not claim arbitrary invalid-pointer recovery.

The owner record holds the backend handle, current offset, size and issued
reference. Use reference `0x77000000 | (native_generation << 16) | (open_sequence
<< 8) | (slot + 1)`, with slot0/1 and monotonic sequence1–6 per client. Require
native generation1–255 and refuse exhaustion instead of truncating or wrapping.
Backend generation retirement still applies: two slots, at most three opens per
slot in one service instance. A new profile starts with a fresh service and does
not run the older composition's allocating pre/post probes; those would consume
this budget. Existing composition profiles and their evidence remain unchanged.

Each new open starts at offset0. Duplication shares the binding and its owner-side
offset; FD_CLOEXEC belongs to each descriptor. Nonfinal close only drops a local
alias. Final close consumes local publication before sending one remote close.
Checked reads advance the owner's offset only by a validated byte count; zero
reads and EOF do not advance it. A failed or lost read response is never retried.
Separate opens have separate offsets. Reuse must reset all adapter fields and
must never publish a previous reference; stale references reject after reopen.
Writes reject EACCES locally and cannot be enabled by a forged direct request.
No seek, create, write, fstat extension or new exec inheritance semantics are added.

#### Ambiguity, cleanup and implementation cost

Keep one in-flight transaction under the existing native signal mask. Caller
buffers remain caller-owned; copy at most16 request/reply data bytes and retain
no raw pointer. Do not publish read bytes before full reply validation. Local
validation errors preserve the transport. Partial/lost/malformed replies poison
it: subsequent remote operations return EIO without traffic or replay, and local
descriptor closes still discard aliases. Restore the signal mask and errno under
the existing contract before returning; failed mask restoration terminates.

An open may have reached the service even if its reply was lost. The owner must
not infer that no record exists or retry open. On client terminal, close known
records when the backend connection is trustworthy, then shut down that service
instance. With an uncertain backend exchange, use confirmed native stop before
endpoint/backing reclaim. Reclaim success requires observed termination and the
existing all-channel cleanup checks; timeout is failure. Normal completion also
requires zero live file records before service EOF, exact client/stream/file
terminal order and six reclaims across two generations. Abnormal cleanup uses
its own explicit terminal oracle, never the normal success claim.

Simplicity questions: a fake local open is shorter but duplicates the service and
bypasses its authority/lifetime checks. Choose the existing service plus a small
owner table and reuse the current FD alias/masking machinery. Borrow Unix shared
open-description offsets only for dash's actual savefd path; defer general VFS,
mounts, concurrent callers and descriptor passing. No existing consumed path can
be removed yet. Added cost is two adapter bindings and two owner records, with
no additional domain, channel, kernel grant, allocator or dependency. Preserve
the touched compact C style as the existing migration exception; use Rust2024
formatting for Rust changes, without a broad runtime or harness refactor.

#### Selected executable acceptance

Extend the existing command suite and workflow group, binding exact stage codes
when implementing cases. First run actual `sh -c ". hello.sh; exit 7"` and require
only `hello\n`, exit7, real service reads and complete cleanup. Observe dash's
F_DUPFD_CLOEXEC allocation at or above10 and shared-offset reads after closing
the original descriptor. Direct boundary cases additionally cover independent
opens, two-record/16-FD exhaustion, EOF, last-alias close, reopen/stale reference,
denied write and foreign-root/CWD-root substitution. Verify no backend mutation
or cursor change on rejection; client status alone is insufficient.

Admission controls cover corrupt root rights/kind/generation/reserved/alias,
truncated final record and V3↔V4 mismatch with unread-byte teardown. Transport
controls cover malformed open/read replies, lost open/read/close replies,
unchanged destination buffers and no traffic after poison. Deliberately skip
root publication, split a duplicated offset or omit final remote close and
require the corresponding semantic oracle to fail. Distinguish service-stop
cleanup evidence from normal remote-close evidence.

Run the complete command suite and host/pin/workflow checks on frozen sources;
select fresh M4 if touching shared transport/kernel/build behavior. Then qualify
the already planned actual-main ENV loading/suppression matrix and unsupported
-p control, followed by argv/signal/syntax and exec/wait. This basename-only
experiment does not claim general ENV paths, persistent storage, interactive
TTY acceptance or release readiness. Matching userland intake remains required.

Implementation selection correction: inspection of pinned dash main.c shows that
`. hello.sh` first searches PATH using stat64 and requires a regular-file result.
Use actual `sh hello.sh` for this first basename-only bridge instead: it enters
setinputfile directly, executes the unchanged script, and exits0 with `hello\n`.
Do not invent file stat or silently normalize `./` to satisfy the earlier command.
The ENV matrix remains a follow-on. Initial bridge qualification covers positive
execution and skipped publication/close controls; the full admission, exhaustion
and ambiguous-outcome matrix remains required before claiming the whole selection.

The [first V4 bridge qualification](evidence/shell-file-root-2026-09-09/README.md)
passes369 command cases, seven fresh M4 regressions and98 Python host tests with
pin/workflow checks. It implements the opt-in carrier, open/open64 and service-backed
read/final-close path with two descriptions and existing masked FD aliasing. Actual
`sh hello.sh` prints exactly `hello\n`, exits0 and requires CLOEXEC duplication
above9; two generations require ordered0/17/17 terminals and six reclaims. Missing
root publication rejects client2/owner1501; skipped remote close rejects owner1599
even though dash exits0. Legacy profiles remain passing. No unexpected failed
qualification attempt; passing preflight host evidence is retained.

This is the initial execution slice, not full V4 acceptance. The selected admission,
exhaustion, independent-open/stale/offset and ambiguous-reply matrix remains open.
Current unexpected backend failures reject through the fixture check path; confirmed
service-stop recovery for uncertain exchanges still needs implementation and target
evidence. No sibling acceptance, ENV, persistent filesystem or release claim follows.

### V4 admission boundary selection — 2026-09-09

Before implementation: extend the existing V4 experiment with missing root,
root aliases to CWD and each stream, rights/kind/stale-generation/reserved-byte
corruption, root-record EOF at192/208/223 bytes and V3/V4 mismatch in both
directions. Require client110 with every descriptor, identity, CWD and file root
unpublished, no client requests or backend file opens, empty stream sinks and
ordered client110/stream17/file17 terminals with six reclaims over two generations.
The mismatched sender sends only the header and closes; this does not qualify
queued-body mismatch recovery. Existing queued-body controls remain unchanged.

Add a deliberately early root publication before late reserved-byte rejection:
client113/owner1501 must fail with zero reclaims. For V4 receivers, public open before/after failed
admission must return EAGAIN, independently of the root token. The V3 receiver
retains its older unpublished descriptor/identity/CWD checks and no file facade. This extends the
existing client/owner/harness and AT-SHELL-GUARDS record; no new API, owner, pool,
shared standard or sibling change. Foundations O-02/03/04, I-01/02/04/05 and
E-04/05/06 apply. Simplicity: reuse whole-carrier validation and existing bounded
bootstrap/teardown rather than adding another decoder or admission service; no
consumed path can be removed. Keep compact C conventions and Rust2024 formatting.
Buffers remain stack-owned, pointer lifetimes synchronous and masking unchanged.
Run host/pin/workflow checks and the complete command suite on frozen sources.
No shared kernel/transport/build behavior changes; no fresh M4 selection here.
Descriptor exhaustion/stale/offset and ambiguous-outcome recovery remain next.

The [V4 admission qualification](evidence/shell-file-admission-2026-09-09/README.md)
passes all384 command cases and98 Python host tests with pin/workflow checks.
Fourteen malformed/truncated/header-mismatch cases require client110, no published
state or file requests, empty sinks and six reclaims across two generations. The
early-publication counterexample fails client113/owner1501 with zero reclaims.
The V3 receiver retains its prior no-file-facade profile. Previous actual dash
execution and all legacy cases remain passing. No unexpected failed attempt;
no fresh M4 run or shared kernel/transport/build/pin change. V4 queued-body,
descriptor-resource/offset/stale and ambiguous-reply coverage remains pending.

### V4 file-description boundary selection — 2026-09-09

Before implementation: add a separate conformance client after V4 admission, not
pre-probes in the actual dash script case. Open hello.sh twice, reject a third
live description with EMFILE, duplicate the first at10 with CLOEXEC, and compare
reads across original/alias/independent open. Fill all16 facade descriptors using
stream aliases; open must return EMFILE without any transport call. Close those
aliases without remote stream closure, close the original file alias, finish the
file through its duplicate, verify EOF, and close both descriptions.

Reopen, then directly submit the old reference and an invalid binding pairing:
EBADF replies must have zero payload and preserve the new offset. Reject CWD as
file root, write-open rights and missing names; public write is denied without
traffic. Consume the remaining open budget, checking fresh offsets, then reject
open after six successful opens without reference wrap. Require client0, empty
streams, exactly six opens/nine reads, no live file records and six reclaims over
two generations. Broken offset advancement and ignored reference matching must
each reject client114/owner1501; they must not count as successful recovery.

Reuse the existing owner table, masked adapter and harness group. Foundations
O-02/03/04, I-01/04/05 and E-04/05/06 apply. Simplicity: fixed arrays and exact
byte comparisons are sufficient; no new descriptor service, protocol, dependency,
resource quota or kernel API. No obsolete consumed path can be removed. Test
request/data buffers remain synchronous stack-owned values, with the existing
signal mask around direct exchanges. Keep compact C and Rust2024 conventions.
Select the complete command suite and host/pin/workflow checks on frozen sources.
The optional transfer counter changes only this client fixture; no fresh M4 run
is needed. V4 queued-body and malformed/lost-reply recovery remain subsequent work.

The [descriptor qualification](evidence/shell-file-descriptions-2026-09-09/README.md)
passes387 command cases and98 Python host tests with pin/workflow checks. The
separate boundary client requires six opens/nine reads, independent and shared
alias offsets, no-traffic descriptor exhaustion/nonfinal close, stale/route/root
and rights rejection, six-open exhaustion and six reclaims across two generations.
Omitted offset advancement and ignored reference matching reject client114/owner1501.
The first positive attempt failed a test expectation: a17-byte script leaves nine,
not eight bytes after two four-byte reads. Preserve that failed run and sources;
the final run uses the corrected suffix count/comparison. Actual dash and legacy
cases remain passing. No fresh M4 run or kernel/API/pin change. V4 queued-body,
malformed/lost-reply recovery and matching consumer acceptance remain open.

### V4 queued bytes and client-reply recovery selection — 2026-09-09

Before implementation: reuse the header acknowledgment/atomic16-byte body witness
for V3↔V4 mismatch. The receiver consumes one tagged byte and leaves15 unread;
require unpublished state, client110 and six reclaims. Wrong witness must reject
client108/owner1501. This extends the existing version tests without a new carrier.

Separately, complete a real backend open, read or close, then corrupt a reserved
reply byte or send only16 of the32 client-reply bytes before EOF. The backend result
is known to the owner; only the client-side outcome is uncertain. Require EIO,
poison, unchanged read buffer, no partial open publication, consuming local close,
restored native mask and no subsequent channel traffic. The client locally drops
remaining descriptors and exits1. Before that observed terminal, no file-record
retirement is permitted. After it, close known retained records through the healthy
backend, verify stale-handle EBADF, then shut down/reclaim all three workers.
Require exact client1/stream17/file17 order and six reclaims over two generations.
A skipped owner retirement must reject owner1599 even after client1.

Foundations O-02/03/04, I-01/04/05/06 and E-04/05/06 apply. Reuse existing bounded
connections, tables, mask and teardown. No new kernel API, service, quota, standard,
sibling or pin change. Simplicity: distinguish which connection failed rather than
adding a general retry framework; never replay an uncertain operation. None of the
consumed profiles can be removed. Keep compact C/Rust2024 conventions and stack-owned
synchronous32-byte messages. Run full command and host/pin/workflow checks on frozen
sources. No fresh M4 selection: shared kernel/default transport behavior is unchanged.
Actual uncertain backend outcomes and confirmed service-stop recovery still require
a separate implementation; these client-leg cases must not claim that coverage.

The [client-reply recovery qualification](evidence/shell-file-reply-recovery-2026-09-09/README.md)
passes397 command cases and98 Python host tests with pin/workflow checks. Both V3/V4
queued-body directions reclaim six workers across two generations; the wrong
witness rejects108/1501. Six malformed/half client-reply cases require EIO, poison,
unchanged buffers/publication rules, no later traffic, restored mask and observed
client1 before retained-record close/stale-handle checks. All complete six reclaims;
skipped retirement rejects1599 after client1. No unexpected failed attempt, new
kernel/API/pin or fresh M4 run. Largest new owner8056 remains within8192 bytes.
These cases have known backend results; uncertain backend outcomes and confirmed
service-stop recovery remain the next implementation, not qualified behavior.

### Uncertain file-backend recovery selection — 2026-09-09

Requirement before implementation: a complete but invalid backend open/read/close
reply must not publish an unverified handle, advance an offset or retire a record.
A failed bounded exchange is also uncertain. The owner closes the client reply
endpoint, rejects later client traffic and never replays the operation or guesses
an unknown handle. After observing client termination it requests scoped native
stop, verifies the file-service terminal record (kind3/detail143), then clears
local descriptions. Endpoint closure and reclaim precede the next generation.
The stream service retains its normal cleanup. A stop acknowledgment alone is
insufficient; skipped stop must fail the terminal check before reclaim.

Select three service-side reserved-byte mutations after real open/read/close and
one omitted-stop control. Reuse the existing poison client to require EIO, unchanged
buffers, restored mask, consuming local descriptor closure and no later traffic.
Require client1, queried file terminal kind3/detail143, stream17 and six reclaims
across both generations. Forced stop emits no normal-exit line; the owner queries
the retained record, and the omitted-stop control must reject that check. Missing/partial/backend-timeout injection needs subsequent qualification;
a checked failure path alone is not executable coverage for those cases.

This is the existing single-context AECAT004 fixture, not a new service API or
sys-init policy. Aether owns the adapter and lifetime experiment; consumer adoption
remains separate. Existing root authority, two records, six channels, three workers,
8192-byte owner limit and pinned SDK/upstream objects remain. Stack-owned32-byte
messages stay live during synchronous traps; no new unsafe boundary, allocation,
concurrency, dependency or pin. Run host/pin/workflow checks and the full command
suite; no kernel or M4 change is selected. Freeze sources and retain failed attempts.

Simplicity: the simpler fatal-owner rejection cannot demonstrate safe reuse after
an unknown operation. A checked exchange into caller-owned zeroed storage, a reply-valid flag and
one connection-local uncertainty flag make failure explicit while reusing transport, poison-client and native-stop paths.
Do not add per-handle retry/reconciliation or a second recovery service. No broad
cleanup is needed; this replaces fatal file-reply validation with bounded teardown.

The size preflight rejected the initial aggregate-return implementation. Request
encoding is shared with the existing fatal backend wrapper; file forwarding uses
one checked reply buffer instead of duplicate32-byte response copies. Private
callers supply zeroed storage and never expose it after a failed exchange. Explicit
outlining keeps common encoding/wrapper code shared. Bounds are unchanged.

The [malformed backend qualification](evidence/shell-file-backend-recovery-2026-09-09/README.md)
passes401 command cases and98 Python host tests plus pins/workflow. Backend
open/read/close corruption requires client1, queried file terminal143/kind3,
stream17 and six reclaims. Omitted stop rejects1601 after client1 with zero reclaims.
The initial image-bound and forced-stop log-expectation failures remain retained;
no bound or runtime check was weakened. The corrected harness matches the existing
absence of a normal-exit line for native stop. Missing/partial/timeout backend
replies, broader service-fault recovery and consumer acceptance remain open.

### Backend EOF recovery selection — 2026-09-09

Before implementation: after a real open/read/close, send either zero reply bytes
or exactly16 of32, then close only the file service's delegated reply endpoint.
Keep that service alive until the owner's existing scoped stop completes. EOF is
not proof of service termination. Neither a missing reply nor its valid-looking
prefix may publish a handle, advance an offset or retire a local description.
Reuse the current checked exchange, poisoned client and confirmed-stop cleanup;
never replay the operation or infer an unknown backend handle.

Select six positive cases and one omitted-stop control after a half open reply.
Require client EIO, unchanged read buffer, no partial publication, consuming local
close, restored mask, no subsequent traffic, client1/stream17 logs and six reclaims
across two generations. The owner separately queries file kind3/detail143 before
clearing descriptions. Omitted stop must reject1601 after client1 with zero reclaims.
A still-open silent backend, timeout and late delivery remain separate coverage.

Aether owns this AECAT004 conformance fixture; SDK defaults, companion ownership,
service wire format, released pins and8192-byte owner bound stay unchanged. Add
only a private C-to-Rust reply-endpoint close bridge over existing0x24003. It uses
the admitted service's own output capability, accepts no pointer and transfers no
new authority. The existing synchronous write reads16 initialized stack bytes;
the call must complete before that buffer can leave scope. The fixture sends into
a drained reply channel, checks the exact write/close result, then yields until
stopped. No allocation or new concurrency; three workers/six channels/two records.

Simplicity: completing EOF qualification by reusing the recovery path is smaller
than another owner mode or retry/reconciliation protocol. Keep owner and client
sources unchanged. No obsolete path can be removed in this scoped test addition.
Retain failures and freeze runtime inputs during the full command suite; run host,
pin and workflow checks. No kernel/M4 change or fresh M4 selection. Preserve the
existing compact C migration exception and Rust2024 conventions.

The [backend EOF qualification](evidence/shell-file-backend-eof-2026-09-09/README.md)
passes408 command cases and98 Python host tests plus pins/workflow. Six zero/half
backend reply EOF cases require client1, queried file terminal143/kind3, stream17
and six reclaims. The half-open omitted-stop control rejects1601 after client1
with zero reclaims. Seven owner binaries match prior sealed artifacts exactly;
owner and client sources remain unchanged. The initial misplaced-bridge link
failure is retained; no runtime oracle was relaxed. Silent live-endpoint timeout,
late responses, broader service faults and consumer acceptance remain open.

### Silent-backend and late-reply selection — 2026-09-09

Before implementation: qualify the existing100000-attempt exchange bound with an
open but silent backend reply endpoint after real open/read/close. No shortened
test budget, retry or inferred success. Select three silent cases and a late-open
case plus its omitted-stop control. Reuse EIO/poison/mask/descriptor checks and
client1/stream17, queried file143/kind3, six reclaims across two generations.

For deterministic late delivery, after exchange failure the selected owner closes
its backend request writer. The service waits for that EOF before sending the
otherwise valid reply; any intervening request bytes reject rather than replay.
The owner consumes only its first status byte as a fixture witness, never as the
operation result. Atomic first16-byte delivery leaves at least15 bytes unread for
confirmed-stop/channel teardown. Local publication stays poisoned; no unknown
handle is guessed and no late result is forwarded to the client. The existing
stop-state query must precede clearing descriptions; omitted stop rejects1601.

This is a connection-local fixture coordination step, not a new wire operation,
retry protocol or sys-init policy. Existing capabilities and bounds apply: three
workers, six channels, two records,8192-byte owner image. Stack-owned initialized
buffers remain valid during synchronous bridge calls. No new unsafe bridge,
allocation, dependency, kernel API, sibling or pin. The service may wait until
explicit stop, while the owner and harness remain bounded. Larger timing claims
and general late-message handling remain outside this experiment.

Simplicity: reuse endpoint EOF as the phase boundary instead of adding a control
channel or guessing a sleep duration. One selected witness is sufficient; do not
parse a late reply into live state. Existing paths stay for consumed regressions.
Run full command and host/pin/workflow checks on frozen sources, retain failures,
and preserve compact C/Rust2024 conventions. No kernel/M4 change is selected.

The initial silent-open attempt reached generation2 but exceeded the harness's
30-second watchdog. Retain that incomplete run. Before the qualified rerun, select
90 seconds only for these five timing cases; all other native cases keep30 seconds.
This is an outer watchdog budget, not a change to the100000-attempt runtime bound
or any outcome/cleanup assertion. Record each selected watchdog in the result.

The extended-watchdog attempt exposed the independent native fixture guard of3000
ticks during generation2. Increasing the external watchdog cannot qualify a run
that violates that guard. Preserve both failures and supersede the initial budget
selection: implement a real4096-attempt limit for every command-backend send/receive,
not a failure-case cfg override. Generic transport keeps100000 attempts; kernel
limits and the30-second harness watchdog remain unchanged. A shared bounded-transfer
helper avoids duplicating the transfer algorithm. The current synchronous32-byte
fixture requests normally finish in a few transfers;4096 supplies bounded waiting
and is not a wall-clock deadline or a future filesystem latency guarantee. Requalify
all command profiles because their real backend polling policy changes. No new
kernel/M4 path is selected. Remove the unused90-second harness override, retaining
its failed evidence instead of keeping a second timeout configuration.

The one-byte late witness now uses the same bounded-transfer helper as32-byte
frames, eliminating its duplicate polling loop. Advancing a remaining mutable
slice preserves partial-EOF and invalid-count rejection. Generic transfer is a
shared100000-attempt wrapper; command backends and the late witness use4096. Size
preflights retain rejected layouts; the final late owner is8152 within8192, and
existing size-sensitive variants also fit. Select the six-case native connections
suite as well as the full command suite because the shared transfer implementation
changed; preserve its generic behavior and all original native/kernel bounds.

The [timeout/late-reply qualification](evidence/shell-file-backend-timeout-2026-09-09/README.md)
passes413 command cases, six native connections cases and98 Python host tests with
pins/workflow. Silent open/read/close and late-open recover with queried stop and
six reclaims; late omitted-stop rejects1601 with zero reclaims. The late reply's
first status byte is a witness only; at least15 bytes remain unread for teardown.
All command backends now use4096 attempts per send/receive. Generic transport keeps
100000, and original kernel/harness limits remain. Failed budget/size attempts are
retained. Final cat owners fit8192 (largest8152). Actual-main ENV/dash qualification
is next; general latency/recovery guarantees and consumer intake remain separate.

### Actual-main ENV execution selection — 2026-09-09

Before implementation: qualify the selected guarded main with the existing V4
file-root grant and hello.sh script. Interactive `-i +m -c` explicitly disables
job control. Equal UID/EUID and GID/EGID must load ENV=hello.sh; independent UID
and GID mismatches, noninteractive mode, absent ENV and empty ENV must not open
or execute it. Exact stdout distinguishes hello followed by dash-main from
only dash-main; status7 and empty diagnostics are required. The existing script's
stdout is the observable side effect. Check file open/read counts, all descriptor
closure and six reclaims across two generations. Two controls select the pinned
original main object with its omitted guard and must execute the forbidden script,
then fail the owner file-access oracle1598 after client7 without reclaim. Also
require actual main's unsupported `-p` rejection, exact diagnostic, status2 and
four reclaims; a skipped-main control must fail the status oracle1501.

Aether owns admitted metadata, file-root authority and adapter lifetime; userland
owns dash compatibility and independent acceptance. Numeric equality grants no
capability. No login, set-ID, TTY, new namespace, kernel API, service boundary,
wire format, SDK patch or resource increase is permitted. The adapter must verify
its existing descriptor-duplication witness for loaded ENV and zero duplicates
for suppression. No pointer escapes or new unsafe boundary is needed. Preserve
existing C compact-style migration exception and Rust edition2024. The simpler
alternative is reusing the already qualified script/service and upstream main
control flow; choose it over a new ENV evaluator or synthetic filesystem. No
obsolete consumed fixture is removed. Qualify all command cases and host checks,
retain attempts and frozen inputs, verify simplicity and released pins. No fresh
M4 selection because kernel and M4 paths are unchanged. This is bounded ENV
execution, not interactive terminal or full-dash/release acceptance.

### Actual-main ENV execution result — 2026-09-09

The [sealed execution packet](evidence/shell-env-execution-2026-09-09/README.md)
passes 423 command cases and 98 Python host tests plus Zig/pin/workflow checks.
All six ENV cases satisfy exact output/status and client open/read/descriptor
oracles across two generations with six reclaims. Original-main omission controls
require client7 with script-FD duplication before owner1598 rejects forbidden file
access; they reject before the later stdout oracle, so exact script stdout is
established by positive loading rather than those controls. Unsupported `-p`
rejects with exact diagnostic/status2 and four reclaims; skipped main rejects1501.
All 271 prior cat-owner binaries are unchanged. New owners max8024, overall max8152,
fit the unchanged8192 bound. No native failures; the pre-compiler local size-list
preparation error remains recorded. No new kernel/SDK/ABI/pin/unsafe boundary.
Next are the consumer's argv, signal-table and syntax-error workloads, followed by
exec/wait, FD closure, redirection/pipelines and OpenZFS. General ENV paths, login,
set-ID, TTY and independent consumer/release acceptance remain outside this result.

### Consumer phase-one dependency review and syntax selection — 2026-09-09

Before implementation: inspect the unchanged consumer scripts, not only their
phase numbers. DASH-argv runs `/inputs/helper argv "a b" "*"` with WITNESS=value;
it needs native child creation, executable resolution, argv/environment transfer,
inherited descriptors and parent wait/status. DASH-signal-table first uses
`$(kill -l 10)`, so it also needs command-substitution child creation, a pipe and
collection before its trap/self-signal check. They cannot be qualified by replacing
the helper with printf or removing substitution. Preserve their original bytes and
oracles. The old startup probe/connection broker does not implement fork or exec.

Select the independent DASH-syntax-error now: unchanged `if then` plus newline,
passed to actual main with `sh -c`, controlled WITNESS=value, LC_ALL=C,
PATH=/nonexistent and admitted PWD=/work. Preserve consumer exit2 and empty stdout;
record native diagnostic bytes separately from the consumer's Linux wording.
Require complete descriptor closure and four reclaims across two generations.
Skipped main must return0 and reject owner1501; skipped adapter final closes must
retain status2 and reject1503 with zero reclaims. Capture the exact script, stdout,
consumer manifest and helper input hashes in the packet, and verify the C literal
matches the retained script before the qualified run. No execution of scripts on
the host is permitted by this input review.

Aether owns native mechanisms/admission and this bounded adapter; userland retains
shell compatibility and independent acceptance. No new service, kernel API, wire,
capability, unsafe/FFI boundary, SDK/object replacement or resource increase. Reuse
actual main and existing diagnostic/cleanup oracles rather than creating a parser
or script engine; no consumed fixture is obsolete yet. Retain current compact C
migration scope and Rust edition2024. Test all command cases and host/pin/workflow
checks on frozen sources, including both deliberate controls. No fresh M4 run is
selected because kernel/M4 paths are unchanged. Then design the bounded process,
inheritance and pipe composition needed by the two unchanged phase-one workloads
before their executable qualification; this is not a consumer acceptance claim.

#### Process composition prerequisites after syntax

The current native launchOperation accepts only the supervisor's factory/image
handles, an unused worker slot and optional transferred channel endpoints; it
loads an immutable image and a fresh startup stack. It neither snapshots the
shell's writable state nor returns from fork in a new address space. The existing
shared-domain thread execution contexts likewise do not establish process isolation.
The admitted command adapter has one synchronous request/reply connection: copying
its channel identifiers into independently running processes would permit interleaved
frames and misattributed replies, not inherited POSIX descriptor semantics.

The next bounded design must specify separate child execution/address-space state,
explicit authority to create it, parent/child return and terminal identities,
per-process authenticated command connections, shared open-description offsets and
reference lifetimes, and failure rollback before child publication. Exec must select
only an explicitly granted helper image, transfer the consumer's exact argv and
WITNESS environment, apply CLOEXEC and preserve parent status through collection.
Substitution additionally needs an actual pipe with last-writer EOF and checked
parent collection. Keep these local native contracts distinct from the unadopted
shared PD proposal and production service ownership. Do not substitute a shared-
address-space thread, successful syscall stub or script rewrite for these requirements.
No particular fork API, copying/COW strategy or resource expansion is adopted by
this dependency review; resolve those against the smallest executable experiment
before implementation, with the existing simplicity questions and failure cases.

Budget the next experiment explicitly: the current program profile has three
worker slots plus its supervisor and at most six channels. The composed shell,
stream backend and file backend already occupy three workers. A simultaneously
live helper or substitution child cannot simply be added to that composition.
Select the required live participants and image grants for the first process
witness before deciding whether scoped service lifetime reuse or a reviewed limit
change is necessary. Do not silently grow pools or call thread contexts spare
process slots. This review authorizes no quota or image-catalog change.

### Consumer syntax execution result — 2026-09-09

The [sealed syntax packet](evidence/shell-syntax-execution-2026-09-09/README.md)
passes 426 command cases and 98 Python host tests plus Zig/pin/workflow checks.
Actual main executes the unchanged eight-byte consumer script with empty stdout,
native diagnostic `sh: 1: Syntax error: "then" unexpected` plus newline, exit2 and
four reclaims across two generations. Skipped main and omitted descriptor closes
reject1501/1503 after client0/client2, respectively, with zero reclaims. No native
attempt failed. All 281 prior cat-owner images remain byte-identical; new owners
are5760 and overall maximum remains8152 within8192. The outer run records UTC
endpoints and about1419 monotonic seconds, below the1800-second review ceiling.
The unchanged argv and signal-table workloads remain unqualified on the explicit
process/descriptor/pipe prerequisites above. No full-dash, TTY, persistent-storage,
consumer acceptance or release claim follows. Next is the bounded process design
and first real helper execution; no new shared PD API or quota was adopted here.

### Real helper child selection — 2026-09-09

Before implementation: qualify the consumer helper itself through the existing
isolated-image launch and AERIO001 owner, before inventing a fork API. Pin the
unchanged userland helper source locally and compile only its main symbol under
a private name; the existing native child wrapper admits descriptors, calls that
body, then closes its two inherited descriptors. Parent requests the explicitly
granted helper image with argv `/inputs/helper`, `argv`, `a b`, `*` and environment
LC_ALL=C, WITNESS=value. No shell expansion or host execution is substituted.
This is a helper-boundary witness, not execution of DASH-argv or fork/exec/waitpid.

The opt-in owner namespace accepts only this helper name and exactly four args/two
allowlisted environment entries; the default bytecount namespace/env policy stays
unchanged. Names do not confer authority: the existing supervisor-held image grant,
parent connection and checked descriptor references still govern admission. Three
workers (parent, stream backend, child) and six channels fit existing quotas; no
concurrent file service is added. Parent and child use independent authenticated
connections and native address spaces. Require child0, parent0, backend17, exact
child output `argv ok` plus newline, no input consumption, empty diagnostics,
consuming collection and six reclaims across two generations. Check parent TLS
sentinel after the child changes its private wrapper sentinel.

Controls corrupt one argument or WITNESS only after validated admission data is
accepted and must expose helper91/owner1407, with no successful collection/reclaim.
Skipping the helper body must fail exact output1405; omitting child descriptor
closure must fail1403. No successful stub, native cap widening, ambient path lookup,
new kernel/wire/SDK API, upstream dash change or resource expansion is allowed.
Aether owns the bounded producer wrapper/owner; userland owns helper/intake and
POSIX compatibility. This opts into a fixture namespace, not a new shared API.

Simplicity: reuse the existing launch, transport, reference lifetime and collection
implementation instead of adding another process service or COW engine for a helper
that already fits the native loader. No obsolete consumed fixture is removed. Full
fork requires copied writable state plus independent client connections; exec and
CLOEXEC remain separate. Existing C compact-style migration and Rust2024 apply;
copy the consumer source verbatim with its BSD notice. No new unsafe/FFI calling
convention: the helper is an ordinary synchronous C function and no pointer escapes.
Select complete command regressions and host/pin/workflow checks, exact helper hash,
size preflight and all failed attempts. No fresh M4 run: no kernel/M4 changes.

### Real helper child result — 2026-09-09

The [sealed helper packet](evidence/shell-helper-child-2026-09-09/README.md) passes
431 command cases and98 Python host tests plus Zig/pin/workflow checks. The real
helper produces exact argv output and status0 with six reclaims across two
generations. All four deliberate mutations reject at their selected1407/1405/1403
checks with zero reclaims. New owners are7368–7384 bytes; the suite maximum stays
8152 within8192. All284 previous cat/shell owner images are unchanged. The target
run took about1437 seconds, within1800; no native attempts failed. The formatting
attempt against recursive modules found old unchanged style, retained in the packet;
scoped formatting passes. No kernel/SDK/wire/quota/pin change or full-DASH-argv
acceptance follows. STATE records the next native fork/exec/wait composition work.

### Bounded process-copy design — 2026-09-09

Design selection for the next implementation, not an allocated syscall ABI or
runtime result. The native helper packet established the child image boundary;
this step specifies the missing copied continuation. Aether owns the bounded
kernel mechanism and producer fixture. Userland owns libc/dash compatibility and
independent acceptance; no production process-service ownership is assigned here.
Foundations O-01–05, I-01/03–06 and E-01–08, proposed PX-01–03, and locally adopted
SE-01–05 apply. Existing releases and consumed profiles remain unchanged.

**Requirement:** copy a cooperating single-context native worker while it is
stopped at an explicit kernel boundary, then resume parent and child with private
writable memory, preserved execution state and separately authenticated I/O.
No ambient factory, arbitrary remote process inspection, copied endpoint ownership,
shared-address-space substitute or successful POSIX fork stub is permitted.
The first target witness is the native copy primitive; unchanged DASH-argv requires
subsequent adapter, transactional exec and parent wait integration.

#### Selected mechanism and publication

Use eager copying of the bounded owned backing, including immutable mapped pages,
into an unused worker slot on the same BSP. Do not introduce COW, page reference
counts, a global process table, another service or a new memory quota. Copying all
owned pages is deliberately simpler than sharing code pages: existing reclaim and
alias protection assume private domain backing. No consumed path is retired yet.

Use symbolic operations in this design; assign exact unused operation numbers,
record sizes and register results in the native reference with implementation.
The selected transaction is:

1. The descriptor owner prepares an independent child request/reply pair and
   provisional inherited open-description references. The parent completes its
   prepare exchange, so no partial request or outstanding reply crosses the copy.
   This reserves resources but does not create or expose a runnable child.
2. The caller enters **self-freeze**, stopping only its own domain at the saved
   syscall continuation. It cannot freeze another worker or create a process.
   A generation-bound, nonwrapping request sequence identifies this exact freeze;
   a later freeze cannot reuse the earlier token. Reject a second live execution
   context, an active signal upcall, or an already pending freeze.
3. A **copy query** lets only the existing scoped supervisor observe the pending
   token. Do not overload readiness, terminal state, yields or a futex address.
   Frozen domains are excluded from rotation; timeout and explicit stop remain
   distinguishable from successful child creation. Existing watchdog policy stays.
4. **Copy commit** requires the supervisor's creation authority, exact source
   lifetime/freeze token, unused destination and two distinct supervisor-owned
   channel endpoints. Source and destination must differ; the source must be a
   live worker, never the supervisor. Preflight destination generation, page and
   table limits, endpoint roles/ownership, supported state and all result bounds.
5. Build destination mappings and copy state while it remains unpublished. On this
   BSP, IF remains clear throughout validation/copy/commit. Preserve parent bytes,
   execution and descriptors. Complete read-only alias protection and the required
   TLB transition before either continuation can use the copied mappings.
6. Only after preparation succeeds, transfer the two endpoints, install the fresh
   child-local grants, publish the child and resume the parent. Parent receives the
   child identity; child receives zero plus explicitly documented rebinding data.
   Publication is the commit point. The supervisor retains the lifecycle handle;
   the user-visible PID does not confer stop/query/reclaim authority.
7. Before commit, rejection leaves the source frozen and retryable or cancellable,
   destination unadmitted, endpoints with their original owner and provisional
   descriptor references uncommitted. Zero any staged backing after detaching its
   mappings. **Copy cancel** checks the same token and resumes the parent with an
   explicit failure after the owner rolls back its provisional references. Stop
   invalidates the token; an old query/commit/cancel must never revive a stopped
   source or affect its replacement. Supervisor fatal behavior remains the current
   bounded profile's behavior, not a new recovery guarantee.

No worker is allowed to write the supervisor's source-state or mapping metadata.
The syscall entry already saves the interrupt frame and FX state. Return data
must be installed in those saved contexts, not a transient stack frame.

#### Copy inventory and concrete implementation hazards

| State | Required treatment |
| --- | --- |
| Saved registers, stack, TLS memory, FS base, FX state | Copy the continuation and owned bytes; change only documented return registers. Preserve stack/red-zone content. Fresh child backing must make pointers at unchanged virtual addresses private. |
| Page records and leaf tables | Walk all live records, including anonymous pages with holes and PROT_NONE. Copy via validated kernel backing, not `byte()`, which rejects inaccessible pages. Rebuild physical PTE addresses; preserve flags and anonymous ownership. Never memcpy page tables or kernel addresses. |
| Unmapped records/backing | Keep records vacant and backing zero; do not expose retired bytes. Existing `addPage()` initializes `anonymous=false`, so a copy path must explicitly preserve source metadata rather than silently converting anonymous pages into image pages. |
| Domain authority | Issue child-local memory authority and transfer only the selected fresh endpoint pair. Do not copy factory, image, thread, block, console or other source grants. Raw integers remaining in copied memory confer no additional ownership. Unsupported authority profiles reject before effects. |
| Execution lifecycle | Fresh child generation/revision, counters and terminal state; no copied waits, thread children, clear-TID registrations, collected status or old readiness. Preserve the caller signal mask and dispositions; start with empty pending signals and no active signal frame. |
| Parent identity | Record the actual parent lifetime in the new opt-in profile. Current getppid always names the direct supervisor and cannot truthfully serve a fork child. PID remains bookkeeping, scoped independently of authority. |
| Descriptor state | Private descriptor tables and flags, shared owner-held open descriptions/offsets. Fresh authenticated connections; no copied transport transaction state or response replay. |

`State` must not be copied wholesale. It contains physical page-table pointers,
backing, mutable grants, thread contexts, streams and lifecycle state in addition
to the user execution being copied. Copy only the enumerated state. The current
`load()` starts fresh ELF execution and cannot supply a fork continuation. Its
RELRO/alias finalization is a required invariant to preserve, not a reason to
re-run ELF startup or discard anonymous mappings.

The native child-return adapter must rebind official libc/transport grant stores,
startup metadata and cached process identity before it can return through public
fork. Do not scan copied memory for integers resembling capabilities or quietly
accept the parent's memory token. The first native witness can consume explicit
return data directly; it does not claim that the current SDK already has this
rebinding hook. Multithreaded fork and atfork semantics remain unsupported.

#### Resource and acceptance budget

Use the existing three workers: parent, stream backend, copied child; the existing
supervisor owns creation and descriptor policy. Three request/reply connections
use six channels. No fourth file-service worker runs concurrently. This is sufficient
for the initial explicit helper grant, not interactive ENV/file-service composition.
Do not expand image catalogs, supervisor code, backing or pool bounds implicitly.
The new profile must also select its own six-reclaim acceptance: current
`native-runner-local` selects four reclaims unless the file profile is active;
enabling unrelated file behavior to get the desired count is forbidden.

Before code, select these executable oracles for the primitive:

- Parent and child resume the same continuation with distinct return values and
  identities. Mutations in stack, TLS and an anonymous page remain private in both
  directions; saved floating-point/register state survives. A deliberate shared
  backing implementation must fail the isolation check.
- Preserve anonymous holes and PROT_NONE/read-only protections. Child protect/unmap
  succeeds with fresh child authority; the copied parent token fails. Fault/reclaim
  and a second generation must expose no retired bytes or old handles.
- Separate parent/child connection requests cannot consume each other's replies.
  Provisional inherited references commit once, with shared offsets and independent
  close. Copied old endpoint tokens and missing rebinding must reject.
- Deny unauthorized caller, foreign/stale source, stale freeze token, wrong endpoint
  role, occupied destination, exhaustion and unsupported multi-context/signal state
  before publication. Force a failure after staging to prove rollback, zeroing and
  retained endpoint ownership; prove cancellation leaves the parent usable.
- Stop before commit invalidates the token; stop/reclaim after commit preserves the
  other domain and retained terminal status. Require exact successful generations,
  terminal order, closes and reclaims; no watchdog or unrelated panic counts as a
  semantic rejection.

Run host/pin/workflow checks, the complete new profile, existing launch/connections,
command regressions and M4 regressions for scheduler/alias changes. Record all
attempts and source/SDK/tool hashes. Current host checks alone do not qualify this
new mechanism. Exact CLI/profile/oracle entries must join the existing workflow
inventory when the implementation exists, not as fictitious runnable commands now.

Then integrate the bounded libc return hook, transactional granted-image exec
(success applies CLOEXEC; failure preserves the old executable and descriptor
state), and parent wait/status before running unchanged DASH-argv. Exec must keep
process identity while replacing its address space; reusing the current fresh
launch as exec would silently change identity and is not sufficient. Substitution
pipes and signal-aware collection follow. No full-dash or release gate closes from
this design record.

#### Freeze boundary implementation selection — 2026-09-09

First executable slice of the copy design: `-Dnative-process-freeze=true` in the
existing connections envelope, with no copy or successful fork return. Local ops:
0x23003 self-freeze (all arguments zero); 0x23004 supervisor query (rdi exact
worker lifecycle handle, other arguments zero); 0x23005 supervisor cancel (rdi
handle, rsi nonzero request sequence, other arguments zero). Query returns zero
when runnable or the pending sequence. Cancellation returns0 to supervisor and
-EAGAIN to the saved worker continuation. Source lifetime is bound by the existing
nonwrapping handle; request sequence never wraps within that lifetime. No token is
an authority grant. Query/cancel require the supervisor before handle inspection.

Disabled operations remain ENOSYS. Self-freeze denies the supervisor; malformed
arguments return EINVAL. Signal-action profiles return ENOTSUP for freeze until their copy rules are
implemented. Existing connections bootstrap rejects thread composition before
these operations can run. Terminal sources return EBUSY; stale
handles or cancellation tokens return EBADF. The sequence ceiling is 2^63-1; exhaustion returns ENOSPC. A cancel against a
live but nonfrozen source returns EBUSY; EBADF for a stale request applies while
the source is frozen.
Stop clears pending freeze; reclaim/relaunch invalidates old handles. Freeze state
is independent of readiness, terminal state, futex waits and I/O, and preserves
register/FX/TLS state through the existing save/restore path. Scheduler excludes
frozen workers while the supervisor remains runnable. No new allocations or grants.

Aether owns this bounded kernel mechanism and Rust supervisor fixture. Reuse the
existing connections suite and C adapter; no new SDK or production service owner.
Add positive repeated cancellation, stop/reclaim/reuse, disabled and unsupported
profiles plus deliberately broken parking/token enforcement. Require exact worker
statuses, six reclaims across two generations and controls that fail before success.
Check malformed/foreign/stale handles and stale requests in the live supervisor.
Select host checks, full connections, launch and command suites plus M4 regression;
retain failures and frozen inputs. The only new unsafe execution boundary is the
existing int0x81 call with documented registers; kernel handles scalar inputs with
interrupts disabled and publishes no user pointers. Eager copy remains subsequent.

#### Freeze boundary result — 2026-09-09

The [retained freeze packet](evidence/process-freeze-2026-09-09/README.md) passes
12 connections, five launch, seven M4 and431 command cases, plus98 Python host
tests and Zig/pin/workflow checks. TLS/stack continuation, stable pending queries,
stale-token rejection, stop/reclaim and two-generation reuse pass. Deliberately
skipped parking and ignored tokens reject1710/1712 with zero reclaims. New owner
images are1544–2408 bytes within8192. The command run took about1411 seconds;
the packet records the timing limitations of the directly invoked short suites.

The two early native fixture failures and sandbox-blocked M4 attempt are retained;
no old bootstrap restriction was broadened to accommodate them. FP isolation and
native sequence-ceiling exhaustion were not newly tested. Copying, destination
publication and libc/process integration remain the next work in STATE, not
completed behavior inferred from freeze/cancel. Existing release pins remain.

#### Private copy/commit implementation selection — 2026-09-09

Before code: add opt-in `native-process-copy`, requiring process-freeze and native
memory. Existing profiles/pins remain unchanged. Aether owns this bounded mechanism
and producer fixture; no POSIX-service ownership or independent adoption is implied.
Reuse private backing, page metadata, saved contexts and transferred channels.
Eager copying avoids COW/reference-count machinery and keeps existing reclaim
ownership; no pool or image limit grows. No consumed fixture is removed.

Local operation0x23006 takes factory/rdi, source lifecycle handle/rsi, destination
slot/rdx, exact pending freeze sequence/r10, child reader/r8 and child writer/r9.
Only the existing supervisor with factory0xa001 may invoke it. Destination must be
unused, distinct from source and within the worker pool, with a remaining generation.
Source must be live/frozen in the supported single-context/no-signal-action profile.
Endpoints must be on distinct empty, open channels with both ends supervisor-owned,
and have reader/writer roles respectively. Denials/stale handles or tokens, invalid
slots, busy state and exhausted generation return EACCES/EBADF/EINVAL/EBUSY/ENOSPC
before mutation. Signals/threads are unsupported. Disabled copy remains ENOSYS.

Copy live owned backing by kernel address, compact holes in metadata without
mapping their virtual addresses, preserve anonymous ownership and PTE flags including
PROT_NONE, and rebuild all physical page-table references. Copy frame/FX/FS/TLS
metadata/mask explicitly; reset clear-TID, waits, child contexts, pending/terminal
and readiness state. No whole-State memcpy or stale-grant acceptance. Child gets a
fresh local memory grant and only the two transferred endpoint grants. Source bytes
and grants remain unchanged. All final aliases and translations are protected before
publication; IF=0 serializes validation through commit on this BSP.

Supervisor receives child lifecycle handle; parent's freeze returns the child PID;
child's freeze returns0 with memory/reader/writer grants in rdi/rsi/rdx. Other
registers retain the saved continuation. This private return binding is not public
libc fork: copied auxv/cached SDK grants are deliberately not rewritten. The native
witness consumes explicit return grants and verifies old tokens fail. In this opt-in
profile getpid/getppid report actual copied-child identity/parent lifetime; names
still confer no authority. General orphan reparenting remains outside the fixture.

Failure injected after copying detaches unpublished mappings and zeroes staged
backing, restoring the vacant destination without consuming its generation or
transferring endpoints; source remains frozen and cancellable. A skip-zero control
must fail an explicit emergency invariant. Successful publication transfers both
endpoints once, marks destination admitted and resumes source only after protection.
No recoverable failure remains after that commit point.

The native witness uses source0, an admitted terminal dummy1 and destination2,
with six channels and six reclaims across two generations. It checks distinct
parent/child returns, TLS/stack/FX continuation, fresh memory/endpoint authority,
independent request/reply bytes, anonymous holes/zero reuse/PROT_NONE contents and
bidirectional memory isolation. Live supervisor trials deny bad factory, source,
sequence, occupied slot and endpoint roles before valid commit. Rollback instead
cancels parent and launches a fresh dummy in destination2 to check generation reuse.
Controls share writable anonymous backing (excluding TLS), lose anonymous metadata,
or skip rollback zeroing; exact status/context must distinguish each from timeout.

Select host/pin/workflow, complete connections/launch/command suites and M4; also
scoped formatting and frozen sources/timing/all failed attempts. The scalar-only
kernel boundary borrows no user pointers. C int0x81 asm binds all changed registers
and memory, with explicit FX witness; ordinary Rust fixture calls reuse the existing
bridge. Existing emergency diagnostic conventions and machine markers remain.
Public libc rebinding, inherited open descriptions, signals, exec/CLOEXEC and wait
remain later; this does not execute unchanged DASH-argv or complete fork semantics.

#### Private copy/commit result — 2026-09-09

The [copy packet](evidence/process-copy-2026-09-09/README.md) passes all 17
connections, five launch, seven M4 and 431 command cases, plus 98 Python host
tests and Zig/pin/workflow checks. Both live isolation directions, fresh grants,
anonymous hole/protection preservation, staged rollback and two-generation reuse
pass; shared backing, lost anonymous metadata and skipped zeroing fail with exact
expected context. The command run took about 1,410 seconds. All final runs retain
UTC/elapsed/status receipts, source hashes and artifacts; both earlier failed
attempts are preserved. Public libc rebinding, inherited descriptors, exec/wait
and independent unchanged-DASH acceptance remain the next work in STATE.

#### Copy-profile thread identity prerequisite — 2026-09-10

Before code: the inspected musl 1.2.6 gettid() returns its cached pthread TID;
__post_Fork(0) refreshes that field from set_tid_address. In the current copy
profile getpid returns generation*4+slot+1, but set_tid_address returns slot+1.
Fix only that opt-in single-context profile to return the same generation-bound
identity after the existing writable-pointer validation. Legacy and threaded
profiles retain their current results. No new syscall or public libc hook is
needed for this kernel prerequisite; IDs remain bookkeeping, never authority.

Extend the existing copy witness: verify initial libc gettid/getpid agreement,
register a dedicated anonymous clear-TID page before freeze, prove the child can
unmap its copied page because the registration was reset, and prove the parent's
registration still pins its page after an invalid replacement. Replacing the
registration with an owned stack word must return the correct parent/child TID.
The child deliberately observes the copied parent TID through libc gettid until
an owner-supplied post-fork hook updates the cache. Do not label a raw registration
call as completed libc rebinding. A deliberate old-slot-ID control must fail exact
parent status 230/owner 1800 before copy publication, with zero reclaims.

Simpler alternative: retain slot IDs and translate them in libc. Rejected because
it creates conflicting process identities and hides generation reuse. Reuse the
existing validated registration path; add no state, pool, service or dependency.
Keep source/child registration ownership, map pinning and clear-on-stop unchanged.
Invalid registration must not replace the existing pointer. Select host checks,
complete connections/launch/command and M4 suites, exact negative context and
source-frozen timed evidence. This is a narrow kernel correction; SDK auxv,
transport/descriptor caches and public fork integration remain separate.


#### Copy-profile thread identity result — 2026-09-10

The [identity packet](evidence/process-copy-tid-2026-09-10/README.md) passes 18
connections, five launch, seven M4 and 431 command cases plus 98 Python host tests
and Zig/pin/workflow checks. The old-slot-TID control rejects parent230/owner1800
with zero reclaims; all earlier controls preserve their exact outcomes. Parent
pin retention, invalid replacement, independent child registration and two-generation
reuse pass. The copied libc cache remains deliberately stale until the future
SDK hook. The initial metadata-control check-order failure is preserved. Final
sources and all attempts are retained with timing; the command suite took about
1,414 seconds. This corrects a kernel prerequisite, not public fork integration.

#### Local child rebinding witness selection — 2026-09-10

Before code: add a connections-only conformance hook using private headers
extracted from the existing receipt-pinned musl 1.2.6 archive. No mutable sibling
headers, magic pthread offsets, public fork interposition or kernel changes.
The hook updates only the three known auxv grant entries, this fixture's input/
output variables and the pthread TID cache. It requires a copied child whose
cached TID names its live parent, a single-thread libc with locking disabled, a zero thread-list lock and self-linked
pthread state. Kernel checks validate the fresh memory grant and endpoint roles
with zero-length operations before registration or cache writes. Scan only the
loader's bounded auxv (15 entries plus terminator), rejecting missing/duplicate
entries. Register the existing libc thread-list lock word, require its return
matches getpid, then commit the known stores. Unexpected identity after successful
registration is fatal; do not resume partially rebound application state.

Simpler alternative: rewrite auxv alone. Insufficient because pthread and transport
caches remain stale. This scoped helper tests the known stores in the raw-connection
fixture only; it does not repair command startup descriptors, locks held by arbitrary
library code, atfork handlers or shared open descriptions. No new service or general
rebinding abstraction is introduced, and no consumed adapter is replaced.

The witness must reject old/invalid grants without changing caches; then public
getauxval/gettid and mmap/mprotect/munmap must use child state, endpoint traffic
must use updated variables, and parent state must remain unchanged. Three deliberate
omissions (auxv, TID, endpoints) require exact child240/241/242 and owner1820 with
zero reclaims. Retain all older cases. Select full connections and host/pin/workflow
checks plus launch compatibility; kernel/M4/command runtime inputs are unchanged,
so prior target evidence remains historical rather than relabeled as a fresh run.
Extracted headers and their upstream COPYRIGHT are retained with source/tool hashes.
This is producer-side experimental hook evidence, not an SDK owner adoption.


#### Local child rebinding result — 2026-09-10

The [rebinding packet](evidence/process-rebind-2026-09-10/README.md) passes 22
connections, five launch and 98 Python host tests plus Zig/pin/workflow checks.
Child libc memory/identity calls and endpoint traffic use refreshed stores while
parent stores remain unchanged. Skipping auxv/TID/endpoint updates rejects exact
child240/241/242, owner1820, zero reclaims. All 18 old connection payloads match
outside the generated bootstrap entropy. Kernel/build sources are unchanged;
prior M4/431-command evidence is historical, not a fresh run of this adapter.
This scoped conformance helper remains separate from SDK-owner adoption and the
command descriptor/atfork/public-fork integration still required in STATE.

#### Command descriptor inheritance selection — 2026-09-10

This source review selects the next native experiment. It does not implement
inherited descriptors or assign the production process service to this repository.
The current raw copy/rebind witness cannot be relabeled as command inheritance.

Current ownership is concrete: startup-adapter.h has 16 private descriptor slots,
per-slot FD_CLOEXEC flags and local duplicate counts; transport.h has binding refs,
rights, live bits, private channel endpoints and poison state. cat-roles.rs owns
three stream positions and binding liveness; native-files/streams.rs owns bytes
and the final backend handles. The current command close removes local ownership
and ultimately closes the one backend stream. Giving a copied client a private
position array, or forwarding its last local close directly, would violate shared
position/lifetime semantics. Rebinding auxv alone cannot repair those effects.

**Selected scope:** source and copied child share three owner-held open stream
descriptions, with distinct connection-local aliases. Each process keeps its own
16-slot descriptor table and flags. Each live binding contributes one holder per
process, not one holder per duplicate FD. Local duplicate counts determine when
that process releases its binding. The final backend close occurs only after the
last holder is gone and no backend operation is unresolved. FD_CLOEXEC survives
copy; only a later successful exec consumes that flag. No files, directory/root
inheritance, additional workers, channel pools, public fork or signals/threads
are silently added to this first stream experiment.

Aether owns the native mechanism and producer-side conformance owner. SDK/libc
integration and production POSIX-service ownership remain coordinated with userland;
sys-init supervision policy and pkg-mgr package policy are unchanged. This is a
local experiment contract under existing Foundations O/I/E rules and the reviewed
PD proposal, not a new shared standard, released ABI or owner approval.

##### Preparation and publication

1. The source wrapper reaches an idle transport boundary outside libc operations,
   blocks signals using the existing mask path, and validates its private table:
   present is boolean, flags contain only FD_CLOEXEC, absent entries are canonical,
   bindings are within the three admitted streams, local counts equal the number
   of present descriptors, and no live descriptor names a dead binding. It retains
   a bounded 16-entry snapshot and restores its original mask on a rejected request.
   Poisoned transport and partially completed requests cannot prepare a copy.
2. A request on the source's authenticated private channel names its current
   lifetime, expected freeze sequence and the bounded descriptor snapshot. Numeric
   refs never select another client's authority. The owner validates each used
   binding against source ownership and rights; no metadata field may add a grant.
   An incomplete frame has no reservation effects. After the full request, the
   source freezes. The owner requires the exact pending freeze sequence and an
   idle backend before reserving anything.
3. Reserve destination capacity, a fresh empty endpoint pair and one staged holder
   per source binding in use. These staged holders retain existing descriptions;
   they do not open new backend handles or copy positions. The owner does not route
   requests from staged aliases. No bootstrap bytes enter the new queues before
   native copy, which requires empty supervisor-owned channels.
4. Invoke existing copy/commit. If it fails before publication, release only staged
   holders/endpoints, leave source descriptors and positions unchanged, and cancel
   the matching freeze. Do not close a still-held backend description. Request
   token and native lifecycle identity remain distinct, and both must match.
5. On success the owner activates the child alias route, keyed by its fresh private
   channel and confirmed lifecycle handle, before servicing either client's next
   command. Send a bounded binding receipt containing the copy identity and fresh
   per-binding refs/rights. The child must validate the receipt and its copied table,
   run libc/grant rebinding, update only binding refs/endpoints, and retain descriptor
   numbers, alias relationships and flags. Re-running startup_begin would overwrite
   duplicated or closed descriptors and is not the selected approach.
6. The child acknowledges successful rebinding before application I/O. The parent
   wrapper also waits for owner completion before exposing public fork success;
   the raw kernel PID result alone is not that completion. The owner may then
   release both wrappers. This user-space gate handles scheduling between the kernel
   copy return and owner publication without a new kernel park/unpark primitive.
7. Failure after kernel publication requires confirmed child stop before removing
   its live holders or reusing its memory/channels. A child may have queued data;
   discard it only after stop, using the existing lifetime boundary. Then notify
   the still-waiting parent of failure. If stop or a backend effect is uncertain,
   retain affected resources and fail closed; do not claim rollback or fabricate
   successful close, readiness or exactly-once processing.

The first implementation must fix/version its bounded request/receipt layouts in
this local reference before adding code. No wire opcode is allocated by this
review. Reuse existing 32-byte transport fragments and 16-byte data chunks, with
explicit whole-record lengths and existing deadlines. Do not add a second general
RPC framework or infer readiness from bytes merely being queued.

##### Shared operations and cleanup

The single owner serializes operations on each description. A read/write obtains
its position from that description, validates the backend result, and advances
only by the accepted byte count. Independent offsets for parent and child are
forbidden. A malformed or missing reply can mean the backend already changed;
mark that description uncertain and stop further operations through *all* aliases
until the existing fail-closed cleanup policy resolves it. Poisoning only the
requesting client would allow the other client to use an unknown position.

Closing a duplicate is local until that client's last descriptor for the binding
closes. The owner then removes that client's holder only. Another holder keeps
position and backend liveness. The last holder triggers one backend close, with
its outcome retained. A reused slot or copied stale reference cannot regain a
closed route. A failed/unknown final close is not a free resource.

##### Executable acceptance and simplicity

Use the existing three worker slots for source, real stream backend and copied
child, with six channels and the current owner image bound. Replace the copy
fixture's terminal dummy with that real backend; do not add a fourth worker or
fake the backend in the kernel. The initial witness freezes outside library calls
with no custom handlers. Keep the source and child alive together long enough to
observe both position and lifetime effects.

- Duplicate stdin to FD >=10 with FD_CLOEXEC before freeze. Child and parent retain
  that flag and their private alias tables; changing one process's descriptor flags
  does not change the other. No close-on-exec claim is made until real exec exists.
- With backend input abcdef, coordinated parent/child/parent reads must return a,
  b, c. A deliberate private-offset implementation must fail this exact sequence.
- Parent closes its two local aliases while the child still holds its copies;
  child can read d. Child closes one alias and reads e through the other. Only its
  final close may close the backend input once. Cross-route stale refs reject.
- Reject malformed snapshots, invalid bindings or duplicate binding definitions
  (valid descriptor aliases remain allowed), widened rights, stale
  lifetime/sequence, poisoned or non-idle transport and exhausted reservations
  before copy. Count source state, pending backend effects and staged resources.
- Inject failure before copy and after publication/before readiness. Check unchanged
  parent state on the first path and confirmed child stop before release on the
  second. Deliberate early backend close, dropped CLOEXEC, missing parent completion
  gate and unresolved shared-position reuse must fail distinct named outcomes.
- Require two-generation reuse and exact stream/backend terminal/close counts.
  Preserve existing raw-copy and all affected command positive/negative oracles.
  Freeze inputs, retain all attempts, run host/pin/workflow and complete affected
  target suites, and record real owner size before claiming it fits.

Simpler alternatives were considered: copying the existing broker state gives
wrong offsets/lifetimes; reopening streams changes open-description identity;
adding a kernel FD table moves policy into the kernel; pausing the child through
a new syscall is unnecessary when neither wrapper has returned to application
code. Choose one user-space owner with explicit holders and staged publication.
No old consumed path is removed yet. The added cost is bounded alias/transaction
state and two wrapper completion gates; keep it local to this required experiment.

#### First inherited-stream witness implementation — 2026-09-10

Before code: implement the positive ownership spine plus private-offset and early
backend-close controls. Use existing startup-adapter/transport, copy_rebind and
Rust streams backend. This first slice does not complete the preceding rollback,
malformed-request or uncertain-operation matrix. The initial selection was host,
full connections and launch with unchanged kernel behavior; the profile-composition
correction and expanded regressions are recorded below. No public SDK or wire ABI
adoption is implied.

Local fixture records are little-endian, transported in existing bounded fragments.
Bootstrap is unchanged AECAT001 (128 bytes). Prepare is 96 bytes: u32 op=64,
sequence=1, source generation, descriptor count=16, then16 reserved zero bytes;
64 bytes encode16 descriptors as binding/flags/present/reserved u8 fields. This
initial owner accepts the exact tested table: descriptors0/1/2 plus stdin duplicate10
with FD_CLOEXEC, all others absent. A complete record and matching frozen sequence
precede reservation. No general snapshot acceptance is implied.

Child binding receipt is32 bytes: u32 op=65, generation, sequence=1, then three
u32 references and8 reserved zero bytes. Child acknowledgment is32 bytes with
u32 op=66 and all remaining bytes zero. Completion is32 bytes with u32 op=67 and
remaining bytes zero; both wrappers wait for it. Existing file requests/replies
retain their32-byte layout and read/write/close opcodes. Source references retain
0x76000000+(binding<<16)+generation; child references use0x77000000 with the same
suffix, scoped to the fresh private connection. These values confer no authority
outside that owner route.

Stage one child holder per stream before native copy; on this positive spine,
require successful copy, activate its route and wait for rebinding acknowledgment.
The owner serially services parent a, child b, parent c; source closes its aliases,
child reads d, closes one alias, reads e through FD10, then closes all remaining
bindings. Backend close is forwarded only on the final holder. Exact terminal order
source71, child72, backend17 and six reclaims is required across two generations.
The private-offset control must reject owner1903 on the b read; early backend close
must reject owner1952 when the still-authorized child next reads. Reject unexpected
records or terminal outcomes rather than treating a watchdog as acceptance.

This reuses real descriptor duplication/close and the existing backend instead of
adding a model or kernel FD service. New conformance owner state is one shared input
position and two sets of binding holders, not duplicate backing or per-client
positions. The existing8192-byte owner and kernel pools remain limits. Further
copy-failure/publication-failure recovery is explicitly pending, not successful stub
behavior; the fixture fails closed on those unexpected paths.

Composition correction after the first native attempt: enable the existing
`native-runner-local` mask guard for these three copy cases. The kernel completion
oracle must retain six reclaims for the copy profile even with that guard enabled;
no syscall or authority semantics change. Re-run the full command suite, launch,
connections, M4 and host checks for this shared fixture-completion change.

The existing C backend bridge translates Rust service success0 to worker exit17.
The first guarded run completed the reads and both clients, then correctly hit
its mismatched expected-backend-status assertion. Preserve that failure and use
bridge exit17 as the exact success oracle; no backend behavior was changed.

The C freeze assembly reuses the documented copy return convention: all changed
registers are explicit outputs and the memory clobber covers continuation stores.
Stack buffers stay owned by the calling domain until synchronous transfer returns.
The copied child passes addresses of its private endpoint variables to the existing
validated rebinding hook; no pointer escapes. Rust uses the existing syscall helper
and C backend bridge without a new FFI convention. This owner is in the witness TCB
for stream position and lifetime; routing integers alone confer no authority.

[First-witness evidence](evidence/inherited-streams-2026-09-10/README.md) retains
positive and deliberate broken-backend controls. The completion-gate implementation
is present, but its omission and malformed/publication-failure controls remain the
next work. Do not infer complete protocol or independent consumer acceptance.

This first client is single-context with custom signal delivery disabled. Existing
descriptor operations use their real mask guards, but the snapshot/freeze sequence
does not yet implement the broader signal-held preparation transaction above.
It accepts only the exact initial table, not arbitrary closed/duplicated layouts;
receipt rights remain the three fixed bootstrap rights. General table validation,
signal-aware preparation and negotiated inheritance remain outside this witness.

#### Inherited-stream publication recovery selection — 2026-09-10

Before code: add recovery after kernel copy but before application I/O. Three
bounded cases reject a receipt with nonzero reserved byte31, reject an invalid
child completion opcode68, or stop the child while its receipt is withheld.
The first two must observe child exit251 with no child-channel application request;
the last must query exact status143/kind3 after native stop0x20007. Only then remove
the child's three holders. Keep backend handles and position unchanged, notify the
parent of failure, and let it read a/b using FD0/10 before final closure. Require
parent73/backend17, all three backend closes, and six reclaims across two generations.
Forced stop has no normal child terminal log; its query is the enforcing witness.

Local records remain32 bytes, with an opcode and zero remaining bytes. Parent
failure notification is68. Probe69/reply70 exercises the parent's still-waiting
completion wrapper before holder cleanup and notification; this is a conformance
probe, not a production readiness protocol. The wrapper accepts at most one probe
and then one success67/failure68. A skipped parent gate must send an application
request instead of reply70 and reject owner1962 before any reclaim. Child traffic
before rejected-receipt termination rejects1961; traffic after rejected-completion
notification rejects1963. Omitting receipt validation, the child completion gate,
or confirmed stop must reject1961/1963/1964, respectively, with zero reclaims.
No probe substitutes for kernel terminal observation or authorizes backend I/O.

This directly implements the existing owner-held reference design and reuses stop,
query, close and reclaim. It adds no kernel operation, shared mutable kernel table,
SDK dependency, channel or worker pool. Sources remain single-context with custom
signal delivery disabled. Pre-copy rollback, arbitrary table preparation, short or
missing records, shared backend uncertainty, signal-aware preparation and public
fork/exec/wait remain subsequent work. The parent failure record does not expose
successful fork or fabricate a public errno contract.

Simpler alternatives are insufficient: exiting the whole fixture preserves safety
but cannot demonstrate parent recovery; closing the backend with the child would
invalidate the parent's remaining authority. Choose direct holder removal after
confirmed terminal state, sharing the existing final cleanup code. None of the
consumed older paths can be removed yet. New byte buffers remain stack-owned over
synchronous syscalls; no pointer escapes, new FFI convention or unsafe boundary is
introduced. Retain Rust2024 formatting and the pinned C21.1.8 formatting profile.
Aether owns this local conformance implementation; SDK adoption and sys-init policy
remain separate, and no sibling or released standards pin changes are selected.

Select full connections and launch suites plus host/pin/workflow checks, exact
negative outcomes, two-generation reuse and owner size. Compare kernel/build and
previous raw connection payloads outside the48 entropy bytes; unchanged command
and M4 evidence stays historical, not a fresh run. Preserve failed attempts and
freeze runtime sources for each qualification run. Foundations O-03/04, I-01/03/04,
E-01/04/06 and the locally adopted simplicity process apply within this scope.

[Publication recovery evidence](evidence/inherit-recovery-2026-09-10/README.md)
passes all32 connections and five launch cases plus host checks. Three recovery
paths preserve parent FD10/CLOEXEC and the original input position across two
generations; the four omitted-safeguard controls reject their exact owner statuses
before reclaim. No kernel change or broader SDK/signal adoption is implied.

#### Inherited-stream pre-copy rollback selection — 2026-09-10

Before code: compose the existing native-copy-fail-stage injection with the real
inherited-stream owner. Require ENOMEM(-12), unchanged pending freeze sequence1,
no destination handle, and four still-owned staged endpoint ends. Release those
ends and only the staged child holders; all closed ends must reject zero-length
I/O with EACCES(-13). Reject stale cancellation sequence0 without waking the source,
then cancel sequence1 and verify no pending freeze. The rollback-only C client
must observe EAGAIN(-11), keep its original libc/FD state and wait for the existing
probe69/failure68 protocol. Parent reads a/b through FD0/10 with CLOEXEC intact and
closes all backend bindings exactly once. No successful fork return is fabricated.

After parent73/backend17 termination and cleanup, launch the existing backend
image into slot2 at the original expected generation: failed copy must not consume
that generation. Validate its hello, close all three streams, terminate17 and reclaim.
This gives six reclaims across two generations without a dummy program or new pool.
The replacement is delayed until original channel cleanup to respect the existing
six-channel, three-generation retirement budget; do not add allocations solely
for probing. The staged-endpoint rejection checks prove closure directly.

Add deliberate skipped endpoint close, premature backend close and skipped freeze
cancellation variants. They must fail owner1972,1952,1973 respectively with zero
reclaims; positive rollback must retain source73/backend17/replacement17 terminal
order each generation. ENOMEM/frozen/vacant-destination checks use1970, endpoint
ownership/close checks1972, cancellation checks1973 and replacement identity1974.

This reuses kernel rollback/cancel and the previous parent recovery path instead
of introducing a second transaction service. Extract the shared parent and backend
cleanup portions only where this caller requires them. No consumed old path can
be removed yet. No kernel, wire-layout, resource, SDK, dependency, unsafe/FFI or
sibling change is selected. The C asm convention is unchanged; the rollback fixture
accepts only its documented cancellation result. Custom signals and threads remain
disabled. General admission failures, arbitrary tables, incomplete messages and
shared backend uncertainty still need subsequent work before public fork/exec/wait.

Apply the existing Foundations O/I/E and simplicity review; preserve released pins.
Run full connections and launch plus host/pin/workflow checks on frozen sources,
verify exact rejection markers and size, compare unaffected payloads/kernel hashes,
and retain every failed attempt. Prior command/M4 results remain historical for
this connections-only change. Use Rust2024 and pinned Clang-format21.1.8 as before.

The first rollback run reached parent73/backend17, then replacement189/owner1950
with two reclaims: the existing launch helper names slot2 `client`, while this
reused backend requires `worker`. Scope that startup label to inherit_rollback
slot2 only; keep the backend's validation and all expected terminal outcomes.
Retain the failed source/target evidence and rerun on corrected frozen inputs.

[Pre-copy rollback evidence](evidence/inherit-rollback-2026-09-10/README.md) passes
all36 connections and five launch cases plus host checks. Exact staged-endpoint,
backend-lifetime and cancellation controls reject before reclaim; parent state and
destination generation survive ENOMEM across two cycles. Two representative
command-owner images remain byte-identical; no new command/M4 runtime run is claimed.

#### Incomplete child publication selection — 2026-09-10

Before code: bound readiness reception to256 native read attempts, yielding on
EAGAIN. Preserve accumulated bytes; only a complete32-byte acknowledgment can be
validated as ready. An incomplete result must never publish parent success. Exercise
missing/16-byte receipt and missing/16-byte acknowledgment. Receipt variants use
the normal child blocked in its existing reader; acknowledgment variants deliberately
stall the child after zero/16 bytes. The existing owner stops it after the bound,
queries exact status143/kind3, then uses the established parent-failure recovery.
Count acknowledgment bytes exactly:16 only in the short-ack case, otherwise0.
No new child reply/completion opcode, kernel timer, pool or public API is needed.

Require parent73/backend17 (no normal forced-child terminal log), two generations
and six reclaims with parent FD10/CLOEXEC and reads a/b intact. The production-like
receiver returns success only at32; test controls that zero-pad an incomplete ack
or omit stop must fail owner1982/1981 before reclaim. Byte-count/classification
mismatches use1980. Missing tool or external watchdog expiration is not acceptance.
The256-attempt budget is a bounded fixture policy, not elapsed-time semantics or
proof of fairness under arbitrary schedules. The intentionally stalled clients are
terminated by the owner; no unbounded successful server wait is introduced.

Use a local Result from the readiness reader rather than a second RPC framework.
The simpler whole-fixture abort cannot demonstrate retained parent usability, while
retrying publication could duplicate effects. Borrow the existing explicit-stop
boundary; do not infer stop from timeout. The initial scope expects a live stalled
child; preexisting unrelated child terminal states, incomplete final completion,
partial parent snapshots and backend uncertainty remain later cases. No old consumed
path is retired yet. Buffers stay stack-owned during synchronous syscalls; no new
unsafe/FFI boundary, dependency, kernel or sibling changes. Keep fixed bootstrap
rights and single-context/custom-signal-disabled constraints.

Select full connections and launch plus host/pin/workflow, exact negative controls,
owner size and kernel/unaffected-payload comparisons. Prior command/M4 evidence is
historical. Freeze sources, retain failed attempts and use the existing Rust2024 /
Clang-format21.1.8 profiles. Foundations O/I/E and locally adopted simplicity apply;
released standards pins and SDK adoption remain separate.

#### Shared inherited backend uncertainty selection — 2026-09-10

Before implementation: select one real-backend malformed read reply after successful
child publication. A shared owner-held uncertainty latch must prevent all later
backend operations through either process's input aliases. Both clients must get
EIO with untouched read buffers through FD0 and FD10, retain private CLOEXEC flags,
and consume their closes. No uncertain position advance, retry, backend close or
resource reuse is allowed. Confirm native backend stop143/kind3 before reclaim.
Repeat two generations using the existing three workers/six channels and8192-byte
owner bound. Source74/child75, zero backend closes and six reclaims are the success
oracle. A child-only latch bypass must reject owner1992 with child254; omitted stop
must reject owner1993 before any reclaim. The first invalid reply is complete, with
a reserved byte set by the real Rust backend; missing/partial replies and uncertain
writes/final close remain later coverage.

Aether owns this bounded producer fixture. Userland's installed SDK and POSIX-service
adoption remain separate; sys-init and package policy do not change. Existing
Foundations O/I/E, local inheritance/transport contracts and reviewed PD ownership
apply. Complete EIO replies here report unresolved backend outcome, not proof of no
effect; the owner blocks the whole three-stream backend until stopped. Client-local
transport remains usable for explicit alias release. No new opcode or ambient
authority, kernel primitive, pool, unsafe/FFI boundary or dependency is introduced.
Stack-owned synchronous messages and the existing signal-masked C adapter remain.

Simplicity: poisoning only the requesting transport is smaller but leaves the other
process able to use an unresolved description. Choose one shared latch and existing
stop/dispose paths; no retry/reconciliation service or per-alias uncertainty state.
No obsolete path can yet be removed. Rust2024 and pinned clang-format21.1.8 apply
to touched files only. Update NATIVE-CONNECTIONS, workflow and STATE. Run host checks,
full connections and launch suites; compare old raw payloads and ordinary backend
image with the preceding packet. Backend injection is cfg-scoped; kernel/build and
command behavior must remain unchanged. Prior full command/M4 runs stay historical.
Freeze runtime inputs during runs and retain every failed attempt.

#### Missing inherited backend reply selection — 2026-09-10

Before implementation: extend the existing shared uncertainty latch to a backend
that sends no reply or only 17 of 32 bytes, then remains live and yields. The partial
record includes the successful count and first input byte; its absent tail would
otherwise look valid if padded with zeroes. Reuse the bounded record accumulator
(256 read attempts, yielding on EAGAIN), retaining exact received counts 0/17.
The bound is an attempt budget, not a wall-clock deadline or fairness guarantee.
No partial result, buffer mutation, offset advance, replay or backend close may
escape. Both clients retain EIO/FD0/FD10/private-flag/consuming-close checks. Require
source74/child75, confirmed backend stop143/kind3 and six reclaims over two generations.

Add positives for missing/partial replies, a partial-padding mutant requiring
source254 then owner1992 before reclaim, and missing-reply omitted-stop requiring
owner1993 before reclaim. Keep all previous oracles. Aether owns this producer
fixture; installed SDK, sys-init and package policy stay separate. Foundations O/I/E,
local inheritance contracts and reviewed PD boundaries apply; pins remain frozen.

Simplicity: reuse one bounded record reader for readiness and backend replies rather
than copy its loop. A shared uncertainty flag and existing stop/dispose remain
sufficient; no retries, new opcode, service, pool or configuration surface is needed.
Only intentional test cfgs select stalls/padding. The 17-byte injection uses the
existing bridge_write FFI with a live stack-owned 32-byte reply and an exact bounded
length, checks the returned count, then yields until native stop; no pointer escapes
or concurrent mutation occurs. Normal backend behavior and kernel stay unchanged.
Rust2024 formatting applies to the two touched Rust files; no C change is selected.
Update NATIVE-CONNECTIONS, workflow and STATE. Run host, full connections and launch
checks on frozen sources; compare ordinary backend/client and older raw payloads
against the preceding packet. Prior command/M4 runtime remains historical. Preserve
failed attempts. Uncertain writes/final closes and general process adoption remain
later work.

Partial-backend fixture correction: the first attempt rejected backend122/owner1994
because it required one write to transfer all 17 bytes. Accumulate the prefix over
at most 256 writes, yielding on EAGAIN and validating each returned count before
advancing the pointer. The stack reply stays live; every pointer and length is
within its first 17 bytes. No protocol or owner oracle changes. Retain this failed
attempt and rerun all selected suites on corrected bytes.

#### Uncertain inherited writes/final closes selection — 2026-09-10

Before implementation: extend the bounded inheritance owner to a malformed reply
following an actual stdout append, and following the last holder's input close.
Writes must report EIO to both processes, never repeat the append, and block all
later backend operations. Final close may consume the local alias but must retain
unresolved backend lifetime until confirmed stop; no success may be fabricated.
The first parent closes only its holders successfully. The child's last input close
gets EIO; its remaining closes consume aliases locally with EIO. Confirm backend
stop143/kind3 before six reclaims over two generations. Write clients retain74/75;
close clients use76/77. FD10/private CLOEXEC and repeated-close EBADF checks remain.

Select write success/replay/omitted-stop and close success/false-success/replay/
omitted-stop cases. The backend injects a reserved byte after applying the selected
operation and rejects any subsequent request with terminal124 in replay controls.
Replay rejects owner1994 for writes or1995 for closes, before reclaim; false close
success rejects child255/owner1996; omitted stop retains owner1993. No missing reply
write/close matrix or exactly-once guarantee is claimed by these malformed witnesses.

Aether owns this local producer fixture under existing Foundations O/I/E and
inheritance contracts; userland SDK/POSIX adoption, sys-init supervision and package
policy remain separate. No kernel, opcode, pool, dependency or new unsafe boundary.
Stack-owned messages use existing synchronous transport. Reuse the shared uncertainty
and stop/dispose paths; a dedicated small final-holder traversal is simpler than a
general transaction service. Copying offsets or reopening handles is insufficient.
No obsolete public path is removed. Rust2024/pinned clang-format21.1.8 apply to touched
sources. Update NATIVE-CONNECTIONS, workflow and STATE; freeze runtime sources and
run host, full connections and launch suites, plus old payload/backend comparisons.
Prior full command/M4 evidence remains historical. Preserve failed attempts and pins.

#### Incomplete inherited effect replies selection — 2026-09-10

Before implementation: use the existing backend prefix/stall injection after an
actual stdout append or last-holder input close. Zero-byte and 17-byte replies
must enter shared uncertainty within the existing 256-read-attempt bound. Do not
publish the partial success count, retry an effect, fabricate close success or
reuse resources before confirmed backend stop143/kind3. Keep source74/child75 for
writes and source76/child77 for final closes, private FD flags, consuming local
closes and six reclaims over two generations. This is not a wall-clock deadline.

Select four positives (missing/partial write/close), two partial-padding controls
(source254/owner1992 for write; child255/owner1996 for close), and two missing-reply
omitted-stop controls (owner1993). All controls require zero reclaims. A partial
close reply is all zeroes: bytes being zero does not make the 32-byte frame complete.
Retain all existing replay and malformed-reply cases and exact received counts0/17.

Aether owns this bounded producer fixture under existing Foundations O/I/E and local
inheritance contracts. Userland SDK, sys-init and package policy are unchanged. Reuse
the backend's checked prefix writer and bounded owner reader; handle incomplete close
responses explicitly rather than add another transport or transaction service.
No backend/kernel/C change, new opcode, pool, dependency or unsafe boundary is needed.
Missing/partial outcomes must retain uncertainty even when local aliases are consumed.
Rust2024 formatting applies to the owner; retain prior code conventions elsewhere.
Update NATIVE-CONNECTIONS, workflow and STATE. Freeze sources; run host, full connections
and launch checks and compare ordinary images/older payloads with the preceding packet.
Command/M4 results remain historical; unchanged backend/command sources justify scoped
qualification. Preserve failed attempts and released pins. Remaining publication and
preparation work still precedes installed SDK fork/exec/wait adoption.

#### Incomplete final publication selection — 2026-09-10

Before implementation: after a validated child readiness acknowledgment, publish
final success completely to one client but send zero or 16 of 32 bytes to the other.
A partially completed pair is not rolled back: one client may have observed success.
The bounded producer fixture must contain both clients before releasing their holders
or discarding queued requests. Do not append a failure record behind a partial frame,
forward an application operation, report successful fork-pair publication or reclaim
a live client. This is a fixture containment choice, not sys-init restart policy or
an installed SDK fork contract.

Select missing/partial parent and child completion cases. Require zero application
bytes from the incomplete client over 256 read attempts, then confirm both clients
stopped143/kind3. Only after stop, inspect/drain the complete peer's one queued input
request and verify EOF on both client response channels. The backend received no
application operation; close its three known idle handles and observe backend17.
Repeat two generations and six reclaims. No user terminal serial lines are expected
for forced stops; backend17 is the sole normal terminal per generation.

Two partial-padding controls must expose an application request and reject owner2001
before stop/reclaim. Omitted parent stop rejects2002; omitted child stop rejects2003,
both before queued-request discard or reclaim. Verify EOF/idle backend cleanup under
owner2004. The bound is 256 attempts with EAGAIN yields, not a wall-clock deadline.

Aether owns this local producer experiment under Foundations O/I/E and the existing
inheritance contracts; userland SDK and companion policy remain separate. Reuse the
bounded record reader, native stop, existing close and dispose paths. One contained
pair avoids adding a retry protocol or another completion opcode; a whole-pair stop
is chosen because replay/rollback cannot undo already published success. No new
kernel mechanism, pool, dependency or backend change is needed. The C padding mutant
uses existing memtrap with a live stack-owned 32-byte buffer, checked remaining length
and bounded reads; no pointer escapes or concurrent mutation occurs. Normal C parsing
continues to require all 32 bytes. Rust2024 and pinned clang-format21.1.8 apply to
touched sources. Update NATIVE-CONNECTIONS, workflow and STATE; freeze sources and run
host, full connections and launch checks, with older payload/image comparisons.
Prior command/M4 results remain historical. Preserve failed attempts and released pins.

#### Client descriptor preparation selection — 2026-09-10

Before implementation: validate the client's 16-entry table before publishing its
96-byte plan or entering native freeze. Preserve the owner's existing exact snapshot
check before reservation. Require boolean present/live fields, canonical absent
entries, in-range binding indices, only FD_CLOEXEC flags, matching per-binding local
duplicate counts, the three admitted live streams, exact parent lifetime refs/roles/
rights, initialized unpoisoned transport and distinct nonzero channel endpoints.
Do not index a binding until its range is checked. This validates the admitted
three-stream fixture; it does not yet admit arbitrary open/closed stream sets.

Select nine rejected preparations: invalid presence, flags, binding range, dirty
absent entry, wrong duplicate count, dead binding, widened rights, stale ref and
poisoned transport. Rejection returns client78 without plan bytes or freeze. Owner
observes terminal78 and empty channel, checks vacant child identity and both remaining
channel slots, then closes known idle backend handles and reclaims source/backend.
Three generations require source78/backend17 and six reclaims, with no slot2 admission.
Three cycles preserve the existing copy-enabled fixture completion count; no kernel
check is relaxed and both spare channels exercise all three admitted generations.
Ignoring a duplicate-count validation failure must expose plan bytes and reject
owner2010 before reclaim. A deliberately leaked reservation must fail the capacity
check with source78/owner2011 before reclaim. Cleanup failures use2012.

Aether owns this producer fixture under Foundations O/I/E and existing inheritance
contracts; SDK, sys-init and package policy stay separate. Client validation is not
an authority boundary: kernel and owner checks remain. Current clients have one
context and no custom signal delivery; signal-masked preparation is subsequent work,
not claimed atomic here. Simpler owner-only validation cannot see private duplicate
counts or transport poison before freeze. Choose a small stack count array and one
validator rather than a new serialized schema or general FD service. No opcode,
kernel/backend change, pool, dependency or unsafe boundary. Rust2024 and pinned
clang-format21.1.8 apply to touched files. Update reference/workflow/STATE, freeze
sources, run host, full connections and launch checks and compare old raw payloads
and backend images. Prior command/M4 runtime remains historical. Retain failures,
released pins and companion ownership.

#### Masked inheritance preparation selection — 2026-09-10

Before implementation: enter the existing signal mask guard after startup/FD10 setup
and before descriptor validation. Retain the saved mask in private copied client
state through plan publication, native freeze/copy, libc/endpoint rebinding and final
completion. Restore it before any application I/O. Restore on validation rejection,
copy cancellation and other returning errors; forced-stopped clients do not resume.
Check held mask at preparation, freeze return, rebinding and completion boundaries,
and verify exact saved mask after restoration. Nested existing FD guards must preserve
the held mask. The kernel already copies the native mask but rejects copy with custom
signal actions/threads; no handler-capable or multi-context fork claim is selected.

Exercise nonzero initial SIGUSR1/SIGUSR2 mask on success, validation rejection,
pre-copy rollback and bad-receipt recovery, while retaining all prior zero-mask cases.
Omitted entry/rejection restoration must produce source79/owner2010 before reclaim;
omitted parent/child restoration must produce the corresponding client79/owner1950
before application traffic or reclaim. Retain the exact old positive lifecycle counts,
including three preparation cycles. A failed mask restoration cannot continue useful
application work; use existing fail-closed mask-leave behavior and fixture79 for
observed invariant failures.

Aether owns this producer fixture under Foundations O/I/E and the local inheritance
contract; installed SDK, sys-init and package policy remain separate. The simpler
per-call FD guards leave gaps across validation and publication, so retain one private
saved mask and active flag across the whole interval, reusing the existing mask API
and adding no kernel, wire opcode, pool or dependency. A private child-side flag scopes
negative controls; no shared mutable cross-process state is introduced. Stack mask
query/set buffers remain live for synchronous existing memtrap calls, checked at eight
bytes; no pointers escape. None of the existing compatibility paths can yet be removed.
Rust2024/current C with pinned clang-format21.1.8 apply. Update reference/workflow/STATE,
freeze runtime sources and run host, full connections and launch suites, old raw-payload
and backend comparisons. Prior command/M4 execution remains historical. Preserve all
failed attempts and released pins. Actual handler delivery and pending-signal semantics
require a later explicit kernel/SDK design, not inference from mask-bit observations.

## Signal state across native process copy — 2026-09-10

This is the selected next producer contract, not implemented signal-capable copy.
The current freeze and copy operations reject the entire `native_signal_actions`
build profile with -95, even when all dispositions are default. Removing only that
rejection would leave the child with zeroed dispositions: copy currently rebuilds
`Execution` explicitly and does not copy `State.signal_actions`. The existing
mask witness therefore cannot qualify this extension.

### Required state and publication boundary

Keep the existing supervisor capability, source lifetime handle, freeze sequence,
empty destination, channel ownership/direction and zeroed backing checks. No new
PID-based authority, opcode, global action table or signal-routing service is
needed. The first supported extension remains one execution context per domain.
Thread-enabled profiles remain rejected with -95 before reservation or mutation.
The deliberately shared-action negative profile must never qualify as a supported
copy configuration.

At the existing successful copy publication boundary, the child must contain a
private value copy of all 64 already validated action records, including supported
flags, restorer and normalized action mask. The child's execution mask comes from
the source as today. The child's pending set is empty; the parent's dispositions,
pending set and mask remain unchanged by the copy operation. Later installs,
posts, delivery commits and reclamation in either domain must not affect its peer.
Copying pending bits would duplicate an occurrence; clearing source pending bits
would lose one. Neither is an acceptable substitute for an empty child set.

Populate child signal state only after backing preparation succeeds and before
`child.admitted` becomes true. It remains unreachable while mappings and endpoint
authority are prepared. A failed pre-publication copy keeps source signal state
intact, leaves the source frozen for the existing explicit cancellation, and
leaves destination generation, channels and zeroing obligations unchanged. Child
signal records must not survive rollback or later slot reuse. No new allocation
or user pointer lifetime is introduced: records contain values and user virtual
addresses, not host pointers. Copying 64 fixed records adds bounded work; it does
not enlarge the existing action-enabled State allocation.

### Handler frames and resumption

The existing delivery design keeps the restorer payload in user memory without
an active-handler kernel token. A copy taken during a handler therefore copies
that handler's stack and interrupted context as ordinary private memory. Do not
invent an active-handler flag that would become stale after a nonlocal escape.
Both copies must be able to finish their inherited handler independently using
the existing validated sigreturn path. Handler and restorer addresses remain the
same virtual addresses; entry/return mapping and FP validation still apply in
each domain. Invalid or changed child mappings must not consume a parent pending
signal or alter its frame.

The inheritance client must retain its all-maskable-signals guard until private
libc/endpoint/descriptor state is complete and publication is settled. Restoring
the saved mask may immediately enter a pending parent handler before the mask
syscall returns. At that point the handler must see complete local state and be
able to use the existing nested descriptor guards. The child must not receive the
parent's pre-copy pending occurrence when it restores the same saved mask.
A mask restored from within an inherited handler is still that handler's mask;
the later validated restorer restores the pre-handler mask from its private frame.
This contract adds neither external posting nor timer-driven delivery. Pending
signals during indefinite I/O, EINTR, default termination, job control and thread
fork semantics remain separate work.

### Qualification before opening the gate

Implement and qualify the raw single-context copy plus action-record state first;
then compose it with the inherited-stream client. Do not open the public SDK fork
path on a raw-copy pass. Required tests must identify the following outcomes:

| Witness | Required observation | Deliberate broken control |
| --- | --- | --- |
| Disposition snapshot | Parent and child query exact DFL, IGN and custom records, masks and supported flags | Omitted child records fail exact comparison |
| Pending isolation | Masked/coalesced parent post survives copy; child explicit poll sees none | Copying pending bits causes unexpected child handler entry |
| Parent preservation | Parent poll/unmask delivers its retained occurrence once after completion | Clearing parent pending loses the expected handler entry |
| Private mutation | Child changes one action and posts locally; parent record and delivery remain unchanged | Shared records or pending state fail peer observation |
| Active-handler copy | Both copies return through their private inherited restorer and preserve CPU/FP/mask state | Corrupt only child return payload; parent remains valid |
| Guarded publication | Parent pending handler runs after endpoint/FD rebinding and final publication, including a nested FD operation | Early restore exposes incomplete client state and fails the publication oracle |
| Rollback and reuse | Injected copy failure retains parent post/actions and original destination generation; later reuse starts clean | Residual child action/pending state fails fresh query/poll |
| Unsupported context | Thread-enabled copy remains -95 with no state or authority mutation | Removed context restriction fails rejection oracle |

Use exact client/owner terminal records and zero-effect/reclaim assertions rather
than accepting a generic panic. The implementation slice must assign concrete
markers and case names before coding. Run host tests, complete connections and
launch suites, and all existing action/frame/mask-delivery target cases affected
by the changed kernel source. If the implementation changes shared dispatch or
scheduling, broaden to the corresponding command and M4 suites. Freeze sources,
retain every failed attempt and publish matching artifact identities. Existing
mask, rollback, incomplete publication and backend-uncertainty controls remain.

### Ownership, standards and simplicity

Aether owns this native enforcement and fixture contract; userland owns installed
SDK adaptation and independent dash acceptance. Sys-init supervision and package
policy are unaffected. Foundations O-01/O-03/O-04 and I-01/I-03/I-06 require those
boundaries, explicit unsupported outcomes and publication checks. E-01/E-04/E-05/
E-06 keep this design separate from target and consumer qualification. Distribution
PX-01–03 still leaves full fork/exec/wait and shell-tier acceptance open. No shared
standard, released pin or sibling source changes here.

The simpler alternative is leaving action-enabled copying rejected. It remains
the safe runtime behavior until these witnesses pass, but cannot complete the
selected dash path. Choose one value copy of existing validated records with an
explicitly empty child pending set; a second service, generic snapshot framework
or active-handler lifecycle table would add ownership and recovery cost without
meeting an additional requirement. No compatibility path is removed before its
replacement qualifies. This design adds no runtime code, dependency, stack budget
or unsafe boundary. The implementation review must account for the fixed record
copy cost and existing synchronous mapping/frame checks; passing host models alone
will not authorize lifting the gate.

### Signal-copy state staging selection — 2026-09-10

Before code: add one owner-local inheritance operation to the existing signal
state, used at the existing child execution initialization before publication.
Copy all validated records by value and clear only destination pending bits.
Caller supplies distinct, serialized domains and an unpublished destination;
no user pointer is retained. Keep both action-profile freeze/copy rejections
unchanged until the full native witness matrix above qualifies their removal.
This slice stages the state operation, not action-enabled native copy admission.

Host tests must show exact record inheritance, empty child pending state, unchanged
parent state, independent subsequent action/post/delivery mutation, and clean reuse
of a destination that previously held records and pending signals. Exercise actual
existing record install/query/post/peek/commit operations. Deliberately copying
pending state, dropping records or clearing parent pending state must fail named
host assertions in isolated source copies. No mutation option enters the build.
Run required host checks and existing complete connections/launch regressions to
preserve the closed profile gate and ordinary copy behavior. Handler-return and
signal-copy rollback target coverage remain pending, not inferred from host tests.

Aether owns the native state and publication point under O-03/O-04, I-01/I-06 and
E-04/E-06. The simpler whole-State assignment would duplicate pending occurrences;
one record-array assignment plus destination pending reset states the required
semantics without a snapshot framework or allocation. No new syscall, build flag,
quota, service, dependency or unsafe boundary. The helper requires disjoint kernel
objects under existing owner serialization. Runtime cost is a fixed 64-record copy
only in the still-rejected action-enabled copy path. Update this reference and STATE;
no new command/profile requires workflow registration. Use Zig formatting. Preserve
released pins, sibling sources, all failed attempts and previous evidence.

### Native signal-copy experiment selection — 2026-09-10

Before code: introduce an explicit default-off native-copy-signals experiment,
requiring process-copy, private actions, runner-local and single-context execution.
Only that profile may pass the existing action-enabled freeze/copy gate; ordinary
signal profiles retain -95. Existing factory, source/token, destination, endpoint,
backing and publication checks remain. No installed SDK support is enabled.

Extend the raw C copy fixture with exact DFL/IGN/custom action queries and a held
mask across copy. Queue/coalesce a masked signal before freeze. Child restoration
must deliver none, then a fresh self-post must invoke its inherited handler once;
parent restoration must deliver its preserved occurrence once. A child disposition
change must not affect the parent after the existing readiness handshake. Repeat
two generations. Also run the entire copy continuation inside a handler and return
through both inherited user-stack restorers; verify the pre-handler mask afterward.
Use the existing pre-copy failure injection for parent pending/action preservation,
cancellation and slot-generation reuse. Thread profiles remain unsupported.

Cases: copy-signals, copy-signals-handler, copy-signals-rollback. Successful clients
remain parent71/child72/dummy29, six reclaims; rollback remains parent71/dummy29/
replacement29. Disabled opt-in must return source246/owner1800. Three intentional
kernel controls drop child records (child247/owner1820), copy pending bits
(child248/owner1820), or clear parent pending (parent248/owner1821), all before
reclaim. Controls use existing release-artifact rejection classification. Native
handler corruption/nonlocal escape and guarded descriptor publication composition
remain later qualification; this bounded experiment does not open a consumer API.

The simpler unconditional gate removal would alter all action profiles. One explicit
experiment flag preserves their rejection while collecting missing native evidence.
The existing fixed records, stack frames and raw copy owner avoid a second service
or new wire format. No dependency, quota or authority widening. New C handler/restorer
calls reuse the checked signal ABI and private copied stack; no pointer escapes.
Only validated existing mask and action buffers cross synchronous traps. Apply
pinned clang-format21.1.8 to the touched C fixture, Zig formatting and existing
Python migration style. Update build-policy inventory, workflow oracle, reference
and STATE; run host, complete connections and launch suites on frozen sources.
Existing signal dispatch/delivery remains unchanged behind its old flags; command
and M4 evidence remains historical unless new failures justify broader runs.
Preserve all failed attempts, pins and sibling ownership under O/I/E and PX-01–03.

### Copied handler return selection — 2026-09-10

Before code: extend the existing raw handler-copy fixture, without kernel changes.
Seed R12 and the low 64 bits of XMM14 around the original self-post trap; deliberately
clear live XMM14 in the handler and verify both saved values after each copied
restorer returns. Preserve the caller's original R12 on the helper stack. This is
selected-register evidence, not a complete CPU/FP register matrix.

In the child only, corrupt the inherited payload's reserved byte at offset8, attempt
sigreturn on that actual private payload, require -22 and unchanged current mask,
repair it, then return normally. Parent return remains valid. A control that omits
the corruption returns early without recording rejection and must fail child250/
owner1820. Separate controls change saved R12 or XMM14 to zero and must fail the
same exact terminal pair before reclaim. A sigsetjmp/siglongjmp case escapes the
copied handler in both processes, restores the original mask and permits one further
self-delivery. Omitting saved-mask restoration must fail child249/owner1820.

Cases add handler-invalid, handler-invalid-skip, handler-register, handler-fp,
handler-escape and handler-escape-mask to the copy-signals prefix (104 suite cases).
Positives retain parent71/child72/dummy29 across two generations and six reclaims;
all new negatives require zero reclaims. Existing raw signal-copy and rollback
controls remain unchanged. No SDK or descriptor-publication adoption is inferred.

Reuse the existing checked frame ABI and musl restorer/nonlocal-return mechanism,
not a kernel active-handler token that could survive nonlocal escape. The naked
assembly helpers have no compiler-generated stack accesses: the invocation restores
callee-saved R12, and rejected-return probing preserves its live RSP in R11 using
the existing rejection contract. Payload is the current handler's private mapped
720-byte frame; its offset is obtained from a forced frame-pointer frame. No pointer
escapes or ownership/authority changes. New synchronous mask query buffers remain
live for each trap. No dependency, quota, kernel flag or new service. Use pinned
clang-format21.1.8 on the touched C fixture. Update reference/workflow/STATE; freeze
runtime sources and run host, complete connections and launch suites. Preserve all
failed attempts and pins. Prior command/M4 evidence remains historical because no
kernel, backend, shared adapter or command source changes are selected. Foundations
O/I/E, Distribution PX and the existing simplicity review continue to apply.

### Signal and descriptor composition selection — 2026-09-10

Before code: select the existing native-copy-signals experiment for bounded inherited
streams. Queue a parent signal while the preparation mask is held; queue a fresh
child signal after libc/endpoint rebinding. Retain masking through receipt validation,
FD10 flag updates and final completion. On release, handlers must observe recorded
completion, matching auxv endpoints and cached/kernel identity, current lifetime refs,
three live admitted roles and expected private FD10 flags. Duplicate FD10 locally
into FD11 and close that duplicate with no backend request, unchanged duplicate
counts and preserved errno. This checks usable private descriptor state without
changing the existing backend byte sequence or forwarding handler application I/O.

Use initial mask16 and require exactly one handler per returning process. Include
normal success and injected pre-copy rollback (parent completion/recovery only).
Early parent unmask before preparation must fail source79/owner1950; corrupt child
reference after completion or omit its fresh post must fail child79/owner1950. All
three controls require zero reclaims. Success and rollback retain existing terminal
orders and six reclaims. Add five cases (109 total) without changing kernel, owner,
backend, wire schema or shared adapter. Rejected preparation and malformed completion
with live handlers remain subsequent composition work, not implied by raw mask tests.

One callback and release gate reuse the existing private client state and mask API;
no transport-busy kernel mechanism, service or allocation is added. The callback
checks publication and bounded state before indexing or descriptor mutation, preserves
errno, and uses nested existing FD guards. User-stack record/mask buffers live through
synchronous checked traps; no pointer escapes. Aether owns this fixture; installed
SDK and companion acceptance remain separate under O/I/E and PX. Apply existing
simplicity guidance and pinned clang-format21.1.8; freeze sources and run host,
complete connections and launch suites. Update reference/workflow/STATE, retain all
attempts and release pins. Prior command/M4 execution remains historical.

Review refinement before final qualification: pass explicit completion validity into
the handler gate. Parent outcomes other than67/68 must keep the gate closed; child
entry remains behind its existing exact67 record check. Add a corrupted decoded
parent-outcome control requiring source79/owner1950 (110 cases total). An
unconditional gate would let the handler run local FD operations and then return252;
the exact79 witness must distinguish that incorrect ordering. This is a local
completion-validity control, not full malformed-wire recovery qualification.
Retain the first frozen run as superseded evidence and rerun final sources.

### Live-handler returning rejection selection — 2026-09-10

Before code: add a fixture observer path for signals delivered while returning from
known unpublished failures: local preparation78 or child receipt/completion251.
The wrapper records that abort state while still masked, restores the saved mask
and errno, then requires one observer call and zero descriptor operations. The
observer must not inspect or repair the incomplete descriptor table; it only checks
that publication never occurred. Successful/recovered parent handlers retain the
existing checked local dup/close path. This is an explicit fixture handler behavior,
not a kernel restriction on arbitrary user handlers or installed SDK acceptance.

Add preparation rejection, malformed child receipt and malformed child completion
with live handlers. Preparation retains three source78/backend17 generations and
six reclaims; malformed child messages retain child251, recovered parent73, backend17
and six reclaims. Omitted abort selection must reject source79/owner2010 or child79/
owner1960. Controls that actually query FD10 from the aborted callback must also
reject those pairs through the descriptor-operation counter. All five controls
require zero reclaims; eight cases bring the suite to118. Callback count, errno and
mask observations precede terminal publication. Partial messages with forced-stop
containment remain subsequent work; stopped processes do not return a callback.

Keep one publication/abort distinction in the private fixture rather than a kernel
transport policy or general recovery framework. Abort selection is bounded to the
known unpublished return outcomes; no guessed completion opens the success path.
Counters witness actual callback branches and FD operations. No kernel, owner,
backend, shared adapter, wire, dependency or quota changes. Existing checked native
mask/action buffers remain live through synchronous traps; no pointer escapes.
Apply O/I/E, PX and existing simplicity guidance; pinned clang-format21.1.8 applies.
Update reference/workflow/STATE, freeze runtime, run host plus full connections and
launch suites, retain all attempts and pins. Prior command/M4 execution remains
historical. Consumer and sibling ownership remains separate.

### Live-handler incomplete publication selection — 2026-09-10

Before code: compose the existing missing/partial receipt, readiness and final
completion fixtures with live copied handlers. Four readiness cases must stop the
child before holder recovery, then restore the parent's checked callback and retain
parent73/backend17 over two generations with six reclaims. Four final completion
cases must confirm both stops before draining and releasing the shared backend;
only backend17 returns, twice, with six reclaims. A complete peer may execute its
handler before containment. Silence alone does not prove a callback never ran.

Reuse existing deliberate zero-padding and omitted-stop controls: readiness1982,
child-stop1981, final-padding2001, parent-stop2002 and child-stop2003, all with zero
reclaims. Fourteen cases bring connections to132. These controls establish bounded
containment and surviving-parent recovery, not arbitrary-handler safety or installed
SDK acceptance. Stopped contexts cannot return through the client cleanup wrapper.

Only add fixture aliases and harness combinations/oracle routing. No kernel, owner,
backend, shared adapter, wire, allocation, pointer-lifetime or quota changes. Existing
capability ownership and checked synchronous trap buffers remain authoritative.
This reuses one recovery implementation rather than adding a signal-specific one;
SE-01–SE-05 and O/I/E/PX apply with Aether as fixture owner. Keep the existing C
format using pinned clang-format21.1.8, without unrelated migration. Update native
reference/workflow/STATE, freeze runtime, run host plus full connections and launch
suites, retain attempts and verify snapshots. Command/M4 evidence stays historical;
released pins and siblings remain untouched. SDK integration is subsequent work.

### SDK process integration selection — 2026-09-10

Requirement: move the qualified eager-copy/descriptor/signal building blocks into
an actual libc call path before attempting dash external commands. This review is
an Aether proposal for the producer seam, not an installed SDK change, affected-owner
approval or a new syscall allocation. Userland owns musl integration and dash build
configuration; Aether owns native mechanisms and this bounded producer experiment.
The existing SDK and released pins remain immutable inputs.

Inspection of the captured native musl 1.2.6 sources finds that `fork()` calls
`_Fork()` inside application-signal masking and atfork coordination. `_Fork()`
blocks all signals, locks the abort state, performs SYS_fork, calls `__post_Fork()`
and then restores its saved mask. The child repair sets cached TID/clear-TID,
resets robust-list fields and thread-list bookkeeping. These steps must remain in
the libc owner implementation. Our current `copy_rebind()` is a private layout
witness that also sets TID; transplanting it unchanged would duplicate that repair.
The native syscall header changes transport to int0x81 but does not compose the
process/descriptor protocol. The kernel currently has no public fork/exec/wait
branches; its private copy returns fresh grants in RDI/RSI/RDX as well as RAX.
An ordinary scalar syscall wrapper does not expose those output grants.

The narrow next experiment is a source-built, isolated `_Fork` integration using
an explicit staging hook at its existing SYS_fork call site, while its all-signal
mask and abort lock are held. Keep upstream `fork()` and `__post_Fork()` behavior.
The hook owns only native copy preparation, fresh grant capture, auxv/transport
rebinding and descriptor publication. It must not unlock musl state, run application
callbacks or restore the application mask. The caller performs normal libc repair
before returning to application code. Aether can build that candidate privately
from pinned sources for producer evidence; installing or accepting it belongs to
userland. Do not silently patch the existing SDK tree.

| Boundary | Required result / forbidden outcome |
| --- | --- |
| Before freeze | Validate a stable local descriptor plan while masked; reject unsupported threaded state and unavailable authority without admission or mutation. No allocation, stdio, arbitrary callbacks or lock-taking libc helpers inside the staging hook. |
| Child continuation | Capture all returned grants in explicit assembly outputs before C calls can clobber them. Validate and rebind auxv/transport and per-connection references before readiness. Do not preempt libc's cached-TID/robust-list/thread repair. |
| Publication | Parent returns the actual child PID and child returns zero only after checked completion. Keep descriptor flags identical at fork, including FD10 CLOEXEC; clearing that flag is a later application operation, unlike the current demonstration sequence. |
| Known failure | Return a raw negative errno to `_Fork` only after confirmed rollback or confirmed child stop and holder cleanup. Preserve the parent's descriptors, memory and pending signals. Let upstream code convert errno and restore masks/locks. |
| Unknown completion | Do not invent a successful fork or return a retryable failure while an unaccounted child may run. Retain the existing bounded pair-containment requirement; broader recovery remains separate. |
| Authority | PID and numeric file references are bookkeeping, never authority. The owner retains lifecycle/image grants and binds process relationships to the requesting connection and generation. |

The current fixture's child mutates FD10 before readiness and its completion wrapper
includes workload-specific reads/exits. Those are evidence clients, not a reusable
public fork implementation. Separate the staging operation from those application
steps only when implementing this next experiment; retain older controls and sealed
fixtures. A thin symbol replacement returning a canned result or calling the
unmodified private client is insufficient. No public `_Fork` claim is made until
both actual libc return paths and error unwinding execute successfully.

Acceptance for that next experiment: actual linked `fork()` returns two branches;
parent PID equals child's getpid, getppid is the source PID, and cached/kernel TID
agree after libc repair. Verify copied private memory/TLS, shared file offsets,
unchanged inherited CLOEXEC, one locally independent FD mutation, parent pending
signal retention, empty child pending state and handler delivery only after libc
repair. Exercise preparation denial, exhausted copy admission and known rollback;
require exact errno, no leaked child/resources and preserved parent state. Include
controls for bypassed rebind, early mask restoration and false success. Repeat over
fresh generations. Check symbols/disassembly to exclude a fake public fork shim.
Select full host, connections and launch suites; broaden only if shared runtime or
other profiles change. Preserve all attempts and qualify final source/tool bytes.

Follow with a separate wait integration: the inspected musl `waitpid` uses the
cancellation-aware wait4 path, while wait4 itself can request rusage. Define a
connection-owned child record and retained exactly-once collection, PID versus -1,
WNOHANG, encoded exit/signal status, interruption, invalid-output atomicity and
repeat/stale rejection before implementation. A consuming native lifecycle query
must not lose a result before the caller's status output can be delivered. Initially
unsupported options/rusage must reject explicitly; do not report fabricated zeros
as measurements. PID alone cannot select another connection's child.

Transactional exec is still a distinct missing kernel mechanism: validate the
scoped executable and bounded argv/env before replacing the image; preserve old
state on rejection, PID/parent relationship on success, and commit CLOEXEC closure
and signal disposition reset at the same observable boundary. The existing runner
launches a different process and cannot substitute for exec. Its exact commit and
failure protocol needs a dedicated implementation selection after public fork/wait.

Native x86_64 `vfork` is a separate assembly trap and bypasses the `_Fork` call site.
Do not enable it by aliasing syscall numbers or infer that a fork hook fixes dash's
vfork path. Userland must review a source-built dash configuration that selects fork,
or separately qualify its vfork implementation, before external-command acceptance.
Pipelines, SIGCHLD/job bookkeeping, general wait interruption and persistent storage
remain later composed workloads. OpenZFS is not required for this process experiment.

Simplicity review (SE-01–SE-05): use the maintained libc fork orchestration and one
explicit native staging hook rather than a second fork implementation. A scalar
syscall redirect is simpler but insufficient for fresh grants, descriptor readiness
and libc repair ordering. No service, global PID table, general allocator or new
compatibility framework is selected. The hook can eventually replace fixture-only
rebinding duplication after consumer acceptance; no historical path is deleted now.
Bounded stack buffers remain synchronous, no user pointer escapes, and the existing
single-context/resource limits remain mandatory. Foundations O-01–04, I-01/03–06
and E rules plus the proposed Distribution POSIX profile apply. Missing owner review,
installed SDK adoption and runtime qualification are open coverage, not exceptions
or approvals. This review changes documentation only; run host/pin/workflow checks
and retain exact reviewed sources and object inspections, without relabeling old
QEMU results as fresh execution.

### Public fork first execution selection — 2026-09-10

Implement the preceding selection as a bounded first public-call witness: unchanged
source-built musl fork plus privately patched _Fork staging call, with libc-owned
child repair. Use the existing owner and backend, preserving inherited CLOEXEC
until application code changes it. Qualify two return paths, PID/TID, mask16,
private TLS/data and shared offsets; known cancellation returns EAGAIN after owner
recovery, local preparation refusal returns ENOTSUP before publication. Both errors
must pass actual musl errno/mask unwinding. Controls omit libc child repair or clear
CLOEXEC prematurely and require child80/owner1950 with zero reclaims. Add five cases.
Live-handler/atfork-callback composition and exhaustive admission failures remain
next coverage, not implied by this first public-call run.

Use a narrow compile-time rebind variant that leaves set_tid_address and cached TID
to musl; ordinary rebind behavior remains unchanged. Extract fork/_Fork from the
already verified musl archive into private output; retain COPYRIGHT and exact patch.
No sibling or installed SDK mutation, new dependency, kernel syscall or public ABI.
The new client owns synchronous bounded buffers; unknown staging failure terminates
rather than reporting safe retry. Existing owner remains responsible for cleanup.
Apply the prior simplicity review: reuse libc orchestration and owner recovery,
not a new process service. Run full host/connections/launch, source/symbol inspection
and pinned C formatting; freeze sources and preserve every attempt.

### Public fork callbacks selection — 2026-09-10

Before code: compose the real pthread_atfork registration/dispatch and native signal
handler with the isolated public fork candidate. Register two callback sets; require
reverse prepare order and forward parent/child order. Prepare callbacks observe the
original mask16; staging queues a coalesced parent signal under musl's full mask.
The child begins with no pending occurrence and receives a fresh post while masked.
Require delivery after publication and libc TID repair, before musl's post callbacks
on this pinned implementation. Check rebound references/endpoints, unchanged CLOEXEC,
private callback state and errno. These ordering observations describe this musl
candidate, not a portable promise that all libc implementations deliver at this point.

Success, known rollback and local refusal retain existing terminal/reclaim sequences.
Reversed registration, omitted child post and omitted libc repair must reject with
client81/owner1950 and zero reclaims. Add six cases (143 connections). Use actual
SDK pthread_atfork allocation/dispatch, not replacement callbacks. Registration
allocates before fork through the existing bounded native allocator; the staging
hook and callbacks allocate nothing. Capture linked symbol provenance. Preserve
three prior build failures as historical evidence; freeze new sources for host,
full connections and launch qualification, pin/workflow/format and archive checks.

A private callback trace and completion gate reuse existing action/mask APIs and
libc bookkeeping. No kernel, owner, wire, quota or SDK installation change; no new
service or recovery implementation. Existing O/I/E/PX and SE-01–05 selection applies.
Arbitrary callback behavior, recursive fork, atfork lock contention, threaded fork,
full admission failures, wait/exec/vfork and independent consumer acceptance remain
outside this bounded witness. No removal of older evidence or released pin changes.

### Public wait first execution selection — 2026-09-10

Before code: add a bounded waitpid candidate after public fork, with result ownership
bound to the parent's existing connection. No PID authorizes another connection's
child. Keep status observation, delivery, acknowledgment and resource reclaim distinct.
Do not reuse the older consume-before-reply collector. Initially qualify normal exit
only, one child, PID or -1, options0/WNOHANG, nullable status and no rusage. Unsupported
options reject EINVAL and unmatched/collected PID rejects ECHILD. This is an isolated
waitpid candidate, not installed SDK wait4, SIGCHLD, job control or cancellation support.

Use private 32-byte little-endian requests: op80 peek or81 acknowledge, signed PID
at4, options at8, bytes12–31 zero. Replies contain signed result at0 (PID/0/-errno),
echoed PID token at4 only for a retained result, then zero padding. A positive peek
is followed by a separate four-byte encoded normal-exit status. The adapter reads
those four bytes directly to the user's status pointer through the existing checked
native channel read, which validates output before dequeueing. On EFAULT it drains
that body to a local word, returns EFAULT and sends no acknowledgment. NULL status
drains locally and may acknowledge normally. No added kernel pointer-probe API.

Op81 acknowledges the retained child PID only after complete status delivery. The
owner marks the result collected and replies0; repeated acknowledgment for the same
collected result is idempotent, while subsequent peek returns ECHILD. This does not
make lost acknowledgment replies transparent: incomplete/invalid transport poisons
the private adapter and returns EIO without replay. The adapter masks signals across
the bounded exchange; threaded callers remain outside this profile. Signals restored
afterward cannot invalidate a mapping during the checked copy. Exact EINTR, libc
cancellation, SIGCHLD and partial/lost-reply recovery need later qualification.

The owner first answers a WNOHANG probe while the child is still blocked on stream
I/O. It then finishes child I/O/closure and observes actual exit72 before handling
retained collection. The client checks status untouched on pending/error, wrong PID,
unsupported options, an actual unmapped-output EFAULT followed by successful wait,
encoded exit72 and repeat ECHILD after all its stream FDs are closed. Run two
generations and six reclaims. Wrong-status and premature-consumption controls require
client82/owner1950 and zero reclaims. A separate NULL-output success case covers status discard. Four cases bring connections to147.

Build waitpid from the pinned musl source in private output and replace only its
wait4 call with the local candidate adapter plus musl errno conversion. Explicitly
label the cancellation gap; no successful cancellation stub. Reuse the existing
owner and four-byte native output validation, avoiding a new process service, global
PID table or kernel syscall. One retained/collected boolean per experiment suffices;
no token namespace or general transaction framework is needed. Keep bounded buffers,
resource/authority checks, source pins and existing modes. Apply O/I/E/PX and SE-01–05;
run full host/connections/launch, pinned C/Rust formatting and link/source inspection,
freeze runtime sources and retain every attempt. Owner code must remain <=8192 bytes.

### Public wait abnormal-exit selection — 2026-09-10

Before code: qualify normal exit134, actual CPU #UD and actual default SIGTERM death
through the retained waitpid path after child stream closure. Preserve native cause
records unchanged: (kind1,detail134), (kind2,detail134), (kind4,detail15). Map these
separately to wait words134<<8, SIGILL4 and SIGTERM15. A shell's conventional
128+signal display is not a wait word. No core bit or core file is claimed. Only
this observed #UD vector and SIGTERM are qualified; unsupported causes reject2022
rather than guessing a signal from a numeric detail.

All three positives repeat pending/error/EFAULT/retained/repeat tests over two
generations with parent71/backend17 and six reclaims. Two controls encode fault or
signal death as a normal exit; both require parent82/owner1950 and zero reclaims.
Five cases bring connections to152. Enable existing signal/copy/termination flags
only for SIGTERM cases; kernel code and all existing profiles remain unchanged.

The owner maps the retained (kind,detail) pair, never rewrites kernel evidence.
A small explicit match is sufficient; no signal framework, new ABI, allocation,
service or global process state is needed. Existing synchronous output validation,
acknowledgment and ownership limits remain. No early-death resource cleanup or
reply-loss acceptance is inferred from death after descriptor closure. Apply the
existing O/I/E/PX and SE-01–05 selection; freeze sources and run full host, connections,
launch, formatting and pin/workflow checks. Preserve prior and new failed attempts.
Signal interruption, wait4/wait3, other faults/signals and independent SDK/dash intake
remain open. Do not modify siblings, installed SDK or release pins.

### Public wait transport-failure selection — 2026-09-10

Before code: exercise missing and partial positive headers, a short status body,
and missing/malformed acknowledgment replies through the existing waitpid adapter.
Close the owner's reply endpoint to make truncation deterministic, without a timer
or retry protocol. Inject only after the existing EFAULT/retry preparation. Missing
or partial headers leave status untouched; a two-byte status read may modify those
two output bytes before EIO. A complete status followed by lost/bad ACK returns EIO
although the owner has consumed the result. No successful wait or transparent replay
is allowed. A second call must return EIO locally with mask16 restored and no wire
traffic. A lost ACK cannot promise exactly-once delivery to the application.

The connection owner must retain an unacknowledged result and record a consumed ACK
before losing its reply. Confirm actual parent71 and child72, no extra request bytes,
then close remaining endpoints and reclaim exactly once over two generations. Add
five positive cases and two deliberate client mutants: replay after poison and false
success on a malformed ACK. Require exact owner2024 (extra request) or parent82/
owner2023 (false success), zero reclaims. Full connections becomes159 plus five launch
cases and host checks. Preserve failed attempts and freeze runtime during qualification.

No new authority, service, ABI, allocation, dependency or kernel change. Existing
checked native reads own pointer validation; partial output on EIO is explicitly
allowed, not rolled back through an unsafe user-pointer store. Reuse existing owner,
transport and poison state rather than adding a recovery framework. No obsolete path
can yet be removed because installed SDK/dash adoption remains separate. Apply the
existing O/I/E/PX and SE-01–SE-05 selection, owner8192-byte ceiling, scoped formatting,
pins/workflow and compatibility/archive checks. Documentation records this bounded
failure behavior; wait4/wait3, interruption/cancellation, exec and independent intake
remain next work. Siblings and released pins remain unchanged.

### Public wait4/wait3 selection — 2026-09-10

Before code: the retained pinned dash jobs.c calls wait3(status, flags, NULL).
Source-build musl1.2.6 src/linux/wait3.c unchanged and wait4.c with a narrow native
call replacement, retaining musl's public errno conversion. Reject any non-NULL
rusage at entry with ENOTSUP before computing output destinations or sending a
request. Do not fabricate accounting values. Null-rusage calls use the existing
connection-owned retained wait adapter; PID alone still grants no authority.

Qualify public wait4 and wait3 over actual forked children with pending WNOHANG,
PID/options rejection, unmapped-status EFAULT/drain/no-ACK, successful retained
collection and repeat ECHILD. Wait3 selects -1; use wait4 for specific-PID checks.
Check valid sentinel and invalid-address rusage rejection through both APIs without
status/usage mutation or request traffic, then complete normal waits. Add actual
#UD through wait3 and malformed-ACK/EIO/poison through wait3. An omitted rusage gate
must fail parent82/owner1950 rather than falsely succeeding on unsupported accounting.
Five new cases bring connections to164, plus host and five launch regressions.

Keep old waitpid objects/profiles unchanged while independently qualifying the
upstream wait3-to-wait4 link path. There is no new service, kernel ABI, wire message,
allocation, quota, unsafe pointer store or resource accounting mechanism. A narrow
upstream call replacement is simpler than another wait implementation and sufficient
for dash's current NULL-rusage call. Reuse existing retention/poison/mask rules;
no obsolete consumed path can yet be removed before SDK intake. Existing O/I/E/PX
and SE-01–SE-05 apply. Record link maps, disassembly and exact pinned upstream bytes,
verify all old payloads/kernel images, freeze sources and preserve every attempt.
Update the existing reference/workflow and STATE after qualification. Installed SDK,
siblings, released pins and prior evidence remain unchanged. Cancellation/EINTR,
SIGCHLD/sigsuspend/job-control and full dash execution remain separate gaps; this
bounded API witness does not claim end-to-end shell acceptance. Transactional exec
is the next mechanism after these entry points pass.

### Transactional exec preparation — 2026-09-10

Before code: the current launchOperation clears State and increments generation;
copyOperation allocates another worker and transfers endpoints. Neither implements
exec. load mutates fixed backing/page tables and sets admitted; it is not a rollback
operation. Keep process identity, image identity and lifecycle reuse distinct.

The next native experiment must replace a frozen single-context worker through its
existing supervisor authority and an explicit immutable image grant. A path or PID
is not image or process authority. Resolve paths in userland; do not add a global
kernel executable namespace. Check live lifecycle handle, exact freeze sequence,
image grant, profile compatibility and complete copied argument record before any
mutation. Reuse ELF parsing/page limits, launch.layout and bounded Arguments. No
borrowed user pointer may survive admission. The current limits are four argv,
four env strings of32 bytes each; this is not arbitrary execve admission.

Commit must preserve slot/generation/PID, parent PID and lifecycle handle, but
replace old user mappings, anonymous memory, TLS, stack, register/FP image and
clear-TID/wait registrations. Preserve the execution signal mask and queued signal
occurrences; caught dispositions become default and ignored dispositions remain
ignored. Canonicalize disposition records so no handler/restorer pointer from the
old image remains. Pending default-ignored signals may subsequently be discarded by
the ordinary delivery path; copying a process's empty pending set is wrong for exec.
Fresh contexts start with standard x87/MXCSR values. All failed admission paths must
leave the old context, dispositions, mappings, descriptor table and return path intact.

This slice implements only pure candidate-state preparation in the existing
Execution and pending State types. A candidate owns its bytes, performs no pointer
access or allocation, and does not mutate its source. Host tests require fresh
register/TLS/wait/FP state, preserved mask/pending/ignored dispositions, reset caught
handlers, source independence and repeatability. No native syscall, dispatch flag,
new service or successful exec behavior is introduced yet. Entry and stack address
validation belongs to the later admitted-image caller, not these state constructors.
The caller must stop the old execution before publishing a candidate; handler-return
frames and clear-TID cleanup must be settled before old mappings are destroyed.

Remaining native commit design must be resolved before wiring these helpers:

- Reusing fixed backing after admission avoids another full State arena, but the
  loader must have no recoverable failure after destruction starts. Prove page/table
  limits, stack bounds and immutable image bytes first. An unexpected invariant
  failure is a kernel fault, never a recoverable exec error after old-state loss.
- aliases currently rewrites kernel mappings in every native State and reloads CR3.
  Perform replacement from the supervisor's address space with the worker parked,
  under the existing IF=0 ownership boundary. Restore immutable aliases before any
  dispatch; never clear the currently active root or expose writable old RX pages.
- The connection owner must prepare surviving descriptors/CLOEXEC removal without
  issuing irreversible backend closes before kernel admission. Kernel does not own
  Unix FD flags. Hold the replacement until descriptor publication and cleanup are
  resolved; lost commit replies require an explicit observable image/commit identity,
  not cancellation that might resume a replaced image as the old program. Specify
  this bounded protocol and its stop/reclaim policy before allocating a trap number.
- Resetting the entire native State would wrongly drop capabilities, pending state,
  parent identity and lifecycle records. Do not relaunch into a new PID, reuse the
  runner as exec, or give the replacement ambient image/factory authority. Review
  which existing endpoint/memory grants survive the image transition explicitly.

Native acceptance must include successful nonreturning replacement with stable PID
and parent, exact argv/env, fresh TLS/registers, stale mapping denial and zeroed reuse;
invalid image/arguments/grants/freeze token with old program continuing unchanged;
CLOEXEC closure only on success and surviving shared offsets; preserved mask/pending,
reset caught/retained ignored signals; repeated replacement, capacity denial, stale
commit and lost acknowledgment containment. Include deliberate mutation controls
for early destruction, changed identity, leaked old state and premature FD close.
Select full affected native memory/process/signal/command suites and regression.py
when native dispatch/mapping changes, recording every attempt. Independent SDK/dash
and sys-init acceptance is separate; no sibling is modified by this preparation.

SE-01–SE-05: reusing whole-State launch is simpler but destroys required identity;
a second full address-space arena is more expensive and not yet justified by fixed
prevalidated images. Choose small value constructors now and retain the existing
owners. No compatibility path is removed before consumers adopt a replacement.
Apply O-01–05, I-01/03–06, E-01–08 and proposed PX-01–03. Current tests are host-only
state-transition evidence, not native exec, fault atomicity or release readiness.
Update STATE/reference/workflow, run zig build test, formatting and pin checks, and
retain exact inputs/results. Native wiring remains the next implementation step.

### Native exec image gate selection — 2026-09-10

Before code: add opt-in native-process-exec, requiring bounded native memory and
freeze, rejecting threads/large-image arenas. Scope is a connections fixture with
no Unix FD table; existing connection grants survive, but this is not execve or
CLOEXEC acceptance. Reuse boot-validated immutable image grants and fixed backing.
No new global executable namespace, backing arena or POSIX policy enters the kernel.

Private supervisor operations use rdi=factory0xa001 and rsi=live lifecycle handle:
0x23007 commit takes rdx=image grant, r10=exact freeze sequence, r8=272-byte Arguments,
r9=0. Validate all authority, state and copied arguments before relaxing aliases or
changing mappings. On success return0, retain commit sequence/image, keep worker
frozen. 0x23008 query takes all other inputs0; returns rax=last committed sequence
(or0), rdx=image grant (or0), r8=publication pending (0/1). 0x23009 publish takes
rdx=matching committed sequence and remaining inputs0; unpark only that image.
Repeated matching publish is idempotent until another freeze; stale sequence rejects.
Cancellation of a committed unpublished image rejects EBUSY. Stop/reclaim remains
available; query survives publication and terminal observation until reclaim.

Commit preserves process slot/generation, PID/parent, endpoint grants and lifecycle
identity. It resets image mappings/backing, execution/TLS and image readiness, using
the tested state constructors to preserve mask/pending and canonicalize dispositions.
Caller runs on supervisor CR3 under IF=0; old immutable backing aliases become writable
only during replacement, then all immutable aliases are restored before dispatch.
The fixed boot ELF/page/table checks eliminate recoverable loader failures after
mutation starts. Invalid invariant after that point is a kernel failure, never a
successful rollback. No user pointer remains after argument copy.

The source first freezes, survives malformed/denied admission and ordinary cancellation
with its TLS/stack cookies intact, then freezes again for replacement. Replace with
a distinct ELF that verifies argv/env, expected PID and fresh TLS. Hold it across yields
before publication, query retained identity, deny cancellation/duplicate commit/stale
publication, then publish and observe its distinct terminal result. Repeat over two
slot generations and six total reclaims, including two unrelated peer launches.
Early-publication and stale-token mutations must fail precise owner checks before
reclamation. Real FD publication, inherited offsets/CLOEXEC, live signal delivery,
stale anonymous mappings and lost transport composition remain follow-on witnesses.

Select host, complete connections/launch, command regressions and regression.py because
native dispatch/mappings change. Preserve all attempts and frozen sources; compare
older profiles, record binary/source identity and resource bounds. Update existing
native reference, build-option classification, workflow and STATE. Simplicity: fixed
in-place reconstruction under owner exclusion avoids another arena; the retained
record and publication gate are necessary to distinguish committed-but-unpublished
from old frozen state. No released pin, sibling or installed SDK changes.


Exec gate review correction before final qualification: process-copy is another
source-unparking path. Deny copying a committed unpublished image with EBUSY before
any destination/endpoint mutation. The native fixture must attempt copy with fresh
valid endpoints and a free slot, verify rejection/retained gate, then close those
still-owned endpoints. A deliberate guard bypass must return a copied child and
fail owner2035 before reclaim. Allocation/cleanup failures use2036, so they cannot
satisfy this control. Four exec cases bring connections to168. The initial167-case
run is superseded; its command suite was interrupted before any runtime edits.

### Exec descriptor preparation selection — 2026-09-10

Before code: introduce a pure bounded Rust preparation routine for the existing
64-byte descriptor snapshot (16 records: binding, flags, present, reserved) and
three local binding-use counts. Reject noncanonical absent records, invalid
presence/reserved/flags/binding and mismatched counts before producing a candidate.
Remove only FD_CLOEXEC entries; retain surviving numbers, binding identity and
flags. Return surviving counts and one release obligation per formerly used binding
whose local count becomes zero. This obligation is a local holder release, not a
backend close: another process may still own the shared open description/offset.
Preparation performs no I/O, allocation, capability operation or mutation of input.

This is host-qualified preparation for the Rust connection owner, not a native
exec integration or a wire/API adoption. The caller must authenticate the session,
validate live binding references/rights, exclude mutation while frozen, and retain
the exact snapshot/commit identity. Rejecting image admission discards the plan.
After known commit, reconcile holder releases and checked backend final-close
outcomes before installing the surviving table and publishing the new image.
Unknown outcomes require containment; never resume the old program after commit.

Simplicity: a value-only transform avoids introducing a second mutable descriptor
owner or generic transaction framework. Directly closing descriptors during
preparation is simpler code but violates rejected-exec preservation. No old path
is removed yet; integration must consume this same routine rather than duplicate
its rules. Fixed arrays bound stack/storage; no unsafe/FFI or new dependency.
O-02–05, I-01/03–06, SE-01–05 and local TE input/evidence rules apply. Kernel ABI,
installed SDK, sibling files, release pins and native payloads remain unchanged.

Select Rust host tests against independent expected tables, all16 descriptor
positions, shared aliases, final-holder obligations, empty/full tables and malformed
records/counts. Deliberately retaining CLOEXEC or releasing a still-used binding
must fail those tests. Run the existing host/inventory/pin checks. Native integration
and target execution remain subsequent work; do not relabel the earlier611 target
cases as fresh qualification of this preparation routine. Update STATE/workflow.

### Native exec descriptor composition selection — 2026-09-10

Before code: compose the reviewed pure preparation routine with the existing Rust
stream owner, real C startup descriptor table, immutable exec gate and Rust file
backend. Keep one client in slot0 and backend in slot1; two generations reclaim
six domains, including a separate backend peer in slot2 after each cycle. The old client reads a, duplicates FD0 to CLOEXEC FD10, marks FD1
CLOEXEC, captures the64-byte table and freezes. Rejected image admission resumes
the old client, which verifies both flags and reads b through FD10 before freezing
again. The owner validates the exact captured fixture table/counts and prepares
without side effects. Successful commit precedes binding1's final close; bindings0
and2 survive. Queue checked bootstrap/surviving table, then explicitly publish.
The distinct replacement verifies closed FD1/10, retained FD0/2 and reads c at the
same owner-maintained offset before closing survivors. Confirm backend17, client62
and peer17, with six reclaims. No change to native ABI or existing fixture modes.

Ownership remains single-context and capability-scoped. The fixed test has no other
process holder of these descriptions: cross-process shared-holder exec remains open.
Removing FD10 must not close binding0 because FD0 survives. The backend close must
return its exact success record before publication; unknown outcomes fail closed in
this bounded experiment, not recover/replay or resume the destroyed old program.
Malformed/partial bootstrap recovery, live signals and unknown native commit replies
are subsequent tests. No claim of complete execve or independent companion adoption.

Use the existing startup facade/transport and backend; the C replacement installs
only the owner-supplied canonical survivor table after validating it. No new namespace,
service, dependency, allocation or global table. Bounded stack records and checked
channel copies retain current pointer/ownership rules. Simplicity: reuse owner I/O
and lifecycle helpers and the exact pure transform, rather than add another broker.
Native rejection controls retain CLOEXEC entries (client216/owner2040) or reset the
shared offset (owner1903). Select complete connections and launch suites plus host,
format and pin/inventory checks. Kernel/command runtime bytes are unchanged; prior
command/M4 evidence remains historical. Preserve every failed attempt and freeze
sources during qualification; update workflow, native reference and STATE afterward.

Pre-run transport correction: the existing channel has32 bytes, so bootstrap/table
streaming cannot finish while the receiver is parked. Complete backend cleanup,
release into the trusted startup receiver, then stream bootstrap and table. The
replacement validates the complete table before application I/O; kernel publication
and descriptor/application readiness are distinct. Incomplete-table recovery remains
open. No larger queue or new mapping is introduced for this fixture.

### Exec close-reply containment selection — 2026-09-10

Before code: extend the existing native exec descriptor owner for missing and17-byte
final-CLOEXEC-close replies, using the already-built incomplete close backends. The
backend has performed the close, but the owner has no complete success receipt.
Keep the new image parked and query the matching pending commit; never replay the
close, continue descriptor publication or cancel back into the old image. Stop the
source, backend and fixture peer through their exact lifecycle handles, observe
kind3/detail144 for each, then close owner endpoints/reclaim. Only confirmed stop
permits discarding queued partial replies and peer hello bytes. Repeat two generations
with six confirmed stop/reclaims. No service can retain external storage authority
in this fixed in-memory backend witness; general persistent recovery is not claimed.

Read the existing bounded32-byte reply helper without zero-tail padding. Distinguish
missing (0 bytes) and partial (17 bytes) observations before containment. A deliberate
pad-to-success control must fail owner2050, and omitted source stop must fail2051
before any reclaim. These exact failures cannot be substituted by generic panics.
No kernel/SDK ABI, new service, mutable global table or dependency is needed. Reuse
bounded observation plus lifecycle stop; a generic retry/transaction framework would
add cost and risk replaying an ambiguous effect. No old path is removed yet.

Apply O-03–05, I-03–06, SE-01–05 and existing TE frozen-input/attempt rules. The owner
runs in the existing one-context capability fixture; buffers are fixed stack arrays,
channel calls copy synchronously, stop is distinct from timeout/acknowledgment and
reclamation. Native methods and existing output markers remain unchanged. Select
complete connections/launch, host, scoped Rust format and pin/workflow checks.
Update reference/STATE and retain every attempt. Kernel/command/M4 behavior is
unchanged; earlier evidence is historical. Bootstrap truncation after publication,
unknown commit replies and cross-process shared-holder recovery remain next work.

### Exec bootstrap-stall containment selection — 2026-09-10

Before code: after confirmed image commit and final CLOEXEC-close success, publish
into the trusted startup receiver, then deliberately stall delivery at0/16 bytes
of the128-byte bootstrap or0/16 bytes of the64-byte survivor table. Keep the writer
open; these are stalled streams, not EOF. The owner must observe no application
request across the existing256-poll bounded receiver, verify the live process and
matching published commit identity, then use confirmed stop of source/backend/peer
before any endpoint closure or reclaim. Repeat two generations and six reclaims.
There is no resend, old-image resumption or backend application I/O after the stall.

Add a C replacement-only mutation that reads16 table bytes into its zeroed64-byte
buffer. Those16 bytes contain every nonzero survivor entry, so an incorrect
zero-padding shortcut reaches real read(0) application traffic. The owner must
reject that request at2060 before reclaim. Omitting source stop must still reject
at2051. Positive checks distinguish incomplete receipt from application readiness;
no generic panic/timeout or spontaneous terminal substitutes for observed stop.

Reuse the exact startup facade, bounded owner receiver and existing contain helper;
no new protocol operation, kernel option, service, allocator, dependency or authority.
The private one-context fixture and fixed stack buffers preserve existing unsafe
channel-copy obligations. This narrow test does not solve transport replay or add
an unbounded wait. O-03–05, I-03–06 and SE-01–05 apply: bounded observation plus
confirmed stop is simpler than adding a general acknowledgment/retry layer now.
No obsolete path is removed; existing full-delivery cases remain regressions.

Select complete181-case connections and five launch suites, host tests, scoped
Rust/C format and pinned workflow/standards checks. Preserve attempts and freeze
inputs during qualification. Update STATE/reference/roadmap. Existing kernel,
SDK, sibling and release bytes remain unchanged. EOF/malformed-bootstrap recovery,
unknown commit receipts and cross-process shared-holder exec remain separate work;
this evidence qualifies stalls at the four selected boundaries only.

### Exec bootstrap rejection selection — 2026-09-10

Before code: test EOF at0/16 bytes of bootstrap or survivor table, a malformed32-byte
bootstrap header and a full64-byte table with reserved byte3 set. Observe no application
request and exact source215 (EOF/header) or216 (table), then stop backend/peer and
confirm kind3/detail144 before any reclaim. The source terminated itself; do not
mislabel it as forced stop. Close each endpoint once, accounting for the writer
already closed in EOF cases. Published commit identity survives until reclaim.
Repeat two generations/six reclaims. A C table-validation bypass must reach read(0)
and fail owner2070; skipping backend stop must fail2072 before reclaim.

Reuse bounded buffers, existing transport/parser and lifecycle calls. Use a scoped
cleanup helper for an already-terminated source rather than weakening live-stall
containment. No new kernel ABI, service, dependency, allocation or global owner.
Apply O-03–05, I-03–06 and SE-01–05: exact observed outcomes and existing primitives
are simpler than a generic recovery framework. No old path is removed; prior
full-delivery and stall cases remain regressions. Fixed RAM backend cleanup does
not establish persistent/shared-holder recovery or public execve acceptance.

Select complete189-case connections, five launch cases, host, scoped Rust/C format,
pins/workflow and exact mutation controls. Freeze sources and preserve attempts.
Update STATE/reference/roadmap after qualification. Record disk failures and the
maintainer-authorized deletion of a hash-verified duplicate unpacked directory;
keep its sealed archive/reports/hashes. Siblings and released pins remain untouched.

Qualification found an older rejection-observation race: copy-inherit-completion-skip
missed queued application traffic in generation1 and rejected only after three
reclaims in generation2. The unchanged payload/kernel had previously passed. The
owner read an empty queue before checking terminal state, then returned on terminal
without inspecting bytes that could arrive between those calls. Before the retry,
add a final read requiring EOF after confirmed termination; no producer can append
then. Keep the exact zero-reclaim negative oracle. This scoped fix affects existing
inheritance rejection consumers and requires the full connections suite, with changed
older owner payloads identified explicitly rather than assuming binary identity.

### Exec shared-holder selection — 2026-09-10

Before code: give two independently admitted clients connection-scoped references
into the same three open-file records. Reuse the existing descriptor plan for the
execing process. Its CLOEXEC removal drops only its local holder; the other client
retains the backend record. After replacement reads the next input byte and closes
its surviving descriptors, the peer must read at the shared offset and successfully
write stdout. Only the peer's final close may release those backend records. Verify
exact successful backend receipts, three total closes and two generations/six
reclaims. Premature backend close and private/reset peer position controls must
reject before reclaim for their specific failed I/O/data observations.

Use the existing bounded holder matrix, per-connection reference validation and
three-worker envelope. No global file table, new kernel operation, allocator,
service, dependency or SDK interface is needed. The current simpler alternative,
independent peer backend state, cannot witness shared lifetime or position. Extend
the existing exec fixture instead of adding a second owner implementation; retain
old cases as regressions. Apply O-03–05, I-03–06 and SE-01–05. Fixed stack buffers and
existing channel-copy/stop ownership remain; public fork/execve and production
owner placement still require separate consumer acceptance.

Select the complete connections suite with new positive and mutation cases, five
launch cases, host tests, scoped format and pinned standards/workflow checks.
Freeze final inputs and retain all attempts. Update STATE and NATIVE-CONNECTIONS
only after executable qualification. Disk capacity must be recovered first; review
hash-verified unpacked duplicates separately from immutable sealed evidence.

Qualification correction before retry: the independently loaded peer uses the
existing strict AECAT001 startup parser, which requires0x76-prefixed references.
Use the same reference values in both private connection namespaces; connection
selection, not a reference prefix, identifies the caller. Reuse the unchanged
bootstrap bytes and specialize the fixture request expectation without widening
parser acceptance or sharing endpoints. Retain the failed215/1950 attempt.

### Exec peer-first terminal selection — 2026-09-11

Before code: after known image commit and source CLOEXEC-holder removal, keep the
replacement parked and release a bounded peer barrier. The peer either closes its
three descriptors and exits64 or faults with #UD (terminal134/kind2). Observe that
exact terminal before removing faulted-peer holders; require its output EOF before
fault cleanup. Only stdout is now unshared and may close. Source input/stderr remain
live, the published replacement must read c and close them, and both holder rows
must end empty with exactly three confirmed backend closes per generation. Repeat
two generations/six domain reclaims. Retain the source commit/freeze identity until
publication. Reclaim neither client before final observations.

Mutants deliberately close source-live handles during peer-fault cleanup or retain
faulted-peer holders. Require failed subsequent input I/O or explicit incomplete
ownership accounting, respectively, with zero reclaims. Reuse the holder matrix,
existing lifecycle operations and C fixture; no kernel ABI, allocation, service,
SDK or dependency change. The one-message barrier establishes the tested ordering,
not production readiness. Existing pointer/buffer and connection ownership rules
remain. O-03–05, I-03–06 and SE-01–05 apply: extend the current fixture rather than
introduce a generic recovery framework. No obsolete path is removed.

Select the full196-case connections suite, five launch cases, host, scoped format,
workflow and pinned standards checks. Freeze sources and retain failed attempts.
Update STATE/reference/roadmap after qualification. Unknown shared-close receipts,
public execve and consumer acceptance remain separate; fixed RAM cleanup is not
persistent-filesystem recovery or supervisor-failure recovery.

### Exec shared-close uncertainty selection — 2026-09-11

Before code: qualify missing and17-byte final stdout-close receipts after the
source's exec commit and local CLOEXEC removal. Exercise both a normal peer waiting
for its close reply and a peer already terminated by #UD. The backend performs the
close then stalls. Neither zero-filled receipt tails nor elapsed polls establish
success. Keep the replacement parked, verify its commit/freeze identity, send no
peer success acknowledgment and issue no close retry. Confirm source/backend stop
and normal-peer stop, or preserve the faulted peer's exact134/kind2 terminal, before
closing endpoints and reclaiming. Repeat each case for two generations/six reclaims.

Use the existing incomplete backend and bounded receiver. A scoped containment path
handles the mixed live/terminated domains; no kernel, SDK, service, allocator or
protocol extension is needed. Drop no additional shared-holder accounting as if
close were confirmed; abandon the fixture records only after all domains stop.
Zero-padding a partial receipt must reject2100; omitting backend stop must reject2101,
both before reclaim. O-03–05, I-03–06 and SE-01–05 apply: bounded fail-closed cleanup
is sufficient here; a generic retry/recovery framework is unnecessary. Existing
fixed stack buffers and synchronous channel-pointer rules remain unchanged.

Select full202-case connections, five launch cases, host, scoped Rust formatting,
workflow and pinned standards checks. Freeze inputs and preserve attempts. Update
STATE/reference/roadmap after qualification. These fixed RAM domains do not establish
persistent reconciliation, production owner recovery, public execve or consumer
acceptance. Unknown native commit receipts remain a separate staging concern.

### Libc exec staging selection — 2026-09-11

Before code: privately source-build pinned musl execve.c, replacing only its native
syscall expression with a staging hook followed by upstream __syscall_ret. Exercise
actual execve calls: local unknown-path rejection, owner-denied image admission
with EACCES and unchanged descriptors, then successful same-process replacement
that does not return. Pass a bounded argv/env snapshot to the owner and validate
its arrival in the new image. Retain two generations and six domain reclaims.

The first witness supports only the existing /next executable grant and a /denied
admission control, in a single context whose signals are already fully blocked
(except unblockable signals). Reject other mask states with ENOTSUP before traffic;
do not change masks or claim general signal-unmasked exec. Caller buffers must be
valid and stable in this scoped witness; arbitrary-pointer fault handling and
threaded callers remain unsupported. Paths select owner policy, never raw grants.

Wire order on the existing private connection: 32-byte zero-padded path,272-byte
native argument record,64-byte descriptor table, then existing freeze. The owner
validates the path and delegates bounded argv/env validation to native commit.
Denied admission cancels freeze, returns a canonical32-byte negative errno record
and leaves the source's table intact. Successful commit uses existing descriptor
preparation, close and replacement bootstrap. No retry after unknown completion.

Reuse the existing source/backend/peer fixture, pinned musl archive and actual
libc error conversion. No installed SDK, sibling, kernel ABI, dependency, allocation
or service change. O-03–05, I-03–06 and SE-01–05 apply: one private call-site hook is
smaller than a parallel libc implementation. Fixed synchronous buffers remain live
for transport; no caller pointer is retained. Extend current sources rather than
add a second owner. Select complete connections/launch and host suites, symbol and
object inspection, scoped format/pin checks and controls for false return and
retained CLOEXEC. Freeze final inputs and preserve attempts; update state/reference
only after qualification. This is a producer candidate, not SDK/dash acceptance.

Staging qualification correction: preserve musl's include order using a quote-only
internal-header path; first-party warnings remain strict. The argument record is
272 bytes but a channel request is limited to256 bytes, so receive it in bounded
chunks without changing the kernel limit. Distinct path/argument/table rejection
codes identify contract failures. Retain all failed builds and diagnostic boots;
rerun the full205-case suite after the corrected single-case witness passes.

### Libc exec mask guard selection — 2026-09-11

Before code: extend the private libc staging witness to caller masks0 and16. After
bounded argument validation and before descriptor snapshot/transport, block all
blockable signals and retain the caller mask. Known denied admission restores that
mask before returning through musl errno conversion. Successful replacement remains
blocked through bootstrap and complete descriptor installation, then restores the
saved mask before application I/O. Require exact mask observations on both sides;
controls skipping failure or replacement restoration must reject before reclaim.

Carry one32-byte AEEMSK01 record (saved u64 at8, zero tail) after the argument record
and relay it after the survivor table. Connection-selected ownership and canonical
mask bits remain mandatory; verify the second request retains the first saved mask.
No kernel ABI, installed SDK, dependency, allocation or new service. Reuse the
existing startup mask helpers and bounded protocol. Local argument errors precede
the guard and have no descriptor effect; ambiguous transport failures remain fatal
in this private candidate and must not resume an uncertain source. Pointers must
still be valid/stable, and threaded callers remain outside this witness.

O-03–05, I-03–06 and SE-01–05 apply: a scoped saved-mask record is sufficient without
an ambient mask override or generic state-transfer framework. All buffers are fixed
and synchronous; no pointer survives the call or crosses image replacement. Preserve
old masked-only cases. Select full209-case connections, five launch cases, host,
scoped Rust/C formatting, workflow and pinned standards checks. Freeze sources and
retain attempts. This proves mask state ordering, not live pending-handler delivery,
general pointer safety or independent SDK/dash acceptance.


### Composed public fork/exec/wait selection — 2026-09-11

Requirement: exercise a complete external-command lifecycle through privately
built musl fork, execve and waitpid in one native workload. The prior independent
fork/wait and same-process exec passes do not establish their composition. This
is the next producer candidate toward dash, not installed SDK or dash acceptance.
Implementation follow-through is qualified in the [composed witness](NATIVE-CONNECTIONS.md#composed-public-forkexecwait--2026-09-11); actual dash/SDK acceptance remains pending.

Reuse the existing three-worker topology: parent, copied child and RAM file
backend, with the existing user-space owner holding all mutable shared positions
and binding holders. No extra kernel operation, worker, channel, global file table,
service policy or dependency is selected. The child's first new freeze sequence
is 1: copy creates a zeroed child state and copies its execution state, not the
parent's freeze counter. Exec must retain that child's PID, parent identity and
connection grants; replacement startup installs its authorized local descriptor
references before any application request. Numeric local references are interpreted
only within the already-bound connection.

The workload will keep the parent alive with its inherited descriptors while the
child calls execve on the fixed /next image grant. Parent and replacement reads
must advance one owner-held position. Child CLOEXEC removal must neither alter the
parent table nor close a backend still held by the parent. Replacement must check
argv/environment, identity, restored caller mask and absent CLOEXEC aliases before
I/O. The parent then collects the replacement's observed terminal status through
public waitpid; a second wait must return ECHILD. Repeat two generations, requiring
exact terminals, three final backend closes per generation and six domain reclaims.
Do not reclaim or reuse a child before its retained terminal and wait acknowledgment.

Forbidden outcomes include returning to the child's old successful-exec call,
changing identity on replacement, premature backend close, a private copied file
position, publishing a CLOEXEC alias, synthetic wait success, duplicate status
consumption and incomplete cleanup counted as success. Select explicit retained-
CLOEXEC and incorrect-wait-status controls alongside existing commit/freeze,
mask-restoration, descriptor-holder and wait-protocol regressions. Controls must
fail for their named cause before reclaim, not merely panic or time out.

Simplicity review (SE-01–SE-05): running the old independent fixtures is simpler
but cannot expose state transitions across copy, replacement and collection.
Compose their existing hooks and owner operations; share the cohesive exec staging
routine if needed instead of copying it. No production dispatcher or generic
filesystem abstraction is justified by this witness. No old accepted fixture is
removed now; its regressions constrain compatibility during composition.

Affected owners/profiles are Aether's native process/descriptor producer and
userland's libc/dash consumer; sys-init supervision and pkg-mgr package policy
remain unchanged. Apply Foundations O/I/E ownership, authority, bounded interfaces
and reproducible-evidence rules plus DEVELOPMENT's CE/CC/CR/CP and TD/TE process.
C caller buffers remain valid, stable and single-context; arbitrary pointer-fault
recovery, concurrent callers, live pending-handler delivery, filesystem-backed
executable lookup and general SDK execution are not covered by this selection.
FFI and channel records must stay within existing bounded storage and transport
limits; the owner remains limited to 8192 bytes and six channels.

Before acceptance run zig build test, the complete connections suite and five
launch cases on frozen inputs, preserve every failed attempt, inspect the linked
libc call path, and compare prior payload/kernel loadable bytes. Update this
reference, NATIVE-CONNECTIONS, workflow inventory, ROADMAP and STATE with actual
evidence. Consumer review and matching-revision native dash execution remain
separate requirements; no sibling repository or released standard pin is changed.

### Bounded post-fork dispatcher selection — 2026-09-11

Requirement: after the existing single-fork admission/publication boundary, service
parent and child requests as they arrive instead of requiring parent-read,
child-exec, child-read, parent-close and wait in a predetermined sequence. In
particular a blocking parent wait must not prevent child exec or file progress.
This is the next producer step toward dash; initial fork admission remains bounded
and scripted, not a general process service or consumer handoff.

Select two fixed per-connection incremental buffers, at most400 bytes each:32-byte
file/wait requests or the existing32-byte /next name plus272 arguments,32 saved mask
and 64 descriptor bytes. Poll each connection once per loop with bounded reads;
one partial client request must not block reading the other connection. Reuse the
existing exec commit/publication helper and backend. Retain one shared position
per binding, per-client holders, one retained child status, one pending blocking
wait and one acknowledged collection. Connection identity, generation and holder
state authorize file operations; supplied references cannot select another caller.
Defer a blocking wait reply until a real terminal; acknowledge only an issued status.

Forbid premature wait success, foreign/stale-reference I/O, duplicate collection,
backend close while another holder survives, partial-frame promotion and unbounded
allocation. Select parent-waits-first and parent-reads-first native workloads,
foreign-reference denial before backend access, and deliberate authority/early-wait
controls with exact failure causes. Require actual child 72 / parent 71 / backend 17,
shared position 3, three backend closes and six reclaims over two generations.
Run host checks, all connections modes and five launch cases on frozen sources.
Record failed attempts and compare old payload/kernel bytes before qualification.

SE-01–SE-05: retaining scripted ordering is simpler but cannot service a real shell's
blocking wait while its child progresses. Use one bounded owner loop, not a new
service or general event framework. Remove the selected profile's application-step
script through compile-time routing; retain old fixtures for compatibility evidence.
Existing trusted backend exchanges and exec bootstrap sends remain bounded and
synchronous. General backend concurrency/recovery, malformed-exec cancellation,
multiple forks, signals during composition and arbitrary path/pointer handling
remain separate acceptance work. No kernel ABI, SDK, sibling or released pin change
is selected. Aether owns this producer; userland owns matching SDK/dash acceptance.

Apply Foundations O/I/E and DEVELOPMENT's CE/CC/CR/CP and TD/TE requirements. C
buffers remain valid/stable and single-context; Rust has fixed owned arrays and
no allocation. No new unsafe boundary or dependency is required. Keep the8 KiB
owner/six-channel limits and preserve current tool pins. Update NATIVE-CONNECTIONS,
workflow inventory, ROADMAP and STATE with actual results, not presumed conformance.

Follow-through: the [bounded dispatcher](NATIVE-CONNECTIONS.md#bounded-post-fork-dispatch--2026-09-11)
now qualifies both selected request orders and rejection controls. Its first size
failure and build-only probes are retained. Explicitly sharing send/control-call
helpers preserves the unchanged 8192-byte bound. Initial admission remains scripted;
actual dash startup/command integration and SDK acceptance are the next work.

### Requests before first fork selection — 2026-09-11

Requirement: remove the current admission assumption that the parent's first
post-bootstrap frame is a fork header. Actual dash startup/command evaluation can
perform file I/O and query child state before it forks. Select a bounded pre-fork
request phase on the existing parent connection, sharing the dispatcher file
validation and owner-held positions. No child exists in that phase: a canonical
wait-any/WNOHANG request must return ECHILD without publishing a status or token.
Read/write frames use existing capability/reference/holder validation; other
pre-fork operations return ENOTSUP. Limit this phase to sixteen complete requests,
then require the existing fork plan. Initial bootstrap and single-fork publication
remain explicit fixture boundaries.

The executable workload queries wait-any before fork, rejects a foreign-reference
read with an untouched output byte, reads a, then forks. Child exec reads b; the
parent collects the actual exit72 and reads c after wait. Positions and holders
must survive the phase transition; require three backend closes per generation
and six reclaims over two generations. Add exact negative controls for false
no-child success and bypassed pre-fork reference checks. Retain both existing
post-fork request orders and all older controls. The new workload uses real private
musl fork/exec/wait callers, not actual dash; neither ordinary dash vfork execution
nor its full startup service composition is qualified by this prerequisite.

SE-01–SE-05: retaining the initial script cannot serve a shell's pre-fork requests.
Reuse the same bounded file-operation handler and position storage rather than
create another service, protocol or fake shell-specific response sequence. Existing
single-parent admission needs no multi-client polling until the child is published.
Fixed buffers, valid/stable single-context caller pointers and synchronous backend
bounds remain; no new unsafe boundary, kernel ABI, SDK, sibling, dependency or pin
change is selected. Aether owns this producer; userland owns SDK/dash acceptance.
Apply Foundations O/I/E and DEVELOPMENT CE/CC/CR/CP and TD/TE requirements. Preserve
the8 KiB owner/six-channel bounds. Run host, full connections and five launch cases
on frozen inputs; retain all attempts, compare older binaries and update the
reference, workflow inventory, ROADMAP and STATE with measured results.

Capacity refinement before implementation: the new pre-fork phase failed the8 KiB
link assertion. Build-only sharing probes still measured10,152 bytes; no oversized
image was booted and the original format was not relaxed. Select opt-in AENMX002 /
bootstrap ABI17, preserving AENMX001 / ABI9 at8 KiB. The new format allows1..16,384
supervisor bytes with the identical80-byte header, three bounded ELF images,
48 entropy bytes, six channels, three worker slots and unchanged grants. Reuse the
loader's existing variable-page supervisor mapping; verify RX user code, RO/NX
kernel aliases, zero final-page tail and the existing separate RW/NX stack. No
extra stack, worker memory quota, syscall or authority is introduced. A separate
linker selects the new bound only for this candidate. Add host size/reserved/length
boundary tests and native old-version/oversize rejection controls before admission.
Older executable inputs and ABI checks remain regressions. This is a local fixture
contract extension owned here, not a shared standard or SDK publication. The
revised requirement justifies capacity for this measured service, rather than
removing correctness checks or adding another service solely to meet a fixture cap.

Follow-through: the [pre-fork request phase](NATIVE-CONNECTIONS.md#pre-fork-requests-and-larger-owner-format--2026-09-11)
passes the selected lifecycle and rejection controls. AENMX002 / ABI 17 supplies
explicit measured capacity while AENMX001 stays unchanged. The new native cases
also cover 16,383/16,384-byte owners; both older init-capacity suites were selected
because they share supervisor mapping verification. Actual dash remains next.

### Actual dash fork-based command selection — 2026-09-11

Requirement: run pinned actual dash main, parser, subshell evaluator, forkshell,
exec builtin and wait3 against the process owner. Select `(exec /next); exit $?`:
an explicit foreground subshell uses upstream fork, and its exec builtin replaces
the child. Ordinary command evaluation's vfork path is not redirected or claimed.
Reuse the pinned native ENV-guard main and unchanged remaining dash objects, private
musl fork/exec/wait hooks, AENMX002 capacity and existing AECAT003 identity/cwd
bootstrap. The owner supplies fixture identity1000 and a connection-scoped /work
directory reference under the existing op4/op5 contract; /next still selects only
its already-delegated image grant. No filesystem executable lookup is implied.

The parent starts with stdio and FD10/CLOEXEC. Actual dash must reach fork with
that table. The child exec snapshot keeps stdio, while only FD10 disappears; use
the existing descriptor preparation helper without inventing a child stdout close.
The replacement verifies /next argv, the bounded PWD/LC_ALL/PATH environment, TLS,
PID/parent, mask and the survivor table before reading a, closing stdio and exiting72.
Dash must collect that real result through wait3 and exit72; the wrapper closes
its remaining descriptors only on the selected known terminal paths. Two generations
require exact child72/parent72/backend17, one shared read, three backend closes per
generation and six reclaims. Do not require a particular scheduling order or an
artificial WNOHANG probe from dash. Preserve old workload-specific checks in their
existing profiles, with all old request/copy/mask/exec/wait regressions selected.

Controls: bypass actual main and falsely exit72 (no fork), retain child CLOEXEC,
and corrupt the wait status. Each must reject for its exact terminal/owner cause
before reclaim; generic panic/timeout is insufficient. Inspect linked/disassembled
main, forkshell, execve and wait3 paths and bind pinned object hashes. Run host,
full connections and five launch cases on frozen sources; preserve all attempts.
No kernel source, SDK, sibling, released standard, dependency or ABI change is
selected. Live SIGCHLD delivery, ordinary vfork, arbitrary pointers/paths, general
recovery, shell redirection/pipelines, persistent storage and independent SDK/dash
acceptance remain separate. Apply Foundations O/I/E and DEVELOPMENT's CE/CC/CR/CP
and TD/TE rules; update this reference, NATIVE-CONNECTIONS, workflow, ROADMAP and STATE.

SE-01–SE-05: another hand-written fork caller would not prove real shell control
flow. Compose the real upstream objects and existing adapters; use explicit shell
syntax rather than a fake vfork alias. Keep one owner and the current protocol.
The process owner's bounded directory implementation follows the already-owned
startup contract; do not extract or refactor the older command-owner experiments
with their injection variants in this change. No allocation/framework or new
unsafe boundary is needed in the owner. C staging buffers remain valid/stable,
single-context and synchronous; all new storage stays bounded. Retain the16 KiB
code, one-page owner stack, six-channel and worker-page limits. Complex policy stays
in user space; this fixture does not take ownership of sys-init or package policy.

## Actual dash fork/exec/wait command — 2026-09-11

Pinned actual dash now evaluates `(exec /next); exit $?` through its main, parser,
foreground subshell, forkshell, exec builtin and wait3. AECAT003 supplies bounded
identity and cwd startup; the existing copied-process owner handles child exec,
shared stdin and collection. The replacement verifies argv/environment, TLS,
PID/parent, zero restored mask and stdio with FD10/CLOEXEC removed before reading a
and exiting 72. Dash collects that actual status and exits 72. Two generations
require backend17, three final backend closes each and six reclaims.

[Evidence](evidence/dash-fork-command-2026-09-11/README.md) records the complete 227
connections cases, five launch cases and host/format/pin checks. Bypassing actual
main rejects parent72/owner1950; leaked child CLOEXEC rejects child224/owner2130;
wrong wait status rejects parent73/owner2130, all before reclaim. Linked call-path
inspection binds real upstream objects and private musl adapters. The first
attempt omitted the existing signal-copy build flag; the second exposed early
bootstrap rejection during mask publication. Both are retained; complete-frame
consumption preserves the exact rejection boundary.

This is a bounded producer shell command, not an interactive shell or installed
SDK/consumer acceptance. Ordinary external-command evaluation still uses upstream
vfork, which is not aliased to fork. Fixed /next uses the existing image grant;
there is no persistent executable lookup. Live SIGCHLD, arbitrary pointers/paths,
redirection/pipelines, recovery and independent SDK/dash adoption remain open.
No kernel source, ABI, dependency, sibling or released pin changes. Next settle
native dash's ordinary command launch/configuration and matching SDK handoff,
then progress toward interactive serial input and persistent storage.

### Ordinary dash command configuration selection — 2026-09-11

Requirement: actual dash evaluates `/next; exit $?` through its ordinary external
command path, using an explicit native build configuration. In upstream jobs.c's
vforkexec helper, AETHER_NATIVE_FORK_EXEC selects makejob plus existing forkshell
and shellexec; the disabled branch remains upstream vfork, including its vforked
state and parent bookkeeping. Do not alias libc vfork to fork or emulate shared
address-space suspension. Reuse the qualified private fork/exec/wait adapters and
single-owner dispatch, identity/cwd and descriptor contracts. Stable valid pointers,
one fork, fixed image authority and existing quotas remain the bounded scope.

Build original, patched-disabled and patched-enabled jobs objects from hash-bound
source/header/config/SDK inputs. Compare imports and inspect relocation disassembly:
only the enabled candidate must drop vfork; existing native main and other30 objects
remain unchanged. Preserve upstream notices, original jobs.c, exact patch and build
commands. Existing main-config snapshots supply headers/config with their original
provenance limits; new source must match the retained reference manifest. No mutable
sibling input is followed by qualified builds, no sibling or released pin changes.

Run the ordinary command twice with child72/parent72/backend17 and six reclaims;
retain CLOEXEC-leak and corrupted-wait controls with the existing exact terminal
causes and zero reclaims. The unconfigured ordinary-command object must fail rather
than silently reach success; inspect and retain its exact native failure. Run full
connections and five launch regressions plus host, format, workflow and standards
checks with frozen sources. Record failures and archive artifacts before cleanup.

SE-01–SE-05: implementing vfork adds shared-memory/suspension obligations absent
from the release requirement. The existing copied-process primitive and upstream
forkshell child/parent setup are the smaller supported composition. A build guard
keeps unconfigured bytes reviewable and avoids a fake libc alias. No new service,
protocol, kernel mechanism or general fallback is added. This config is a producer
candidate for userland review, not independent acceptance or installed SDK support.
General failure recovery, arbitrary paths/pointers, live SIGCHLD, pipelines,
redirection, interactive input and persistent storage remain separate. Apply the
existing Foundations O/I/E and DEVELOPMENT process; update STATE, ROADMAP, native
references and workflow inventory after qualification.

Follow-through: the [ordinary-command native configuration](NATIVE-CONNECTIONS.md#ordinary-dash-external-command--2026-09-11) now passes its selected command and exact rejection controls. Independent SDK/userland adoption and broader shell workloads remain open.

Serial integration follow-through: [AENMX003 / ABI18](NATIVE-CONSOLE.md#console-plus-process-owner-profile-selection-2026-09-11)
now supplies explicit UART handoff in the existing process-owner layout. Actual
dash remains on its qualified ABI17 command fixture until a console backend,
deferred input and shared-stdio behavior are composed and tested. Do not turn raw
UART EAGAIN into EOF or expose its grant directly to an ungranted shell.

## Pending stream experiment — 2026-09-11

The opt-in `stream_pending` process-owner fixture holds nonempty stdin reads
after canonical backend EAGAIN, using the existing per-caller request frame.
Each scheduling round retries at most once per caller and services the other
caller; offsets and holders change only after completed operations. EOF remains
a real zero result, not an empty-console substitute. No new ABI or installed
SDK behavior is defined. Before-fork pending reads and terminal pending callers
reject this bounded experiment; interruption and indefinite waits remain open.

Run the complete `scripts/launch_smoke.py --connections` invocation documented
above. The `copy-inherit-public-fork-wait-exec-dispatch-pending` cases gate input
on a child stderr write after an empty parent read, then check shared a/b/c
consumption, FD10/CLOEXEC, wait status and six reclaims. The reply, EOF and offset
controls must fail at parent85/owner2130. This is a deterministic stream backend,
not actual UART or an interactive dash acceptance claim. Qualification is recorded
in [the pending-read packet](evidence/stream-pending-2026-09-11/README.md).

## Actual serial dash composition — 2026-09-11

The `copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-serial` cases
in the complete connections invocation boot actual dash with `-i +m`: interactive
prompt, job control disabled. The host sends `/next; exit $?\n` (15 bytes), then
a after CHILD READY; the child consumes a through the same stdin description.
Two sessions require parent/child72,16 stdin bytes,24 stdout bytes,2 stderr bytes
and three logical final closes each. One backend serves both; its final17 and a
denied generation2 probe17 complete six reclaims. The original input object
(`-tee`) rejects owner2140 without a child; wrong input rejects child224/owner2130.

The pinned candidate `user/native-command/dash-input-native/input.o` selects
AETHER_NATIVE_NO_TEE in input.c::stdin_tee. It returns EINVAL to the unchanged
upstream preadfd fallback, which reads one byte without consuming future child
input. tcgetattr/lseek remain truthful unsupported operations; no pipe success
or terminal capability is fabricated. Original source, patch, license, generated
header/tool pins and disabled/enabled comparisons are in the
[qualification packet](evidence/dash-console-2026-09-11/README.md). Existing native
main/jobs and all other dash objects are retained. This is not SDK publication.

Pre-fork pending reads retry where no child exists; this profile admits up to64
pre-fork requests for byte-at-a-time input plus startup metadata. Others retain16.
Post-fork pending reads use the existing per-caller frame. Finite request/reply
watchdogs remain; this does not provide indefinite human think time, cancellation,
general commands, job control, editing or a production TTY. The two fixed sessions
are an integration proof, not an assembled sys-init boot release.

## Prompt continuation and parent cleanup — 2026-09-11

The `-serial-resume` connections cases send `/next\n`, wait for the child to read a
and exit72 and for another `$ ` prompt, then send `echo $?;exit 0\n` in session1
and `echo $?;exit 7\n` in session2. Each session requires22 stdin bytes,27 stdout
bytes (including72\n) and4 stderr prompt bytes. The six ordered host exchanges
and four prompts are checked alongside actual parent0/7, child72, backend17 and
denied replacement17 outcomes and six reclaims. No exit command is preloaded with
the first line. Existing serial/scripted commands remain regressions.

The private console driver captures its initialized parent PID. At normal exit,
that original parent closes published descriptors when startup_ready and not
poisoned, regardless of exit value. PID is a local lifecycle distinction from the
copied child, not authority. Other driver modes and copied-child error paths retain
the prior gate. The normal parent path is qualified for0,7 and72; this does not
claim asynchronous cancellation or fault recovery. Underlying poisoned-transport
checks remain, rather than attempting cleanup through an uncertain channel.

The `-resume-cleanup` control retains the old72/73-only gate and rejects
parent0/owner2131 with zero reclaims. `-resume-exit` sends exit8 in session2 and
requires parent8/owner2130 with two reclaims. Full commands, frozen sources and
serial evidence are in [the packet](evidence/shell-resume-2026-09-11/README.md).
This continuation-only profile admits one external child per shell; subsequent
builtins use the existing post-fork dispatcher. The next profile adds repeated
external commands; indefinite interactive sessions remain separate work.

## Repeated external commands — 2026-09-11

The private `-serial-repeat` connections profile keeps parent slot0 generation1
and backend slot1 generation1 alive across three /next commands. The owner uses
parent freeze sequences1–3 for copy admission to child slot2 generations1–3. A
copied child's own exec freeze starts at1. Header/descriptor preparation remains
bound to the parent; receipt and replacement bootstrap refer to the child.
Parent refs stay live; child-generation refs resolve only on that child's channel
to the same three backend descriptions. Shared positions never reset on reuse.
The child validates its real PID7/11/15 and PPID5; identity creates no authority.

The dispatcher reclaims only after terminal72, exec completion, no pending or
partial child request, released child descriptor holders and acknowledgment of an
issued wait result. It verifies the old child capability is invalid before replying
to the parent. New admission requires the collected child to be reaped, parent
holders live, no outstanding wait and no backend close. The same bounded admission
routine handles the first and subsequent children in this profile. Older recovery
fixtures retain their own exercised paths; no public protocol is silently changed.

Host input is three separate /next lines and three child bytes, then
`echo $?;exit 0` after the fourth prompt. Exact stream totals are36 stdin,51 stdout
and8 stderr bytes. Ordered terminals are child1/2/3 exit72, parent1 exit0, backend1
and denial-probe2 exit17. Six reclaims fit unchanged slot/channel/image limits.
The console accepts a single logical session in this profile and never resets
between children. Its ordinary two-session regressions remain unchanged.

Using token1 on the second copy rejects owner2151 after one reclaim. Sending the
parent-generation bootstrap to child2 rejects child224/owner1950 after one reclaim.
Complete commands, failed attempt and source/artifact receipts are in the
[qualification packet](evidence/shell-repeat-2026-09-11/README.md). Existing native
main/jobs/input objects and released standards/SDK pins are unchanged. This is
producer evidence, not independent acceptance, general process recovery or an
unbounded terminal. Pipes, redirection, arbitrary executable lookup and release
assembly remain open.

## Builtin descriptor redirection and canonical snapshots — 2026-09-11

The private `-serial-repeat-redirect` case asks actual dash to execute
`echo redirected >&2; /next`, `echo restored; /next`, `/next`, then
`echo $?;exit 0`, each as a separate host line after the preceding prompt. Three
children still consume one stdin byte each. Exact shared stream totals72/60/19
prove the first builtin used stderr and the later builtin used restored stdout;
the UART combines their physical output but the owner accounts each description
separately. Four prompts, three child generations, stable parent identity and six
reclaims remain required. Every replacement bootstrap table excludes saved temporary descriptors
and FD10; the normal inherited streams stay live until their last holders close.

A closed local FD slot has present=0 and may retain inactive binding/flag fields.
Fork preparation requires present exactly0/1, counts/validates only live entries,
and leaves absent wire entries zero in its initialized snapshot. Exec staging
also emits empty entries for absent local slots. No closed entry gains a reference,
route or authority; malformed live entries still reach the existing strict checks.
The owner wire schema and exact table validation are unchanged. Serialization
remains under the existing process mask. This avoids imposing a new local table
representation on unrelated users of the shared startup facade.

The `-redirect-stale` control sends inactive local metadata in the fork table and
requires owner2150 before child copy, with zero reclaims. `-redirect-exec-stale`
uses the old exec encoding after a successful copy and requires owner2120 before
image replacement, also with zero reclaims. Both first produce the actual
redirected builtin marker. The first failed native attempt exposed that second
boundary and is retained in the [packet](evidence/shell-redirect-2026-09-11/README.md).
Full connections/launch/console and host checks pass on the final source revision.

The repeated-profile exchange receipt now records session1 for each child-input
event and an explicit child ordinal; prior sealed receipts retain their legacy
field meaning. Existing non-repeated session numbering is unchanged. No SDK
installation, upstream object, released pin or sibling mutation occurred. This
qualifies builtin descriptor redirection restored before fork, not file creation,
external-command redirection, pipes, TTY semantics or a complete shell release.

Next scope one-child command substitution before two-child pipelines. Shell,
backend and substitution child fit the existing three-worker budget. A pipeline
with two simultaneous children plus the shell/backend does not fit; do not grow
quotas or silently serialize it. The next pipe contract must address authenticated
endpoint allocation, per-process aliases, fork/exec inheritance, last-reader and
last-writer behavior, bounded buffering/backpressure, cancellation/failure and
cleanup before any implementation or consumer acceptance claim.

## Bounded pipe and command-substitution contract — 2026-09-11

Status: selected design for the next private native experiment. The owner core is
host-tested and connected to the private native probe below. Public pipe() and
actual dash substitution remain unqualified.
This completes the contract review called for by STATE. It does not add pipe()
to an installed SDK or change any released ABI/pin. Aether owns this fixture and
native enforcement; userland owns independent facade/consumer acceptance;
sys-init retains supervision policy. Production FD/pipe-service ownership is not
assigned here. Evidence and reviewed source identities are in the
[contract packet](evidence/pipe-contract-2026-09-11/README.md).

### Requirement and choice

Run actual dash command substitution through a real FIFO byte stream, first with
one builtin child. `evalbackcmd` in the reviewed dash source calls pipe(), forks,
closes the unused ends and makes the child writer stdout with dup2. `expbackq`
reads to EOF, closes its reader, then waits for the child and removes trailing
newlines. Therefore retaining writer ownership until wait acknowledgment would
deadlock this workload. A successful fork/exec test is insufficient evidence.

Choose one pipe object inside the existing Rust request owner, reached only over
authenticated process connections. Keep the console backend separate and reuse
the current pending-frame dispatcher. Shell, backend and one child fit three
worker slots and six channels; pipe data consumes no extra kernel channel or
worker. Two simultaneous pipeline children plus shell/backend do not fit. Do not
increase limits or serialize a pipeline silently. No named FIFO, filesystem
lookup, polling API, job control, shared mutable kernel FD table or pipe service
process is introduced by this experiment.

Simplicity review (SE-01–SE-05): reusing a raw kernel channel is superficially
smaller but does not provide per-process aliases, fork inheritance or last-holder
EOF; transferring its sole endpoint owner would not implement shared lifetime.
Use an owner-local256-byte FIFO with fixed endpoint-holder state instead. This
retains the existing authenticated request/reply path and avoids another process
and recovery protocol. The necessary new complexity is two pipe bindings and
pending writes as well as reads. No obsolete consumed fixture is removed; no
new general object framework or future filesystem abstraction is justified.

### Authority, bounds and private records

The next opt-in profile retains AENMX003/ABI18 and its existing native grants.
It adds a separately validated32-byte supplemental record after AECAT003 startup;
legacy clients/profiles never send or consume it. Do not mutate AECAT003 bytes.
All words below are little-endian u32 and every reserved byte must be zero.

| Record | Proposed private layout |
| --- | --- |
| Supplemental startup | Bytes0–7 `AEPIPE01`; word8 version1; word12 factory reference; word16 capacity256; word20 request bound16; word24 object limit1; word28 zero |
| Create request | Word0 op82; word4 factory reference; word8 version1; bytes12–31 zero |
| Create success | Word0 zero; word4 pipe generation1–3; words8/12 reader/writer references; words16/20 bindings3/4; word24 capacity256; word28 request bound16 |
| Create failure | Signed negative errno at word0; bytes4–31 zero |
| Data/close request | Existing32-byte op1 read/op2 write/op3 close shape, endpoint reference at4, binding at8, length0–16 at12, payload/tail at16 |
| Data/close reply | Existing canonical signed-result record; read data only after byte16; no caller pointers on the wire |

Factory reference is0x76050001 for this fixed parent1 experiment. It is not a
secret or ambient authority: the owner ACL authorizes only the granted parent's
actual connection. The child's copied integer cannot create a pipe. References
are0x78000000 | (pipe_generation << 8) | endpoint, with endpoint1 reader or2 writer.
The owner checks connection, holder, exact object generation, binding and direction
before effects. Parent and child share the pipe references after validated fork;
pipe generation is independent of process generation and freeze sequence.
Foreign/unauthorized/wrong-direction requests return EACCES; a matching formerly
issued but retired reference returns EBADF. Invalid framing/version/length returns
EINVAL without changing object state. No arithmetic on a reference grants access.

One object may be live, with at most three successfully published generations
in this test. Exhaustion returns ENFILE; no wrap or implicit replacement. Rejected
creation leaves the generation available. Data storage is256 bytes; each accepted
write request1–16 bytes is all-or-wait. Bounds and wraparound must be tested.
Owner image remains within16KiB; measure added data, stack and image use rather
than assuming the existing margin is sufficient. Client binding arrays grow from
three to five only in this opt-in profile; the16-entry FD table stays unchanged.
The STARTUP_FILES profile already uses bindings3/4: reject combining the two
private profiles rather than aliasing their authority or silently widening tables.

### Local publication and inheritance

The initial libc surface is pipe() with blocking read/write endpoints and clear
FD_CLOEXEC. Allocate the two lowest available local FD numbers. Reserve both
under the existing single-context signal mask before sending creation; fewer than
two slots returns EMFILE without traffic. Null output is EFAULT before traffic.
The first bounded adapter requires a valid writable two-int output span; arbitrary
faulting-pointer EFAULT behavior is NOT established. An output-store fault must
be covered by confirmed-domain-stop resource cleanup, not counted as successful
allocation or safe rollback. No new memory-query capability is assumed.

Validate the complete create response before installing either descriptor or
changing caller output. The owner commits endpoint holders when it accepts the
create operation. A malformed, missing or partial reply is an unknown outcome:
poison the caller transport, do not retry/reallocate, and contain the caller with
confirmed stop before retiring its possible endpoint holdings. Do not claim the
server did nothing merely because the caller installed no descriptors. Rejecting
local flags/capacity or owner authority is a known no-effect result.

Use a version2 fork plan in this opt-in profile: retain the96-byte envelope and
16 four-byte FD entries, but permit validated bindings0–4. The header version at
word4 distinguishes it from v1. Absent records remain canonical zero. The copy
receipt retains op65 and child generation, sets its word8 version2, and uses all
five words at12–31 for binding references. V1's final eight reserved bytes remain
zero in every old profile. Initial stdio references continue their current rebinding;
pipe references remain tied to the shared pipe generation. No generic receiver
should accept either version merely because the length matches.

Local aliases use existing fcntl/dup2 bookkeeping. The owner holds one boolean per
process per endpoint, not one per local FD; only the last local close sends an
endpoint close. Stage child endpoint holders before copying; require completed
copy/rebinding/readiness before servicing child operations. Failed copy removes
only staged child holders and cancels the exact parent freeze token. Ambiguous
publication requires stopping the affected processes before releasing their
holders. Parent aliases and queued data survive a known rejected fork unchanged.

After validated readiness, authorize builtin-child I/O without requiring exec.
Parent stdio keeps its0x76000000-class references; the copied child uses the
0x77000000-class references actually supplied by its receipt, checked against
its own connection/generation/holders. Both resolve to the same backend descriptions.
Do not accept pre-readiness traffic or silently retag references as if replacement
bootstrap had occurred. Pipe bindings keep their separate shared object generation.

Do not extend pipe inheritance across exec in the first builtin-child experiment.
An exec request with live pipe bindings is explicitly rejected before image
replacement and returns through the existing known-failure/mask restoration path.
CLOEXEC and surviving pipe descriptors across exec need their own later contract
and tests; the current three-binding exec planner must not truncate a five-binding
snapshot. pipe2 flags, FD status-flag operations and fpathconf are also unsupported
until separately implemented and qualified; no successful stubs or pipe limits
are advertised through those APIs.

### FIFO, pending requests and endpoint death

| Condition | Required owner behavior |
| --- | --- |
| Buffered read | Return up to the requested bound, FIFO order; writers may already be gone |
| Empty read with any writer holder | Keep this caller's request pending; never return a false EOF |
| Empty read with no writer holders | Return0, even if an exited child has not yet been waited for |
| Write with enough room and a reader holder | Enqueue the complete bounded request exactly once, then reply with its length |
| Write without enough room, readers remain | Retain the original frame pending; permit the other process to read/close |
| Nonempty write with no reader holders | Enqueue nothing; return EPIPE and follow the scoped SIGPIPE rules below |
| Zero-length read/write | Return0 after validating authority, endpoint and framing; do not wait or change counts/data |
| Last reader closes | No subsequent write succeeds; discard unread bytes once no reader can observe them |
| Last writer closes | Preserve buffered bytes for readers, then EOF; close does not imply child wait acknowledgment |

At most one pending operation per authenticated process uses its existing frame.
Do not dequeue a read or enqueue a write again because reply delivery is uncertain.
Continue round-robin progress for the other caller; reset a frame only after its
completed reply or confirmed caller termination. A full/empty buffer is not a
transport failure. The current finite watchdog remains a fixture failure/containment
boundary, never synthetic EOF, EAGAIN for a blocking caller or successful timeout.
Asynchronous EINTR/cancellation during a masked blocking transaction is not yet
supported; indefinite interactive use remains outside this stage.

On actual terminal observation, release that process's endpoint holders regardless
of whether its client close path ran. A stop request alone is insufficient. Partial
unapplied requests are discarded only after terminal confirmation; already applied
bytes are not replayed. Peer holders remain live. Normal and abnormal terminal
causes retain their real status for wait independently of descriptor retirement.
The current child exit0 cleanup gate and dispatcher requirement that every child
executes an image are insufficient: the new profile must handle a builtin child
that exits0 without exec or explicit descriptor closes. Do not fake exit72 or an
exec completion merely to reuse the prior oracle.

Process reclaim still follows terminal observation, detached pending routes,
released resources and valid wait acknowledgment. Pipe retirement is separate:
retire after both endpoint holder sets and pending references are empty; clear
buffer/storage before a later generation. Buffered bytes may be discarded after
the last reader disappears. Reuse must not let an old reference close or consume
new data. No extra dummy workers are launched merely to satisfy a reclaim counter.

### Compatibility and signal gates

POSIX's [pipe](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pipe.html)
reference defines separate read/write descriptors and initial clear descriptor
flags. The [read reference](https://pubs.opengroup.org/onlinepubs/9799919799/functions/read.html)
distinguishes empty-with-writers from EOF. These guide the experiment; they do not
establish compliance. The existing16-byte facade and a256-byte object do not
provide the larger atomic-write guarantees discussed in the
[POSIX.1-2017 write reference](https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html).
Keep this an explicitly adapted bounded pipe experiment, not a full POSIX pipe or
PIPE_BUF claim. The adopted Distribution reference remains POSIX.1-2024; fetching
its write page was unavailable during this review, so no newer wording is inferred.

Broken-pipe EPIPE and SIGPIPE must be tested together before the public adapter is
accepted. The existing self-signal mechanism accepts signal13; default termination
requires native-signal-termination, which the current serial-dash profile does not
enable. Scope that existing flag to the new qualified pipe profile. Post SIGPIPE
once after the no-reader result while preserving transaction state; restore the
caller's original mask and use the explicit pending-delivery poll for default
termination. Posting twice to force delivery is forbidden. Test ignored, blocked,
handled and default dispositions, including unblocking a previously pending signal.
Current automatic delivery deliberately does not terminate default dispositions;
any needed opt-in facade poll on mask restoration must be reviewed and tested.
Missing default/deferred delivery remains blocked compatibility coverage, not a
reason to return fictitious success or suppress SIGPIPE silently. No broader kernel
signal refactor is authorized by this contract.

The native SIGPIPE adapter section below now records scoped producer coverage for
these selected schedules. Integration into the serial-dash profile remains separate.

### Required implementation and acceptance order

1. Implement the bounded owner object and private pipe adapter in the existing
   connection fixture. Test FIFO/wraparound, full-buffer progress, reader/writer
   direction, two-slot reservation, alias lifetime and unknown create replies.
   Use real parent/child copies with scoped endpoints, not a simulated fork.
2. Add terminal-driven endpoint retirement and default/ignored/blocked SIGPIPE
   qualification. Retain real status while delivering EOF before wait. Mutants
   must detect early EOF, retained writer after terminal, early release before
   stop, wrong-generation access, duplicate enqueue and false EPIPE success.
3. Run actual dash unchanged with `echo "$(echo pipe)"`, `echo "$(echo)"` and
   `echo "$(echo reused)"`, then `exit 0`, as separately supplied serial lines.
   Require exact output `pipe\n`, `\n`, `reused\n`, four prompts, real child0
   terminals for generations1–3, stable parent identity, parent0, backend/probe17
   and six reclaims. Calculate input/stream counts from the exact recorded bytes
   before freezing sources. Cover trailing-newline removal and pipe-slot reuse.
4. Run the complete matching connections suite, launch/console regressions,
   affected signal profiles, host/format/workflow and offline pin checks. Preserve
   all failed attempts and qualify final frozen inputs within existing limits.
   Deliver a producer packet for independent userland intake; do not declare
   installed-SDK acceptance, full pipelines or an assembled release from it.

Native acceptance is NOT RUN. This design review uses source inspection and local
documentation checks only. Standards clauses O-01–O-05, I-01/I-03–I-06, E-01–E-04,
PX-01–PX-03 and SE-01–SE-05 remain scoped as documented in STANDARDS/DEVELOPMENT;
no released standard or consumer pin is changed. Implementation review, arbitrary
pointer handling, asynchronous cancellation, full atomic writes, external/file
redirection, two-child pipeline capacity and owner acceptance remain open gates.

### Owner core implementation — 2026-09-11

[pipe.rs](../user/native-connections/pipe.rs) implements the fixed FIFO, canonical
create/data replies, generation-limited endpoints, staged child inheritance and
confirmed-terminal holder retirement. Its 12 host tests cover FIFO wraparound,
all-or-wait writes, malformed/unauthorized requests, failed-copy preservation,
EOF before wait, last-reader EPIPE, old terminal/reference denial and retirement
with pending frames. The same module compiles as a no_std x86_64 object.
[Evidence](evidence/pipe-owner-core-2026-09-11/README.md) records the scope and checks.

The core's host tests alone do not verify caller identity or terminal observation;
those are trusted inputs to its owner API. The native probe below now supplies
these inputs from real process connections and lifecycle observations. The integration must derive Caller from the authenticated connection,
retain each pending frame unchanged, send/cache completed replies without
reapplying the operation, and include partial requests and undelivered replies
when testing retirement. A known failed copy can undo staged holders; ambiguous
copy/publication requires confirmed termination. Wait collection remains separate.

The native probe below extends these host results to startup, fork-plan v2,
FD reservation/alias behavior and actual parent/child endpoint lifetimes. Unknown
reply recovery, signal delivery and actual dash substitution remain unqualified.
No installed SDK, released ABI, kernel, sibling source or standard pin changed.

### Native pipe transfer probe — 2026-09-11

The opt-in `copy-inherit-public-fork-wait-pipe` profile connects the pipe core to
real musl fork/copy through `pipe-native.rs` and a private `native_pipe_pair`
adapter. It uses the existing ABI17/AENMX002 envelope, three worker slots, six
channels and 16 KiB owner limit. No UART grant is needed for this protocol probe;
serial dash will continue to use ABI18/AENMX003. Legacy fork profiles remain v1.

Each of two complete parent/backend/child lifetimes owns a fresh pipe object.
The pipe generation is 1 in each lifetime, independent of process generation 1/2;
the fixed factory reference is authorized only on that lifetime's actual parent
connection. All old routes and processes are reclaimed before the next lifetime.
No numeric reference by itself obtains authority, and no extra probe worker is
launched to satisfy a reclaim counter.

After AECAT003, the owner sends AEPIPE01. The adapter verifies it, rejects null
output or fewer than two available local FD slots without create traffic, validates
the full creation reply, then installs blocking reader/writer descriptors 3/4 with
clear CLOEXEC. It aliases reader3 to11 and closes3 without closing the endpoint;
FD10 remains a CLOEXEC alias of stdin. The v2 fork table carries bindings0–4 and
canonical absent entries. The child validates the complete five-reference receipt
before replacing stdio references; pipe references retain their object generation.
FORK_PIPE combined with STARTUP_FILES or FORK_EXEC is explicitly rejected at build
time. This probe neither supplies public pipe() nor supports pipe-preserving exec.

The child proves denied factory use and wrong-direction access, closes its reader,
then writes 320 patterned bytes in 16-byte requests and exits0 without closing its
writer. Private op83 (all remaining bytes zero, parent only, once per lifetime)
keeps the parent's first read behind a full-buffer pending-write witness. It is a
scheduling assertion for this fixture, not a new public operation. The parent
then drains the exact pattern through EOF, collects the real exit0 with waitpid,
closes descriptors and exits0. Independent TLS/private-memory values survive the
copy. Three real processes per lifetime account for six reclaims.

The owner services only authenticated ready connections, retains partial/pending
frames, and never replays a completed I/O after send failure. The positive probe
expects normal exit0; abnormal termination and partial in-flight cleanup remain
unqualified. Terminal observation
releases pipe and stdio holders independently of wait; reclaim still waits for
collection and closed routes. EOF-with-live-writer and retained-terminal-writer
mutants must respectively reach parent90/owner2163 and child0/owner2164 with zero
reclaims. Generic boot failure or timeout is not acceptance.

Run the complete matching suite with the commands in the
[producer packet](evidence/pipe-native-2026-09-11/README.md), then the launch and
console regressions plus host checks. See that packet for final run status and
failed attempts. The following section covers interrupted create replies ending
in channel EOF. Public SIGPIPE, silent-stall/live-client recovery, failed native
copy rollback, native pipe-generation reuse in one parent lifetime,
arbitrary-pointer recovery and actual dash substitution remain required work.
This bounded producer probe does not establish installed SDK or R1 acceptance.

The `-pipe-reply` control sends a zero-tailed INT32_MIN create result after owner
allocation. The adapter checks the signed value against allowed errors before
negation, reports EIO and poison, publishes neither output FD nor binding, and
exits with witness92. The owner requires the actual terminal and empty request
route before retiring the possible pipe, then aborts the intentionally corrupted
fixture with2167 and zero reclaims. This is one malformed complete-reply boundary;
it does not qualify partial replies, automatic recovery or continued availability.

### Interrupted create cleanup probe — 2026-09-11

The `-pipe-lost`, `-pipe-one` and `-pipe-short` profiles commit the same pipe
creation, send respectively zero, one and 31 response bytes, then close the
reply writer. Channel EOF interrupts the adapter's whole-record exchange. It
returns EIO, preserves the original signal mask, poisons the route and leaves
both output elements and descriptor bindings unpublished. A second create must
fail locally. Exit92 witnesses those checks; it is not application success.

The owner first verifies that closing the reply transport cannot retire the
pipe while parent holders remain. Only after observed exit92 and an empty request
route does it release the parent's pipe holders and retire the object, close all
three backend handles, observe backend17, detach the remaining route and reclaim
both tasks. The reply writer is already closed and must not be closed twice.
Three real parent/backend lifetimes use existing process generations1–3 and
produce six reclaims under the unchanged kernel profile. The owner stays alive
across those lifetimes; each gets a fresh pipe object at pipe generation1.

The `-pipe-lost-retain` mutant omits confirmed-terminal holder release and must
fail retirement with owner2168 after parent92, with zero reclaims. Exact traces,
source identities, commands and qualification status are recorded in the
[cleanup packet](evidence/pipe-reply-cleanup-2026-09-11/README.md).
This covers fail-closed teardown and bounded task/resource reuse after transport
closure. It does not qualify a silent stall without EOF, continued use of a
poisoned client, abnormal in-flight child cleanup, native copy rollback, public
pipe/SIGPIPE or actual dash substitution. No sibling or released ABI/pin changes.

### Partial request at child fault — 2026-09-11

The `-pipe-fault` profile writes 256 patterned bytes from the real copied child,
then sends 17 bytes of the next canonical 16-byte write request and executes UD2.
The owner observes kind2/detail134 for that exact child before draining its request
route through EOF. It requires the exact 17-byte prefix, discards the unapplied
frame, then releases the child's pipe and stdio holders. The parent reader keeps
all 256 committed bytes alive. Its private scheduling witness waits for the fault;
it then drains the pattern through EOF before waitpid reports SIGILL with no core
dump flag. The existing wait mapping and collection acknowledgment remain in use.
Two complete parent/backend/child lifetimes finish with six actual reclaims.

The `-pipe-fault-frame` control retains the partial frame and must reach owner 2166
at retirement after actual child fault and parent exit0, with zero reclaims.
The `-pipe-fault-status` control reports normal exit134 instead of SIGILL; the real
parent exits90 and the owner rejects at 2163, again with zero reclaims. Generic
panic or timeout is insufficient. See the [fault cleanup packet](evidence/pipe-fault-cleanup-2026-09-11/README.md)
for commands, final qualification status and exact source/artifact identities.

This covers one partial-request fault schedule. Forced stop of a fully pending
write, other fault/transport schedules, native copy rollback, public SIGPIPE,
same-client pipe generations and actual dash substitution remain unqualified.

### Stopping a pending pipe writer — 2026-09-11

The `-pipe-stop` profile receives the child's complete seventeenth write after
256 committed bytes fill the FIFO. Only after the core returns Pending does the
owner request a stop through its existing child capability. It observes retained
kind3/detail143 before any holder/frame cleanup. The cleanup path rechecks that
terminal, the exact 32-byte pending request, empty request route and 256 committed
bytes with none read. It then discards the unapplied request and releases child
holders. The parent drains all 256 bytes through EOF before wait/ack and exit0.

This private wait policy maps the exact supervisor stop to SIGTERM status15; it
does not claim native signal delivery or public kill support. The shared wait
mapping is unchanged. Forced stop emits no normal/fault child serial marker, so
the owner checks retained native state directly. Two parent/backend/child lifetimes
still account for six real reclaims, with parent0/backend17 in each generation.
No dummy process or quota change supplies that count.

The `-pipe-stop-skip` control omits the actual stop and must reject at owner2171
with zero reclaims. The `-pipe-stop-frame` control retains the unapplied frame and
must reject retirement at owner2166 after parent0, with zero reclaims. See the
[stop cleanup packet](evidence/pipe-stop-cleanup-2026-09-11/README.md) for commands,
qualification status, exact traces and artifact identities. SIGPIPE, silent stalls,
native copy rollback, same-client pipe reuse and actual dash substitution remain
separate work; this is not general cancellation or release acceptance.

### Native SIGPIPE adapter — 2026-09-11

The `-pipe-signal` and `-pipe-signal-block` profiles opt into the existing native
signal actions/public/mask-delivery/termination flags. A validated EPIPE from a
nonempty write to the pipe writer posts signal13 once under the transaction mask.
Mask restoration then polls with signal0. Successful public sigprocmask changes
also poll after publishing any old-mask output, so unblocking a default SIGPIPE
terminates before returning. Both mask-restoration paths restore the caller's
saved errno after handler delivery. The write
wrapper returns EPIPE when disposition/mask permits return. Old profiles do not
acquire these opt-in polls.

The real C client checks zero-length and invalid-FD operations without signal,
ignored and handled EPIPE, two blocked writes coalescing into one handler on
unblock, and discard of a pending signal upon installing ignore. It checks handler
mask/count and errno. The final default action must produce real native terminal
kind4/detail13, either from write or on deferred unblock. The owner requires exactly
six EPIPE writes, one zero write and reader closure before accepting that terminal;
actual terminal and request EOF precede pipe/backend cleanup. Three fresh parent/
backend lifetimes produce six reclaims, without a child or quota increase.

The `-pipe-signal-no-post` and `-pipe-signal-no-poll` controls must reach parent94
and owner2172 with zero reclaims. See the [SIGPIPE packet](evidence/pipe-sigpipe-2026-09-11/README.md)
for exact qualification status, commands and source/artifact identity. This uses
actual pinned musl sigaction/restorer but does not install an SDK adapter or public
pipe(). Serial dash adoption, same-client pipe generations, general EINTR/restart
and arbitrary-pointer semantics remain separate work. No kernel source or pin changed.


### Pipe descriptors at execution commit — 2026-09-13

`exec_fds::prepare_pipe` applies the existing CLOEXEC filter to the five private
bindings (three streams, pipe reader, pipe writer). It retains the 16-slot,
four-byte canonical descriptor records. Counts include aliases; the last local
alias controls endpoint release. The three-binding `prepare` entry point still
rejects pipe bindings. Both preparation operations are pure and confer no authority.

`Pipe::commit_exec` is an internal owner method, not a client request. With a ready
authenticated caller, active matching pipe generation and exact previous holder
set, it replaces only that caller's holders with a subset. All checks precede
mutation. Other holders, pipe generation and child identity remain unchanged.
Dropping the last reader clears buffered bytes; dropping the last writer allows
remaining readers to drain through EOF. It does not retire the pipe or collect a
process. Stale state or added rights reject without effects.

Before a native caller uses this method, its dispatcher must quiesce the caller's
I/O and bind the complete descriptor plan to validated executable admission and
replacement readiness. Commit must publish the descriptor plan and holder changes
without intervening caller mutation. Admission failure discards the plan; ambiguous
replacement requires retained reconciliation/terminal evidence, never guessed
rollback or retry. These native transitions remain to be implemented and tested.
The [boundary packet](evidence/pipe-exec-boundary-2026-09-13/README.md) distinguishes
host core checks from unchanged native regression coverage. The PIPE+EXEC build
guard and pipe client's explicit ENOTSUP remain until the native path is qualified.


### Bounded native pipe exec — 2026-09-13

The opt-in `copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec` profile
uses actual dash `/next` command substitution. Its `FORK_DASH_PIPE_EXEC` adapter
uses the existing exec staging transport; the old generic PIPE+EXEC combination
remains rejected. Only this dedicated owner branch enables image replacement.
The frozen child submits a complete name/argument/mask/descriptor record. The
owner validates stdin0, stdout4, stderr2, FD10->0/CLOEXEC and FD11->4/CLOEXEC,
then uses the existing five-binding filter. Both retained stream holders and the
pipe writer remain; no backend release is required by removing these two aliases.

The first request uses `/denied`: native image0xc004 is rejected with EACCES, its
image receipt remains empty, and the owner cancels freeze1 before returning the
error. The client checks descriptor flags before submitting `/next` under freeze2.
The boot-granted third image0xc003 replaces the child while frozen. Receipt2 must
identify that image as pending before pipe generation/holder validation and resume.
The child generation, authenticated connection and pipe generation are retained.

Replacement startup is the bounded AECAT001 prelude, filtered64-byte FD table,
32-byte private AEPEX001 record and existing AEEMSK01 mask. AEPEX001 contains
magic8, child generation at8, pipe generation1 at12, reader/writer references at16/20
and eight reserved zero bytes. These records convey only the owner's admitted
bindings, never pipe-factory or new executable authority. The replacement validates
all bytes before I/O; reconstructs the surviving local table and child references;
restores the saved zero mask; checks FD10/11 absent; writes exactly `pipe\n` through
stdout; and closes its remaining three FDs. Parent drains EOF and waits for the
real child result before acknowledgment and disposal. Two complete generations
must produce child0/parent0/backend17 and six actual reclaims.

The `-stale` control supplies pipe generation2 at commit and must reject2184 with
zero reclaims before replacement startup. The `-drop` control removes the surviving
stdout table entry and must produce child227/owner2176 with zero reclaims and no
successful pipe output. [Evidence and current qualification](evidence/pipe-exec-native-2026-09-13/README.md)
remain distinct from installed SDK/independent consumer acceptance. The current
fixed admission test does not handle general interrupted exec, concurrent pipelines
or arbitrary executables. The following serial profile composes this boundary
with prompt-driven input; its linked packet records qualification.

### Serial external substitution — 2026-09-13

`copy-inherit-public-fork-wait-prefork-dash-command-pipe-exec-serial` composes the
bounded pipe-exec owner with serial dash and the existing two-session UART backend.
Actual `sh -i +m` receives these commands at four observed prompts:

```sh
a=$(/next); echo "$a"
b=$(/next); echo "$b"
exit 0
echo clean; exit 0
```

The fourth command belongs to a fresh shell. The first parent retains identity
through two real children and two pipes. Source-copy tokens advance1→2; each new
child independently uses exec freeze1 for denied admission and freeze2 for its
successful replacement. Per-child denied/success state resets on admission and
must be complete before wait acknowledgment. The no-child second parent requires
no exec receipt. Pipe commit and AEPEX001 publication use the owner's actual pipe
creation record, rather than assuming pipe generation1. The serial replacement
validates the admitted two-cycle relation between child and pipe generations;
the older nonserial replacement still requires pipe generation1 in both lifetimes.
No general equality between process and pipe generations is introduced.

Each child validates TLS, startup, filtered descriptors and saved mask before
writing five bytes and closing its three surviving descriptors. FD10/11 remain
CLOEXEC probes, not user commands. Both stdout results, EOF, actual wait/ACK,
reclaim-before-reuse, pending serial reads and clean backend reset are required.
The positive trace is child1/child2/parent1/parent2/backend1/backend2, statuses
0/0/0/0/17/17 and six reclaims. The owner remains within the existing16KiB envelope.

The `-stale` control supplies pipe generation1 during the second child's commit:
owner2184, exactly one reclaimed child, no second-child terminal or output. The
`-grant` control publishes the first pipe's generation and references to the second
replacement: child227/owner2176, exactly one reclaim and no second result. The
serial driver checks complete panic lines, two commands/two prompts and the exact
terminal sequence. Existing native/builtin-serial controls remain unchanged.

[Review and qualification](evidence/pipe-exec-serial-2026-09-13/README.md) record
execution status. This remains a fixed producer workload, not an arbitrary shell,
installed SDK or independent consumer acceptance. Next use the unchanged consumer
DASH-argv and DASH-signal-table workloads to drive the adapter handoff; general
pipelines, interruption recovery and filesystem/package/sys-init assembly remain.

### Unchanged consumer DASH-argv — 2026-09-13

The opt-in `copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-argv`
profile runs actual dash with the unchanged consumer command string:

```sh
WITNESS=value /inputs/helper argv "a b" "*"
```

The newline-terminated script is pinned in `user/native-command/dash-argv-inputs`;
the build checks both its digest and equality with the C command literal. The
existing pinned consumer helper body is compiled unchanged under a private main
symbol. A separately linked replacement wrapper validates startup, TLS, identity,
filtered descriptors and saved mask, then calls that helper with the real incoming
argv/environment. It closes the three surviving descriptors after the helper
returns. The wrapper does not reimplement its argument or environment checks.
Existing dash objects, SDK archives, helper source and older replacement roles
remain pinned; no build follows the sibling checkout.

This profile explicitly maps `/inputs/helper` to the existing boot-granted image;
it does not provide filesystem path resolution. The existing exec frame carries
four arguments and at most four environment entries, each at most31 bytes. Dash
creates the assignment environment and quotes before real fork/exec/wait3. FD10's
CLOEXEC alias is removed during replacement. The helper requires arguments
`argv`, `a b`, `*` and WITNESS=value, writes `argv ok\n` and returns0. The parent
then exits0 and closes its descriptors. Before final stdout close, the owner
independently reads back the backend's eight output bytes and checks stream
positions0/8/0. Child0/parent0/backend17 repeat for two generations and six actual
reclaims; an empty output or a successful child status alone cannot pass.

`-arg` changes the first byte of the whitespace argument before image admission;
`-env` changes WITNESS's value. Both must produce the unchanged helper's status91
and owner2130 before any reclaim. `-skip` returns0 without calling the helper;
child0 is retained but final backend readback rejects2310 with zero reclaims.
These are private negative profiles; the unchanged script and helper pins are
never rewritten to create controls. Other shell failure oracles remain separate.

Use the existing complete `scripts/launch_smoke.py --connections --libc-build SDK
--tools-lock LOCK` invocation. The [review and evidence](evidence/dash-consumer-argv-2026-09-13/README.md)
record qualification status and all attempts. This qualifies producer execution
of DASH-argv, not an installed SDK or independent consumer acceptance. Next run
unchanged DASH-signal-table with its real substitution and trap/self-signal path,
then consolidate the consumer adapter handoff. General pipelines and R1 assembly
remain separate requirements.

### Unchanged consumer DASH-signal-table — 2026-09-13

`copy-inherit-public-fork-wait-prefork-dash-command-pipe-signal-table` evaluates
the unchanged userland script with actual dash:

```sh
[ "$(kill -l 10)" = USR1 ] || exit 26
trap 'printf "signal ok\n"' USR1
kill -USR1 $$
```

The script and original twelve-workload manifest are captured under
`user/native-command/dash-signal-inputs` with hashes in pin.json. Builds check
script-literal equality, manifest script/exit/stdout fields, and the initial
environment for both this profile and DASH-argv. Both now use WITNESS=value,
LC_ALL=C and PATH=/nonexistent, with PWD=/work for the existing granted cwd.
This corrects the earlier argv fixture's initial environment without rewriting
its sealed evidence or changing the script/helper. No sibling bytes are followed
at build time. Other private-shell environments remain unchanged.

The existing child pipe carries exactly five bytes `USR1\n`; both its writes and
parent reads are checked. Real EOF and child wait/ack precede trap execution.
The parent installs dash's actual USR1 handler through the existing public-action
bridge, and its kill builtin calls the opt-in private facade. That facade accepts
only the current positive PID: signal0 probes locally, SIGUSR1 invokes existing
native operation0x29002 with zero remaining arguments. Foreign positive PIDs return
EPERM; process groups/nonpositive PIDs and other valid signals return ENOTSUP;
signal numbers outside0..64 return EINVAL. Before startup readiness it returns
EAGAIN. These are declared private limits, not general POSIX kill semantics.
The PID check never authorizes another process or consults a mutable global table.

Native delivery may enter the validated handler before the call returns; existing
kernel-owned mask, pending record and handler/restorer checks apply. No pointers
are borrowed by the added FFI call. Dash's deferred trap then writes exactly
`signal ok\n`; the owner independently reads those ten bytes from the backend,
requires empty stdin/stderr and checks descriptor cleanup. Two complete lifetimes
produce child0/parent0/backend17 and six real reclaims. Signal0 and denied scope,
group, invalid-signal and unsupported-signal requests are checked before the script.

`-post` falsely returns success without posting SIGUSR1. After child0, absent trap
output rejects2175 with zero reclaims. `-scope` omits the PID guard, so the initial
foreign-PID probe is wrongly delivered to the caller, whose default USR1 action
terminates it: parent kind4/detail10, owner2176, zero reclaims and no child admitted.
Neither control changes the consumer script or fabricates trap output. The second
control detects misrouting to self; it does not signal an actual foreign process.

The existing complete connections invocation runs all three profiles plus the
four environment-corrected DASH-argv profiles. [Review and evidence](evidence/dash-consumer-signal-2026-09-13/README.md)
record qualification and all attempts. Next consolidate the phase-one producer
handoff (startup, argv, signal-table and independently consumed syntax) with exact
matched artifacts and explicit remaining workload gates. No SDK installation,
independent consumer acceptance or full twelve-script completion is implied.

### Consumer closure and background-wait dependency — 2026-09-13

The unchanged `fd-closure.sh` is selected next using the existing native helper
exec path, manifest environment and retained wait/cleanup protocol. It checks
helper descriptors3–63 through real fcntl calls and prints closed ok only after
status0. The fixture's FD10 CLOEXEC alias must not survive replacement. An injected
post-startup FD3 control tests the helper's check; a corrupt wait-status control
tests dash's script decision. These controls do not qualify fd-leak-control.sh,
which opens /scratch/leak for writing and intentionally expects exit22.

The unchanged wait.sh requires background fork. Dash forkchild closes stdin and
opens /dev/null for that mode. The current fixed helper route supplies no such
openable object. Define a scoped null descriptor and its inheritance/exec lifetime
before claiming this workload; do not bypass redirection or substitute existing
nonempty input. See the [closure review](evidence/dash-consumer-closure-2026-09-13/README.md).

### Scoped null descriptor selection — 2026-09-13

This is the selected next private experiment, not an implemented open API.
Background dash closes FD0 then opens /dev/null O_RDONLY. Keep the parent's
original input distinct: add binding3 for the null object alongside the three
standard-stream descriptions. The sixteen-entry, four-byte-per-entry table stays
unchanged. Existing three-binding consumers must reject binding3; the pipe
profile's bindings3/4 retain their existing meaning and cannot be combined with
null by reinterpreting a numeric binding. The new profile must explicitly advertise
its own bootstrap and create authority; no released bootstrap is silently extended.

The owner will authorize null creation through a separately advertised handle on
the authenticated child connection. A pathname is only a lookup request, never
ambient authority. Bind each returned object handle to its owner lifetime and open
instance, reject stale/foreign handles before I/O, and forbid wrapping reuse.
Select read-only opens plus O_CLOEXEC for this experiment; unsupported access modes
and flags must reject. A valid null read returns EOF without reading, advancing or
consuming original stdin, even while the parent still owns that stream. Closing
the last null alias ends that holder; confirmed-stop cleanup releases survivors.
The native fixture must exercise exhaustion and stale reuse before acceptance.

For the required background sequence, the null object is opened **after fork**.
The copied FD10 CLOEXEC alias can still hold the child's original stdin after FD0
is closed. Exec therefore releases the child's last original-input alias while
retaining null at FD0; that release must not close the parent's input. A denied
exec leaves both aliases/holders unchanged. Commit uses the existing frozen
replacement transaction, then publishes the validated surviving null descriptor.
A new fork while a null descriptor is live is outside this first experiment and
must reject before publishing a child, not silently copy or discard the binding.

`exec_fds::prepare_null` implements only pure four-binding validation and CLOEXEC
planning. It grants no capability and commits no holder change. At the preparation milestone, dispatcher, bootstrap decoder, C adapter and
replacement helper still required native wiring. The live experiment below now
provides that opt-in path; existing three-binding assertions remain unchanged.
Signal dispositions and masks across background fork/exec also remain part of
actual wait-script qualification, not assumptions supplied by a null object.

See [preparation evidence](evidence/null-exec-plan-2026-09-13/README.md). Native
positive/denial/stale/read/rollback/cleanup controls are required before declaring
/dev/null usable or running the unchanged consumer wait workload successfully.


### Live null experiment and remaining background wait — 2026-09-13

The [private null route](NATIVE-CONNECTIONS.md#private-read-only-null-route--2026-09-13)
now wires the fourth binding through child authorization, open, EOF, real exec
publication and normal last-alias cleanup. It supersedes the preparation-only
implementation status above, not the remaining acceptance requirements. A private
foreground subshell tests helper status7 and untouched parent input. Raw native owner stale/reopen/exhaustion coverage is recorded below;
native prepare denial and recovery are qualified in the rollback evidence below.
The subsequent [null fault cleanup](evidence/null-stop-2026-09-14/README.md) covers
an actual pre-exec #UD at an idle request boundary; other interruption schedules
remain unqualified.

The unchanged consumer `wait.sh` was attempted with this route: its helper reached
terminal7, but dash timed out in `wait`. Pinned `jobs.c` uses WNOHANG through wait3
and then waits for SIGCHLD through sigsuspend. The current fixture has neither
child-terminal signal production nor the required atomic mask/suspend path. Preserve
that failure; the foreground null experiment is not a passing consumer wait result.

Next scope authenticated notification from the lifecycle owner and atomic temporary
mask/wait/restore behavior, including the child-exits-before-suspend race. Preserve
nonblocking wait semantics and retained status/acknowledgment. Do not fabricate
SIGCHLD, make WNOHANG block, change the consumer script, or introduce ambient process
signaling. The existing signal self-post path does not authorize a lifecycle owner
to signal another process. Review the smallest required authority/lifetime contract
before implementation; no new kernel signal interface is adopted in this change.

The subsequent [native null lifetime probes](NATIVE-CONNECTIONS.md#native-null-lifetime-probes--2026-09-13)
exercise raw owner reopening and stale/exhausted requests after the actual helper
closes FD0. They do not add a libc reopen API. The subsequent
[null rollback evidence](evidence/null-rollback-2026-09-14/README.md) qualifies native
prepare denial, public EACCES return and successful retry on a new freeze token.
[Null fault cleanup](evidence/null-stop-2026-09-14/README.md) now covers owner release
after real pre-exec #UD, parent stream preservation and SIGILL wait conversion.
Other interruption schedules remain open; background-wait integration is next.

For the next signal review, polling WNOHANG in a wrapper or adding an IPC-only
notification cannot satisfy dash's existing SIGCHLD handler and sigsuspend path.
The necessary primitive must preserve owner-scoped target identity and atomically
check pending delivery while changing the calling thread's temporary mask; the
existing self-post operation must not become ambient PID-based signaling. Review
child exit before and during suspension, stale/reused parent identity, blocked or
ignored SIGCHLD, mask restoration and interruption, and retained wait status without
implicit reaping. This is a required review checklist, not a new ABI or implemented
signal operation. Kernel source and signal behavior remain unchanged in this step.

### Child notification and atomic suspension design — 2026-09-14

Selected next experiment, not an installed ABI or runtime pass. Unchanged dash
`wait.sh` requires both real child-terminal SIGCHLD and musl `sigsuspend`; busy
polling or blocking WNOHANG cannot substitute. Aether owns kernel enforcement and
the private process dispatcher; userland owns the libc/shell consumer. Sys-init
supervision policy and package activation are unaffected.

**Authority and lifetime.** For this copied-process profile, choose a fixed SIGCHLD
post at the child's first committed terminal transition. The native copy operation
already records its actual source parent's generation and slot in `parent_pid`;
only that kernel-established relationship may select the recipient. Validate an
admitted, nonterminal parent with exactly the recorded generation before posting.
A user-supplied PID, guessed handle, signal number or RPC cannot select a target.
Reclaimed/reused parent slots must receive nothing. Preserve the link across child
exec; clear it on fresh admission. Non-copied workers have no such notification.
Normal exit, fault and supervisor stop must share the same once-per-terminal
transition rule; repeat stop/observe/reclaim must not repost. Use existing pending
bit coalescing; notification is a hint to query retained status, never a reap or
acknowledgment. Discard ignored/default-ignored SIGCHLD as the current action table
requires; installing a later handler must not resurrect a discarded occurrence.

This choice adds no remote signal syscall or arbitrary targeting authority. The
kernel records a completion event through an already established parent relation;
the user-space owner retains wait selection/status/acknowledgment policy. The
bounded four-slot BSP fixture is not a new global process table for swarm cores.
Before enabling it, test forged/wrong-role attempts and stale parent reuse against
the enforcing boundary, not just the C adapter.

**Suspension.** Gate public `rt_sigsuspend` (existing libc encoding 0x10082) on the
new opt-in single-context signal profile. Copy exactly eight bytes from a checked
user mapping, reject bad size/pointer before effects, and normalize unmaskable
bits. Unused public-call registers must not become private reserved arguments.
Retain the original mask and set the temporary mask under the existing local IF=0
serialization. Check eligible pending handlers in the same critical section that
parks the caller. A pending signal before entry must enter its handler immediately;
a later post must make the parked caller eligible without a lost wakeup.

A signal frame carries the original mask and an EINTR continuation, while the
handler runs under temporary-mask | action-mask | signal-bit. The existing frame
codec currently uses one mask for both purposes. Add a narrow preparation helper
that separates them, preserving ordinary entry and the existing frame wire layout.
Return restores the original mask through the normal checked sigreturn path;
nonlocal exits retain the existing user-controlled mask-restoration contract.
Do not leave an active suspend token after successfully publishing a handler.

Invalid handler/stack preparation must retain the pending bit, restore the original
mask, clear parked state and return a defined preparation error (EINVAL in this
bounded profile). It must not silently sleep forever or consume an undelivered
signal. A discarded/blocked occurrence does not make sigsuspend return EINTR.
Eligible default termination uses the existing terminal outcome and clears parked
bookkeeping; it must not masquerade as handler return or EINTR. Unsupported default
stop/continue behavior must remain an explicit unsupported-profile outcome, not a
successful no-op. Posting while a parent is copy-frozen may retain a pending bit
but must never unfreeze it or satisfy a copy token. Termination clears parked
bookkeeping before reclaim. Fork/exec cannot inherit an
active suspension; the single-context caller cannot issue them while parked.
The scheduler must skip suspended contexts without treating them as frozen-copy
contexts or fabricating futex addresses. Idle/timer selection must account for
suspension without panicking when no user context is runnable. No timeout or
spurious wakeup may report successful signal delivery.

**Qualification sequence.** First test separate saved/active masks and atomic
frame failure as host preparation. Then wire kernel terminal posting and suspend
scheduling together with a small real libc witness: child exits before entry and
after parking; blocked and ignored posts; old parent generation; repeated terminal
observation; handler return and failure; stop/reclaim while parked. Require exact
state/status and negative controls for dropped post, mask confusion and premature
wake. Only then run unchanged background `wait.sh`, all affected connections and
command-runner signal cases, and scheduler regressions on frozen sources. Consumer
replay/installed SDK adoption remain separate. No current command or pin changes.

**Simplicity review (SE-01–05).** Prefer terminal-derived notification over adding
another owner-post RPC with target selection, duplicate tracking and recovery.
A user-space polling adapter cannot atomically unblock the kernel signal mask and
sleep; putting that primitive in the kernel is necessary. Reuse pending bits,
validated parent provenance, signal frames and status retention. Keep the new state
to one saved mask plus parked indication per eligible context; no event service,
process-group signaling or generalized scheduler framework is justified. No old
runtime path can yet be removed. The first implementation must measure actual
storage/code cost and exercise each cleanup boundary before claiming integration.

[Preparation evidence](evidence/suspend-frame-2026-09-14/README.md) covers only the
codec step; the lifecycle/scheduler behavior above remains to be implemented.

### First native background-wait integration — 2026-09-14

The selected paths are now implemented behind `-Dnative-signal-suspend=true`,
requiring public signal actions. Public suspension additionally rejects the
supervisor, non-connections and multi-context/thread profiles with ENOSYS.
Default builds retain previous behavior. The connections harness enables the flag
for `copy-inherit-public-fork-wait-exec-dispatch-prefork-dash-command-null-wait`
and the later `copy-inherit-public-fork-wait-suspend-*` ordering fixtures.
Its `-disabled` companion uses identical clients with the flag absent.

The kernel stores one optional original mask per opt-in domain. `suspendOperation`
validates size8 and every user byte before replacing the execution mask;
`resumeSuspended` prepares the checked two-mask frame with EINTR continuation,
then consumes the pending occurrence and clears parked state. Scheduler rotation
checks eligible suspended domains, skips still-parked ones and preserves the
existing idle fallback. Frozen and terminal domains are skipped first. Normal
return and preparation failure restore the appropriate mask through the documented
paths; stop clears parked state before reclaim. There is no retained user pointer.

Normal terminal publication and the first supervisor stop call `notifyParent`
after recording termination and stopping contexts. It posts fixed SIGCHLD only to
an admitted, live, exact-generation kernel-recorded copied parent. Repeated stop
skips the transition and cannot repost. Self-post remains self-only. Notification
does not alter retained status, acknowledge wait, close descriptors or reap tasks.

The initial opt-in route is **handler-only suspension**: eligible unsupported
non-handler default effects restore the original mask and return ENOTSUP while
retaining their pending occurrence. Default termination during suspension remains
unimplemented against the broader selected contract. Ignored/default-ignored
occurrences are discarded and do not report handler completion. This is a scoped
experimental limitation, not complete POSIX signal support or an approved waiver.

The C startup probe validates bad size/pointer rejection, posts blocked SIGCHLD,
then uses real musl sigsuspend. Its handler checks the temporary mask; return checks
EINTR and restoration of the original SIGCHLD/USR1 mask. It restores the original
action and empty mask before dash starts. Missing routing yields raw parent233
and owner1950, with no successful reclaim. The generated C script literal comes
from the pinned `user/native-command/dash-wait-inputs/wait.sh` bytes unchanged.
The owner checks exactly `wait ok\n`, helper7/parent0/backend17 in both generations
and six reclaims. [Native evidence](evidence/native-suspend-2026-09-14/README.md)
records the actual run and its qualification scope.

This demonstrates pending-before-entry plus the real background consumer workload;
it does not force terminal delivery to occur strictly after parking. Deterministic
before/after-park races, ignored/blocked notification, stale parent replacement,
repeat-terminal and parked-stop controls, default termination, invalid handler
recovery, nested delivery and independent consumer/SDK adoption remain work before
full acceptance. Existing signal-frame bytes and released pins are unchanged.

### Deterministic suspend ordering review — 2026-09-14

Requirement: prove real copied-child SIGCHLD on both sides of atomic suspension.
The private connections supervisor holds the first WNOHANG reply until child
termination for the before-entry case. For the after-park case it replies normally
and withholds remaining child I/O until a parked parent is observed. No sleeps or
probabilistic scheduling constitute ordering evidence. Parent handler count must
be exactly one, handler mask temporary, return EINTR, original mask restored;
ordinary wait must still collect the retained child status once, across two
complete generations. An omitted-park client must fail the supervisor's ordering
check rather than accidentally qualify through a later wait.

The opt-in suspension profile adds only R9=0/1 parked observation to the existing
supervisor-only, generation-checked lifecycle query 0x20001. Existing result,
ready/yield/kind outputs and disabled profiles are unchanged. This grants no post,
resume, pointer, mapping or new object authority; inspection does not select or
wake a task. A terminal or reclaimed task cannot remain parked. This fixture-only
output is not a released SDK contract. Single-core IF=0 serializes the snapshot.

Simpler alternative: infer ordering from the successful dash script or add a
delay. Neither proves that the parent parked before child termination. One
read-only bit reuses existing authority and lets user-space own the rendezvous;
no scheduling policy, new syscall or mutable counter is needed. No obsolete path
can yet be removed. Scope is the existing bounded connections profile; sys-init,
userland policy, package boundaries and released pins remain unchanged. No new
unsafe memory access, allocation, dependency or retained user pointer is added.

Selection: host/workflow/offline checks, focused before/after/omitted-park and
unchanged dash cases, complete connections suite and scheduler regressions on
frozen sources; retain failed attempts. Independent consumer review and matched
command-runner evidence remain required before adoption. Reference and STATE
will record actual results and remaining cleanup gaps.

[Ordering evidence](evidence/suspend-order-2026-09-14/README.md) now qualifies both
forced races and the omitted-park rejection. All 306 connections cases, five
focused cases, seven scheduler regressions and host/offline checks pass. The parent
uses real public sigaction plus musl sigsuspend; the ordinary startup facade is
explicitly disabled for these fixtures. No earlier profile is switched to this
mode. Native lifecycle cleanup controls and independent acceptance remain open.

### Suspend lifecycle cleanup review — 2026-09-14

Requirement: stop a confirmed parked parent without resuming its saved frame;
ignored or temporarily blocked SIGCHLD must not complete suspension; repeated
stop of an already-exited child must neither change retained status nor post again.
Use the existing single-core copied-process fixture and read-only parked query.
The stop/ignore/block cases must observe terminal143/kind3, cleared parked state,
parent-channel EOF, unchanged child72/kind1 and backend17, then reclaim all three
slots in each of two generations. A skipped stop must reject owner2331 before
child completion. For repeated child stop, hold the parent's first post-handler
invalid-wait reply, stop the already-terminal child twice, check retained72/kind1,
then release ECHILD; explicit self-poll must not invoke the parent handler again.

No kernel implementation, ABI, authority, quota, SDK or sibling change is planned.
The supervisor owns all existing stop/reclaim handles. The checked parked query
now accepts an explicit expected lifecycle result so terminal cleanup can be
observed without relaxing its oracle. No new pointers or persistent state are
introduced; caller-owned stack outputs retain the existing synchronous assembly
boundary. Bounded yields establish continued parking, not a timing guarantee.

The simpler alternative is to infer cleanup from ordinary exit and two-generation
reuse. It does not exercise a stopped saved suspend frame or a late duplicate
terminal request. Reuse the fixture and retained records rather than adding a
service, remote signal API or kernel fault-injection flag. No obsolete production
path is removed. This is scoped lifecycle verification, not general POSIX or
consumer acceptance. Stale-parent replacement before old-child termination and
bad-handler recovery remain distinct tests.

Select all suspend family and unchanged dash wait controls, host/offline/format
checks, and the complete connections suite on frozen sources. No scheduler code
changes are planned; the preceding qualified scheduler evidence remains scoped to
unchanged kernel bytes. Preserve failed attempts and update STATE, workflow and
this reference with actual coverage. Independent consumer review and matched
command-runner qualification remain outstanding.

The repeated-stop probe also gets a client-side semantic rejection control: an
explicit extra self-post after the held ECHILD reply must produce raw parent236 /
owner1950, with no reclaims. Keep the handler installed until that poll; restoring
DFL before it would discard a broken duplicate and invalidate the oracle. Existing
supervisor stop does not print a `NATIVE terminal` line: query143/kind3 is checked
inside the owner, while the serial inventory contains child/backend exits only.

The next stale-parent test can preserve the six-reclaim bound without an API or
quota change: after stopping/reclaiming parent generation1, launch its replacement
in slot0 before allowing old child1 to finish. Replacement2 can install/block its
SIGCHLD handler and acknowledge a raw pre-bootstrap rendezvous on its own granted
channels. Complete old child1 and backend1, then release replacement2 to poll for
an incorrectly delivered old notification before its ordinary startup. Retain
that connection into iteration2, launch backend2 and perform the normal fork/
suspend/wait cycle with child2. Reclaims are parent1/child1/backend1 and then
parent2/child2/backend2. This is a prospective schedule only; no replacement
before old-child termination is qualified by the current stop/ignore/block cases.

[Native cleanup evidence](evidence/suspend-cleanup-2026-09-14/README.md) now passes
all eleven focused and 312 connections cases, host/offline and format checks.
Parked stop, bounded ignored/blocked posting, repeated terminal stop and both
semantic rejection controls qualify across two generations. Stale-parent
replacement and bad-handler recovery remain unqualified; ignored/blocked cases
do not establish eventual unblocking. No kernel or released-interface change
was needed. Independent consumer adoption remains separate.

### Stale-parent replacement review — 2026-09-14

Implement the prospective two-generation schedule above in the existing suspend
fixture. Replacement2 must install and block SIGCHLD before acknowledging a
canonical 32-byte pre-bootstrap readiness record (op86, generation2, zero tail).
Only then may child1 exit. After reclaiming child1/backend1, the owner sends op87;
replacement2 unblocks, polls, requires zero handler calls, restores its prior
action and empty mask, and acknowledges op88 before normal startup. Each record
uses the replacement's existing granted channels, not names or ambient authority.
The owner retains one Connection between iterations; no new object, kernel state,
quota, signal-post API, syscall or SDK contract is added.

Require cleared parking, old-parent request EOF and reclaim before replacement
launch, old query/stop handles rejected even after slot reuse, and child1 live
when replacement readiness is confirmed. Then require replacement2's own child2
notification to wake it once and ordinary wait/stream cleanup to complete. Six
reclaims remain exact. A client-injected post at the post-exit poll must reject
raw replacement237/owner1950 with exactly three prior reclaims; retaining the
handler through that poll makes a false no-notification result detectable.

Simpler alternative: rely on ordinary sequential reuse. It cannot distinguish
an old child exiting after parent-slot replacement. The bounded rendezvous reuses
existing channels and the same two iterations; no scheduling mechanism or extra
service is justified. No obsolete production path can be removed yet. Stack
buffers remain owned through synchronous copies, readiness never lends a pointer,
and single-core owner sequencing establishes order without timing assumptions.

Select all suspend-family controls plus unchanged dash wait, the complete
connections suite, host/offline and scoped formatting on frozen sources. Preserve
failures and compare older artifacts. Kernel code is unchanged; prior scheduler
coverage remains explicitly prior. Record results in STATE and the references;
independent consumer acceptance, bad-handler recovery and broader signal effects
remain separate work. Released pins and sibling repositories remain untouched.

Pre-bootstrap mask changes use the existing raw 0x1000e size8 operation: the
fixture's sigprocmask facade intentionally rejects until startup_ready, and this
rendezvous precedes descriptor bootstrap. Do not fake startup_ready or weaken
that facade. Public libc sigaction and the original mask/handler checks remain.

For the next failure-recovery test, the current memory grant excludes immutable
image and stack mappings from protect/unmap, so an installed handler's RX mapping
cannot be revoked through that grant. A failing suspend-frame preparation can
instead be forced with an insufficient user stack in a bounded assembly wrapper:
require EINVAL, original mask and pending occurrence preserved, then retry from a
valid stack and require one handler/EINTR. This is a prospective test direction,
not native failure-recovery evidence or permission to weaken immutable mappings.

[Stale-parent evidence](evidence/suspend-stale-2026-09-14/README.md) now qualifies
the replacement-before-old-child-exit schedule, zero old deliveries, successful
new-child wake and the injected-post rejection. All thirteen focused and 314
connections cases, host/offline and format checks pass. The early failed attempt
is preserved. This closes the bounded stale-parent test, not independent consumer
adoption or the remaining frame/default/nested signal behavior.

### Suspend-frame failure recovery review — 2026-09-14

Use the existing pending-before-entry owner schedule: a real child exits before
its parent enters suspension. The parent attempts entry on three insufficient
stack positions (base+128, +848 and +856), requiring EINVAL, zero handler calls,
original SIGCHLD/TRAP mask and unchanged 1024-byte bottom-stack canary after each.
It then uses real musl sigsuspend on the normal stack and requires one handler,
EINTR, correct masks and the existing retained wait/cleanup checks in two generations.
No new post occurs between rejection and retry, so success witnesses preservation
of the original pending notification. A valid-stack control deliberately omits
the stack switch and must reject raw parent238/owner1950, zero reclaims, with the
child72 terminal already recorded.

A naked x86_64 wrapper retains its real RSP in R11, switches RSP only for the
existing raw size8 suspend operation, restores RSP on return and then returns
normally. It calls no C code and touches no user stack while on the insufficient
stack. The interrupt path already saves/restores R11. All mask and canary buffers
are in mapped, owned stack storage; no pointer is retained across completion.
The canary uses unused bottom-stack bytes, not another domain or a new mapping.
These fixtures remain single-context BSP experiments. No kernel, ABI, quota,
SDK, dependency, released pin or sibling change is planned.

Simpler alternative: host-only placement tests already reject these boundaries,
but cannot prove the native syscall restores the original mask and preserves
pending state through recovery. Reuse the checked wrapper idiom from existing
signal-return tests and the before-entry fixture, rather than new mapping rights
or a kernel failure-injection flag. No obsolete production path is removed.
Select the complete suspend family/unchanged dash tests, full connections suite,
host/offline and scoped formatting on frozen sources. Preserve failed attempts;
record coverage and compare older artifacts. Prior scheduler coverage remains
prior because kernel sources are unchanged. This is failed-frame recovery, not
revocation of immutable handler code or full signal/consumer acceptance.

After focused recovery passes, also run the outstanding complete command-runner
suite with the same frozen sources, SDK and tools lock. This supplies matching
startup/syntax/runner regression coverage for a bounded consumer handoff; it does
not implement default termination or nested suspension, change released pins, or
constitute independent owner acceptance. Keep separate results, source identity
checks and archives for the two suites.

[Recovery evidence](evidence/suspend-recovery-2026-09-14/README.md) passes all three
stack rejections and the retained-notification retry, with the valid-stack control.
All fifteen focused, 316 connections and host/offline checks pass. The matching
runner hit its 1800-second deadline after starting 429/431 cases and remains
incomplete; preserve that attempt and rerun with adequate overall time. No full
matching-suite or independent acceptance claim is made.

[Matching runner retry and bounded replay intake](evidence/suspend-runner-2026-09-14/README.md)
completes all 431 command-runner cases on the exact 265 sources/SDK/tools of the
316-case recovery connections run. Its restored support/source host check passes.
The earlier timeout is preserved. This supersedes the unmatched-runner status,
with independent acceptance and broader signal semantics still open.

### Unchanged failed-exec owner review — 2026-09-14

Requirement: consume userland's unchanged DASH-failed-exec script and distinguish
an absent executable (ENOENT, dash127) from an owner-backed object without execute
authority (EACCES, dash126). Actual dash must collect both children, preserve its
state and print exactly `exec errors ok\n`, then exit0. This is a selected private
producer experiment, not implemented behavior or installed SDK acceptance.
Userland owns the script/acceptance and UL-081 boundary; Aether owns the existing
private execution adapter and capability enforcement. No sys-init/package policy
or shared ABI is assigned here. Foundations O-01–05, I-01/03–06, E-01–08 and the
scoped Distribution PX-01–03 and simplicity process apply.

Source inspection found four prerequisite changes. The initial exec allow-list
currently classifies both names as absent. `deny_null` proves rejected image
replacement using invalid image token0xffff; that alone cannot establish a present
non-executable object. The dispatch loop denies ordinary child I/O until successful
replacement, but failed exec needs diagnostics and descriptor closure from the
unchanged child image. Finally, its reusable-child branch requires successful
replacement before reaping and expects three successful commands. Reusing that
branch without changing its coherent admission/collection contract would be wrong.

Select a bounded extension of the current owner, not a new filesystem/loader.
Provide an immutable, inert object in the owner's private fixture for
`/inputs/not-executable`, with no delegated executable image capability. Pin its
bytes with the experiment before execution. `/inputs/missing` has no object.
Paths only select this scoped namespace; they do not confer authority. Both names
must reach the owner over the caller's existing authenticated connection so that
absence, presence and attempted execution are independently observable. Neither
raw errno selection in the C allow-list nor the invalid-token probe is sufficient.

Reuse the existing bounded exec request layout (name32, arguments272, mask32,
descriptors64) and freeze/inspect/thaw sequence. Validate arguments, captured mask,
descriptor holders and exact child identity before replying. Query the original
image-commit state before/after denial; it must remain unchanged, with no image
commit pending. Deny at the owner when no execute grant exists, without attempting
replacement with a made-up token. Restore the caller's original mask on every
failure. Read-only validation must leave image, descriptors, offsets, references
and signal disposition intact. Child diagnostics and close operations remain
capability-checked even though image replacement did not happen. Success text
must originate from dash; the adapter never creates shell statuses127/126.

Use the existing single live copied-child slot sequentially: collect and reclaim
child1 before admitting child2, retain the parent's three backend references, then
close/reclaim the parent and backend. Track attempted route and observed terminal
status separately from replacement success. Do not mark a denied exec as executed
to satisfy the old cleanup guard. Preserve all older successful-exec paths and
exact stale-handle/collection behavior; no ambient handles, descriptor widening,
new kernel operation or increased generation quota is selected.

The expected initial native trace is child slot2 generation1 exit127, child slot2
generation2 exit126, parent slot0 generation1 exit0, backend slot1 generation1
exit17, with four reclaims and owner100. This is a prospective oracle to confirm
with actual native execution, not inferred acceptance from the Linux reference.
The reference trace contains two vfork/exec attempts; the native experiment must
measure and retain its own admissions and transcripts before final qualification.

The current kernel rejects a fourth admission to one slot. Therefore two complete
script lifetimes in one boot cannot be copied from the existing one-child fixture
without exceeding its three-generation bound. Select two fresh VM runs of this
same script, each exercising generation1→2 reuse and four reclaims. This does
not qualify cross-script reuse in one VM. Keep that limit visible in the consumer
handoff instead of silently increasing quotas or claiming eight same-VM reclaims.

Forbidden outcomes: missing and denied paths both returning127; status substitution;
false success/output; skipped second attempt; authority inferred from mode bits;
child I/O denied merely because exec failed; premature reuse, stale references,
partial state mutation, unexpected ENOTSUP or a watchdog counted as rejection.
Keep stderr bounded by the existing256-byte backend and capture its bytes without
requiring Linux wording. Preserve emergency/boot markers and existing output rules;
read EXPERIENCE before changing the actual diagnostic path.

Selection before implementation: pin script/manifest/stdout/proposal and source
inspection; then one focused real-script prototype to establish native admission,
diagnostic and rollback behavior. Add independent missing-as-denied and
denied-as-missing controls, a skipped second owner request, false success/output,
and stale/uncollected-child rejection. Assign and check exact owner/terminal
outcomes before qualifying controls. Run both fresh positive lifetimes, host tests
and complete affected connections/command-runner suites on frozen final bytes,
sequentially with a selected3600-second outer deadline and unchanged per-case
watchdogs. Report timing against the1800-second review ceiling. Retain every
attempt. Changed scheduler/kernel code would additionally require scheduler
regression; none is selected. Record replay inputs, concrete limits and consumer
acceptance separately. Update workflow coverage when adding executable profiles.

Simplicity: returning a different errno in the client is smaller but fails the
owner-authority and cleanup witness. Reuse the current owner-backed transaction
and sequential child admission rather than add a synthetic filesystem service or
increase kernel quotas. Clarify denial versus replacement completion in the
existing dispatch responsibility. No consumed path can be removed yet; broad
extraction, arbitrary paths and general process/FS services remain deferred.

Prototype completion review, before the next change: the first native run now
observes the intended127/126/0/17 trace and four real reclaims, then the legacy
kernel fixture verdict rejects because every copy fixture expects six reclaims.
Select `native-exec-denial` as an explicit positive experiment flag requiring
copy, exec, local runner and single-context signal-copy prerequisites. Its terminal
verdict requires exactly four reclaims and slot generations1/1/2; every other
profile retains its prior verdict. This changes only fixture completion validation,
not operation authority, allocations, quotas or a public ABI. Do not pad the run
with unrelated task admissions. Add the flag to the reviewed positive-option
inventory and require disabled-flag rejection evidence plus host/target checks.

[Native failed-exec qualification](evidence/failed-exec-native-2026-09-14/README.md)
now passes the selected unchanged script and five semantic controls. The owner
retains copied descriptor references after failed replacement; it validates exact
environment membership without imposing an unsupported ordering. Full322/431
matching suites and host checks pass; the explicit completion flag and limits
remain as reviewed above. Independent consumer/SDK acceptance remains open.

### Writable shell descriptor owner review — 2026-09-14

Requirement: run the unchanged consumer fd-leak-control, then redirection and
permission-denied redirection. [Pinned intake](evidence/writable-shell-intake-2026-09-14/README.md)
captures scripts, helper, manifest, output and reviewed producer sources. This is
a selected private experiment, not an implemented open API or consumer acceptance.
Aether owns this conformance adapter and native enforcement; userland retains
public SDK/facade and workload acceptance. Sys-init and package policy are unaffected.
O-01–05, I-01/03–06, E-01–08 and the proposed PX-01–03/DS-01/05 apply.

The leak workload intentionally keeps FD9 open across a real helper exec. The
unchanged helper returns95 when any descriptor3–63 is open; dash must then exit22
with empty stdout. A mere parent22 is insufficient: require successful owner-backed
creation, FD9 without CLOEXEC in the committed child table, actual helper95 and
cleanup. Existing startup FD10 remains CLOEXEC and must disappear. Redirection
requires FD3/4 aliases to share one offset, producing exactly AB; closing both
aliases retains file contents, and a fresh read-only open starts at offset0.
The unchanged helper copy must read those bytes through inherited stdin and reach
EOF. Denied redirection must leave /inputs/denied unchanged, never print wrong,
and produce denied ok followed by newline through the original stdout.

Existing coverage and incompatibilities:

- The standalone writable file service already provides one64-byte scratch file,
  two open slots, three nonwrapping generations per slot, create/open/read/write/
  truncate/close, explicit offsets and a delegated write root. It is not currently
  the stream backend used by the fork/exec fixture.
- The connections owner currently tracks three stream descriptions and two holders;
  the stream backend uses a different wire operation layout. The optional null
  binding3 and pipe bindings3/4 are different profiles, not reusable file grants.
  Relabelling either as a writable file would confuse authority and lifetime.
- The shell, backend and child already occupy the three worker slots. Adding a
  fourth service would require unrelated lifecycle/resource changes. Select the
  existing backend process to own scratch bytes as well as standard-stream bytes;
  retain the supervisor's existing responsibility for open-description offsets,
  holder accounting and authenticated child connections. Reuse the bounded file
  logic through a scoped integration, preserving existing backend modes. Do not
  create a second mutable copy of file contents in the supervisor.

Selected bounds and semantics for implementation:

1. Opt-in bootstrap advertises a distinct scratch-root grant on the authenticated
   owner connection. Lookup accepts the fixture /scratch/leak or /scratch/data,
   never arbitrary host paths. A fresh backend begins with no scratch file. One
   file64bytes, at most two open descriptions, existing16 descriptor slots and
   existing worker/generation bounds suffice; report exhaustion explicitly.
2. Support read-only open and write-only create/truncate plus CLOEXEC as required
   by dash. No append, directories, unlink, seek or general pathname resolver is
   implied. Unsupported flags reject before mutation. Require a valid root before
   lookup; unknown names return ENOENT, denied scope returns EACCES. No path grants
   access and a writable backing token never widens the client's declared rights.
3. Validate canonical records and reserve descriptor/description capacity before
   create/truncate. Do not truncate on failed FD allocation. Define exact versioned
   bootstrap/request/reply bytes before code; no operation numbers are allocated
   by this review. Existing three-binding consumers must still reject extra entries.
4. Duplication and fork share the owner-held open description and offset; a separate
   open receives an independent offset. Exec retains non-CLOEXEC descriptions,
   drops CLOEXEC aliases, and rebinds references to the new authenticated child.
   Denied exec preserves all original aliases, flags, offsets and holders. Closing
   an alias is distinct from releasing the last holder and from deleting contents.
5. Validate connection, generation, object kind and read/write rights at the owner
   before backend effects. No client-supplied offset overrides shared-position
   accounting. Preserve bounded16-byte transport chunks. Invalid requests leave
   bytes, positions and holders unchanged. Ambiguous backend replies poison the
   connection; do not retry an operation that may have executed.
6. Confirm terminal state before stop cleanup; release all surviving descriptions
   once and invalidate stale references before replacement. New backend lifetime
   starts with zeroed scratch, while closing and reopening within one lifetime
   retains data. No durable storage or OpenZFS claim follows from these RAM files.

Test selection: first qualify root/open/read/write/close and alias offsets in the
existing connections harness, then the exact consumer leak script and redirection.
Require independent backend readback, exact child/parent terminals and complete
reclaims. Controls must detect omitted create, dropped FD9, wrong CLOEXEC inheritance,
independent duplicate offsets, lost reopen data, forged/stale references, denied
writes, exhaustion-induced truncation, ambiguous reply replay and retained holders.
Existing null/pipe/exec/failure profiles must remain covered. Final changed profiles
need the complete connections suite and matching command-runner on frozen inputs,
plus host checks; scheduler regressions only if scheduler/kernel/build changes
require them. Public SDK integration and independent consumer acceptance remain
separate. Every failed attempt is retained with its semantic result.

Simplicity review (SE-01–05): a fake open sufficient for fcntl is smaller but cannot
prove writable-file or shared-offset behavior. Choose bounded backend integration
using the established file operations rather than another service or a general VFS.
Borrow the open-description/descriptor distinction for precisely the alias and
inheritance requirement; defer general namespace and persistent-engine machinery.
No obsolete runtime path can be removed yet because old fixtures remain consumers.
The added cost is one narrow advertised root and bounded file-description lifetime
handling; no new kernel syscall, dependency, dynamic allocation or quota increase
is selected. Implementation must record actual stack/image cost and new pointer/
FFI obligations; existing fixed-record copy/mask guards remain mandatory. This
review introduces no unsafe code or runtime output. Update this reference, STATE
and the existing workflow inventory when executable profiles are added.

#### Scratch backend records and first implementation slice

The first code slice is the transport-independent backend state used by the
planned integration. It remains unconnected to the running stream backend until
native transport qualification. Its two open handles represent backend descriptions;
the authenticated connections owner will retain alias/holder/shared-offset state.
This deliberately does not implement shell open or duplicate that owner state.

The private32-byte backend record is eight little-endian u32 words: operation at0,
reference at4, explicit byte offset at8, mode/count at12, payload at16. Operation1
opens with offset0, mode1 (read only) or14 (write/create/truncate), and canonical
NUL-padded exact /scratch/leak or /scratch/data. Other modes return ENOTSUP. Root
is0xfb000000 | backend generation (1–255). Success returns status0, handle at4 and
length at8, other bytes zero. Handle is0xfa000000 | generation<<16 | sequence<<8 |
(slot+1); two slots, each sequence1–3, never wrapped. Backend generations are
assigned by the caller from the actual lifetime, never by an untrusted request.
Names distinguish two possible names for the single file; creating another name
while one exists returns ENOSPC. Both names start absent in a new instance.

Operations2/3/4 read/close/write using the open handle. Close requires remaining
words/payload zero. Read count<=16 and zero payload; write count<=16 and zero
padding beyond count. Read past end returns EOF; writes may zero-fill holes but
must fit64bytes, including zero-length offset bounds. Reply status is count or
negative errno, read bytes at16; unused bytes zero. Read-only/write-only rights
are enforced here, independently of the future facade. Allocation is checked
before truncation; closing retains contents. Bad references return EBADF (open
with bad root EACCES), malformed records EINVAL, slot exhaustion ENFILE, and
missing read opens ENOENT. Unsupported operations return ENOTSUP. Rejected
requests leave complete backend state unchanged.

No raw pointer, FFI, allocation, new dependency or concurrent access is introduced.
Rust exclusive mutable access serializes each transition; payload copies use fixed
checked spans. The backend does not authenticate arbitrary callers: the future
integration must expose it only on the delegated owner channel. Root/handle tokens
are meaningful only inside that authenticated namespace. Host transition tests and
no_std target compilation qualify this slice; native suites and real dash remain
required when wiring it into an executable profile. Tests cover byte preservation,
rights, canonical records, full allocation before truncation, generation retirement,
foreign lifetime and fresh-instance zeroing. Use Rust1.98 edition2024 formatting.

The first slice now has [host implementation evidence](evidence/scratch-backend-2026-09-14/README.md):
six debug/optimized transition tests, two deliberate semantic failures and no_std
x86_64 object compilation. Run `python3 -m unittest discover -s tests -p
"test_scratch_backend.py" -v` or the complete `zig build test` command. The module
is not imported by the running service yet; shared offsets, holder transfer,
transport failure and native shell workload qualification remain open.

#### Native scratch transport selection

Next slice: opt-in `scratch_backend` joins scratch and streams in the same backend
process. Before its existing hello, the authenticated supervisor sends32 bytes:
AESCR001 at0, actual backend generation at8, remaining bytes zero. Valid generations
are1–255. Hello retains stream handles at4/8/12 and advertises scratch root at16,
generation at20 and AESCR001 at24. Old modes retain the original zero tail and no
initial receive. The owner supplies the generation from its launched connection;
the bootstrap cannot be used as an application-controlled epoch reset.

Only scratch-root/object reference namespaces (top byte fb/fa) route to the new
component. The complete reference is then checked by Scratch; stream handles keep
their current route. End-of-input succeeds only after both streams and scratch
handles are closed. One native preflight will create/write/close/reopen/read through
real IPC, deny wrong rights/root and stale handles, and verify fresh namespace on
the second backend lifetime. It then runs the unchanged copy/inheritance fixture.
An omitted write control must fail exact readback; an old-epoch bootstrap control
must fail the second hello. Neither timeout nor arbitrary panic counts. No shell
FD or public API changes occur in this slice; the backend preflight cannot stand
in for unchanged dash workload acceptance. Full connections coverage and host
checks are selected; matching runner qualification remains required before the
combined producer handoff. Existing Rust formatting only in touched modules.

The [native transport packet](evidence/scratch-native-2026-09-14/README.md) now
qualifies `copy-inherit-scratch`, `copy-inherit-scratch-drop` and
`copy-inherit-scratch-epoch` through the existing complete connections invocation
in NATIVE-CONNECTIONS. The positive finishes source71/child72/backend17 twice
and six reclaims. Dropped-write rejects2502 with zero reclaims; stale epoch
rejects2501 after the first three reclaims. All325 connections cases pass. This
is backend IPC qualification; shared shell offsets/descriptor inheritance and
a matching command-runner suite remain required before the next producer handoff.

#### Scratch open-description ownership

The next prerequisite is a two-description owner component, before C/dash wiring.
It stores backend handle, rights, shared offset and one holder per authenticated
parent/child connection; local FD aliases remain the existing adapter's job. This
is not another FD table or backend byte store. A duplicate uses the same reference;
a separate open gets a separate description/offset. Fork retains descriptions
for the child with distinct references. Final close forwards once; another live
holder prevents backend close. The caller must authenticate connection identity
and only issue a holder close after its last local alias disappears.

Implement synchronous exchanges through a supplied bounded transport callback.
Missing, malformed or impossible replies poison the whole owner; no further
backend call or retry is allowed. Confirmed-stop cleanup after poison remains
outside this component and must be wired at native integration. Reserve one of
two local slots and a nonwrapping sequence before forwarding create/truncate.
A rejected open cannot mutate local state; an uncertain one poisons it rather
than guessing whether the backend created a file. Backend errors have canonical
zero tails. Offsets advance only by a valid acknowledged count. Reject wrong
rights/reference before calling transport. No arbitrary caller offset is accepted.

Owner-local references use fc in the top byte, owner lifetime at16, connection
lifetime at8, open sequence1–6 at4, holder index at3, and slot+1 in the low bits.
These are private connection-scoped tokens, not kernel capabilities or a published
ABI. Owner lifetime1–255 is trusted bootstrap data; child lifetimes advance without
wrap and may change only after all prior child holders are gone. Fork publication
is owner-only and validates an exact set of currently held parent references before
changing any holder. It does not grant native process admission or replace frozen
FD-table validation. A failed fork publishes nothing in this component.

Tests first compose the owner with the existing Scratch backend on the host:
shared parent/child offset, independent reopen, sibling-safe close, stale child
replacement, allocation-before-truncate, denied authority, and no transport replay
after uncertain effects. Include deliberate broken offset/last-holder controls.
No unsafe/FFI, allocator, dependency, kernel operation or quota increase. Use the
existing Rust1.98 edition2024/no_std test pattern and AT-HOST inventory. This pure
component does not change any running native profile, so target qualification is
still required when wiring it in. Existing null/pipe meanings remain unchanged.
SE-01–05: reuse backend bytes and existing local alias tracking; a single offset
per FD is simpler but breaks dup/fork. No old path can yet be removed because its
consumers remain active. This small owner centralizes the currently required
lifetime decisions without introducing a general filesystem or VFS layer.

The [owner component packet](evidence/scratch-owner-2026-09-14/README.md) records
host composition and no_std compilation of these rules. Run `python3 -m unittest
discover -s tests -p "test_scratch_owner.py" -v` or `zig build test`. Actual C
alias counting, CLOEXEC filtering, native fork admission and transport integration
are not qualified by these tests; no new shell workload result is claimed.

#### Native open-description owner composition

Select a new `scratch_owner_probe` within the existing scratch backend profile.
After validating its hello, the supervisor composes Owner with real bounded IPC.
It writes A as the parent holder, retains a distinct child-holder reference,
closes the parent, writes B as the child, closes it, then opens two independent
read descriptions and checks A/B versus AB and EOF. Denied rights and stale
references must fail before transport. Both reads close before the original
copy fixture proceeds; repeat in the second backend lifetime, with six reclaims.
Holder transitions here are directed by the trusted supervisor; this does not
claim that the application FD table or real fork/exec yet carries scratch files.

Two opt-in implementation controls omit offset advancement or prematurely close
on the first holder release. Both must fail supervisor2503 with zero reclaims,
before any copy-fixture completion, rather than time out. No new transport ABI,
backend byte store, worker, unsafe pointer boundary or public flag is introduced.
The bounded callback borrows one stack request through synchronous send/receive;
no borrowed record survives it. Existing transport failure exits the fixture;
poison/confirmed-stop recovery integration remains required before application use.
Run the three focused profiles, host tests and full connections suite on frozen
sources; matching runner and real dash qualification remain separate handoff gates.

The first native link exceeded the legacy two-page owner code budget. Retain that
failed attempt and select the existing four-page owner envelope/linker only for
`scratch_owner_probe`, as already used by larger shell owners. No kernel limit
changes. Measure the final owner bytes and retain the four-page bound check; this
is a declared resource cost of composing description policy with the copy fixture.

[Native owner composition evidence](evidence/scratch-owner-native-2026-09-14/README.md)
now passes the three focused cases and all328 connections cases. The positive
owner is9752bytes, within the existing16384-byte envelope; offset control9752bytes
and early-close control9720bytes. Host checks pass. The second failed attempt
linked but rejected949 because the supervisor still expected ABI9; the opt-in
profile now explicitly expects existing ABI17. Both failed attempts are retained.
Next integrate actual C descriptors and fork/exec snapshots; these owner-directed
holder tests are not application inheritance or real dash redirection evidence.

#### Scratch descriptor adapter and owner gateway

The next slice connects private descriptor operations to the tested Owner through
a canonical gateway; native fork/exec table publication is still separate. The
parent/child selector is supplied by an authenticated owner connection, never
read from a request. `Owner::root(peer)` returns fd in the high byte, owner epoch
at16, peer epoch at8, and peer+1 in the low byte. No root exists for an unadmitted
peer. The opt-in32-byte AESFD001 grant contains root at8, peer epoch at12, first
binding3 at16, count2 at20 and zero tail. The adapter checks the epoch against its
current native generation, validates the shape, and retains the root privately.

Open request32bytes: op6/root/zero/mode, then canonical NUL-padded path. Mode1 is
read-only; mode14 is write/create/truncate. Exact C flags are O_RDONLY or
O_WRONLY|O_CREAT|O_TRUNC, optionally O_CLOEXEC. Unsupported modes reject before
transport. The adapter reserves local FD capacity and checks for an unused file
binding before sending. Owner reserves description capacity before backend effects.
A successful reply is0/reference/binding/zero with zero payload. Binding3/4 must
match reference slot1/2; owner/peer epoch and holder bits must match the grant.
Unknown, malformed or conflicting replies poison the adapter. Errors have a zero
tail and an explicit bounded errno set. No retry follows an uncertain reply.

I/O uses existing client operations1/2/3 for read/write/close, reference at4,
binding at8 and count at12. Gateway validates binding/reference agreement and
canonical payload before converting to backend operations. Caller offsets are
never accepted. Only the last local FD alias closes its owner holder, preserving
existing startup_users accounting. C mask guards serialize these private one-context
state transitions; no raw pointer is retained. The shim accepts only valid C-string
pointers under the existing facade contract, not arbitrary unvalidated pointers.
No kernel ABI, binding reinterpretation for old profiles or public SDK installation.

Test the gateway against actual Scratch state on the host, and compile/run the C
adapter with a deterministic transport witness that checks allocation-before-send,
flags, reply validation and poisoning. Keep these host/adaptor claims distinct from
QEMU, actual dash, dup across exec and peer authentication. The existing no_std and
host suites remain selected. Native profile wiring, frozen tables, CLOEXEC holder
release and poisoned-process stop/reclaim remain required before application use.
This uses the existing file owner and local descriptor arrays, adding no extra file
store, alias registry, allocator or general VFS. Old null/pipe profiles remain
incompatible and must reject accidental combined selection. No obsolete path can
be removed while its existing consumer profiles remain in use. Use the pinned C
formatter and Rust1.98 edition2024; old unrelated C formatting is unchanged.

[Adapter and gateway evidence](evidence/scratch-adapter-2026-09-14/README.md) now
passes the owner/backend host composition, deterministic C transport witness and
native SDK object compilation. Run `python3 -m unittest discover -s tests -p
"test_scratch_*.py" -v` or the full `zig build test`. The C witness uses host libc
constants; it is not a linked native client/owner interoperability run. The native
SDK compile checks target declarations only. A live profile must still emit the
grant, select five scratch bindings without combining old profiles, invoke the
gateway and validate actual fork/exec tables and cleanup before acceptance.

#### Live C scratch descriptor selection

Select `scratch_client` as a pre-copy native C descriptor witness using the existing
three-worker/four-page-owner envelope. It receives the unchanged three-stream
bootstrap followed by AESFD001, enables five local bindings and calls the actual
private open/fcntl/read/write/close adapter. It duplicates a writer, writes A,
closes the first alias, writes B through the survivor, then opens two readers to
check shared versus independent offsets and CLOEXEC flags. All scratch aliases
close before a canonical96 completion record and the existing copy fixture.
This does not carry scratch descriptors through fork/exec and does not change
consumer scripts or claim actual dash redirection.

The owner serves only canonical scratch requests on the authenticated source
connection. Before accepting96 it requires no holders and no poison, independently
opens/reads exact AB/EOF and closes that description. Standard streams remain
untouched for the old copy fixture. Complete EIO close remains the legacy stream
contract only; scratch close EIO must poison instead of claiming holder release.
The client clears metadata of its already-closed temporary FDs before the old
strict frozen-table validator; extra bindings must be empty, never inherited as
unvalidated streams. Native poison/stop recovery remains separate future coverage.

Offset-loss and CLOEXEC-loss controls must produce client252 followed by owner1950,
zero reclaims and the expected fixture rejection. Positive71/72/17 twice and six
reclaims plus independent readback are required. Select focused cases, full
connections and host checks on frozen bytes. Native FD inheritance and matching
runner remain required before consumer handoff. No kernel operation, quota or
new service process; existing scoped C/Rust formatting and buffer/mask rules apply.

[Live C descriptor evidence](evidence/scratch-client-native-2026-09-14/README.md)
now passes three focused cases and all331 connections cases. The client uses
actual adapter operations, closes scratch FDs before copy, and clears metadata
only for those already-closed entries under the mask guard. The owner independently
reads AB and EOF before continuing. Owner9520bytes and client ELF22872bytes fit
existing limits. CLOEXEC control client ELF22856bytes rejects client252/owner1950
with zero reclaims, as does offset loss. No attempt failed unexpectedly.
Injected scratch close-EIO and confirmed-stop poison recovery remain unqualified;
no live scratch FD inheritance, actual dash file-script or matching runner claim.

#### Scratch exec snapshot preparation — 2026-09-14

Requirement: prepare the sixteen-record snapshot for three streams and two
separately authorized scratch descriptions. Reuse the existing pure alias-count
validator through an explicit files entry point; it must not reinterpret the
pipe profile or grant authority. Reject noncanonical records and count mismatches
without changing the input. A successful plan removes CLOEXEC aliases and releases
only the replacing process's last local holder. Fork preserves flags; denied exec
must discard the plan without closing anything. Native callers must independently
validate live binding references and frozen process admission before publishing.

This step adds preparation and host composition coverage, not native publication.
Exercise mixed flags, both file bindings, alias positions, empty/full tables,
forged counts and parent/child shared offsets against the actual Rust scratch
owner/backend. Mutation controls must reject dropped offsets and premature
backend close. No kernel ABI, resource quota, unsafe boundary, dependency or sibling
contract changes. Existing native consumers do not call the new entry point;
native wiring requires the full connections suite and matching runner before
handoff. Run the existing host suite and workflow/pin checks for this step.

Simplicity: reuse the bounded validator rather than build a second descriptor
implementation. A named files entry point keeps authority distinctions explicit
without copying the algorithm. No obsolete path can be removed yet; native
stream, null and pipe consumers retain their existing contracts.

#### Live scratch copy selection — 2026-09-14

Requirement before exec wiring: opt-in `scratch_copy` carries a writer and its
CLOEXEC alias through the actual frozen copy operation. The owner validates the
exact five-binding snapshot before admission, stages child holders only after
successful admission, and gives the child generation-scoped references in the
otherwise unused receipt tail. Parent and child retain separate local alias
counts and flags. Parent closes both aliases before the child writes B/C after
pre-copy A; independent backend readback must be ABC. No alias or holder release
is inferred from a process timeout. Streams keep their existing checks/reclaims.

Forbidden: early backend close, copied parent authority in the child, mismatched
snapshot flags/counts, offset reset, or claiming this as exec/CLOEXEC removal.
The private opt-in receipt uses bytes24/28 for file reference/root; old receipts
remain zero there. Fixed sixteen-FD/two-description bounds and single-context
masked copy remain. No new kernel operation, quota, service or unsafe boundary.
Simplicity: reuse the existing copy and owner paths; a separate copy mechanism
would duplicate admission and cleanup. No existing profile can yet be removed.
Select native positive, offset-loss, early-close and malformed-snapshot controls,
then full connections and host checks on frozen sources. Matching runner and
actual dash exec/redirection remain required before consumer handoff. Siblings,
released pins and public SDK remain unchanged.

The live-copy implementation uses FD3 and FD4 on scratch binding3; FD4 retains
CLOEXEC through copy. Both processes must report the expected flags. The parent
then closes both aliases before child application I/O. The child writes B through
FD3, closes it, writes C through FD4 and closes it. Generation-scoped file/root
references are validated in the child before readiness; the owner grants its
holder only after native copy admission. The exact frozen table includes the
existing FD10 stream alias and cannot silently drop or change scratch flags.
Parent completion96 alone is not a cleanup proof: final owner closure and backend
readback/termination are independently required. This uses the existing two full
lifetimes and six-reclaim completion oracle, without adding exec semantics.

[Live scratch copy evidence](evidence/scratch-copy-native-2026-09-14/README.md)
passes four focused cases and all335 connections cases on276 frozen sources.
Two successful lifetimes finish71/72/17 with six reclaims. Offset-loss2507,
early-close child251/owner1950 and snapshot2506 controls reject exactly with zero
reclaims. Host and formatting/standards checks pass. No failed attempt occurred;
owner13832bytes and client ELF22064bytes fit existing limits. Actual scratch
exec/CLOEXEC holder removal, poisoned-close recovery, matching runner and consumer
acceptance are still required; the files preparation helper remains host-qualified
until native exec wiring consumes it.

#### Replacement scratch-table restoration — 2026-09-15

Preimplementation requirement: restore an exec survivor table in a fresh private
C image after the existing three-stream bootstrap and validated AESFD001 root.
The bounded helper accepts64 table bytes and32 description bytes (two16-byte
records: reference, mode, local alias count, reserved zero). This is local parser
input, not a published transport extension. Native publication is still pending.
All validation precedes descriptor mutation. Reject nonzero absent records,
CLOEXEC survivors, out-of-range bindings, stale/foreign/parent references,
invalid modes, counts differing from the table, and nonfresh adapter state.
Failure poisons the connection without partial publication or backend calls.

The committed snapshot supplies only local descriptor metadata; the owner must
validate authority/admission and execute holder release separately. Standard
stream bindings retain their bootstrap references/rights only when present in
the survivor table. Scratch bindings require exact generation/root/slot encoding.
No namespace lookup, new dependency, kernel operation, service or quota. Caller
buffers must remain valid for the synchronous call; the existing mask guard
protects publication and preserves errno. Native inclusion remains opt-in pending
actual exec wiring and full target regression/consumer acceptance.

Select the deterministic C transport witness, rejection/atomicity cases, explicit
stale-reference and CLOEXEC-loss mutants, native SDK object compilation, and host
checks. No QEMU result is claimed for an uncalled helper. Simplicity: reuse the
existing table/binding arrays and mask discipline; avoid a second descriptor store
or partial incremental restoration. Old native profiles need no changes.

[Restoration helper evidence](evidence/scratch-restore-2026-09-15/README.md)
passes the extended C host witness, two exact rejection controls and native SDK
object compilation. Full host/format/workflow/standards checks pass. The new header
is not included by native profiles yet; this is parser/publication coverage,
not actual exec, owner authority validation, or process recovery acceptance.

#### Native scratch image replacement — 2026-09-15

Requirement: extend the live-copy witness with actual native image replacement.
Child FD3 survives, FD4 and the extra stdin alias are CLOEXEC and must disappear.
The owner checks an exact frozen snapshot and the files preparation plan before
prepare/query/commit; surviving descriptions retain their existing holder and
shared offset. The fresh image receives the original scoped stream grants, its
validated scratch root, survivor table and description record, then uses the
restoration helper before I/O. Exact ABC readback and six real reclaims remain
required. This first selection removes aliases, not a last-description holder;
that cleanup and failed-exec rollback remain separate tests before dash handoff.

Forbidden: accepting old parent references in the replacement, retaining CLOEXEC
aliases, synthesizing exec success, or widening bootstrap authority. Add no kernel
operation or quota; reuse existing image admission and the bounded scratch owner.
The new private97 header plus64 table bytes identifies this fixture only. Client
buffers obey the existing synchronous transport/mask contract. Select positive,
CLOEXEC-table corruption and stale-reference target controls, complete connections
and host checks on frozen sources. Simplicity: reuse the same small C image as the
replacement with an explicit argument, avoiding a second fixture implementation.
Siblings, released pins and public SDK are unchanged; full dash remains open.

The replacement receives the unchanged AECAT001 stream record and validates it
with the existing parser, then uses the established private child-reference
rebinding convention before issuing stream requests. Its AESFD001 root must name
the admitted child peer; description references must match that root exactly.
The owner checks the native staged-image query before commit. The old staging
call cannot return success, and the fresh image must begin with pristine adapter
state. FD4 and FD10 are verified absent before application I/O; the witness then
creates a new FD10 alias for the unchanged stream-cleanup sequence. Writer FD3
continues at the pre-exec offset. The owner independently checks ABC and closure.

This deliberately uses private staging rather than claiming public execve or
dash integration. The plan must have no last-holder releases in this selection;
last-description CLOEXEC release and denied-exec retention are the next native
cases. Full connections, matching runner and consumer acceptance remain distinct
requirements before a dash handoff.

[Native scratch exec evidence](evidence/scratch-exec-native-2026-09-15/README.md)
passes three focused cases and all338 connections cases on278 frozen inputs in
1051.06seconds. Exact ABC, fresh-image descriptor restoration and six reclaims
pass. Kept-CLOEXEC and stale-parent controls reject child254/owner1950/reclaimed0.
Host/format/workflow/standards checks pass. Two failed attempts are retained with
sources: a module/buffer compilation failure, then an incompatible stream
bootstrap rejected by the existing parser. The final path preserves that parser.
Positive owner15320bytes/client ELF25856bytes fit existing limits. Last-description
release, denied-exec scratch retention, public execve/dash and matching runner
are still required before handoff.

#### Last scratch description at exec — 2026-09-15

Requirement: extend the native exec witness with a separate child-owned reader
opened CLOEXEC before replacement. The child reads A through it; the frozen
snapshot contains exactly one alias of binding4. After native image preparation
and verified staging, close that child's last reader holder and require backend
acknowledgment before commit. Preserve the writer holder and its shared offset.
The replacement must reject access to the removed reader; final owner closure,
ABC readback and six reclaims remain required. Skip-close and wrong-description
controls must fail exact checks, not timeouts. Failed-exec retention is the next
separate selection; this does not implement poisoned-close recovery.

Use the existing two-description owner, C open adapter, files plan, and image
replacement path. Do not add quotas, ambient authority or a service. The readonly
open/read occurs on the authenticated child route; exact canonical requests and
frozen table/counts constrain this private fixture. Existing mask and synchronous
buffer rules apply. Select focused positive/controls, full connections and host
checks on frozen sources. Simplicity: reuse the current exec path rather than
introduce an independent lifecycle or descriptor store. No sibling/public API or
released-pin change. Matching runner and consumer acceptance remain separate.

The same bounded selection also gains a denied-admission retry. While the child
is frozen, the owner requests an unauthorized image, requires EACCES and an
unchanged empty staged-image query, then resumes the original image. It must
retain exact descriptor flags/counts/references, reader EOF position and writer
access before staging the same table again with the next freeze sequence.
Only the successful retry releases the CLOEXEC reader. Closing that reader on
denial or returning the wrong denial code must reject. No failed-admission
cleanup is inferred from the pure plan. Existing stream and failed-exec profiles
remain separate compatibility coverage. A scoped shared scratch forwarding
function replaces repeated generic gateway instantiations after the first build
exceeded the four-page bound; authority validation and native limits remain.

[Last-close/denied-exec native evidence](evidence/scratch-exec-last-2026-09-15/README.md)
passes six focused cases and all344 connections cases on278 frozen inputs in
1086.48seconds. Both positives finish two71/72/17 lifetimes with six reclaims.
Skip-close rejects2507, wrong close child254/owner1950, premature denial close2510,
and wrong denial child251/owner1950, all with zero reclaims. The latter restores
the caller mask before poisoned failure return. Host/format/standards checks pass.
Positive owners13912/14888bytes fit existing limits after sharing request forwarding.
Two failed attempts and the intermediate last-close success are retained. Ten
older scratch images change and pass regression;639 other compared images remain
identical. This is private native staging; unchanged dash scripts, matching runner,
SDK/consumer acceptance and poisoned-close recovery remain open.

#### Dash scratch fork adapter boundary — 2026-09-15

Preimplementation requirement: the opt-in FORK_SHELL_FILES C adapter must accept
live scratch descriptions at arbitrary local FDs, without assuming the fixture's
first open sequence or FD3/FD4 placement. Validate exact local alias counts,
rights, binding slots and generation-scoped parent references before staging.
After the normal three-stream copy receipt, consume a separate32-byte AESFC001
record: child root, child generation, two file references, then eight zero bytes.
All references must rebind the copied description sequence/slot to the actual
child generation/peer, or be zero for an unused binding. Validate the whole record
before changing any file reference/root. Preserve FD flags and alias counts.
The existing owner must authenticate/admit and issue this record; numeric handles
and this client validator do not grant authority.

This step wires the C fork path, not the owner dispatcher. No native profile
selects FORK_SHELL_FILES until the matching owner and replacement helper are
integrated. Select host validation/atomicity controls, native SDK compilation of
the real fork client, and existing host checks; full connections/matching runner
are required on later native inclusion. No QEMU or unchanged-script result is
claimed from this boundary alone. Keep existing profiles and released pins fixed.
No new kernel operation, service or unsafe boundary. Reuse the existing masked
copy transaction and arrays; reject ambiguous records rather than publishing
partial rebinding. This avoids a second fork implementation. Document the owner
wire contract here; public SDK and sibling adoption remain separate.

The opt-in C caller now receives the initial scratch grant before running the
script, validates its extra bindings during fork preparation, and consumes the
separate child file receipt before readiness. If that receipt fails, it poisons
transport before the existing failed-stage exit, preventing wrapper cleanup with
unvalidated copied references. The initial three-stream receipt stays unchanged.

[Dash scratch fork adapter evidence](evidence/dash-scratch-fork-2026-09-15/README.md)
records host validation/atomicity controls and native SDK compilation of the real
fork client with the unchanged consumer script. Existing fork preprocessing is
unchanged apart from blank lines. Owner dispatch, replacement-helper support and
actual unchanged-script execution are still required before native acceptance.

#### Dash scratch owner fork grant — 2026-09-15

Preimplementation requirement: add the owner counterpart to AESFC001, gated by
the still-unselected shell_files mode. The authenticated owner caller must freeze
the parent, validate its three stream holders and obtain successful native child
admission before calling this boundary. Recount the canonical sixteen-record FD
snapshot against supplied counts, including CLOEXEC aliases (fork retains them),
and require each scratch binding's presence to match the owner's live parent
holder. Revalidate exact parent references with the existing inheritance method.
Only then acquire child holders and emit the child root/generation/two references
with a zero tail. Rejection must leave all owner state unchanged; no backend RPC,
allocation, new authority, quota or unsafe boundary is introduced. The method is
owner-internal and does not establish native admission itself.

Reuse the existing descriptor validator and holder transition instead of adding
a second descriptor store or a general transaction framework. The extra code is
bounded snapshot validation and record encoding; no existing path is removed yet.
O-02–04, I-01/05/06 and E-01/04–06 apply. Select host malformed/count/reference,
generation/replay and shared-lifetime tests, deliberate validation/grant omission
controls, enabled no_std target compilation and required host/pin checks. Since
no native profile selects this boundary, native dispatch, replacement-helper and
unchanged-script qualification remain required, with full connections and matching
runner before handoff. Released pins and sibling contracts stay unchanged.

The owner-internal `inherit_files` boundary now returns that complete grant after
validation and the existing atomic holder transition. Its caller must stop/reclaim
an admitted child on validation or delivery failure; this helper performs neither
native admission nor transport recovery. All32 owner/composed Rust tests pass,
including CLOEXEC-only reader inheritance, FD9/11/15 aliases, canonical table
rejection, empty closed slots, replay rejection and final-holder backend closure.
Two deliberately broken versions fail the named assertions: bypassed holder
validation and a parent reference emitted in the child grant. Enabled no_std
target compilation and all104 required host tests pass. This remains unselected
by native profiles; no new dash/QEMU acceptance is claimed. See
[owner boundary evidence](evidence/dash-scratch-owner-2026-09-15/README.md).

#### Dash scratch replacement helper — 2026-09-15

Preimplementation requirement: the opt-in FORK_SHELL_FILES replacement helper
must consume the existing stream bootstrap, survivor table and saved-mask record,
then an AESFD001 scratch grant and the two sixteen-byte description records.
Use scratch_restore to validate the entire survivor table and scoped references
before publishing file aliases. Preserve the existing mask/identity checks and
FD10 CLOEXEC rejection. Run the unchanged consumer helper against the restored
FD table; close every surviving local alias on normal return, including FD9.
Malformed restore must return224 without invoking the consumer. Close failure
must return224, preserving existing poisoned transport behavior.

This is C replacement-side integration only; no launch profile selects the mode
until owner dispatch/exec publishes this sequence. Reuse the existing restore
validator and close operation rather than duplicate their state machines. No new
service, kernel operation, quota, unsafe boundary or sibling API. O-02–04,
I-01/05/06 and E-01/04–06 apply. Select native SDK object compilation, existing
restore rejection/atomicity host coverage, required host/pin checks and exact
preprocessing comparison of all existing helper selections. Native loader,
unchanged helper95/parent22 and cleanup witnesses remain required with the full
connections/matching runner before handoff. No runtime acceptance from compilation.

The replacement now implements this receive/restore/cleanup sequence under
FORK_SHELL_FILES. It and the unchanged consumer helper compile against the native
SDK; all eight older helper selections preprocess identically apart from blank
lines. All104 host tests pass, including existing malformed restore, stale-scope,
CLOEXEC and atomicity checks. The new receive/consumer/cleanup sequence has not
executed in QEMU; owner dispatch and matching replay remain open. See
[replacement boundary evidence](evidence/dash-scratch-helper-2026-09-15/README.md).

#### Dash scratch dispatch integration — 2026-09-15

Preimplementation requirement: carry one scratch Owner through pre-fork open,
authenticated child admission, post-fork dispatch and replacement publication for
the unchanged leak workload. The bounded fixture permits exactly the initial
writer at FD9 plus the existing FD10 CLOEXEC stdin alias. Validate that snapshot
before admission; obtain the child-specific AESFC001 only after native admission.
Route file requests by authenticated connection, never by caller-supplied peer.
At exec validate the same table and require the writer survivor; publish the
existing stream/table/mask sequence followed by AESFD001 and the live writer
record. Parent22, actual helper95, empty stdout and complete owner/backend closure
are the target oracles. No kernel quota or general filesystem policy change.

Reuse the existing gateway and fork/exec transitions with cfg-scoped parameters;
no parallel owner table or service is needed. This scope does not add general
exec-time last-file release, denied-exec recovery or nested forks to dash; those
remain separately qualified private experiments. O-02–04, I-01/05/06 and E-01–06
apply. First compile the complete enabled owner and run host checks; activating a
native launch selection requires focused semantic controls, full connections and
matching runner before consumer handoff. No acceptance from unexecuted code.

The focused integration now executes the unchanged leak script in QEMU, with
helper95/parent22/backend17 twice and six reclaims. Before regular inclusion,
select three semantic controls: substitute the parent reference in the child
fork grant (readiness rejection1950), omit the replacement description (helper224,
owner2130), and skip the actual consumer helper (helper0, owner2130). None may pass
because of timeout, and all must report zero reclaims at the exact rejection.
Pin the unchanged consumer script locally before adding the regular cases; leave
sibling and released-standard bytes unchanged. Run the expanded full connections
suite and host checks on final frozen sources. Matching command-runner and owner
intake remain separate before any consumer handoff.

[Integrated native evidence](evidence/dash-scratch-dispatch-2026-09-15/README.md)
now passes all348 connections cases on262 frozen inputs in1093.87seconds. The
unchanged script produces helper95/dash22/backend17 twice with six reclaims and
empty stdout. Bad child grant rejects child80/owner1980 (the existing readiness
failure, correcting the initial1950 oracle); omitted description rejects
child224/owner2130; skipped helper rejects child0/owner2130. All controls have zero
reclaims. All104 host checks and33 owner/composed Rust tests pass, and661 older
ELF/raw images are unchanged. The positive owner is14136bytes within four pages.
The new owner description encoder validates peer/liveness/count bounds and emits
only current holder references; the exact frozen exec table supplies its counts.

The first integrated helper build exposed duplicate ARGV macro definitions;
a guard fixes that without changing older images. The failure and corrected
readiness oracle remain retained, alongside two selector setup failures. The
unchanged script is now pinned locally, and the regular harness owns its four
selections. This is producer evidence for volatile file inheritance/cleanup;
redirection/readback, matching runner, independent SDK acceptance, poisoned-close
recovery and persistent storage remain separate work.

#### Unchanged scratch redirection workload — 2026-09-15

Requirement, corrected against the native frozen snapshots: run the unchanged
userland redirection.sh. Parent writes A/B through aliases of one writer, closes
both, then opens the retained file readonly and redirects stdin before fork.
Frozen fork and exec have stdin bound to the reader and FD10/FD11 retaining old
stdin with CLOEXEC. Inherit the reader through the existing child grant. After
successful image staging remove both old-stdin aliases and drop only the child's
old stream holder, preserving the parent's stream and the reader. Require helper0,
dash0, exact stdout AB, all file/stream closures and six reclaims over two runs.

Extend the existing shell_files owner/dispatcher under shell_files_redirect;
reuse scoped gateway, alias tables, descriptor plan and replacement restore.
No new service, kernel operation, quota or persistence claim. Both opens use the
authenticated parent route; copied numeric handles grant no new authority. Preserve all existing leak/legacy cases. O-02–04, I-01/05/06 and
E-01–06 apply. Simplicity: existing ownership and explicit synchronous messages
suffice; no additional mutable descriptor store or general VFS is needed.
Pin the unchanged input before use. Focused controls must reject a lost B write,
a retained old stdin holder, and skipped actual helper without relying on timeout.
Then run the full connections suite, host checks and pin/format checks on frozen
sources. Matching runner and independent consumer acceptance remain separate.

The first native attempts rejected the narrower child-open assumption. Scoped
diagnostics identified the parent's readonly open and recorded identical frozen
fork/exec layouts: FD0 binding3, FD1/2 standard streams, FD10/11 binding0 with
CLOEXEC. The diagnostic code is removed; exact layouts are now validated before
admission/publication. The unnecessary child-open path was removed. All attempts
and their source hashes are retained. Focused positive and three controls pass;
STATE and the evidence packet record final full-suite qualification separately.

[Full redirection qualification](evidence/dash-redirection-2026-09-15/README.md):
352 connections cases in 1091.44 seconds on 264 unchanged inputs, 104 host tests,
and 671 byte-identical prior images. All three semantic controls reject with
zero reclaims. Matching runner and independent consumer acceptance remain open;
the next workload is denied redirection into the read-only input namespace.

#### Unchanged denied redirection — 2026-09-15

Requirement: run unchanged userland denied-redirection.sh through a real dash
subshell. The authenticated child receives the existing backend's EACCES for
/inputs/denied; no file handle or mutation results. Dash reports failure on stderr,
wait observes the child failure, and the parent prints exactly denied ok followed
by newline and exits0. Repeat with six reclaims. Require exact denial, no exec,
closed owner/stream state and actual backend stdout readback. Wrong errno and
lost stdout must reject explicitly, not time out.

Use the existing scratch root, empty fork grant and serialized dispatcher; allow
this profile's pre-exec child I/O only after observed denial. Preserve other
profiles. Aether owns this private native adapter/owner integration; userland owns
independent intake and the eventual public SDK. O-02–04, I-01/05/06, E-01–06 and
SE-01–05 apply. Existing denial is the simplest enforcement; no new namespace
service or kernel API is needed. Remove no compatibility path until its consumers
migrate. No dependency, unsafe boundary, resource increase or persistence claim.
Pin the unchanged script, retain all attempts, run focused semantic controls,
full connections and host checks on frozen sources, then update STATE/workflow.
Matching runner and independent intake remain separate. Existing upstream dash
error wording and machine markers are preserved under the experience exception.

[Denied-redirection qualification](evidence/dash-denied-redirection-2026-09-15/README.md)
passes all 355 connections cases in 1105.85 seconds on 266 frozen inputs and all
104 host tests. Child fork-issued stream references remain valid without exec;
backend EACCES precedes child I/O. Exact denied ok newline, child2/parent0/backend17
twice and six reclaims pass. Wrong errno rejects owner2554; dropped output rejects
child2/owner2310, both with zero reclaims. Of 679 prior images, 671 are unchanged;
eight scratch owners grow 32–48 bytes and pass within existing bounds. Exact
consumer substitution/pipeline/early-reader qualification, matching runner and
independent intake remain before full handoff.

#### Unchanged consumer substitution — 2026-09-15

Requirement: run pinned substitution.sh and unchanged consumer helper through
actual pipe/fork/exec/wait. Preserve four arguments including quoted space and
literal wildcard, and WITNESS=value. Helper writes argv ok newline; dash captures
it, strips the trailing newline, checks argv ok and prints substitution ok newline.
Both lifetimes require helper0/parent0/backend17 and six reclaims. Preserve native
denied-exec retry, CLOEXEC filtering, pipe EOF and authenticated owner grants.
Wrong replacement arguments and skipped helper must reject explicitly without
false output or reclamation success.

Reuse the existing pipe owner and replacement bootstrap, adding the consumer
helper selection. No new service, kernel API, capacity or FFI boundary. Existing
fixed-width argument records suffice; pipe byte accounting uses the selected
workload length. This removes the hardcoded five-byte assumption for this current
requirement without adding a general namespace or pipeline scheduler. Aether owns
the private adapter; userland retains SDK and independent intake authority.
O-02–04, I-01/05/06, E-01–06 and SE-01–05 apply. Pin input bytes, preserve attempts,
run focused controls, full connections and host checks on frozen sources, and
update workflow/reference/STATE. Preserve released pins and sibling repositories.

[Unchanged consumer substitution qualification](evidence/dash-consumer-substitution-2026-09-15/README.md)
passes all 358 connections cases in 1107.50 seconds on 268 frozen inputs and all
104 host tests. The actual helper receives the four quoted arguments and
WITNESS=value, writes eight pipe bytes and exits0; dash checks its captured value
and emits exact substitution ok newline. Two lifetimes reclaim six tasks.
Wrong arguments and skipping the helper both reject premature EOF with owner2175
and zero reclaims before terminal observation. Of 685 prior images, 674 are
unchanged; nine pipe owners and two small writers change and pass the full suite.
The new owner is 14,152 bytes within the existing bound. Multi-stage pipeline and
early-reader workloads, matching runner and independent intake remain open.

#### Pipeline participant ownership and capacity review — 2026-09-15

The unchanged pipeline.sh needs shell parent, printf child, two helper children,
and the current backend: five workers plus the supervising owner, with two pipes.
The current native connections/program fixture has three worker slots plus owner
(workerCount/supervisorSlot in native_c.zig), six channels, one child per pipe
owner and five descriptor bindings (three streams plus one pipe). Children in
State.children are execution threads, not extra independent process slots. Merely
selecting the script cannot meet this requirement. A future native profile must
review five worker slots, ten request/reply channels, seven bindings, memory and
PID/handle encoding before changing capacity. Do not silently widen old profiles.
Two simultaneous pipe objects also need distinct authenticated object routing;
the current handle format alone cannot distinguish two equal-generation objects.

Current bounded step: one shared FIFO/ownership implementation with retained
Pipe (parent plus one child) and PipelinePipe (parent plus three children) types.
Caller slot and generation come from the dispatcher connection, never request
bytes. Stage only endpoints held by the parent, reserve them while copy is
pending, admit I/O only after readiness, and release only the exact stopped peer.
No premature EOF/EPIPE while another ready or staged holder exists; failed or
stale operations must not mutate bytes, offsets, identities or unrelated holders.
Exec may only drop existing endpoints. Retirement requires no holders and no
partial/pending/undelivered references across all participants, then zeroes bytes.
Preserve existing Pipe signatures, wire bytes, capacities and generation limits.

Simplicity: parameterize the existing owner rather than duplicate its FIFO and
recovery rules or maintain a second aggregate-holder ledger. Only the existing
two-party shape and the currently required four-party shape are supported. No new
service, kernel operation, unsafe boundary, public SDK or wire-format adoption.
Aether owns this private core; userland and sys-init retain their intake/policy.
O-02–04, I-01/05/06, E-01–06 and SE-01–05 apply. Add semantic host tests for multiple
writers/readers, staged readiness/failure, independent peer generations, exec
rights and pending-aware retirement. Compile for no_std; run required host and
full existing native connections regressions on frozen sources. Four-party host
coverage does not prove native multi-stage pipeline execution. Update existing
workflow/reference and STATE; preserve all attempts, sibling repos and pins.

#### Two-pipe routing review — 2026-09-15

Requirement: route the unchanged three-stage pipeline's two simultaneously live
pipes without confusing equal object generations or widening participant rights.
This step adds a private, host-qualified adapter; native profiles keep their
existing pipe module and wire bytes. Aether owns this adapter; userland owns SDK
adoption and sys-init retains supervision policy. No sibling edits or pin changes.

Use exactly two existing PipelinePipe objects, owned by the same dispatcher.
A typed owner-selected First/Second identifies creation, not application-supplied
caller authority. External references are 0x79000000 | (object << 16) |
(generation << 8) | end, with object 0–1, generation 1–3 and end 1–2. Reject every
other bit pattern. Bindings are 3/4 for First and 5/6 for Second, reserving 0–2 for
stdio. Validate the reference/binding pair before translating to the existing
core's local 0x7800 references and bindings 3/4. Caller identity still comes from
the authenticated connection; the selected core checks readiness, generation,
endpoint holders and operation rights before effects. Numeric references alone
never grant access. This new private family is not a public ABI allocation.

Creation receives a trusted object selection and the unchanged factory frame;
only the parent may create. A busy/exhausted selected object returns ENFILE rather
than silently choosing another. Successful replies translate both references and
binding IDs. Non-create calls to creation and create calls to data routing reject
EINVAL; invalid routes/binding pairs reject EACCES. Valid stale references retain
the selected core's EBADF behavior. Replies/Pending have the existing one-effect
contract: retain the external request on Pending and cache completed replies;
never replay an effect on uncertain delivery. Lifecycle calls continue directly
on the same two objects. The future fork adapter must validate both objects before
multi-object changes, stage endpoints before readiness, and confirm the exact peer
before cleanup; this routing layer does not implement a fork transaction.

Simplicity (SE-01–05): using two unmodified cores without routing is insufficient
because equal generations produce equal references. Choose a small pure routing
adapter instead of duplicating FIFO/lifetime code or adding a registry, allocator,
second holder ledger or global generation authority. It adds no stored state,
heap, unsafe code, new service, kernel capacity or retry policy. Existing cores
retain independent three-generation bounds and 256-byte FIFOs. O-02–04,
I-01/03–06 and E-01–06 apply. Test equal-generation data isolation, unauthorized
cross-object access, stale reuse, malformed route/binding rejection, independent
EOF/EPIPE, Pending and retirement. Deliberately break routing and binding checks
and require exact semantic failures. Run the existing host gate and no_std target
compilation. Because no native path imports this new module, verify every prior
runtime input is unchanged instead of claiming a new native pipeline run. Native
capacity, seven-binding fork/exec integration, matching target evidence and
independent consumer acceptance remain required before adoption.

#### Two-pipe descriptor transitions — 2026-09-15

Requirement: the private owner must prepare seven bindings (stdio plus both pipe
endpoint pairs), stage fork inheritance including CLOEXEC aliases, and drop only
exec-filtered holders without partially changing one pipe when the other rejects.
Aether owns the adapter; userland retains SDK intake and sys-init supervision.
This adds host-qualified transitions, not a native fork/exec dispatcher.

Recompute the plan from the frozen 16-record descriptor table and exact seven
alias counts on each call. Validate each caller's live holdings and supplied
object generation first. None means no endpoint held by that caller, not that
the object is absent; Some requires a live matching generation. Stdio validation
and actual image admission remain the enclosing owner's responsibility. Fork
inherits all aliases including CLOEXEC; exec filters them and releases a holder
only when its last local alias disappears. Both cores track every staged child,
even on an object where the child has no endpoints, so readiness and confirmed
terminal can be applied consistently before or after later pipe creation.

Apply the two transitions to a bounded temporary copy of the existing two cores,
then replace the pair only on success. The exclusive mutable borrow excludes
interleaving. There is no transport/native effect inside this operation; a failed
second transition discards the copy and leaves bytes, generations and holdings
unchanged. Copy readiness/known failure and exact confirmed terminal use the same
atomic mechanism. The caller must quiesce I/O, retain pending/completed frames,
and independently validate readiness or terminal evidence. Neither a stop request
nor timeout authorizes confirmed-terminal cleanup. Cross-service transactions,
image commit and native frame delivery are not covered by this local operation.

Simplicity: sequential mutation needs rollback after the second rejection, which
can lose FIFO bytes during last-reader cleanup. Choose a fixed pair copy over
new rollback state or duplicated validation logic. It adds bounded stack copying
of two small owner structs, no heap, persistent ledger, unsafe boundary or kernel
capacity. Cloning data is private owner bookkeeping, never a wire authority grant.
O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply. Test seven-binding CLOEXEC/count
validation, two-object staging/readiness/terminal atomicity, stale generations,
last-reader byte preservation on failed exec and successful holder cleanup.
Run host and target compilation; compare existing native images and run selected
pipe regressions because additive helpers must preserve the old core behavior.
Full matching native pipeline/runner evidence remains before consumer adoption.

#### Five-worker bundle and capacity review — 2026-09-15

The native pipeline needs five workers (shell, backend, three pipeline children)
and one owner. The present connections envelope carries three images but only
48 entropy bytes, bootstrap storage is 48 bytes, and load indexes 16 bytes by
worker slot. Merely enlarging states would overrun slots 3/4 entropy. PID and
parent notification use generation * states.len + slot + 1, so globally changing
states.len would also change old profile identities. The native kernel mapping
must still fit kpt.len * memory.leaf_span; memory backing grows per State.

First add a separately callable candidate bundle parser, leaving bundle() and
native start's accepted magic unchanged. AENMX004 reserves a 112-byte header:
bytes 8–24 hold the existing three image lengths and supervisor length, 24–32
are zero, and 32–112 contain five 16-byte developer entropy inputs. Payload order
is the same three reusable images then supervisor. Each image remains 1..1 MiB;
supervisor remains 1..16 KiB. Require exact total size and reject truncation,
reserved bits, zero/oversized sections and older magic in the candidate parser.
No extra image factory is implied: worker slots and admitted image templates are
different resources. The current general bundle parser must reject AENMX004
until native capacity and authority witnesses are ready.

The subsequent opt-in kernel profile must select six State entries, ten channels,
80-byte bootstrap storage and supervisor slot5 only for this profile. Keep old
profiles' four-entry PID stride and limits unchanged. Review kernel mapping span,
per-worker backing and stack, scheduling over six entries, parent notification,
slot-based handles, entropy slicing, channel exhaustion, exact stop/reclaim and
repeated generations. Require denied worker-slot5 admission, wrong-owner channel
use, stale generations and ten-channel exhaustion before real pipeline assembly.
Do not enlarge global tables or accept the new envelope as a side effect of this
parser change. No native profile is enabled in this step.

Aether owns the boot envelope; sys-init and userland retain lifecycle/SDK policy.
O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply. Share the existing three-image
length/slicing validation instead of duplicating it or inventing a general bundle
registry. Only this candidate uses the larger header. No dependency, unsafe code,
new authority or released pin. Test section boundaries and distinct entropy/payload
slices, all malformed headers, and continued old-profile rejection/limits; run the
host gate and compile the kernel. Native acceptance and actual five-worker execution
remain separate, required follow-on evidence.

#### Native five-worker capacity witness — 2026-09-15

Implement the opt-in native-pipeline-capacity build selection only with bounded
native memory, a supplied native image and SMP disabled; reject large-memory and
thread variants. Require AENMX004 exactly when selected, retain every old profile's
four-state layout when unselected. Six states give five workers and owner slot5;
ten channels each retain single-owner endpoint enforcement and generation limit3.
Bootstrap carries 80 bytes; old profiles retain48. Reuse the three image factories.
Profile entry19 and completion require15 reclaims, all worker admissions retired
and every channel closed/zeroed. Preserve old smoke markers and completion counts.

The capacity witness admits five workers simultaneously for three generations,
checks PID generation*6+slot+1 and owner parent identity, validates each slot's
16-byte entropy, rejects worker use of owner-held channel endpoints and factories,
and checks ten-channel exhaustion. One live worker is stopped in the second
cycle; all others exit normally. Retire exact terminal records before reusing
slots, reject stale handles, and require third-generation exhaustion. Include
wrong header/build pairing and malformed candidate entropy framing as rejection
controls. Record actual kernel mapped size and preserve old mapping-span bounds;
if the six states exceed the bound, stop and review rather than enlarge it silently.

This is a native capacity fixture, not sys-init or pipeline policy. No new SDK,
service or image factory. Aether owns mechanism and test; sibling repos/pins remain
unchanged. O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply. The fixed opt-in array
sizes are simpler than dynamic allocation/topology; no extra runtime allocator or
shared mutable authority. Existing state mapping, scheduling, endpoint transfer
and cleanup are reused. Build policy, host tests, new native positives/rejections
and selected old pipe regressions are required; wider scheduler/full matching
suites and actual pipeline assembly remain before a consumer handoff.

Capacity integration exposed a real zero-argument getpid mismatch: musl leaves
argument registers unspecified, while the kernel rejected nonzero values. Remove
that input check while preserving the existing profile gate and slot/generation
identity; PID remains bookkeeping, never authority. The witness uses actual musl
getpid plus an explicit raw call with nonzero unused registers. Existing checked
capability operations retain their argument validation. Native prelude adapters
previously zeroed these registers, masking the mismatch. This scoped compatibility
fix is required for the actual native SDK, not a successful stub.

The capacity owner's private int0x81 wrapper follows the existing connections
fixture: stack-resident argument/frame buffers remain live through the call,
register in/out operands model kernel return values, and no nomem assumption is
made. The kernel validates user ranges before copying; endpoint identity is
checked separately. C borrows AT_RANDOM only for its admitted lifetime and uses
fixed 16-byte frames. Neither wrapper transfers Rust/C memory ownership or runs
as an init policy service. Qualified sources retain the exact wrapper and flags.

#### Native two-pipe dispatch witness — 2026-09-15

Requirement: use the qualified five-worker profile to execute the private two-pipe
routing core with concurrent writer, relay and reader. The existing capacity
clients in slots0/1 remain idle until release; slots2/3/4 receive scoped pipe
roles, mapping authenticated connection slots to participants1/2/3. These are
independently admitted conformance workers, not actual forked dash children.
The trusted fixture creates/stages endpoint holdings before release, observes
native readiness, drops its own endpoints, and dispatches only authenticated
worker channel frames. Reuse the same two cores across three pipe generations.

Each worker has one bounded 32-byte request and one retained completed reply.
Accept at most the remaining bytes of the current request; apply only a complete
frame. Pending retains the original request; Reply freezes response bytes and a
send cursor until all32 bytes are delivered. Never invoke the pipe again while
its completed reply is partially sent. Poll peers fairly; fragmented writes and
reads must not block progress of another pipe. Writer sends exact pipe data
newline and closes; relay drains First to Second then closes both ends; reader
checks exact bytes and EOF. Observed terminal must precede holder cleanup; reject
unexpected status or leftover normal frames. Retire both objects only after all
participants, holders and pending frames are gone. No early success/reclaim.

Use fixed local frame storage and existing pipe cores rather than a generic
transport framework or a second authority ledger. The enclosing fixture owns
channel bindings and authenticated identity; numeric pipe references grant
nothing alone. No kernel operation, resource limit, service policy, public SDK,
sibling or released pin changes. Reuse the existing unsafe transport contract;
borrowed frame buffers remain live through each checked native transfer. O-02–04,
I-01/03–06, E-01–06 and SE-01–05 apply. Extend the existing capacity harness with
positive dispatch and a deliberate wrong-object control, preserve old capacity
cases, run host/format checks and target cases on frozen inputs. Actual fork/exec
integration, uncertain-reply/stop schedules, full matching suites and unchanged
shell pipeline/early-reader acceptance remain separate follow-ons.

#### Confirmed-stop interrupted writer — 2026-09-15

Requirement: the native two-pipe dispatcher must release a stopped participant's
holders and discard its incomplete transport state only after observing the exact
terminal record. Exercise two deterministic schedules in the existing fixture:
stop the writer after seven request bytes (no pipe effect), or after seven reply
bytes for its completed ten-byte write (effect retained exactly once). The relay
and reader must receive respectively zero or ten exact bytes and one EOF each.
Repeat three generations with fifteen reclaims, including three confirmed stops.

Forbidden outcomes: cleanup on an unconfirmed stop request, applying an incomplete
request, replaying a completed write, retaining old frames across reuse, or hiding
unexpected worker exits. Authenticate the existing native handle and participant
generation; require stop kind3/status143 before clearing frames and holders. Derive
retirement's pending flags from real dispatcher state. A retained-frame mutant
must reject before any reclaim. Preserve eight existing capacity/dispatch cases.

The simpler alternative is a direct terminal branch in the current dispatcher;
choose it over a generalized cancellation service or recovery protocol. No new
kernel primitive, authority, dependency, unsafe boundary, quota or public ABI is
needed. Three local stop-request flags identify the fixture's expected terminal
records; bounded borrowed transport buffers keep the existing syscall contract.
None of the existing machinery can be removed yet: native fork/exec and ordinary
EPIPE delivery remain separate requirements. O-02–04, I-01/03–06, E-01–06 and
SE-01–05 apply. Run the complete expanded capacity suite, a semantic retained-frame
control, host checks, pinned formatters and standards/workflow checks on frozen
sources. Record results in STATE, the native reference and existing inventory.
This does not qualify dash pipelines, companion intake or the assembled R1 image.

#### Native early-reader EPIPE delivery — 2026-09-15

Requirement: forward an ordinary pipe EPIPE reply intact through fragmented native
transport, preserve its zero payload, and let surviving workers close their held
ends normally. In the existing two-pipe fixture the final reader closes without
reading, or exits with its reader still held. Observe its terminal before allowing
the relay's write to Second. The relay checks exact First data, receives EPIPE on
Second, closes its two ends and exits. After observing that terminal the original
writer retries First and must receive EPIPE too. Both pipe generations then retire.
These owner scheduling gates force the boundaries being tested, not application
policy or a public blocking protocol. No SIGPIPE delivery is claimed here.

Forbid false success/wrong errno, payload publication on error, effects from failed
writes, early holder cleanup, stale frames and incomplete reclaim. Require ten
successful bytes written/read on First, none on Second, one EPIPE per pipe, no EOF
read request, fifteen normal exits/reclaims across three generations. A wrong-errno
reply mutant must make the native worker fail with its exact status before reclaim.
Retain all eleven earlier cases and their rejection meanings.

Choose the simpler direct error-reply path in the existing dispatcher. A new error
service or exception protocol is unnecessary; the frozen 32-byte reply already
carries signed errno. No abstraction or old path can be removed now. Counters and
two scheduling gates are bounded fixture-only witnesses; no authority, shared ABI,
kernel, dependency, quota or unsafe boundary changes. Existing borrowed-buffer
lifetimes and authenticated participant generations remain required. O-02–04,
I-01/03–06, E-01–06 and SE-01–05 apply. Run expanded native capacity suite, host
checks, formatters, workflow/pins and exact negative controls on frozen sources.
Update STATE and existing native references/inventory. Actual dash fork/exec,
seven-binding integration and independent intake remain separate next work.

#### Native copied pipeline participants — 2026-09-15

Requirement: replace the independently admitted writer/relay/reader in one private
AENMX004 variant with three actual native copies of parent slot0. Slot1 remains a
capacity peer. Parent sends its bounded seven-binding/16-descriptor snapshot,
including a CLOEXEC alias at FD10, then freezes. The owner drains exactly64 bytes,
observes the exact freeze sequence, validates the snapshot/counts against its live
parent holdings and stages both pipe objects before invoking native copy. A stale
copy token must reject without consuming the new channels; only then use the
observed token. Readiness must be observed before completing staged inheritance.

The copied child checks its actual PID/parent, private TLS/stack snapshot, retained
CLOEXEC alias and denied old channel authority; it uses the newly granted channel
registers. Parent verifies child writes did not change its TLS/snapshot. Each child
closes its unused inherited endpoints before doing the existing ten-byte pipeline.
Owner drops parent holders after all child readiness. Three generations require
six image admissions, nine copies and fifteen normal exits/reclaims, exact data
and EOF, stale-handle rejection and unchanged channel/generation limits.

Forbidden: staging from an unfrozen source, using an unverified snapshot, filtering
CLOEXEC at fork, marking a failed/ambiguous copy ready, borrowing parent channel
rights, or reclaiming before terminal. A descriptor-count mismatch must reject
before copying or reclaim. This fixture snapshot is not a libc FD installation;
actual exec replacement, libc rebind and unchanged dash scripts remain next work.

Reuse the existing copy syscall and two-pipe stage_fork/finish_copy routines; a
new process service or kernel ABI is unnecessary. The small private copy helper
owns framing/validation only, not a second holder ledger. No existing path can be
removed while it remains regression coverage. The C freeze boundary explicitly
models all returned grant registers and memory effects; copied stack buffers remain
private/live, and no copied parent capability authorizes child I/O. No kernel,
dependency, quota, sibling or released pin changes. O-02–04, I-01/03–06, E-01–06
and SE-01–05 apply. Run the full expanded capacity suite, exact negative control,
host/format/pin checks on frozen inputs; update STATE and existing references.

#### Copied pipeline replacement exec — 2026-09-15

Requirement: replace each copied pipeline child with a distinct ELF while retaining
its PID, parent identity and required pipe holders. After validated copy readiness,
the owner asks each child to send its seven-binding descriptor snapshot and freeze.
The child marks unused endpoints and FD10 CLOEXEC; the owner validates exact role
records, observes freeze token1, tries an unauthorized image and requires unchanged
commit state, then admits the authorized replacement while it remains parked.
Only then recompute/commit both pipes' CLOEXEC changes from the frozen table.
Reject stale publication, publish the exact token, deliver the filtered table and
observe fresh-image readiness before releasing workers to exchange pipe data.

The replacement verifies fresh TLS, new argv identity, retained native PID/parent,
slot entropy, exact filtered records (including absent FD10), and required native
channel authority. It uses only the endpoints its role retains. Require nine real
copies and nine replacement admissions over three generations, exact ten-byte data
and EOF per pipe, fifteen normal exits/reclaims. A delivered retained-FD10 mutant
must fail the replacement's independent table check before pipe effects/reclaim.

No successful stub, early policy commit, descriptor amplification, stale publish,
application readiness before installation, or silent exec return is allowed. Reuse
existing native prepare/inspect/publish and atomic pipeline commit_exec; a new exec
service or ABI is unnecessary. The small helper remains fixture orchestration,
not a second holder ledger. No removal now: old variants remain regressions.
No kernel, SDK, dependency, quota, sibling or released pin change. Borrowed buffers
remain live through checked syscalls; fresh image startup replaces copied libc
state. This is a validated fixture table, not production libc FD installation.
O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply. Run the complete expanded native
suite, host checks, exact rejection control and format/pin/inventory checks on
frozen sources. Ambiguous admission/transport failure cleanup and unchanged dash
scripts remain subsequent work; this is not a full-shell handoff.

#### Interrupted pipeline exec cancellation — 2026-09-15

Requirement: cancel the bounded copied pipeline if exec is interrupted after image
admission while parked, or after publication with only seven filtered-table bytes
delivered. At either boundary the first replacement must be unready. Stop all three
pipeline participants, observe each exact kind3/status143 terminal, then remove
both objects' holders, discard local table frames and retire the pipes. Reject
publication of the stopped first image. Parent and capacity peer exit normally;
three generations require nine stops, six normal exits and fifteen reclaims.
No pipe data request is dispatched in a cancelled generation.

Choose whole-pipeline cancellation for this bounded admission failure; continuing
a partially assembled pipeline would need policy and error propagation not yet
required by this fixture. Reuse existing stop/terminal/holder cleanup and fixed
buffers, with no new service, kernel primitive, authority, quota or dependency.
No obsolete paths can be removed while they remain regression controls. Never
infer termination from stop acceptance or timeout. The retained-holder mutant must
fail retirement before reclaim, even with all native workers confirmed stopped.
Cancelled frames cannot authorize a replacement generation or be replayed.

This adds no unsafe boundary: synchronous syscalls borrow local buffers and all
participants are confirmed stopped before their local descriptors are discarded.
O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply. Run the complete expanded native
suite, exact retained-holder control, host/formatter/pin/workflow checks on frozen
sources. Preserve failed attempts and update STATE/reference/inventory. This is
scheduled cancellation, not detection of arbitrary missing receipts or actual dash
policy. Libc descriptor installation, consumer scripts and full intake remain open.

#### Seven-binding libc replacement I/O — 2026-09-15

Requirement: use the existing startup descriptor facade and actual musl I/O entry
points in replacement workers, rather than raw pipe calls. Add a private seven-
binding transport selection with a validated-table bootstrap/install hook; older
profiles retain their bootstrap and three-standard-FD initialization. The new
profile starts with no standard streams: source marks bindings0–2 CLOEXEC, and
only the role's live pipe ends survive. Validate the entire received table before
publishing descriptors or readiness. References and rights remain owner-enforced.

Replacement maps retained ends onto stdin/stdout via dup2, closes original aliases,
creates/checks/closes a CLOEXEC duplicate at FD10, verifies EBADF after close, then
uses musl read/write/close for exact data and EOF. No fabricated standard-stream
backend is installed. Reuse the existing guarded alias/count/errno/poison logic;
a separate FD implementation would duplicate subtle ownership and cleanup rules.
The bootstrap hook is private and compile-selected, not a new public ABI. No old
path is removed while it remains consumed. No kernel, SDK, dependency, quota,
sibling or released pin changes. Local C uses pinned existing style conventions.

Forbid partial/malformed table publication, wrong binding/mode, leaked FD10,
shared-alias premature close, readiness before install and successful I/O stubs.
A delivered retained-FD10 control must fail the replacement before pipe traffic or
reclaim. O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply. Run full expanded native
capacity and host checks, relevant legacy pipe regressions, formatter/pin/inventory
checks and compare old images. Frozen buffers stay valid through synchronous
masked installation; no new unsafe boundary. Actual dash fork/exec orchestration,
SIGPIPE and independent consumer intake remain beyond this adapter witness.

#### Public musl fork in the pipeline parent — 2026-09-15

Requirement: create the three pipeline children through the existing private musl
fork candidate, including _Fork child repair, rather than returning directly from
raw freeze assembly. Reuse the verified musl1.2.6 archive, the same bounded staging
substitution and existing REBIND_LIBC_REPAIR helper. The stage boundary receives
new grant registers and repairs auxv/channel caches while upstream _Fork repairs
thread identity. The parent still sends its fixture snapshot before fork; the
owner observes freeze and stages inherited pipe rights before native copy.

Children must observe their own gettid/getpid and updated auxv, reject the copied
parent channels, preserve copied CLOEXEC metadata and private TLS/stack state, then
exec into the existing libc pipe workers. Parent retains its own identity and
private state across all three forks. A no-child-repair _Fork mutant must fail the
child identity check before replacement/data/reclaim. Preserve old variants.
No fork stub, invented PID, parent-cache use or public SDK adoption claim is allowed.

Using maintained upstream fork plus the existing rebind helper avoids duplicating
atfork/mask/TID repair. No new service, kernel ABI, dependency version or quota is
needed; the private archive-derived build records source/header hashes and retains
upstream copyright. No existing path is removed yet. The assembly explicitly models
grant outputs and memory effects; copied local buffers stay live and private. This
is not actual dash orchestration: consumer-driven snapshots, wait/pipe creation and
unchanged scripts remain next. O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply.
Run expanded native/host checks and exact no-repair control on frozen sources;
verify old images, formatters, pins and workflow. Do not modify sibling repositories.

#### Live libc fork/exec snapshots — 2026-09-15

Requirement: capture actual startup_fds at the public fork staging boundary and
exec freeze, rather than manually constructing wire records. A dedicated parent
uses the shared seven-binding facade with four owner-granted pipe ends and absent
standard streams. Before each fork it creates a CLOEXEC alias at FD10/11/12 using
fcntl. Capture occurs inside musl's masked staging boundary. Child and parent
independently check and close the inherited/local alias. Child uses F_SETFD on
unused ends, captures its current table while masked, then freezes for replacement.

Owner derives bounded alias counts from received records and validates syntax and
live pipe holdings through stage_fork. Numeric metadata cannot create authority;
nonexistent standard bindings remain forbidden. Exec uses the same real table and
counts; known role constraints still validate the final replacement contract.
Require nine public forks/execs, exact data/EOF and fifteen reclaims. Corrupting the
Second-writer binding in the captured fork frame must fail live-holder validation
before native copy/reclaim. Parent/child caches and TLS remain private.

Reuse the shared facade and existing public fork/rebind hook; a second descriptor
implementation or alias ledger is unnecessary. Fixed owner scheduling and initial
pipe grants remain fixture scope, not a dynamic pipe factory or dash implementation.
No old path is removed yet. No kernel, shared adapter, SDK, dependency, quota,
sibling or released pin changes. Capture buffers stay live through synchronous
masked sends; publish no staged holder before native observation. O-02–04,
I-01/03–06, E-01–06 and SE-01–05 apply. Run expanded native and host checks, exact
corruption control, old-image comparison and format/pin/workflow verification on
frozen inputs. The unchanged consumer pipeline and early-reader scripts remain
acceptance targets; this does not implement their wait/status orchestration yet.

#### Client pipe creation and wait collection — 2026-09-15

Requirement: the live libc parent requests two pipes through an explicit bounded
factory grant, closes its own ends through public close, and collects each child
through the existing archive-derived musl waitpid hook. Owner chooses object slots;
client validates full create replies before publishing the two lowest free FDs.
The witness relocates them with fcntl into FD3–6, retaining absent stdio. Factory
capacity is two; local exhaustion publishes no descriptors. Parent closes its
four ends after fork; owner observes those close frames before data dispatch.

Wait requests identify a child of this authenticated parent, never authority by
PID alone. Owner maps it to its generation-bound handle and observes terminal
before publishing PID/status. Collect each child once; repeated collection returns
ECHILD. Preserve exact data/EOF, three generations and fifteen reclaims. A wrong
third wait status must fail the parent's independent wait macros before reclaim.
Do not claim a general event loop or dash from this bounded phase ordering.

Reuse pipe create/request and public musl waitpid substitution, rather than a new
process service or FD ledger. Fixed parent prelude/collection phases suffice here;
dynamic interleaving for dash remains next. No old path is removed yet. No kernel,
shared adapter, SDK, dependency version, quota, sibling or released pin change.
Buffers stay live through guarded synchronous calls; create/close completion and
native terminal observation precede publication/retirement. O-02–04, I-01/03–06,
E-01–06 and SE-01–05 apply. Run expanded native/host checks, exact false-status
control, old-image comparison and format/pin/workflow checks on frozen inputs.

Result: [sealed parent-operation evidence](evidence/pipeline-parent-ops-2026-09-15/README.md)
records29 native cases and104 host checks, exact false-status rejection before
reclaim, all37 prior ELF/raw images unchanged and278 frozen runtime inputs. Positive
owner13072 bytes fits16 KiB. No failed attempts occurred. Public waitpid uses a
private archive-derived substitution here; blocking cancellation and arbitrary
signals are not qualified. Wait exchange runs in the single parent context after
pipe close; this adds no general event loop or asynchronous callback support.

#### Interleaved pipeline construction — 2026-09-15

Requirement: remove the all-pipes-before-all-forks restriction before actual dash
integration. The bounded live parent creates First, forks writer, closes First
writer, creates Second, forks relay, closes First reader/Second writer, forks
reader, and closes Second reader. Each copy inherits only the current live table.
The first child has no Second endpoint before that object exists. Existing atomic
stage_fork supports absent object generations; use it without a second ledger.

The opt-in private fork hook sends a canonical 32-byte opcode83/length64 prefix
before the existing snapshot/freeze. A bounded parent intake handles create/close
frames until that prefix, validating authenticated Parent and using the same pipe
core. No request retransmission after effects; preserve reply completion before
reading the next frame. Each stage allows at most four operation frames plus the
snapshot prefix. Reject unsupported/malformed operations. Owner still chooses two
object slots and controls exec/data/wait phases; no general event loop or actual
dash claim. Native handle/readiness checks and fifteen reclaims remain required.

Simpler alternative: retain both initial grants. It cannot exercise dash's reduced
inheritance or creation between forks. Reuse current core/staging instead of adding
process/FD services; no legacy path removal now because its regression cases remain
consumers. Sixteen descriptors, two pipes, five workers, 16-KiB owner and existing
transport bounds remain. No kernel/shared-core/SDK/sibling/pin changes. Existing
C21.1.8 formatting and Rust1.98 edition2024 apply. Pointer buffers remain live
through synchronous masked fork snapshot calls; no new unsafe boundary.

O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply. Run full capacity and host checks
on frozen sources. A deliberately acknowledged-but-unapplied First writer close
must fail live-holder comparison before the second copy/reclaim. Preserve old
image comparison and all attempts; update STATE and existing workflow/reference.

Result: [interleaved evidence](evidence/pipeline-interleave-2026-09-15/README.md)
records31 native cases and104 host checks on278 frozen inputs. All40 prior ELF/raw
images are unchanged. Both new owners are13344 bytes. False close acknowledgment
rejects owner2731; positive preserves exact data/EOF and fifteen reclaims across
three generations. No failed attempts. This is parent operation ordering only;
actual dash, wait-any/nonblocking requests, standard streams and child scheduling
remain next. Existing fixed exec/data/wait phases are not a general dispatcher.

#### Multi-child wait-any intake — 2026-09-15

Requirement: connect the public musl wait3/wait4 path used by dash to the private
three-child pipeline collection scope. Reuse the archive-derived substitutions
already exercised by native-connections. Wait-any selects an uncollected terminal
child; positive PID selects that exact child. WNOHANG returns zero while matching
children remain live, without consuming a child or changing caller status. An
unrelated peer PID and exhausted scope return ECHILD. No PID grants authority:
only the authenticated parent's three current native handles are candidates.

Use opcode68, signed PID at4, options0/WNOHANG at8 and canonical zero padding.
Reply is PID/status, zero/no status, or negative errno/no status. Client validates
returned PID against its scoped children and requested selection before publishing
status, under the existing mask. Reject unsupported options and non-null wait4
resource usage. Preserve existing PID-only variants byte behavior. Early polls run
while replacement children are ready but unreleased; terminal collection runs
following data dispatch. Blocking live-child scheduling, signal interruption,
usage accounting and full dash remain unqualified, not successful stubs.

Simpler alternative is retaining PID-only waitpid; it cannot consume dash's
wait3(-1)/WNOHANG calls. Reuse musl wrappers and existing transport with bounded
owner selection rather than a new process service. No old fixture retirement yet;
no new ledger beyond three collection flags already required for exactly-once
collection. No kernel/shared adapter/SDK/sibling/pin/quota change. No new unsafe
boundary; request/reply and status buffers remain live during masked synchronous
calls. O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply.

Test three early probes (unrelated PID, live wait-any, live exact PID), then mixed
wait3/waitpid/wait4 collection and exhausted scope. A false terminal reply to the
live wait-any must independently fail parent123 then owner2730 before reclaim.
Run expanded capacity and host suites on frozen inputs, compare prior images,
preserve attempts and verify formats/pins/workflow. Update existing status/reference.

Implementation correction: the early reply may still occupy the bounded parent
channel when release begins. The wait-any profile sends release through the
existing bounded backpressure-aware helper; no capacity increase or retry of
already-applied wait operations. Retain the owner2610 failed attempt as regression
evidence; repeat the complete suite on final bytes.

Result: [wait-any evidence](evidence/pipeline-wait-any-2026-09-15/README.md)
records33 native cases and104 host checks on278 frozen inputs. False early terminal
rejects parent123/owner2730 before reclaim. First compile failure and second native
backpressure failure are retained with their source snapshots; final reruns pass.
Positive owner13536 bytes fits16 KiB.41/43 prior images are identical; affected
parent/interleave clients pass their regressions. Fixed early/late phases do not
qualify general blocking wait/data scheduling or signal interruption.

#### Pipeline final stdout grant — 2026-09-15

Requirement: the last replacement worker must forward actual pipeline bytes to
an explicitly granted stdout destination, rather than only validate its input.
Use the existing seven-binding C transport and fragmented dispatcher. After its
validated exec table, only slot4 receives a16-byte stdout grant: reference
0x7a010000|generation, binding1, write-right2, capacity32. The replacement validates
all fields before installing FD1. This is an explicit post-exec grant, not inherited
stdio or authority derived from numeric FD. Other roles keep stdout absent until
redirecting their own pipe endpoints. No console/UART ambient authority.

The owner captures up to32 bytes, requests at most16, on authenticated slot4 only.
Accept canonical write and close; reject wrong caller/reference/binding/direction,
closed references and capacity overflow. Retain completed replies across partial
sends; never reapply a write. Final oracle requires explicit close and exactly
pipe data newline, independently of child status and both pipes' transfer counters.
A bad grant must reject child105 then owner2734 before data/reclaim. A dropped final
write must fail owner2743 despite workers returning success. Both are native tests.

Simpler alternative retains local last-worker byte checks; insufficient because no
output is delivered. Reuse shared client I/O and dispatcher, adding only a bounded
private memory sink with visible state. No new service or general stream framework;
existing larger stream fixtures couple unrelated lifecycle/backend phases and are
not reusable standalone cores. No old path removed yet. Full inherited stdin/
stdout/stderr, actual dash, child-driven exec and console integration remain next.
No kernel/shared adapter/SDK/sibling/pin/quota change. No user-facing output or new
unsafe boundary; buffers stay live during existing guarded calls. O-02–04,
I-01/03–06, E-01–06 and SE-01–05 apply. Run expanded capacity/host suites, negative
controls and old-image comparison on frozen inputs; preserve all attempts and
update STATE/reference/workflow. C21.1.8 and Rust1.98 edition2024 formatting apply.

The native writer additionally forges the final stdout reference on its own
channel; the owner must return EACCES with a canonical empty reply and record one
denial. The final worker checks write-only access locally, forwards bytes using
actual musl write and explicitly closes FD1. The output oracle requires that denial
as well as exact bytes/close, proving reference knowledge alone is insufficient.

Result: [final stdout evidence](evidence/pipeline-stdout-2026-09-15/README.md)
records36 native cases and104 host checks on279 frozen inputs. Both output/grant
mutants fail before reclaim; the positive preserves exact output and fifteen
reclaims across three generations. No failed attempts. New owner14264 bytes fits
16 KiB.22/46 prior images are unchanged; all changed private owners are requalified
and prior client ELFs remain identical. Full inherited stdio and actual dash remain
open; this grant is explicitly post-exec and captures output in memory.

#### Inherited pipeline stdout — 2026-09-15

Requirement: replace fresh last-worker output authority with parent-granted stdout
that survives actual copy and checked exec. Scope this step to stdout; stdin/stderr
and actual dash remain open. Parent receives the existing generation-bound16-byte
output description after its factory grant and installs FD1. Each live fork snapshot
includes that binding. Owner stages an output holding only after validating the
parent's actual holding and the whole pipe snapshot. Native copy/readiness checks
remain unchanged. Children set stdout CLOEXEC except the final reader. Exec validates
its before/after counts and removes holdings before publishing replacement. The
final replacement receives a description of its retained holding, not new authority.
Parent closes its own stdout through the authenticated stream before dispatch.

Keep output ownership in one generation-local object passed through staging,
exec and dispatch. Four holding bits represent parent and three children; no
second descriptor ledger or global mutable table. Use existing snapshot counts,
shared descriptor validation, guarded client operations and capture bounds. Retain
old post-exec grant variants as explicit regressions. Simpler fresh-output grants
cannot prove inheritance or CLOEXEC revocation; this narrow owner extension avoids
a general stdio service and retires no still-tested path yet. No kernel/shared
adapter/SDK/sibling/pin/quota changes or new unsafe boundary. Buffer lifetime and
masked snapshot contracts remain. O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply.

Positive: copied stdout, role-specific exec removal, independent parent close,
existing denied writer forgery, exact captured bytes, all holdings gone,15 reclaims
across3 generations. Negative: deliberately retain writer output authority through
exec; the existing forged-write probe must fail child124 then owner2726 with zero
reclaims. Run complete capacity/host checks and old-image comparison on frozen
sources; preserve attempts and verify formatting/pins/workflow. Use existing
C21.1.8/Rust1.98 edition2024 rules and update STATE/reference.

Result: [inherited stdout evidence](evidence/pipeline-stdout-inherit-2026-09-15/README.md)
records38 native cases and104 host checks on279 frozen inputs. Retained authority
rejects child124/owner2726 before reclaim; positive preserves exact output and
fifteen reclaims. No failed attempts. Both new owners14536 bytes fit16 KiB.47/50
prior images are identical; changed stdout owners are requalified. Inherited
stdin/stderr and actual dash remain open; no console or release acceptance claim.

#### Inherited stdin and stderr — 2026-09-15

Requirement: complete the bounded inherited standard-stream path before actual
dash scheduling. Parent receives stdin (binding0/read/reference0x7a000000|generation,
10-byte source) and stderr (binding2/write/reference0x7a020000|generation,32-byte
capture) descriptions after stdout. Validate full16-byte records before installation.
Fork reserves actual parent holdings; exec retains stdin only in writer and stderr
in all three stages. Parent closes its copies independently before dispatch. Existing
stdout behavior is unchanged. Replacement descriptions report retained authority.

The same generation-local stream owner holds stdin/stderr ownership and cursor/
capture state. Input provides exact pipe data newline then EOF, never fabricated
success for missing input. Each worker writes its role byte to stderr and closes
it; capture checks all three distinct bytes, separate from exact stdout. Writer
uses actual musl read and closes stdin. A relay forges a zero-length stdin read
after CLOEXEC removal and must receive EACCES. Deliberately retain its holding:
child126/owner2726 must reject before reclaim. A dropped diagnostic write must fail
owner2743 despite normal child status. Requests remain16 bytes, captures32 bytes,
owner16 KiB. No capacity or kernel/shared adapter/SDK/sibling/pin change.

Simpler absent streams cannot satisfy real shell inheritance; reuse current
transport, snapshots, native lifecycle and single stream owner instead of adding
services or a second FD ledger. Existing stdout-only variants remain regression
consumers, so none are removed now. Validate both new stream plans before committing
their holdings; invalid plans fail before native publication. Buffers remain live
through guarded synchronous calls, with no new unsafe boundary. O-02–04,
I-01/03–06, E-01–06 and SE-01–05 apply. Run expanded capacity/host checks on frozen
sources, exact negative controls and old-image comparison; preserve all attempts,
format/pin/workflow checks and update STATE/reference. Actual dash and arbitrary
interruptions/general stream services remain outside this witness.

Result: [stdio evidence](evidence/pipeline-stdio-2026-09-15/README.md) records41
native cases and104 host checks on280 frozen inputs. Retained stdin authority
rejects child126/owner2726; lost diagnostics rejects owner2743 before reclaim.
Positive preserves exact input/EOF, output, diagnostic bytes and fifteen reclaims.
No failed attempts; all54 earlier ELF/raw images are identical. Positive owner16096
bytes and controls16176/16032 fit16 KiB. Actual dash scheduling and consumer intake
remain open; this is not console/TTY or assembled-release evidence.

#### Child-requested pipeline exec — 2026-09-15

Requirement: copied children initiate bounded exec through public execve instead
of awaiting an owner token2. Each reports copy readiness, sets live CLOEXEC flags,
requests a denied image and checks EACCES plus unchanged descriptor flags, then
requests its granted replacement. Private opcode84 carries image selector, exact
role and generation in16 bytes with16 zero padding. Parent/channel identity is
not supplied by the frame: owner authenticates the copied slot and maps the only
allowed image to its existing grant. Unknown/malformed requests reject; no ambient
path lookup. This execve shim accepts only this fixture's two paths, three bounded
arguments and empty environment; no general exec API is claimed.

Denial precedes snapshot/freeze and returns a canonical error; no table or native
image changes. Accepted request receives zero, then the child captures its live
table and freezes. Owner validates that exact table/freeze before admission,
CLOEXEC commit and publication. Accepted request alone is not completion. Existing
native denied-image/receipt checks remain. No success returns to old execve context.
Three child requests may queue; the owner still processes them in slot order.
The general event loop, builtin child execution and actual dash remain open.

Simpler token scheduling cannot follow shell-originated exec. Reuse existing
snapshot/replacement pipeline and add only the bounded request/ack prelude, without
new services or wider lookup authority. Existing token modes remain regression
consumers; no obsolete path removed yet. No kernel/shared adapter/SDK/sibling/pin/
quota change. Stack request/argument buffers stay live through masked synchronous
calls; no new unsafe boundary. O-02–04, I-01/03–06, E-01–06 and SE-01–05 apply.

Run complete capacity/host checks on frozen inputs. Wrong denial errno must fail
child127 then owner2730 before reclaim; positive retains exact input/output/
diagnostics and15 reclaims over3 generations. Preserve attempts, old-image
comparison and format/pin/workflow checks. Maintain owner16-KiB limit. Update
STATE/reference; C21.1.8 and Rust1.98 edition2024 rules apply.

Result: [child-requested exec evidence](evidence/pipeline-exec-request-2026-09-15/README.md)
records43 native cases and104 host checks on281 frozen inputs. Wrong denial errno
rejects child127/owner2730 before reclaim. Positive preserves exact inherited-stream
behavior and fifteen reclaims. No failed attempts. Both new owners16360 bytes fit
16 KiB;52/59 previous images are identical, with prior owners unchanged and changed
clients requalified. Actual dash builtin execution and general scheduling remain open.

## Actual dash pipeline builtin review — 2026-09-15

Requirement: replace the private writer's direct write with pinned dash printfcmd
and its buffered output/flush path, through the existing three-stage native pipe.
This is a replacement-worker prerequisite, not copied-child builtin scheduling or
an unchanged shell script. Keep all existing cases and owner authority checks.
Forbidden: successful output without exact bytes/EOF, enlarged owner quota, new
ambient descriptors, fabricated dash implementations, changed pins or sibling edits.

Reuse the verified32 dash objects in dash-inputs (including original notices), with
main wrapped to this fixture entry. Initialize the builtin argument cursor explicitly;
use a literal format and flushall, without claiming shell initialization. The existing
stdio read/EOF check remains separate. C pointers refer to writable, null-terminated
argv storage valid through the call; dash owns its output buffer until process exit.
No kernel, owner, SDK or shared transport change. Existing bounded channel dispatch,
FD cleanup, three generations,15 reclaims and16-KiB owner ceiling remain authoritative.
The enlarged client ELF remains subject to existing loader limits. General dash
signals/errors, parsing, evaluation and inherited builtin state remain unqualified.

Simpler alternative: retain write-only synthetic output. It cannot test dash's
buffered builtin path. Reuse actual immutable objects instead of recreating printf;
no new service or compatibility protocol is needed. No consumed paths can yet be
removed. Test the complete capacity suite and host checks; a wrong-byte builtin
format must fail relay111 then owner2726 before reclaim. Preserve evidence and
compare prior images. Update STATE, native references and the existing workflow
entry. Use the current pinned C formatter; no broad formatting/refactoring.

Outcome: [sealed builtin evidence](evidence/pipeline-dash-builtin-2026-09-15/README.md)
passes45 native cases and104 host checks. Wrong-byte output rejects relay111 then
owner2726, before reclaim. All62 prior images are identical. No failed attempts;
281 frozen inputs, unchanged16360-byte owners,248664-byte new client and74/128
mapped pages. The simple literal-format/flush path works without shell main/init;
this does not qualify general builtin error/signal handling or copied-child state.
Next remove the writer's replacement dependency while retaining scoped descriptor
ownership; coordinate execution/data/wait subsequently, within the owner quota.

## Copied-child dash builtin review — 2026-09-15

Requirement: execute the pinned printf builtin in the actual forked writer without
replacing its image. Other two children retain denied/retried exec. Keep exact
inherited input/EOF, diagnostics, pipe output and scoped wait/reclaim checks.
Forbidden: hidden writer exec, stale descriptor authority, omitted close, weakened
oracles, widened quotas, shared adapter/kernel changes or sibling/pin changes.

The owner skips only writer replacement in this private profile, retaining native
copy readiness and normal dispatch. Writer waits for existing dispatch release,
checks copied TLS identity, closes its inherited capture and unused pipe reader,
redirects its pipe writer to stdout and explicitly probes the closed capture for
EACCES. It consumes/closes stdin and stderr and invokes actual printfcmd/flushall.
Live FD ownership stays in the existing facade and generation-local pipe/stream
owners; no new table or protocol. Captured C argv remains valid throughout the
call. Existing fork rebinding/musl repair and bounded channel guards apply.

Simpler alternative: keep replacing the writer. It loses the builtin's copied
context, so cannot meet this requirement. Skip that unnecessary replacement and
reuse existing dispatch rather than introduce an event loop now. The release token
and sequential peer exec phases remain explicit limitations. Existing replacement
profiles remain regression consumers. No new dependency or unsafe primitive;
link the same32 hash-checked dash objects with original notices and public fork
objects. Source image growth is checked against existing native loader limits.

Run complete capacity and host suites. Require12 admissions (parent/peer plus two
replacement children per generation), all15 normal terminals/reclaims, exact output,
and wrong-byte rejection at relay111 then owner2726 before reclaim. Check per-slot
admission counts to rule out a writer replacement. Compare all prior ELF/raw bytes,
freeze runtime inputs, retain failures, and update STATE/native references/workflow.
Use current pinned Rust/C formatters; do not broaden runtime refactoring.

Outcome: [copied builtin evidence](evidence/pipeline-copied-builtin-2026-09-15/README.md)
passes47 native cases and104 host checks without failed attempts. Exact per-slot
admission counts exclude writer replacement; copied TLS, authority denial, output
and15 normal reclaims pass. Wrong-byte control rejects relay111 then owner2726.
All66 previous images are identical; new owners16296 bytes remain within16 KiB.
Source ELF255048 bytes maps76/128 pages; no quota increase. Next coordinate owner
execution/data/wait handling; actual main/eval and independent acceptance stay open.

## Pipeline workers without dispatch release — 2026-09-15

Requirement: copied builtin and replacement relay/reader initiate I/O after native
readiness, without a separate owner token. Retain parent/peer release, parent early
WNOHANG probes, sequential exec validation and descriptor enforcement. This removes
only the child dispatch-release dependency; it is not a concurrent wait/exec loop.
Forbidden: extra protocol bytes accepted as replies, authority widening, changed
quotas, false full-shell claims or sibling/pin edits.

Use the existing bounded FIFO and retained request/reply dispatch. Workers may queue
requests while peers are replacing; full queues backpressure normally. No new
message, state table, syscall or unsafe primitive. Skip only child release sends
and reads under this private profile. Existing parent close phase remains before
child dispatch. Simpler alternative retains redundant release messages and cannot
exercise autonomous child request initiation. Removing those messages is smaller
than introducing a general scheduler before its wait/replacement states are ready.
Old profiles remain regression consumers; no broad refactor is justified here.

Run all native capacity cases and host checks on frozen inputs. Positive retains
12 admissions with counts3/3/0/3/3 and15 normal terminals/reclaims across3 generations.
An owner inserting the obsolete token only for the copied writer must corrupt its
first close reply and reject writer129 then owner2726 before reclaim, not timeout.
Exact pipe/stdout/input/EOF/diagnostic and authority checks remain unchanged. Compare
all prior images and enforce16-KiB owner limit. Preserve attempts; update STATE,
existing references and workflow. Apply current pinned C/Rust formatting.

Outcome: [autonomous-child evidence](evidence/pipeline-autonomous-2026-09-15/README.md)
passes49 native cases and104 host checks. Obsolete token rejects writer129 then
owner2726 before reclaim; positive retains all stream/admission/cleanup checks.
No failed attempts.68/70 old images identical; changed copied clients requalified,
all previous owners/replacements identical. New owners16296 bytes fit16 KiB.
Next retain parent waits alongside I/O; fixed exec/close/dispatch phases remain.

## Parent wait and child I/O dispatch review — 2026-09-15

Requirement: retain one authenticated parent blocking wait while child I/O advances
in the same bounded dispatcher. Preserve child-local authority, once-only collection,
fragmented replies,12 admissions/15 reclaims, exact streams and16-KiB owner limit.
Forbidden: spinning inside a wait and starving I/O, repeated collection on partial
reply, stale/out-of-scope PID authority, early successful wait or changed SDK/pins.

New private profile skips the old early/late wait phases. Existing profiles retain
all early WNOHANG/denial tests. Parent uses blocking specific waits followed by
exhausted wait-any. A small generation-local wait state holds one32-byte frame,
read/write offsets, collected bits and completion count. Poll once per dispatch
iteration; pending wait yields back to child I/O. Only native handles2..4 can match.
Commit collection once when constructing the retained reply, never on retransmit.
Before allowing initial child I/O, require the first complete blocking wait to be
observed against a live child. Complete only after all children and four replies.
Parent abnormal termination rejects; quota/time bounds are unchanged.

Simpler alternative is the existing sequential wait after I/O; it cannot demonstrate
live wait progress. Reuse the current dispatcher and channels instead of another
service/event framework. No new kernel primitive or unsafe boundary: frame pointers
remain in the owner stack throughout each synchronous trap. No dynamic allocation.
Exec and parent descriptor closure remain setup phases; this is not general exec
multiplexing, signals, full dash main/eval or independent SDK adoption.

Test full capacity and host suites, comparing previous images. A mutant returning
zero for a pending blocking wait must fail parent121 then owner2750 before reclaim.
Freeze inputs and retain every attempt. Record resource costs, update STATE/native
references/workflow, and use pinned Rust/C formatters. Missing capacity remains a
failure, not authorization to raise the owner limit.

Attempt1 failed the unchanged four-code-page linker bound before native cases.
Retain its sources, build logs and passing host run. Revised implementation keeps
shared bounded receive/send routines out of line, avoiding compiler duplication
at their fixed-size call sites. Their validation, timeout and backpressure behavior
remain unchanged. Requalify all older owner modes affected by code generation;
this local size optimization does not change the quota or remove authority checks.

Size follow-up: attempts2–6 remain over the unchanged limit. Attempts3–6 are
link-only probes with retained maps, command receipts and source snapshots, not
native runs. Consolidate the duplicated bounded read/write transfer loop; wrappers
retain borrowed storage and operation direction, and positive counts are now checked
against the requested chunk limit. Wait request/reply phases share one offset.
Keep poll out of line; moving the entire dispatcher out of line was worse and is
not retained. Final probe is40 bytes over. Select rustc opt-level=z only for the new
wait/I/O profile, keeping the same pinned compiler, target, LTO, panic/relocation
and linker limits. This trades optimizer heuristics for size, not contract checks;
qualify both positive and mutant in that exact mode. Old profiles remain opt-level=s.

Final size decision: opt-level=z increased size and is not retained. Attempts8–10
are additional link-only probes, all preserved. Final code keeps opt-level=s, one
out-of-line wait poll, a shared transfer loop with remaining-byte progress, and a
single request/reply offset. Final parent status stays with the enclosing owner's
existing pre-reclaim check; while replies remain, wait polling still rejects parent
termination. Other attempted outlining and slot-width changes are not retained.
The final positive link fits16360 bytes. Re-run every capacity mode on these bytes;
link success alone does not establish live scheduling.

Outcome: [wait/I/O evidence](evidence/pipeline-wait-io-2026-09-15/README.md) passes51
native cases and104 host checks on final attempt11. Ten earlier size-bound failures
and probes are retained; none ran native cases. Positive/mutant16360/16312 bytes fit
the original limit and opt-level=s. Parent121 then owner2750 rejects early zero;
positive proves a live pending wait before child I/O and15 normal reclaims.
All35 changed prior owners are requalified; every old client is identical.
Next qualify wait-any/WNOHANG/scope-denial and retained-reply controls directly in
this state machine before extending exec multiplexing. Old wait-profile coverage
is not a substitute for those new-state tests.

## Wait dispatcher intake qualification — 2026-09-15

Require direct native checks of scope denial, live wait-any/specific WNOHANG,
blocking wait-any, once-only collection and complete fragmented replies in the new
wait/I/O dispatcher. Parent first probes an unrelated peer PID and both live
nonblocking forms, requiring untouched status. It then collects three distinct
scoped child PIDs in any completion order through wait3/waitpid/wait4, probes the
first collected PID again for ECHILD, and checks exhausted wait-any. Eight replies
are required in this private profile. No completion ordering is assumed.

Initial probes leave child I/O held; the first live blocking wait enables it as
before. Initial terminal selection is still forbidden. Retain one frame/offset,
collected bits, explicit authenticated parent channel and existing bounds. A
wrong scope errno and omitted collection bit must independently fail parent131
then owner2750 before reclaim. Exact bytes, all12 admissions/15 reclaims, quota,
partial7-byte replies and old profile regressions remain. No new kernel/SDK/pipe
core operation, sibling edit, pin or service. Existing signals remain out of scope.

Simpler alternative is testing only the prior sequential wait handler; it does not
qualify this state machine. Extend its existing private client and compile-time
reply count rather than add another harness or runtime configuration. This changes
no published contract. Run the complete capacity/host suites, freeze inputs, retain
attempts, compare old artifacts and update existing references/workflow/STATE.
Use current pinned C/Rust formatters and enforce the same16-KiB owner limit.

Outcome: [wait intake evidence](evidence/pipeline-wait-probes-2026-09-15/README.md)
passes54 native cases and104 host checks on final attempt2. Attempt1's harness
prefix-call typo is retained with sources/artifacts; no native cases ran then.
Wrong scope errno and recollection independently reject parent131 then owner2750.
Positive preserves status sentinels, accepts any unique child completion order,
finishes all eight replies and15 normal reclaims.75/77 old images identical; both
changed old owners requalified. New owners16328/16328/16312 fit16 KiB. Next integrate
exec with I/O without losing pending waits; interruption/recovery and independent
consumer acceptance remain separate gates.

## Exec transaction boundaries for dispatch — 2026-09-15

Requirement: make exec's bounded descriptor validation, frozen-image admission and
ledger-commit/publication steps independently callable before advancing their
transport incrementally from the I/O dispatcher. Preserve the exact existing
ordering, denial receipts, cancellation points, CLOEXEC checks and owner quota.
This is a prerequisite refactor, not a claim that exec already interleaves with I/O.

Extract three private functions in copies.rs: validated replacement table, native
admission for an already observed frozen child, and descriptor commit/publication.
Channel receives/sends, freeze/readiness polling and cancellation orchestration
remain in replace. Existing stop-after-admission and stop-during-table controls
stay on their original sides of publication. Caller uses the same authenticated
slot/handle/generation; synchronous argument/descriptor borrows outlive their traps.
No new state, allocation, unsafe primitive, service, dependency or shared ABI.
Inline the extracted steps to retain the original target layout intent.

Simpler alternative is calling the entire blocking replace routine from dispatch;
it would stall unrelated I/O. Duplicating validation inside a new state machine
would create competing authority rules. Share these exact transaction steps now;
nonblocking transport progression follows separately. Keep this extraction confined
to the currently touched exec routine, without broad runtime refactoring.

Run all54 native cases and host checks; compare every prior client/owner artifact.
Existing denied-image, stale publication, CLOEXEC/authority, cancellation and
fragmented table controls are the relevant regressions. Freeze inputs and preserve
attempts. Update STATE and existing native references/workflow with the unchanged
runtime behavior and remaining integration. Preserve16-KiB owner limit and pins.

Extraction follow-up: attempt1 hit the unchanged size guard before native cases;
its host checks passed. Attempts2/3 are preserved link-only size probes. The final
helper fills caller-owned filtered storage and keeps all three extracted functions
out of line; this supersedes the initial inline-layout assumption. That explicit
function boundary fits the tested wait/I/O owner at16360 bytes with unchanged
compiler/linker settings. No denial, receipt, cancellation or publication check was
removed. Qualify all profiles, not only this link probe, on final sources.

Next integration boundary (not implemented here): each replacing child's channel
must advance through request/reply, snapshot intake, observed freeze, admission,
commit/publication, filtered-table/grant output and readiness before becoming an
I/O channel. Keep partial buffers with their phase; never reinterpret an exec reply
as an I/O frame. The copied builtin is already an I/O participant. Polling a channel
must return on backpressure or incomplete readiness rather than entering the old
receive/send wait loop. Preserve the admitted-but-unpublished cancellation boundary.
An overlap witness should hold a peer's partial exec reply while requiring copied-
builtin I/O progress, then finish replacement and normal wait/reclaim. This would
expose the starvation that sequential setup cannot test. It remains planned work,
not qualified behavior or a new published protocol.

Outcome: [exec boundary evidence](evidence/pipeline-exec-boundaries-2026-09-15/README.md)
passes54 native cases and104 host checks on final attempt4. Three earlier size
failures/probes are retained; no native cases ran then. All38 changed owners are
requalified; all clients identical. Largest owner16376 bytes fits16 KiB. Only
copies.rs changes at runtime. Transaction extraction preserves blocking behavior;
actual incremental exec/I/O progression and its overlap witness are next.

## Resumable exec preparation — 2026-09-22

Requirement: replace the private blocking exec transport/readiness routine with
retained per-child progression. One poll performs at most one channel operation or
one bounded transaction step and returns on backpressure; its caller owns scheduling
and the watchdog. Qualify with the existing sequential driver before wiring I/O
interleaving. This step alone must not claim an overlap witness or full shell.

Keep authenticated slot/handle/generation supplied by the owner, snapshot and
filtered tables owned by the progression state, and an offset tied to the current
phase. Malicious or incomplete worker input cannot skip validation, freeze,
admission or commit/publication. Reset the offset only after a complete phase;
never interpret partial exec bytes as an I/O frame. Preserve denied-image receipts,
stale-publication rejection and cancellation before publication and during filtered
output. No pointer survives a synchronous trap, no allocation or shared ABI changes.

The simpler blocking routine cannot return control to a future I/O dispatcher.
A private explicit progression state replaces that routine instead of duplicating
its authority rules or introducing a general async framework. Existing complete
54-case capacity suite covers old profiles and semantic rejection/cancellation;
host checks and optimized native artifacts must pass within unchanged16-KiB limits.
Add focused progression checks if coverage needs them. Preserve every failed attempt.
Update this reference and STATE with actual evidence and remaining work.

Deferred coverage: overlapping exec and copied-builtin I/O must be demonstrated
when dispatch takes ownership of these states, before claiming starvation handling.
Unexpected peer death and lost-reply recovery beyond existing cancellation controls
remain separate integration work; this bounded sequential qualification does not
establish arbitrary scheduling, malicious-state exploration or release readiness.

Scope adjustment before qualification: full retained replacement state exceeded
four code pages in probes1–4 (17200,17376,17392,17248 bytes). It is preserved as
unqualified evidence, not active runtime. This step instead implements the request/
reply handshake in exec_request.rs. Snapshot, freeze, admission, publication,
filtered/grant output and readiness remain in the existing sequential routine.
Probes5–9 refined that narrower implementation but still exceeded the limit.
Probes10/11 fit at15880 bytes after the existing control-trap wrapper is compiled
out of line for exec-request profiles. No traps, validation or quota checks were
removed; original compiler flags and four-page allowance remain unchanged.

The handshake retains a32-byte frame, offset and four request/reply phases plus
completion. One poll performs at most one transfer; EAGAIN preserves state, and
complete repeated polling performs none. Complete requests must match opcode84,
image, authenticated slot, generation and zero padding. Denial precedes the valid
retry; a complete successful reply precedes snapshot intake. The shared single-
transfer helper also serves older blocking transfers, requiring their regression
coverage. Commit reuses one validated pre-exec descriptor count array in the live
profiles. No new authority, heap allocation or unsafe native boundary is added.

Focused host tests use the actual handshake module with a synchronous mock. They
exercise fragments1–16, repeated EAGAIN, exactly one operation per poll, no traffic
after completion and corrupted fields/padding in both requests with exact2746
rejection before any corresponding reply. Run with
`python3 -m unittest discover -s tests -p test_pipe_owner.py`; the normal host suite
also discovers these tests. These are transport-state checks, not a native
adversarial scheduler test. Native qualification still requires all54 cases.

The owner-size constraint is now a demonstrated integration risk. Before another
full exec state machine attempt, review the conformance owner's bounded code
capacity and removable duplication together with the remaining dispatch state;
do not repeatedly tune compiler layout or remove checks to fit new behavior.
A broader budget change, if needed, requires explicit mapping/loader/resource
review and negative boundary tests, not just relaxing a linker assertion.

Native attempt1 passed54 case oracles but was rejected by the final source-integrity
check: Finder changed user/.DS_Store during execution. Preserve the incomplete run
and its input snapshot. Exclude only .DS_Store metadata alongside the existing
__pycache__ exclusion in the capacity harness; actual source integrity remains
checked. Refreeze inputs and rerun the full suite and host checks for qualification.

Outcome (2026-09-23): [sealed request progression evidence](evidence/pipeline-exec-progress-2026-09-22/README.md)
records final native attempt2 passing54 cases and105 host tests on280 frozen runtime
inputs. Largest owner15880 bytes;41/81 prior images identical and all clients
unchanged. Nine failed size probes, two successful probes and the integrity-rejected
native attempt1 are retained. Request polling remains inside the sequential driver;
full retained replacement and exec/I/O overlap still require implementation and
qualification after the owner resource review described above.

## Private owner code budget review — 2026-09-23

Requirement: provide bounded code space for the already attempted retained exec
state machine and its I/O integration without further layout tuning. The prior
full trial required17200–17392 bytes, beyond AENMX004's16384. Adopt a private
AENMX005 envelope with a24576-byte (six-page) supervisor ceiling; retain every
AENMX004 and ordinary bundle limit. Six pages cover the observed trial plus bounded
remaining dispatch work; this is not dynamic growth or a general kernel budget.

Aether owns this fixture; no sibling API or consumer pin changes. The header remains
112 bytes with three image sizes, supervisor size, reserved zero and80 entropy
bytes. Native ABI19, five workers, ten channels, entry0x400000, one RW/NX stack page
at0x800000 and all capability grants remain unchanged. Only the existing opt-in
native-pipeline-capacity build accepts004/005. Normal bundle parsing rejects both.
No new launch flag, heap allocation, scheduler state or service boundary is needed.

Security: the boot envelope is untrusted input to bounds parsing. Zero, oversized,
truncated, trailing or reserved-nonzero data must reject before supervisor execution.
The existing loader maps each code page user RX, removes writable kernel aliases
in every native domain, verifies those entries and zero tail, and maps the stack
RW/NX. Two extra pages consume existing fixed supervisor backing; no backing pool
or worker quota grows. Native tests must execute the sixth page, reject writes to
it, reject instruction fetch from the stack and reject fetch beyond six code pages.
A supervisor fault ends this fixture; no production recovery claim follows.

Simpler alternatives: reuse004 with a larger limit would silently change its
contract; compiler-layout tuning already caused repeated failures; splitting a
single authority owner into services adds unnecessary communication/lifetime cost.
Use a new private envelope discriminator and reuse the existing mapping path.
Retain the existing four-page linker for old fixtures; no larger owner is silently
admitted under004. A new source linker is needed only when the actual extended
owner is compiled in subsequent work.

Run boundary host tests for both versions and normal-parser rejection, then all
existing54 native cases plus wide positive/negative/mapping cases, and zig build
test. Compare prior client/owner bytes; freeze runtime inputs and preserve failures.
Record the envelope in the existing reference/workflow. This qualifies code capacity,
not retained exec scheduling, actual dash, or independent consumer acceptance.

Outcome: [owner budget evidence](evidence/pipeline-owner-budget-2026-09-23/README.md) passes all65 native cases and the host suite (105 Python tests plus Zig/Rust checks). All81 prior client/owner binaries remain identical. The six-page private envelope is qualified; retained exec phases and their I/O overlap witness remain next.

## Retained replacement progression — 2026-09-23

Requirement: extend the qualified request poll through snapshot intake, observed
freeze, admission, descriptor commit/publication, filtered-table/grant delivery and
readiness. Use a private per-child state with immutable owner-supplied handle, slot,
generation and channel bindings. One poll advances one phase, performs at most one
channel transfer or a bounded existing transaction, and returns on incomplete input
or backpressure. The sequential driver remains for this qualification; I/O overlap
is a subsequent integration witness, not claimed here.

Reuse ExecRequest and the existing validation/admission/commit helpers. Keep snapshot
and filtered tables local until native completion or confirmed-stop cancellation.
Preserve the admitted/unpublished cancellation point and seven-byte table-output
cancellation after publication. Cancel orchestration stays in the driver; poll must
not enter its wait loops. Never route this connection as I/O until its report and
native readiness are complete. Report intake deliberately uses at most three bytes
per poll to qualify retained offsets, instead of assuming a single16-byte receive.

Security: malformed worker bytes, stale authority and incomplete tables must not
skip validation, admission or publication order. Bind routing fields at construction
rather than accepting a potentially different slot on each poll. All trap pointers
borrow live state synchronously. No new unsafe boundary, shared authority, dynamic
allocation or kernel behavior. Cancellation still confirms terminal before clearing
retained data/releasing holders. Unanticipated peer death/lost-reply recovery remains
an integration gap; the current driver keeps a bounded watchdog and fails closed.

The simpler blocking routine cannot compose with active I/O. Replacing it with one
explicit state machine avoids parallel authority rules or a general async framework.
Use the qualified005 envelope and a private six-page linker for exec owners;
non-exec fixtures retain004 and their existing four-page linker. Add one legacy004
execution of the small basic exec owner to retain native compatibility coverage.
Run all existing65 cases plus that compatibility case and host tests, compare prior
images and freeze/preserve every attempt. Budget state for the existing one-page
owner stack; multi-child retention and combined dispatcher stack usage must be
reviewed before overlapping states. Update existing references/workflow and STATE.

Final review after native attempt1 passed66 cases: retain previous phase-specific
watchdog diagnostics in the new driver (request2746, snapshot2730, freeze2733,
remaining transport/readiness2734). The driver now shares one100000-poll ceiling per
child rather than resetting an inner loop budget; this bounds total work more
strictly. Record the first successful source set, then rerun qualification on the
final diagnostic-preserving implementation. No native failure prompted this change.

Next overlap integration must give each replacing child one retained state, poll it
before dispatching that child's I/O, and keep the copied builtin eligible for I/O.
Do not interpret queued report bytes as a32-byte I/O request before Done. Preserve
parent descriptor closure and pending wait ownership, with readiness/terminal
observations scoped to the same handle. The witness should hold a peer after a
partial exec reply, require at least one successful copied-writer pipe write while
that reply remains incomplete, then resume the peer and verify complete streams,
waits and reclaim. Requiring the entire stream before resuming a reader could itself
deadlock a bounded pipe; first progress is the relevant starvation witness. Review
combined stack use before retaining the child states together with I/O buffers.

Outcome: [retained replacement evidence](evidence/pipeline-exec-state-2026-09-23/README.md) records final66 native cases and105 Python host tests plus Zig/Rust checks passing. Largest owner17016; legacy-envelope exec13072. All38 changed owners requalified and all clients identical. Snapshot through readiness progression is retained, but the enclosing driver remains sequential; the overlap integration/witness above remains next.

## Exec and pipe overlap witness — 2026-09-23

Requirement: in a private extension of the copied-builtin/autonomous/wait-probe
profile, move the two replacement states into the I/O dispatcher. Release parent
and peer, close the parent's descriptors, then retain parent waits while polling
replacement children and servicing the already copied builtin. Non-overlap profiles
keep the qualified sequential driver and cancellation witnesses.

Bind each state to its existing authenticated handle/route. Until Done, only the
replacement poll consumes its channel; afterward the I/O frame decoder owns it.
Retain two inline states, not references into discarded setup frames; no heap or
new service/authority. Their buffers add bounded stack use under the same one-page
stack. Qualify actual target execution with both states and existing dispatcher
buffers live; future additional participants require renewed stack review.

Hold the relay's denied-exec reply after exactly seven bytes. The copied writer must
complete at least one pipe write while that reply remains incomplete, then release
the hold and finish all streams, eight waits and15 reclaims across three generations.
A deliberate serial-wait mutant suppresses I/O during the hold and must terminate
with exact2760 after32 held dispatcher rounds, with no pipe write; timeout is not
success. Positive completion must verify hold observation and overlapping progress.
All existing authority, CLOEXEC, publication and terminal gates remain unchanged.

The simpler sequential driver causes this starvation; reuse the retained states
rather than duplicating exec rules. This adds only two opt-in private test cases,
using005 and the existing six-page linker. Run all68 native cases and host checks;
compare every prior client/owner artifact and preserve frozen attempts. This does
not establish general interrupted/lost-reply recovery or unchanged full-dash scripts.

Attempt1 exposed an owner stack overflow in the new overlap profile. The exact
binary's start/poll/commit chain needs at least4136 bytes before nested calls,
exceeding4088 usable bytes. The simpler correction retains one active replacement
at a time while continuing I/O for the copied writer and completed replacements.
Reuse that state only after Done; slot ordering keeps pending exec/report bytes
out of the I/O decoder. Concurrent replacement of both peers is unnecessary for
this witness. Keep the one-page stack, validate the final linked call frames and
rerun all68 cases; preserve the failed run and exact-binary stack audit.

Outcome: [overlap evidence](evidence/pipeline-exec-overlap-2026-09-23/README.md)
records68 native cases and105 Python host tests plus Zig/Rust checks passing on
final inputs. Prior81 images are unchanged. The one-state correction retains the
one-page stack; exact-binary reviewed call depth3920 leaves168 usable bytes and must
be revisited on growth. The initial overflow is retained as a failed product attempt.
Next qualify confirmed-stop/partial-frame cleanup during active I/O before consumer
exposure; unchanged full-dash workloads and assembly acceptance remain outstanding.

## Interrupted replacement during pipe I/O — 2026-09-23

Before implementation: extend only the private overlap fixture. Stop slot4 after
publication and exactly seven filtered-table bytes, while writer/relay I/O remains
active. Retain the partial frame until exact native143/kind3 terminal observation;
then clear replacement buffers and release its pipe and standard-stream holders.
Continue the surviving relay, requiring EPIPE on its second-pipe writes while it
drains the first pipe to EOF. Parent wait maps this scoped stop to SIGTERM15 and
collects all three children once; other children exit normally. No public ABI,
SDK, signal delivery or kernel policy change. Update native reference and workflow.

The untrusted child's partial channel bytes cannot authorize cleanup. Authenticated
handle/slot/generation and terminal observation remain the boundary. No frame may
be decoded as I/O before readiness or after cancellation, and no backing may be
reused before terminal/reclaim. Add omission controls for stop and frame clearing:
exact2770 after32 held polls for a live child, and2772 for retained partial state.
Neither timeout nor generic panic is success. Reuse the existing pipe terminal
operation and add only bounded standard-stream holder cleanup. No new allocations,
unsafe/FFI boundaries, participants, stack pages or dependencies. Review final linked
stack use and run the complete71-case native suite plus host checks on frozen bytes.

The simpler existing all-child cancellation cannot demonstrate survivor progress;
use one polled cleanup boundary in the existing retained state. Avoid a separate
recovery framework or parallel descriptor ledger. This qualifies one injected
post-publication stop, not arbitrary peer faults, lost replies or interrupted parent
waits. Those need review before general consumer exposure. C uses existing scoped
style (no whole-file migration); Rust uses rustfmt1.98 edition2024. All attempts and
source sets remain retained, with verified generated duplicates removed afterward.

Attempt1: all prior68 cases passed; the new positive reached result100/reclaimed15,
then the harness incorrectly required a stop log line. Forced stop intentionally
has no normal terminal log. Remove that nonexistent-marker assertion; preserve the
owner's exact143/kind3/readiness0 observation and final terminal checks, parent
SIGTERM assertion, admissions/reclaim counts and explicit omission controls. This
is a harness-oracle failure, not a native failure. Rerun71 cases on final inputs.

Outcome: [interrupted overlap evidence](evidence/pipeline-exec-overlap-stop-2026-09-23/README.md)
records71 native cases and105 Python host tests plus Zig/Rust checks passing. All83
prior images remain identical; new maximum18072 fits005. The queried stop/clear/
holder-release sequence, EPIPE/EOF survivors and signal-status wait all complete
three generations. Missing-stop and retained-frame controls reject2770/2772. The
initial nonexistent-log harness failure is retained. Pre-publication overlap
cancellation and interrupted parent replies remain next; no general shell handoff.

## Cancellation before publication with active I/O — 2026-09-23

Before implementation: extend the existing interrupted-overlap fixture to stop
slot4 immediately after actual image admission and before descriptor commit/native
publication. Use its existing retained Commit phase and the same authenticated
handle, generation and channels. The admitted image remains frozen and unready;
no replacement transport or I/O may run. After exact143/kind3/readiness0, require
publication of that stopped instance to reject EBUSY(-16), then clear retained
state and release its pre-commit pipe/standard-stream holdings. Survivors must still
drain the first pipe to EOF, observe second-pipe EPIPE, and complete scoped waits
and15 reclaims over three generations. No protocol, kernel or SDK change.

Reuse the same cleanup path rather than add another cancellation state machine.
The pre-commit holder set differs from the post-commit set: terminal cleanup must
remove either without pretending the descriptor commit happened. Untrusted peer
bytes and stop acknowledgment remain insufficient authority for cleanup; source
state is cleared only after queried terminal. Missing-stop and retained-state
controls must still reject2770/2772 before reclaim. Add three opt-in cases, run all74
native cases and host checks on frozen inputs, compare prior images and review the
linked positive's stack. Rust formatting stays1.98/edition2024; no new unsafe code,
heap, dependency, stack page or participant. Preserve every attempt and released
pins. Interrupted parent wait replies remain next; arbitrary peer-fault recovery
and consumer exposure are not implied by these injected cancellation boundaries.

Outcome: [pre-publication cancellation evidence](evidence/pipeline-exec-overlap-admit-2026-09-23/README.md)
records74 native cases and105 Python host tests plus Zig/Rust checks passing in one
attempt. The admitted/frozen stop rejects later publication, releases pre-commit
holdings only after terminal confirmation, and finishes survivor I/O/waits/reclaim.
Both omission controls reject exactly2770/2772.85/88 prior images remain identical;
all clients are unchanged and the three changed stop owners requalified. Interrupted
parent wait replies remain next, before general consumer/full-shell exposure.

## Interrupted parent wait reply — 2026-09-23

Before implementation: in the private exec/I/O overlap profile, stop the parent
once the first successful child result has been collected and seven of32 reply
bytes sent. Preserve that result's collected bit across partial delivery and stop
observation. Clear the abandoned reply only after exact143/kind3 from the bound
parent handle; mark cancellation separately from the completed-reply count. Do not
fabricate delivery, re-collect the child or route another request on the dead parent.
The parent's descriptors were already closed before the wait dispatcher started.
Surviving children retain their own holders and must finish all streams and reclaim.

Hold final-reader I/O until parent cancellation, requiring that reader to be live
at the interruption. This makes survivor progress after interruption observable
without another service or retry protocol. Keep the existing initial wait probes;
require three complete probe replies, one collected result, and an abandoned seven-
byte successful reply. Add missing-stop2780 (32 held polls), lost-collection2781 and
retained-reply2782 controls with zero reclaims. Generic failure/timeout is not success.

The untrusted reply consumer cannot authorize early cleanup; exact native terminal
is the boundary. Retain buffers synchronously and keep collection ownership through
cleanup. No new unsafe/FFI, heap, kernel/SDK API, dependency, authority, stack page or
participant. Reuse the existing Wait state with explicit bounded cancellation fields;
a new retry/session protocol would be unnecessary for this terminal-parent case.
Run all78 native cases and host checks on frozen inputs, audit linked stack usage,
compare prior images and preserve all attempts. Update STATE and workflow/reference.
Rust remains1.98/edition2024. This does not establish retry after a lost reply to a
live parent, arbitrary transport failure, orphan/reparent policy or shell adoption;
resolve those at the actual consumer boundary before exposing broader semantics.

Outcome: [wait interruption evidence](evidence/pipeline-wait-interrupt-2026-09-23/README.md)
records78 native cases and105 Python host tests plus Zig/Rust checks passing in one
attempt. Collection survives the partial reply and exact parent stop; reply cleanup
is distinct from delivery, and surviving workers complete15 reclaims. Omission
controls reject2780/2781/2782. All clients remain unchanged;13 changed private owners
are requalified. Next integrate the actual dash consumer path with a narrow failure
contract; live-parent retry and arbitrary transport recovery remain unsupported.

## Actual dash path: pre-exec descriptor traffic — 2026-09-23

Trace before implementation: userland's unchanged pipeline.sh is `printf "pipe
 data\\n" | /inputs/helper copy | /inputs/helper copy` (the actual file has no
newline within its string). The existing pipe-shell-client.h invokes real dash
main with native main/jobs objects, but uses the older two-process owner. Capacity's
live-worker.c instead creates three children explicitly, assigns fixed descriptors
and exec arguments, and only calls the printf builtin. Its parent construction,
report/readiness, exec path/argv, descriptor layout and fixed wait probes are not a
drop-in actual-main contract. No full-dash handoff can follow from fixture counts.

First concrete mismatch: real dash redirects/closes inherited descriptors before
exec. Replacement::Request currently consumes that channel exclusively and rejects
ordinary descriptor operations as malformed exec. Add an opt-in multiplexed intake
only while the bound replacement awaits a complete exec request. The existing I/O
dispatcher owns frame accumulation, routes opcode84 to validated exec intake, and
routes ordinary requests through existing scoped pipe/standard-stream handlers.
Exec replies, snapshots, freeze/admission/publication, reports and readiness retain
exclusive channel ownership. Finish any pending I/O reply before accepting exec;
no decoder may consume the same bytes twice or apply an operation again on partial
reply delivery. Later replacing slots remain parked until their turn.

Witness: both helper-source children close inherited stdin before the first exec
request, then complete denied/retried exec, streams, waits and15 reclaims. Their
snapshot must omit fd0 and the same ledger must record that close before commit.
Gate the copied writer's first pipe write until the existing held-denial witness,
so added pre-exec traffic cannot invalidate the overlap oracle. Reject a control
that refuses ordinary pre-exec traffic with exact2790 before reclaim. Reuse bounded
frames and existing handlers; no new service, authority, allocation, kernel/SDK API,
unsafe boundary or dependency. Client paths/argv remain the private subset; stdin
closure is an integration prerequisite, not real dash execution or the full script.

Untrusted opcode84 still requires canonical slot/generation/image/padding checks;
channel identity supplies the caller. Buffer ownership changes only at complete
frame boundaries. This is simpler than a parallel descriptor service or speculative
retry protocol. Run all80 native cases plus host checks, review linked stack usage,
compare previous images and preserve failures. Rust1.98/edition2024; retain scoped
C style without migration. Update STATE/workflow. Next actual descriptor remapping
and consumer orchestration must reuse this seam, not fabricate successful main/init.

Attempt1 failed compilation in the new cfg branch before any native case ran:
Rust slice assignment required fill(0), not assigning an array to a slice. Preserve
the failed compiler/audit receipts and inputs; correct that expression and rerun.

Outcome: [pre-exec I/O evidence](evidence/pipeline-preexec-io-2026-09-23/README.md)
records80 native cases and105 Python host tests plus Zig/Rust checks passing on final
inputs. Both helpers close stdin through scoped intake before denied/retried exec;
full streams/waits/reclaim and exact2790 refusal pass. All95 prior images remain
identical. Attempt1's native-only compile failure is retained. Actual descriptor
remapping and consumer orchestration remain next; no actual-main/full-script claim.

## Pre-exec stdin/stdout remapping — 2026-09-23

Before implementation: extend pre-exec intake to the descriptor layout dash's
pipeline helpers need. After closing inherited stdin, sources dup their pipe reader
to fd0; relay dup2s its pipe writer onto fd1, closing inherited capture through the
existing scoped dispatcher. Final reader retains its capture fd1. Keep old pipe
aliases only as CLOEXEC and add a CLOEXEC reader alias at fd10. Denied exec must
preserve every descriptor flag; successful replacement must inherit fd0/1/2 and
remove all fd3..15 aliases. Replacement helpers consume that table directly and do
no post-exec redirection. Parent/copy/path/argv orchestration remains private.

Source snapshots must match the new layout and real holder ledger before commit;
filtering uses the existing shared descriptor transaction. Descriptor numbers are
not authority: authenticated channel/slot/generation and binding rights remain the
boundary. Canonical input, partial reply ownership, stop/reclaim and endpoint lifetime
rules stay unchanged. Reject fd0 incorrectly marked CLOEXEC or an unflagged fd10
alias with exact2733 before replacement admission; neither should reach readiness.
Full streams, denied-exec preservation,8 waits and15 reclaims remain positive oracles.

Reuse the existing intake/commit/facade instead of adding a second redirection path
or descriptor service. Only opt-in source/replacement witnesses, expected layout
and harness selection change; no kernel/shared core/SDK/sibling/pin/new dependency,
unsafe boundary, heap or resource increase. Rust1.98/edition2024 and scoped existing
C style. Run all83 native cases and host checks on frozen bytes, compare previous
images and audit linked stack. Preserve attempts. Then address consumer path/argv
and dash-driven creation/wait; this step does not claim unchanged full-script/main.

Outcome: [remapping evidence](evidence/pipeline-preexec-remap-2026-09-23/README.md)
records83 native cases and105 Python host tests plus Zig/Rust checks passing in one
attempt. Helpers inherit fd0/1/2 directly; denied exec preserves flags and successful
exec removes all old aliases. Incorrect flags reject2733 before replacement admission.
All98 prior images remain identical. Consumer path/argv and dash orchestration remain
next; actual-main and unchanged full-script acceptance are still outstanding.

## Consumer helper arguments at exec — 2026-09-24

Before implementation: support exactly /inputs/helper with argv [/inputs/helper,
copy] and empty environment in the opt-in remapped capacity profile. The bounded
request carries argc2 at byte16 and copy at bytes20..23, with trailing zero bytes;
the image selector defines argv0. The authenticated owner validates this canonical
vector before acknowledging exec and installs the same two arguments at admission.
Path bytes select only an already granted image; no path resolution or ambient
execution authority is introduced. /denied remains the explicit denial witness.
Unsupported paths, argv and environment fail explicitly before sending a request.
Replacement checks the consumer vector and obtains fixture role/generation from
native PID/PPID, removing private role/generation arguments from the new profile.

Forbidden: silently accepting untransmitted arbitrary arguments, losing descriptor
flags on failure, accepting a forged vector, or admitting a replacement after malformed
intake. Keep canonical channel/slot/generation/image validation, partial reply ownership,
stop/reclaim, scoped descriptor transactions and old profiles. Positive probes cover
unknown path, wrong argv0/argument/count and nonempty environment before denied/retried
exec; one wire mutation must reject2746 before helper replacement admission. Full
streams, waits and reclamation remain required. Run all85 native cases and host checks,
compare prior images, audit linked stack and preserve attempts on frozen sources.

This fixed vector is simpler than a general argv serialization/allocation service
and satisfies the immediate traced workload. It adds no service, heap, unsafe boundary,
kernel/SDK API, resource budget or dependency. Rust1.98/edition2024; retain existing
scoped C formatting. Public argv/env transport remains separate. The unchanged consumer
helper allocates a4096-byte buffer; review its separate native worker stack and remove
fixture report/readiness assumptions when integrating that body. The Rust owner has
a one-page stack; do not confuse that with the worker stack. Actual helper body and
dash main/init/eval/process orchestration still need integration and consumer acceptance. This step only qualifies
consumer path/argv plus existing inherited descriptors, not full pipeline acceptance.
Update STATE, companion reference and workflow; preserve released pins and sibling bytes.

Outcome: [helper argument evidence](evidence/pipeline-helper-args-2026-09-24/README.md)
records85 native cases and105 Python host tests plus Zig/Rust checks passing. The
consumer vector reaches replacement admission; forged wire bytes reject2746 before
admission. Of105 prior images,75 are identical;30 legacy owner images changed and
pass regressions, with representative constant-pointer equivalence reviewed. Actual
helper body, dash orchestration and independent consumer acceptance remain open.

## Actual consumer helper in the pipeline — 2026-09-24

Before implementation: compile the existing hash-pinned dash-helper-inputs/helper.c
unchanged with its established private main symbol and call its copy branch in both
remapped replacement workers. The wrapper retains authenticated bootstrap, descriptor
validation, private report/readiness, diagnostics/rights probes and explicit descriptor
cleanup after main returns. Replace the fixture's read/compare/write loop only in this
opt-in profile. Do not claim actual dash process orchestration or generic exit cleanup.
Use the already qualified /inputs/helper copy vector and existing owner bytes.

The consumer asks read for4096 bytes and retries partial writes/EINTR. The existing
facade limits each transfer to16 bytes without widening rights or copying beyond the
reply length; current ten-byte workload fits those bounds. Native C workers have a
separate64-KiB stack mapping (initial RSP at base+0xc000), unlike the one-page Rust
owner; audit the linked helper/wrapper frames and preserve that resource distinction.
No new kernel/SDK API, owner state, grant, buffer quota, unsafe boundary, dependency
or sibling input is needed. Verify the existing source pin before compilation; retain
its BSD-2-Clause notice. Do not reformat pinned source. Keep scoped existing C style.

Forbidden: substituting a private copy loop while claiming consumer execution, passing
with no helper output, changed inherited authority, changed old profiles, or reclaim
before confirmed termination. Positive requires unchanged bytes/EOF through both pipes,
all diagnostics,8 waits and15 reclaims. A control skips only relay main after the held
exec witness has forced the copied writer's ten-byte write; wrapper closes its ends,
so the real final helper reads EOF with no output. Require exact2743 missing-capture
rejection with zero reclaims, not a timeout or generic failure. Run all87 native cases
and host checks on frozen sources; compare old images and owner identity and preserve
all attempts. Existing malformed exec, rights, interruption and cleanup tests remain.

Calling the existing body is simpler and more relevant than another helper reimplementation.
The wrapper is still needed for the private startup seam; retain it explicitly until
dash orchestration supplies a replacement. No new service boundary or abstraction.
Update STATE, companion reference and workflow with scoped evidence. Independent
consumer replay, environment forwarding, dash creation/wait and full-script acceptance
remain open. Next trace actual-main integration using the existing startup facilities.

Outcome: [consumer helper review](evidence/pipeline-consumer-helper-review-2026-09-24/README.md)
records87 native cases and105 Python host tests plus Zig/Rust checks passing. Both
replacements execute the pinned copy body; skipping relay main rejects2743 for missing
output despite normal worker exits. All110 previous images are identical. A post-run
summary assertion over-required parent exit; the linked review preserves and corrects
that analysis failure without changing native evidence or runtime checks. Actual dash
main/init/orchestration and independent script acceptance remain next.

## Shell wait scheduling prerequisite — 2026-09-24

Before implementation: tracing actual-main integration found a private wait protocol
constraint: pipes::dispatch does not advance children until Wait.started, and Wait
requires a first blocking wait with no exited child plus exactly eight fixture replies.
Real dash cannot promise that scheduling or issue conformance probes as lifecycle work.
Add an opt-in natural collection profile: child exec/I/O proceeds independently of
parent wait arrival; wait finishes only after all three authorized children are collected
and the final reply is fully delivered. Preserve the old fixed-probe witnesses unchanged.
The source parent issues three ordinary waitpid(-1) calls, checks unique PIDs/status,
and exits without extra probe/exhaustion traffic. Actual dash main is still next.

Caller authority remains its authenticated parent channel and existing child set.
Collection is recorded once when producing a reply; partial sends retain it and cannot
finish early. No ambient PID lookup, changed status encoding, unbounded request queue,
new service/unsafe boundary or resource budget. A forced-late schedule delays first
wait intake until all three children have native terminal records while allowing I/O.
The positive must complete all bytes/EOF and15 reclaims over three generations. A
control restores the old pre-exit requirement under that schedule and must reject2751
with zero reclaims; watchdog failure is not acceptance. Existing interrupted-reply,
wrong-scope, once-only and malformed request regressions remain in the full90-case suite.

This removes dependence on arbitrary probe count for the new profile instead of adding
fake calls around dash. Reuse the retained Wait state and canonical decoder. Existing
fixed tests remain compatibility witnesses until real-main replacement is qualified.
Rust1.98/edition2024 and existing scoped C style; no dependency/pin/kernel/SDK/sibling
change. Freeze runtime inputs, run host and full selected native checks, audit owner
stack, compare images and preserve all attempts. Update STATE/reference/workflow.
Actual dash startup, parent construction, private readiness and argv/env limitations
remain integration work; this scheduling prerequisite is not full-script acceptance.

Outcome: [natural wait evidence](evidence/pipeline-natural-wait-2026-09-24/README.md)
records90 native cases and105 Python host tests plus Zig/Rust checks on final attempt2.
First wait may observe already exited children; completion follows collection and full
reply delivery, not a probe count. Restoring the old ordering rejects2751. All114 prior
images remain identical. Passing attempt1 is retained because review removed residual
counter logic before rerunning. Actual-main/startup and parent construction remain next.

## Real dash startup inside the pipeline — 2026-09-24

Before implementation: replace the copied writer's direct printfcmd call with the
pinned native dash main object and real main/init/eval for a bounded printf command.
Both downstream consumers remain the unchanged helper copy body; the parent still
constructs the job. This is real shell startup inside the pipeline, not dash-driven
construction or unchanged pipeline.sh acceptance. Keep old builtin profiles intact.

The owner delegates only the copied writer a validated64-byte startup packet: existing
AECAT003 identity metadata shape (four advisory1000 IDs, version1, zero reserved), plus
its connection-scoped read-only /work directory grant shape (reference, rights1, kind1,
generation, reserved zeros). Validate the complete packet and native auxiliary IDs
before publishing IDs/directory. Use existing STARTUP_IDENTITY/STARTUP_CWD libc facades
and real musl signal operations, with the pinned native main ENV guard configuration.
No successful identity/cwd/signal stubs. Identity is advisory; a path/UID is not authority.

Outcome correction from the parent-driven review below: this earlier profile linked
musl signal functions but did not enable native public routing. Its completed evidence
qualifies identity/cwd and shell evaluation, not successful public signal operations.
The original prospective intent above is retained; sealed evidence is unchanged.

Route directory op4/5 through the existing retained dispatcher frame/reply, independently
of pipe byte counters. Only authenticated slot2 and current directory reference authorize
/work or dot. Stale/wrong references, other participants, malformed padding/length and
path escape reject explicitly with canonical zero reply tails. This immutable namespace
is a private startup service view, not a persistent filesystem. Borrow the existing
AECAT003 shapes/semantics; a small pure local decoder avoids coupling the old blocking
connection transport to retained dispatch. No new global directory table or service.
The startup send occurs before dispatcher I/O and the writer receives it before any
request, keeping channel ownership explicit. Exit wrapper closes only the copied shell's
live descriptors; other roles retain current lifecycle behavior.

Positive checks native ID agreement, cwd and denied reference queries, then actual dash
prints ten bytes through both helpers, with EOF/three waits/15 reclaims. Mutating only
the shell command's first output byte must reject2743 at capture with zero reclaims.
Host decoder checks cover caller/ref authority, malformed data and path bounds. Run all
92 native cases and host checks on frozen inputs; verify main/object pins, audit linked
owner stack and shell calls, compare legacy images, preserve attempts and verify archives
before duplicate cleanup. Rust1.98/edition2024; existing C style, no pinned input edits.

Direct builtin invocation is simpler but cannot qualify init/eval. This removes that
shortcut in the new profile without adding a shell reimplementation, dynamic namespace,
resource budget, kernel/SDK API, unsafe interface, dependency or sibling/pin change.
Startup packet buffers remain stack-owned during synchronous transfer; no pointers cross
native authority boundaries. Update STATE/reference/workflow; parent construction,
readiness, general argv/env and independent full-script/serial-shell acceptance remain.

Outcome: [dash startup evidence](evidence/pipeline-dash-main-2026-09-24/README.md)
records92 native cases and105 Python host tests plus Zig/Rust checks passing. Real main,
init and evaluator run in the copied writer, composing with both actual helper bodies.
Wrong shell output rejects2743; all118 prior images are identical. The owner stays within
existing resource bounds. Parent-side main/job creation remains next. Native malformed
bootstrap/truncation permutations require coverage before broadening the fixed-owner
startup seam; no general or independent full-shell acceptance is claimed.

## Natural pipe descriptor layout — 2026-09-24

Before implementation: the real parent pipeline must use the descriptors returned by
pipe(), including reuse of fd4/5 for the second pipe, and close redundant aliases
before exec. The current fixture moves these to fd5/6 so that descriptor numbers
match internal bindings, then requires CLOEXEC aliases in its replacement snapshot.
That test layout is not a shell contract. Add an opt-in natural-descriptor profile
alongside real copied-writer main and both unchanged helper copy bodies. Preserve
legacy profiles. Keep the second pair at fd4/5, take live fork snapshots as returned,
duplicate the selected endpoints to fd0/1 and close all redundant pipe descriptors
before requesting exec. The native replacement must receive exactly fd0/1/2 with
existing binding identities and rights, not arbitrary descriptors or new authority.

The protected state is each pipe's generation-bound holder ledger and inherited
stream authority. Closing a descriptor must retire its binding only after the last
local alias, without losing another pipe whose descriptor number reuses that slot.
Denied exec must preserve the remaining descriptors; successful exec and terminal
cleanup must release all holders. A deliberately retained unflagged fd10 alias must
fail the exact snapshot check2733 before admission/reclaim, not hang or silently gain
an inherited descriptor. Positive: ten bytes, both pipe EOFs, three collected children
and15 reclaims over three generations. Full94-case native suite, host checks, linked
owner stack audit and previous-image comparison on frozen sources; retain all attempts.

Simpler alternative: continue rearranging descriptors in the client. That hides the
actual shell layout and adds unnecessary alias churn. The new profile removes that
churn and checks the already-supported descriptor-to-binding separation. This does
not generalize accepted replacement vectors or add a service, unsafe boundary,
dependency, ABI, resource budget or shared standard. Existing guarded libc adapters
own synchronization and buffers; unchanged pipe/exec cores own authority validation.
Update STATE, companion reference and workflow. This remains a fixture prerequisite:
parent main/job creation, bootstrap placement, private readiness and inherited env
still need integration before unchanged pipeline.sh or full-shell acceptance.

Outcome: [natural descriptor evidence](evidence/pipeline-natural-fds-2026-09-24/README.md)
records both attempts passing94 native cases and final105 Python host tests plus
Zig/Rust checks. Reused descriptor numbers retain the correct distinct bindings;
redundant aliases are closed before replacement. Extra fd10 rejects2733 before
admission with zero reclaims. Final122 prior images are identical after isolating
the validator at compile time; attempt1 and its code-generation differences remain
retained. Actual parent main/job creation, fork readiness and environment remain next.

## Parent-driven consumer pipeline — 2026-09-24

Before implementation: execute the pinned unchanged userland pipeline script in the
parent's actual dash main/init/eval, letting upstream dash create both pipes, fork all
three children, remap/close their descriptors, execute both helpers and collect jobs.
Reuse the native main and fork-exec jobs objects, existing musl copy repair, capability
factory and retained exec/I/O dispatcher. Move startup metadata to the parent. Its
immutable directory view authorizes startup queries before the first fork. Private
report/readiness belongs in the copy adapter, not a replacement shell evaluator.
The helper copy body remains unchanged. No successful stubs for unsupported calls.

Replace fixture ordering constraints only in an opt-in parent profile: a real exec
request need not first ask for a deliberate denial; a parent may close pipe ends and
standard descriptors while collecting children. Retain complete fragmented requests
and replies with one owner per channel. Collection remains once-only and cleanup
waits for complete replies and native terminal confirmation. Preserve legacy tests.
The helper selector accepts exactly argv [/inputs/helper, copy] and an explicitly
validated fixed environment profile (PWD=/work, WITNESS=value, LC_ALL=C,
PATH=/nonexistent), transported as an exact bounded profile ID/count and reconstructed
for native admission. This is a bounded workload contract, not arbitrary argv/env
support; unknown fields/vectors fail rather than silently dropping environment.

Authority remains the authenticated parent/child channels, current generations and
inherited bindings. New routing cannot turn a path, PID or descriptor number into
ambient authority. No kernel/SDK ABI or new resource budget. Review stack growth
against the one-page owner stack before qualification; use existing state storage
where possible. New adapters lend stack buffers only through synchronous traps;
no raw pointer survives a return. Parent environment and script buffers remain live
through main and copied private address spaces. Userland remains acceptance owner.

Simpler alternative: keep the manual fixture driver. It cannot qualify dash's job
bookkeeping or unchanged pipeline.sh. Remove its explicit probe traffic and release
ordering from the new profile, retaining old profiles as compatibility witnesses.
Target positive: exact ten-byte output, clean child/parent statuses, EOF and complete
reclaim over three generations. Mutated output and leaked-descriptor controls must
reject semantically, not by timeout. Preserve every exploratory failure, freeze inputs
for qualified runs, run full affected native and host checks, compare old binaries,
audit linked stack, and update STATE/reference/workflow. Matching runner/connection
and independent consumer replay remain required before broad handoff claims.

The same parent integration will also consume unchanged early-reader.sh: a two-child
job with actual helper pump/one, ignored SIGPIPE, one consumed byte, EPIPE and pump
status42, pipefail verification and exact `epipe ok` output. Slots0/1/4 remain the
parent and unrelated fresh capacity peers; only copied slots2/3 are the parent's
collectible children. No nonexistent third job is invented. The second pipe remains
uncreated, with no delegated endpoints. Existing absent-object holder validation
applies. Preserve fixed five-domain resource limits and15 total domain reclaims.
Route parent stdout writes through its existing scoped capture while waits progress.
A wrong EPIPE errno must be rejected through actual helper status, not timeout.
This adds only the second already-required consumer script, not general job control.

Exploratory findings: attempt1 failed compilation due a legacy-only local referenced
by unreachable helper fallback; attempt2 exposed copy-rebind channel initialization
that lived in the manual caller. Move that initialization into the real fork hook.
The existing launch ABI stores environment at strings[4..8], regardless of argc.
Attempt3 passed the unchanged pipeline but lacked public signal build flags. Attempt4
early-reader exposed that gap through actual helper97 (signal() failure). Enable
existing public/private signal actions and signal-copy options for the new parent
profiles, and require a successful native SIGCHLD action query before main. A disabled
routing control must retain parent138 and reject2730; linking musl calls alone is not
runtime signal evidence. Earlier copied-main packets remain immutable but their public
signal-operation claim is narrowed: routing was not enabled there. Attempt5 passes
actual early-reader with routing enabled. Final qualification must replay both scripts
and all controls on one frozen source set; no exploratory pass substitutes for that.

The bounded --case option on scripts/pipeline_capacity.py selects one exact case and
records selected_case in the report; unknown names fail. Omit --case for full coverage.
It is for targeted diagnosis/independent replay, never a full-suite claim. Exact script
and native main/jobs/helper pins are validated offline before consumption. Host tests
exercise fragmented exec and malformed environment/profile bytes under legacy, parent
and early-reader configurations, plus each directory owner's cross-slot denial.

Matching runner review found a stale startup-client expectation: it required EINVAL
from getpid with a nonzero unused register, although the current zero-argument native
contract correctly ignores unused registers (already exercised by capacity workers).
Before fixing the assertion, preserve the failing runner receipt (client62/owner1501).
Replace it with equality to the independently checked actual caller PID, including
nonzero values in all four supplied unused registers. Do not change kernel behavior
or treat register contents as a requested PID. Existing wrong-PID controls must still
reject. Prototype this in an isolated generated copy while the frozen connections
run finishes; only then change the source and qualify the final matching set.


Outcome: [sealed parent-driven evidence](evidence/pipeline-parent-2026-09-24/README.md)
qualifies unchanged pipeline.sh and early-reader.sh, actual parent main/job creation,
unchanged helpers, exact output/status/cleanup and all five semantic controls.
Final matching101 capacity+358 connections+431 runner cases pass (890 native),
with105 Python host tests plus Zig/Rust, on287 runtime inputs. Runner's stale
unused-register assertion is corrected; kernel behavior is unchanged. All failed
and successful attempts are retained. Final program/stack audits and exact native
terminal/rejection checks pass; verified archives precede duplicate cleanup.

This completes producer delivery of the two remaining bounded workload scripts.
Independent userland replay/acceptance remains open; its matrix stays10/12 until
that owner records its own result. No SDK publication or full shell/R1 claim follows.
Next combine the accepted pipeline path with the already-qualified serial sessions
and shared SDK/runtime, then filesystem/package/sys-init assembly. Do not replace
that integration with another manual shell-orchestration fixture. Public default
SIGPIPE delivery, broader interruption/TTY behavior and independent security/resource
review remain separate gates before broader exposure. No sibling or released pin changed.

## Interactive parent pipeline — 2026-09-24

Before code: independent userland now records12/12 unchanged scripts in its sealed
`docs/evidence/dash-parent-consumer-2026-09-24` packet. The next executable requirement
is entering a pipeline at real dash's serial prompt, seeing its output and a returned
prompt, then entering a builtin/exit command in the same shell. Repeat three fresh
shell generations with the existing five-worker cleanup. This is a bounded integration
step toward composing all accepted paths in one runtime, not installed SDK/R1 closure.

Use AENMX006 / bootstrap ABI20: the AENMX005 three-image/80-byte entropy layout,
24-KiB owner code and existing six-domain memory/channel limits, with an additional
non-transferable bootstrap-owner UART grant at selector0xf001. Preserve the six
bootstrap arguments (image grants included). Only this explicit envelope grants
console authority;004/005 and their ABI19 remain unchanged. Reuse existing v1
0x26000..2 bounds, pointer validation, EAGAIN and permanent close;006 exposes no
handoff operation. Parent, copies and replacements obtain only their scoped stream
references, never UART authority. Names/PIDs/fds do not authorize console access.

The current Rust pipe/stdio owner forwards checked stream requests to its UART grant.
Do not add another backend process or a line editor: the owner already owns these
stream descriptions and dash already owns parsing/jobs. Retain the ordinary directory,
copy, exec and wait paths. During construction and after collection, service parent
stdio requests through the same authenticated channel. Empty RX must remain EAGAIN,
never EOF; short writes advance only their actual bytes. Validate fields/rights before
UART effects and retain partial RPC replies without replaying writes. No retained raw
pointer: each native call borrows a live bounded frame slice synchronously. No new
allocator, dependency, shared mutable kernel owner, public POSIX API or sibling change.

Use actual main with -i +m (the existing explicit no-job-control serial scope), unchanged
helper copy bodies and the existing four-entry environment. Host sends the pipeline
only after a real prompt and sends the follow-up only after child terminal records and
returned prompt. Capture/output checks and prompt-driven UART transcript must agree.
New negative controls: changed pipeline output, wrong console grant and006 paired with
capacity disabled must reject exactly; direct UART access from parent/copies must fail.
Final close must remove owner access, with no more console requests after closure.
Keep kernel emergency markers and upstream ASCII prompts unchanged under EXPERIENCE's
existing bounded serial exception; no general TTY, paste or default SIGPIPE claim.

Simpler alternative: continue sh -c fixtures; insufficient because they cannot prove
serial input, returned prompts or progress after child collection. Choose direct scoped
forwarding within the existing owner to avoid another transport and lifetime. Retain
legacy profiles until consumers migrate. Keep resource bounds and inspect the linked
owner stack before accepting new calls; the current one-page stack has little headroom.
Use existing Rust2024 formatting, new C21.1.8 style and scoped legacy C/Python style.
Tests: meaningful envelope boundaries/legacy rejection, complete capacity suite including
interactive positive and semantic controls, existing serial exec/substitution/console
regressions, full matching connections/runner and host tests. Preserve all attempts,
freeze runtime sources, bind inputs/tools/transcripts and verify archives before cleanup.
Update STATE, companion/console references and workflow; no released pin changes.

Exploration: attempts1/2 reach the real prompt, then reject construction2739 before
host input. The serial facade had exposed UART EAGAIN through a blocking descriptor.
Retain that complete request until bytes arrive instead: construction yields while
waiting; the active job dispatcher returns to other participants with the frame intact.
A successful/short transfer is recorded exactly once before retaining its reply. Do
not turn empty UART into EOF or repeatedly apply a partially sent successful reply.
The temporary unknown-op diagnostic did not change the rejection and is removed.

The next probe identifies a second pipe create before the first application fork:
the generic dash input object allocates a Linux tee staging pipe while reading stdin.
Select the already-pinned AETHER_NATIVE_NO_TEE input.o used by the accepted serial
profiles. It chooses upstream's one-byte fallback; no fake tee operation or new input
implementation is added. Record/verify this additional link selection explicitly.
The serial owner also requests at most one UART byte per trap in this experiment to
exercise actual short-write progression; scoped stream requests still allow16 bytes.

Attempt4 executes the pipeline and follow-up but rejects2743: the capture oracle
incorrectly counted the16-byte `pipe data\nafter\n` output as15. Derive the
expected length from the literal; probe4 then completes all three generations.
This is a completion-oracle fix, not a relaxed output comparison. All exploratory
logs, artifact/source bytes and transient diagnostic variants are retained.

Outcome: [sealed interactive pipeline evidence](evidence/pipeline-serial-2026-09-24/README.md)
passes105 capacity+358 connections+431 runner+four console cases (898 native),
with105 Python tests plus Zig/Rust. All match287 runtime inputs. Serial owner18616
bytes and linked critical stack4000/4088 are qualified within existing limits;88-byte
headroom requires review before further growth. All failures and successful runs
are retained, with readback/hash verification before duplicate cleanup. Existing C
ELF images remain unchanged; changed Rust owner bytes have fresh target evidence.
The next requirement is reusable jobs and composed exec/substitution/redirection
in the shared native SDK/runtime, with independent consumer review. This bounded
serial session does not complete full dash, persistent storage or R1 assembly.

## Script-independent serial forwarding — 2026-09-24

Before code: remove script-output policy from the AENMX006 stdio owner. Its32-byte
captures and literal output/prompt expectations are test oracles, not device quotas.
Forward valid bounded requests without retaining cumulative stdout/stderr. Keep
caller/generation/holder checks, frame bounds, short-count/EAGAIN handling, explicit
close and terminal-confirmed cleanup. Nonserial capture fixtures retain their exact
behavior. No kernel ABI, resource cap, dependency, released pin or sibling changes.

Consumer intake: userland now supplies SESSION-01–06 in
`experiments/dash-native/SESSION.md` and pinned `session/manifest.json`. Review and
snapshot those inputs without editing the consumer script. Full composed-session
execution remains pending: external argv, two pipelines, substitution, fd closure
and three complete generations need new lifecycle accounting. This change removes
a prerequisite restriction; it must not claim SESSION-01–06 or full SDK acceptance.

The serial owner must not decide whether command output is correct. Keep that oracle
in the host harness, which checks exact serial bytes after removing known native
markers, all terminal statuses, command/prompt order and15 reclaims. Exercise long
stdout and stderr output before the pipeline, then long stdout afterward, exceeding
the old32-byte captures. Preserve the real dash parser, main/jobs and pinned native
input object. Negative control: a deliberately corrupted stdout byte must make the
ordinary host validator fail for output mismatch after successful guest cleanup;
wrong console authority and disabled profile still reject at their existing bounds.

Simpler alternative: raise capture sizes. Reject it because a larger script-specific
buffer retains the wrong responsibility and spends scarce owner stack. Remove the
serial captures instead; leave legacy fixtures unchanged for compatibility. Native
serial transfers still borrow a live request/reply slice synchronously, at most one
UART byte per call and16 bytes per RPC. No queue, allocator, global authority or new
policy service is needed. Review linked stack against4088 usable bytes before
qualification. Keep the existing finite driver/request budgets; this is not a
long-lived arbitrary-job runtime or a general TTY.

Tests: host output-oracle counterexamples and all host checks; complete105-case
capacity regression on frozen sources, including real long-stream positive and
semantic controls. Compare all nonserial C/owner artifacts to the preceding sealed
packet. Kernel, existing connections/runner sources and tool/SDK pins are unchanged;
those suites are not selected anew for this capacity-owner-only change. A later
SESSION delivery still requires its own fresh matching consumer regressions.
Use existing Rust2024 and scoped Python conventions, preserve all attempts and
verify archives before deleting owned duplicate outputs. Update STATE, console and
companion references and workflow; keep independent owner acceptance explicit.

Outcome: [sealed serial-stream evidence](evidence/shell-streams-2026-09-24/README.md)
passes the focused run and both full105-case suites, plus110 Python and Zig/Rust
host checks. The final host-corruption classification also checks positive guest
admission, terminal and mapping outcomes. All253 code artifacts are unchanged by
that harness correction; all105 kernel ELFs match the earlier qualification.
Serial owner17960 bytes and reviewed stack3888/4088 remove656 image bytes and
112 critical stack bytes without changing quotas. Nonserial capture behavior is
qualified by the full suite. SESSION-01–06 and general repeated-job execution remain
open; the owner lifecycle/accounting review for that unchanged script is next.


## Composed-session lifetime review — 2026-09-24

Prospective owner design for userland SESSION-01–06; **not implemented or native
acceptance**. Use the six verified consumer inputs in
[evidence/shell-streams-2026-09-24/consumer-inputs.json](evidence/shell-streams-2026-09-24/consumer-inputs.json)
and its archive. The unchanged composed.sh must be one actual dash `-c` input.
The manifest specifies 65 stdout bytes, 19 stderr bytes and exit0 per session.
No sibling, released pin, existing profile or sealed packet changes in this review.
Aether owns the enforcing runtime/fixture; userland owns independent acceptance.

### Required lifecycle and compatibility change

Source review finds independent three-use bounds in native admission, process copy,
channel allocation **and Channel.create**, plus pipe creation, participant admission
and routed pipe-reference validation. Changing only the outer driver cannot deliver
SESSION. Existing `getpid() - getppid()` slot discovery also assumes equal parent and
child generations; it is invalid after child reuse. The exec adapter accepts only
copy/pump/one arguments, its environment validator rejects wrong WITNESS before the
helper, and the wait dispatcher reconstructs child PIDs from the parent generation.
These are concrete composition blockers, not missing userland input.

Implement an explicit new private session profile before executing this workload;
do not reinterpret AENMX004–006 or silently relax their exhaustion tests. Reserve
AENMX007/ABI21 for implementation review, retaining the existing six-domain backing,
ten channel objects, three image grants, 24-KiB owner-text ceiling and 4088 usable
owner-stack bytes. This reservation is not a supported launch format. The new
profile needs no UART grant for `-c`; separate bounded stdout/stderr observations
must preserve stream identity. A later serial delivery needs its own reviewed grant
and framing contract. Existing serial authority remains AENMX006 only.

Use slot0 for the persistent shell and slots2–4 for at most three copied children;
slot1 stays unused rather than launching an unrelated peer. The bootstrap owner
stays alive across all three shell generations, as in the existing qualification
harness. SESSION's three generations mean three complete shell lifetimes under that
owner, not three independently reset kernel boots. Distinguish owner instance,
shell generation, child-slot generation, fork sequence and pipe generation.

| Phase in each shell | Children in slots2/3/4 | Exec replacements | Pipe instances |
| --- | --- | --- | --- |
| External argv | argv / absent / absent | 1 | 0 |
| First pipeline | printf / copy / copy | 2 | 2 |
| Substitution | argv / absent / absent | 1 | 1 |
| Second pipeline | printf / copy / copy | 2 | 2 |
| Descriptor check | closed / absent / absent | 1 | 0 |

Consequently each shell has nine copied children, seven helper image replacements,
ten terminal records and ten reclaims including the shell. Across three shells:
27 copies, 21 exec replacements, three fresh parent-image launches, 30 terminals
and 30 reclaims. Replacement does not create a second process lifetime. Do not
confuse the 24 image-load operations with 27 copied snapshots or count exec as a
reclaim. Peak is four workers plus owner, within the existing allocation.

For shell generation g=1..3, slot0 has generation g; slot2 uses generations
5(g-1)+1 through 5g, and slots3/4 use 2(g-1)+1 and 2g. Authentic PID is
`slot_generation * 6 + slot + 1`; handle is the existing generation-tagged handle.
Each copied child retains that shell's authentic parent PID. A child's PID delta
must not select its role or authority. Bind role from the owner-authenticated
copy/readiness exchange, validate native PID and endpoints against the live ledger,
and never grant authority from child-supplied role bytes. Exec preserves identity.

The session-only process/channel lifetime ceiling is proposed as 15, inclusive;
old profiles retain three. There are two channels per process lifetime: 20 creates
per shell, 60 total. With current first-free allocation, parent channels0/1 advance
three times, child channels2/3 fifteen times, channels4–7 six times and channels8/9
remain unused. Last close must zero the stream before reuse. Do not reset a
channel's generation or expect global channel exhaustion at session completion.
Use dedicated bound checks to prove the next create on an exhausted object fails
with ENOSPC(-28), without modifying unrelated old-profile behavior.

Use the first pipe object for each pipeline's first pipe and substitution; use the
second object for each pipeline's second pipe. Their final generations are nine and
six. A session-only ceiling of nine pipe creations and fifteen participant lifetimes
suffices; preserve old three-use rules and ENFILE(-23) on exhausted pipe creation.
Each pipe still buffers256 bytes and accepts at most16 bytes per request. Keep
existing per-process memory limits, 16 descriptor entries, bounded launch vectors,
and two pipe objects. Supporting fd3–63 F_GETFD requires truthful EBADF outside the
supported table, not allocating a new64-entry table. No heap or new service needed.

### Reuse, progress and security obligations

At each job boundary retain terminal records until all its real children have been
collected exactly once and their completed wait replies have been delivered. A
valid wait-any returns an actual uncollected child; a live WNOHANG returns0; an
unknown/already-collected PID returns ECHILD(-10) without consuming another record.
A blocking wait stays pending while I/O and exec progress. Clear pending frames or
undelivered replies only on delivery or confirmed terminal of their exact caller.

Then close owner endpoints, confirm each exact child's terminal, remove its pipe
and standard-stream holders, reclaim mappings/backing and verify old handles fail.
Retire a pipe only when holders and pending references are empty; preserve its
monotonic generation and participant history. Fully complete this barrier before
admitting the next job into those slots. Retain the shell's stdio, variables,
identity and authority across barriers. Pipe EOF requires no live writers; a short
read, EAGAIN, deadline or completed builtin does not establish EOF.

The state machine handles authenticated requests, not script-line positions. The
phase table is an independent observation oracle, not permission to synthesize a
fork, helper invocation, output, wait or EOF. Serialize actual bounded argv/env
through the existing admission transaction: argv/"a b"/"*", copy and closed.
The wrong-WITNESS control must reach the unchanged helper and exit91; it must not
be rejected earlier by the legacy fixed-environment selector. Reject oversized,
malformed, unauthorized and duplicate-field requests before publication. Keep the
existing /inputs/helper grant boundary and denial controls. Do not execute arbitrary
paths or accept a caller-supplied image grant as authority.

Two independent stream observations must match the consumer bytes; combined UART
capture is insufficient. Keep output comparison in the harness, and separately
observe pipeline transfer counts/EOF, terminal statuses, wait collection and
reclaims. Native marker text is not child authority. Any new observation framing
must be length-bounded and distinguish authenticated owner records from program
bytes, including bytes resembling boot markers; review it before implementation.

### Negative outcomes to freeze before native execution

The following are the selected semantic boundaries. Owner codes2800–2804 are
reserved for the session driver only; they are not new syscall errnos. A panic or
watchdog expiry never substitutes for any named outcome. Failed runs retain their
partial stream and lifecycle records. Actual implementation must bind exact frame
formats and cleanup assertions before the first qualified native run.

| Control | Required result and cleanup |
| --- | --- |
| Wrong WITNESS in first admitted helper | Helper91, shell31, one copy/exec, two normal-exit terminals/reclaims; no later job or output. Owner2800 only after verified cleanup. |
| Change first pipeline output byte | All processes still exit0; all30 reclaims and other positive observations required; ordinary host oracle rejects exact stdout mismatch. No guest success is enough. |
| Corrupt captured substitution byte | Substitution helper exits0, shell33; five children plus parent reclaimed (six), four exec replacements; no second pipeline. Owner2801 after cleanup. |
| Add unflagged fd3 to final helper | Preserve a real scoped alias through exec; helper95, shell35; nine children plus parent reclaimed (ten), seven exec replacements. Owner2802 after cleanup. |
| Old collected PID after slot reuse | Diagnostic request through the same authenticated wait path returns ECHILD(-10), no state change, new child remains collectible. Deliberately accepting it must trigger owner2803; retain observed records and confirm stop/reclaim of every admitted process before owner exit. No fabricated positive wait response. |
| Retain first-pipe writer alias | After first pipeline admissions and builtin exit, helpers cannot observe EOF. Bounded no-progress rejection2804 after confirming the retained writer and pending read, then stop/reclaim parent and both blocked helpers. Earlier argv and builtin exit0; three stop terminals; five total reclaims. No next job or synthetic EOF. |

For stale-wait validation, freeze the injection point after the first argv job has
been collected and all first-pipeline children admitted: five process lifetimes have
been admitted including the parent. Cleanup must account for exactly those five,
using observed normal terminals or confirmed stops, with no next-job admission.
The correct stale-request rejection control may continue to the full positive
session; only its deliberately incorrect implementation takes owner2803 cleanup.
No timeout-only negative may be promoted to evidence of the intended boundary.

### Simplicity and qualification

The simpler alternative is the existing single-job owner. It cannot retain one
parent through this workload. Choose a bounded request-driven loop with reusable
child slots over a general scheduler/service framework or five script-specific
orchestrators. Reuse upstream dash's real parser/jobs and the existing pipe,
copy/exec and endpoint ownership cores. This borrows Unix process composition,
not ambient POSIX authority or a complete Unix kernel. Remove the new path's dummy
peer, PID-delta routing, fixed child count and fixed job sequence. Keep old private
fixtures until their consumers have qualified replacements. None of this imports
init/package policy or starts the deferred OpenZFS work.

The latest serial owner's200-byte stack margin is not enough evidence for the new
loop. Audit the new linked call paths, retained frames, copy/exec transaction and
failure cleanup before target execution; do not place an additional nested job
ledger on the stack without accounting. Preserve code/stack caps or stop and review
an explicit change. All borrowed user/FFI buffers must remain live and stable through
the synchronous trap; retain complete request/reply storage across partial progress.
Use current Zig0.16, Rust2024 and scoped C/Python conventions, not a broad reformat.

Implementation order: explicit profile and bounded lifetime plumbing with legacy
rejection tests; authenticated identities and reusable dispatch/collection; actual
argv/env and substitution stream routing; then the unchanged full session and
semantic controls. Qualify all changes together before a consumer delivery. Run
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`, complete
capacity, connections and command-runner suites, plus affected console profiles,
using the existing pinned SDK/tool lock and commands in DEVELOPMENT/workflow.
Add the new profile and its authoritative reference to workflow when implemented.
Fresh consumer replay remains separate; no earlier12-script receipt covers SESSION.

Freeze all source/support including tests/test_build_policy.py, exact flags,
SDK/tools and launch rights. Preserve failures, measure monotonic time, run native
suites sequentially with3600-second hard/1800-second review budgets and512-MiB log
bounds. Verify archived bytes before deleting owned outputs. Documentation-only
review selects input-hash, offline-pin/workflow/link and host checks; it does not
rerun QEMU or establish SESSION execution. No exception to capability isolation,
zero-before-reuse, evidence retention or release pins is requested.


### Session channel core implementation scope — 2026-09-24

First implement the channel object's fifteen-use creation path without enabling
AENMX007 or changing native allocation/profile selection. Existing create retains
its three-use contract. The private kernel caller will select createSession only
when the explicit profile is implemented; no application chooses the limit.
Both paths share the same generation-tagged capability, holder transfer, last-close
zeroing and exhaustion logic. No field, buffer, allocation, authority, ABI or
concurrent path is added. The simpler alternative is raising the existing limit;
that would weaken legacy exhaustion, so keep the explicit scoped entry instead.
The shared implementation removes duplicate initialization/error handling.

Host tests must exercise all fifteen generations, stale references to every prior
lifetime, distinct channel identities, partial closure, forbidden old-owner actions,
zeroing and terminal exhaustion with no mutation. A separate legacy object still
retires at three. Test the actual channel implementation, not a second model.
Retain the existing source style under Zig0.16; run zig fmt and zig build test.
Select the full capacity target regression for the refactored legacy entry and
compare kernel artifacts with prior evidence. Additional matching native profiles
are required if executable legacy kernel bytes change. This step cannot claim
native fifteen-generation reuse, process reuse or SESSION acceptance: its new entry
is deliberately unreachable from the launch path until that profile is ready.


The channel core implementation now provides the separate createSession entry with
a15-use bound; existing create remains3. Both share creation logic and reject at
or beyond their bound. No native caller selects createSession yet. Two host tests
exercise all15 lifetimes and a copied generation-blind lookup mutant fails the new
stale-handle assertion. Scope/qualification are retained in the
[channel packet](evidence/session-channel-2026-09-24/README.md); this is not an
implemented launch profile or SESSION execution. Next wire the explicit profile
and process/pipe lifetimes before enabling the composed-session dispatcher.

Qualification:105 capacity,358 connections and431 command-runner cases pass
(894 native), plus110 Python and configured Zig/Rust checks. All287 runtime inputs
match across the native runs. All148 capacity worker/owner code artifacts are
unchanged from the previous packet; all105 kernel executables changed and were
rerun. Native suites exercise the legacy entry only. The two new session-core
host tests and retained stale-lookup mutant qualify only that component; there is
no guest-visible fifteen-generation claim. No quota/ABI/pin or sibling change.


### AENMX007 admission and channel integration — 2026-09-24

Before code: expose ABI21 with the existing112-byte five-worker envelope and
24-KiB owner-text ceiling. Retain six domains, ten32-byte channel objects, image
and memory limits, capability rights and all004–006 behavior. Only exact007 with
the existing native-pipeline-capacity build opt-in selects fifteen process and
channel lifetimes; old profiles still select three. No UART or console handoff is
granted by007; direct UART operations remain unsupported(-38). A request cannot
choose its own limit. Bootstrap arguments retain factory, three images and channel
factory. Native completion requires30 reclaims and all workers/endpoints released;
this count is a private qualification oracle, not an allocator admission rule.

Use one profile-selected lifetime bound in fresh launch, copied-child admission,
nonlaunch creation and channel selection; channel creation selects the already
host-tested createSession entry. Reject before effects on an exhausted slot. Do
not reset counters or reuse backing before confirmed terminal, mapping removal,
TLB cleanup and zeroing. Keep snapshot/freeze and copy authorization unchanged.

Qualify the new kernel admission/resource mechanism using the existing capacity
worker/owner, not a substitute shell job: two fresh workers per generation for
fifteen generations,30 launches/terminals/reclaims,60 paired channel creations.
A final61st channel creation must select previously unused object4/generation1,
proving exhausted objects0–3 are skipped; close both ends. This tests fixed-pool
allocation/reuse and authentic native PID reports, not fork or dash. It intentionally
differs from SESSION's three persistent parents and27 copied children. SESSION
remains NOT RUN. Do not report this case as child-tracking/dispatcher acceptance.

Expected worker identities are kernel PID=6*generation+slot+1 for slots0/1.
The trusted owner compares each report to its actual admitted handle/slot epoch;
report bytes grant no authority. Check adjacent/foreign endpoints and stale task
handles as before. Session-only canonical channel identity/generation mismatch
rejects2810; wrong worker epoch rejects existing2608. A deliberate fourth-generation
worker report using generation3 must reject2608 after6 prior reclaims. A007 owner
with ordinary005 ABI expectation overridden only for the compatibility control
must still hit legacy process exhaustion at generation4 (2603,6 reclaims).
Disabled007 and truncated007 reject before owner execution. Add005/007 ABI mismatch
and007 owner-code bounds controls, preserving existing capacity negative oracles.
No new application operation, compiler flag in the kernel or service boundary.

Simpler alternative: raise all profile limits. Reject it because it would silently
change consumed contracts. Select the bound once from the validated envelope and
reuse existing checks. This removes duplicated literal limits in the enforcing
kernel path; no new mutable ledger or parser framework. Existing C style is a
scoped compatibility edit; Zig0.16 and Rust2024 formatting apply. No new unsafe
boundary: existing synchronous borrowed request/argument buffers remain live.

Test the parser's version, size, reserved-byte and legacy rejection boundaries;
full capacity suite including positive and specific semantic controls; full host,
connections and command-runner regressions for the affected common kernel.
Review the linked new owner stack against4088 usable bytes before qualification.
Retain all attempts and source/support/tools, verify archives before duplicate
cleanup, and update workflow/profile documentation. Authenticated reusable copied
children, pipe limits, real argv/env and request-driven dispatch are still required
before the unchanged SESSION script can run. Native copy at higher generations
needs its own exercised path in that integration; selecting its bound is not
proof that copied-child/session behavior has run.

Qualification: all113 capacity,358 connections and431 command-runner cases pass
(902 distinct native cases), plus one focused resource rerun,110 Python and configured
Zig/Rust host checks. All287 runtime inputs and306 host/support inputs remain frozen;
full suites share tool and SDK identities. Both qualified raw/linked resource owners
match the inspected stack artifacts. All148 legacy worker/owner binaries are unchanged.
The failed preliminary Rust compilation is retained with source and diagnosis.
Archive readback and original-file verification precede duplicate cleanup. No new
higher-generation copied child or SESSION case has run. Continue with reusable
pipes/copies and one-parent dispatch under the existing composed-session contract.

### Session pipe lifetime implementation — 2026-09-25

Before code: extend the existing Rust pipe core with an owner-selected static
session profile: nine pipe creations and fifteen participant generations. Legacy
Pipe/PipelinePipe keep three for both. SessionPipe has four participants, the same
256-byte FIFO and16-byte request bound; no mutable quota, new wire field, grant,
heap or kernel change. Generic routing must validate against the selected core's
creation bound, preserving exact object/reference/binding and holder checks.
A caller frame cannot select the profile or revive an exhausted object.

The simpler alternative, raising shared constants, would weaken old exhaustion
contracts. A compile-time profile reuses existing transitions without adding a
second holder ledger or duplicating routing/exec transactions. No obsolete consumer
path can yet be removed. Existing retained/pending-reply barriers and terminal-only
participant release remain required; process identity does not derive from pipe
creation count. This change adds no unsafe code or FFI boundary. Rust2024 formatting
applies to touched Rust; Python changes stay scoped to the existing host harness.

Test independent pipe/participant epochs, all nine/fifteen lifetimes, old references,
staged and confirmed-terminal peers, undelivered replies blocking retirement,
unread-byte zeroing, exhausted allocation without mutation and legacy limits.
Exercise routing and transactional descriptor staging across object epochs.
Run the existing no_std pipe host check and full host suite. Keep a deliberately
broken generation check as a separate retained negative test. Native session
selection/dispatcher execution remains required before any guest reuse claim;
qualify all changed native consumers on frozen final sources before delivery.

### Persistent child collection core — 2026-09-25

Before code: the new session dispatcher needs three reusable child records,
separate from parent generation and from pipe generations. Each record binds the
admitted native slot/generation/handle and authentic PID; request PIDs only select
among those records. Keep terminal observation, reserved wait reply, delivered
collection and reclaim eligibility distinct. Reserving a terminal for a partial
wait reply must prevent duplicate collection. A stale completion or release token
must not change a later occupant. A pending blocking wait must not prevent the
surrounding I/O/exec loop from polling other children.

Use a small pure Rust record core called by the future authenticated dispatcher;
it neither observes kernel state nor authorizes traps. Admission is recorded only
after a successful native copy; terminal recording requires that exact handle's
observed status. Record a known normal exit or stop explicitly; no timeout-to-exit
conversion. Release requires delivered collection, completed endpoint/holder cleanup
and successful native reclaim, all supplied by the enforcing dispatcher. No reset
of child generation history across parent lifetimes.

The simpler alternative is deriving PIDs from the parent generation, which fails
on the second job. A fixed three-record ledger removes that assumption and the
fixed wait-response count for the new path; it is not a general process service.
Keep wire decoding/transport outside the core. Tests cover all fifteen generations,
stale PIDs and completion tokens, two ready children, WNOHANG/blocking wait,
reserved reply replay, bad/native-mismatched identity and no reuse before release.
Compile in the existing no_std host wrapper. Host passes do not establish native
copy/terminal authority, pipe cleanup or composed-session acceptance.

### Session exec vector framing — 2026-09-25

Before code: use an explicit32-byte request header (u32 little-endian operation84,
image selector0xc002, body length272, remaining20 bytes zero), followed by the
existing272-byte launch record (u64 argc/envc, four32-byte argv slots, four32-byte
environment slots). The owner authenticates the requesting child through its live
endpoint ledger; neither PID nor role is accepted from this frame. Select only the
already granted /inputs/helper image. Header acknowledgment follows complete vector
validation, then the existing descriptor snapshot/freeze/admit/commit protocol;
framing validation alone never authorizes replacement or holder mutation.

Each used string has a NUL and zero padding, unused slots are zero, argc1..4,
envc0..4. argv0 must name the granted /inputs/helper; remaining arguments are bytes
passed unchanged to the real helper, not validated against an expected test result.
Environment entries require a nonempty key and '='; duplicate keys reject. Values,
including wrong WITNESS, pass unchanged so the unchanged helper owns its result.
The parent serializer must preserve actual argv/env and report oversize data before
sending a header. Old fixed-environment exec frames remain separate legacy inputs.

The simpler alternative is adding argv/closed selectors and a second fixed
WITNESS profile; that would keep script-specific policy in the runtime. Reusing the
existing bounded launch layout removes that selector scheme from the session path.
No new dynamic parser, allocation, library, syscall or authority is introduced.
Test valid quoted arguments and changed WITNESS preservation; malformed counts,
missing terminators, hidden tail bytes, unused records, duplicate environment keys,
wrong path/image and malformed header. Compile in the existing host/no_std wrapper.
Actual adapter transfer, admitted helper91 and complete SESSION execution remain
required native evidence; parser success is not a delivery.

### Remove parent-generation PID inference — 2026-09-25

Before code: use the canonical native handle's slot/generation when selecting a
child in existing capacity wait paths. Never reconstruct a child PID from the
parent's generation. Reuse the checked Identity representation above; the current
legacy fixtures still produce the same IDs and must preserve all wait/error and
cleanup oracles. This does not itself introduce a persistent dispatcher.

Copied dash and replacement-helper readiness derive their local slot from the
kernel-provided, rebound memory capability in auxv and cross-check getpid against
its canonical slot/epoch. The owner still authenticates readiness through the
assigned endpoint and admitted handle; application-supplied role bytes grant no
rights. Parent PID remains a separate check. Do not broaden any profile limit,
image authority, environment policy or native API. Existing C style remains a
scoped compatibility edit; no whole-file formatting. Run full capacity and matching
connections/runner regressions on frozen final sources, with the host core checks.

### Session stream observation proposal — 2026-09-25

For the isolated persistent-dispatcher draft, before native implementation: retain
one176-byte owner observation record per completed parent, rather than three live
records. Layout is u32 stdout length, stderr length, observed copy count, observed
exec count, followed by128 stdout bytes and32 stderr bytes. Used bytes come only
from authenticated standard-stream writes; unused bytes remain zero. The host
compares exact separate streams and lifecycle counts with pinned consumer inputs.
The owner does not compare against or synthesize expected script output.

Propose private AENMX007-only operation0x2000a: the bootstrap owner presents its
0xa001 factory grant, record pointer, exact length176 and ordinal1..3; remaining
arguments zero. Workers, wrong grants, old profiles, invalid ranges/records and
exhaustion reject before output/counter changes. Copy and validate the entire record
before emitting. Kernel output is ASCII hexadecimal with explicit ordinal, stream
and length; program bytes cannot forge diagnostic markers. Three records maximum,
one after each parent's verified cleanup. The record contains no usable grants.
This is test observation authority scoped to the privileged fixture owner, not a
UART grant, general logging API or new application I/O facility. Existing ABI20
console authority and ABI21 resource-only qualification retain their behavior.

At the time of this prospective review, the proposal was not implemented or
qualified. The implementation and producer packet are now recorded below. It avoids retaining three captures
on the4-KiB owner stack without moving shell/stream policy into the kernel. The
alternative of raw UART forwarding would lose stderr identity and silently grant
console access to007. Record framing, host corruption/duplicate/missing-record
controls and owner/worker rejection cases must be implemented and tested before
any SESSION acceptance; the existing source freeze excludes this scratch draft.


The proposed dispatcher handles normal helper statuses and parent abandonment:
wait replies carry the observed status; a confirmed terminal parent permits
abandoning retained waits only after each child is terminal, with scoped stop,
holder disposal, transport closure and reclaim in that order. Tests must never
interpret a timeout or accepted stop request as terminal evidence. The existing
stop control retains status143/kind3 and queries return144; for the007 session
profile only, add a canonical terminal diagnostic when that retained record is
first created. This exposes actual stop identity/status to the host oracle without
changing existing profiles or granting workers diagnostic access. Normal and
stopped terminal rows must be unique and match the final reclaim total.

### Persistent session integration — 2026-09-25 (producer qualified; private consumer acceptance recorded)

The private implementation is now `user/native-capacity/session-owner.rs` and
`session-client.c`, selected only by the new `session-*` composed cases in the
existing capacity harness. It uses four active workers plus the owner: one dash
parent and up to three children. The parent runs the pinned unchanged composed.sh
through actual dash main/jobs; helper replacements run the unchanged pinned C
helper with actual argv/env. No dummy worker, script phase sequencer or expected
output string lives in the owner. Target evidence and independent SESSION replay
are now recorded in the producer packet and consumer intake above.

The owner holds two bounded SessionPipe objects and three exact child records.
It processes authenticated endpoint requests, retains partial frames/replies,
reserves waits until complete reply delivery, and reclaims only observed terminal
children whose collection/abandonment and holders/transport have been resolved.
Normal parent closure must leave no retained pipe epoch; abnormal parent closure
first confirms its terminal, stops remaining admitted children, observes their
terminal records and abandons outstanding waits before reclaim. No timeout permits
reuse. Each complete parent observation is released only after native resources
are reclaimed; the three-parent loop is a repeated experiment, not a job sequence.

AENMX007 operation0x2000a implements the proposed176-byte observation layout above.
The ASCII line has ordinal/copy/exec fields and separate lowercase hexadecimal
stdout/stderr fields; their lengths are derived exactly from those fields. The
caller must be the bootstrap owner with its0xa001 grant. It rejects old profiles,
workers, wrong grant/length/ordinal/reserved arguments, invalid pointers or records,
live workers/channels and inconsistent reclaim deltas. Rejection cannot advance
the three-record quota or emit program bytes. A stopped007 worker now emits its
actual retained kind3/detail143 once; query code144 remains unchanged. No UART
capability, released ABI or general application logging API is added.

Host `scripts/session_smoke.py` owns immutable consumer input verification and
independent exact stream/lifecycle checks inside the existing capacity suite.
Five host tests cover missing/duplicate/malformed observations, corrupted streams,
identity reuse, premature success and diagnostic-shaped encoded program bytes.
The byte-mutated native control must finish guest cleanup and fail the ordinary
host stream comparison, with every other lifecycle check already satisfied.
Other controls exercise helper91 from wrong WITNESS, helper95 from a real inherited
unflagged descriptor, corrupted command substitution, stale wait/ECHILD, a deliberate
stale-accept mutant and a retained real writer that requires confirmed stop.

Run the focused exploratory case with the same pinned SDK and tool lock:

```sh
python3 scripts/pipeline_capacity.py --libc-build <pinned-sdk> --tools-lock <pinned-tools.json> --case session-composed
python3 -m unittest discover -s tests -p test_session_smoke.py -v
```

Full capacity, connections and runner regressions pass on matching frozen final
sources in the producer packet. Linked owner stack inspection binds to executed raw
bytes; compile success and resource-only007 evidence remain insufficient alone.
Sources and every failed target/host attempt are retained. Independent userland
acceptance for this private profile is recorded above; shared SDK and R1 remain open.


Implemented retained-writer control refinement: preserve a real fd10 alias to
the first pipe writer in the parent using F_DUPFD_CLOEXEC. Actual fork snapshots
therefore remain consistent; helper exec closes the alias while the waiting parent
retains it. Require both helpers blocked on reads, a retained parent writer and a
pending parent wait before confirmed-stop cleanup. Do not simulate retention by
acknowledging a close without updating holders: that correctly fails subsequent
snapshot validation before the EOF behavior under test.


### Early-reader recovery composition — 2026-09-25 (producer checks pass; replay pending)

Userland supplied SESSION-RECOVERY.md and an unchanged early-reader recovery script.
The [local attempt packet](evidence/recovery-native-2026-09-25/README.md) freezes the
manifest, script, expected separate streams and unchanged helper. This closes the
missing-input dependency for recovery only; failed exec, scratch and real serial
composition still need their own inputs. Sustained SI-07 remains separate.

The existing AENMX007/ABI21 dispatcher/client is reused with `session_recovery` /
`SESSION_RECOVERY` selection. Expected slots per parent: pump2 and one3, argv2,
healthy builtin2/helpers3+4, closure2. Parent generations1–3; slot2 uses1–12,
slot3 uses1–6, slot4 uses1–3. Seven copies and six helper replacements per parent
require24 total terminal/reclaims and21 admissions. Before the argv, healthy-pipeline
and closure forks, all preceding children must have been collected/reclaimed.
The argv/closure forks require no pipe epochs; the healthy pipeline has already
created its next pipes before its first fork, through the existing retirement
and creation checks. The fixed15 lifetime, three-child, two-pipe,24KiB owner
and4088-byte usable stack limits remain. Fit requires linked/target evidence.

The privileged test-only finish accepts either the unchanged zero-observation,
30-reclaim resource probe or exactly three cleanup-checked observations with their
matching kernel-owned cumulative reclaim count. Partial or stale totals reject.
Live workers/channels still reject. This removes a workload-specific30 total from
the observation path; no application authority, ABI or public logging is added.
Existing accepted SESSION must still satisfy its exact30-reclaim host oracle.

`scripts/recovery_smoke.py` separately checks recovery status42, unique child
identities, actual phase/parent ordering,24 reclaims,21 admissions and unchanged
49-byte stdout/20-byte stderr. Controls target wrong EPIPE, inherited reader,
collected-child ECHILD, wrong environment, fd3 leakage and healthy byte corruption.
The real fd10 reader alias is CLOEXEC: children inherit it and exec drops it, while
the waiting parent retains it. A pending pump write and parent wait must be observed
with the other helper terminal before stopping the parent, then confirming child
termination and reclaim. Following parent reader closure pump can either observe
EPIPE/exit42 or be stopped with kind3/detail143; neither timeout nor a crash passes.
No extra terminal rows or uncollected resources are permitted.

```sh
python3 scripts/pipeline_capacity.py --libc-build <pinned-sdk> --tools-lock <pinned-tools.json> --case recovery-composed
python3 -m unittest discover -s tests -p test_recovery_smoke.py -v
```

The producer packet records128 capacity cases, five unchanged non-pipeline command
cases,119 Python/configured Zig/Rust/pin checks and linked stack inspection (maximum
3688/4088 bytes), with every target attempt retained. Independent RECOVERY-01–06
replay, reader reviews and shared SDK integration remain open. STATE is authoritative.

## Failed-exec session lookup — 2026-09-29 (experimental)

The next pinned userland composition is in
[the integration packet](evidence/failed-exec-session-2026-09-29/README.md).
Its private session client uses opcode85 instead of84: a32-byte little-endian
header contains opcode85, path length32, vector length272 and20 zero reserved
bytes. It is followed by a32-byte NUL-terminated, zero-padded actual path, then
the unchanged272-byte argv/environment record. The actual path is separate from
argv[0]. The authenticated child endpoint selects the owner-held native instance;
no caller-supplied image identifier or POSIX identity confers authority.

The owner validates the entire request before deciding against its immutable
fixture namespace: `/inputs/helper` has the existing0xc002 replacement grant;
`/inputs/not-executable` is present without an execution grant (EACCES);
other paths are absent (ENOENT). There is no mounted filesystem or path traversal.
Malformed headers, padding or vectors return EINVAL. A32-byte reply carries signed
negative errno in its first word and zero padding. Successful lookup returns zero
and follows the existing descriptor snapshot/freeze/replacement exchange. Denial
never begins that exchange, changes descriptors or admits an image. Legacy opcode84
and its helper-only argument contract remain unchanged in other builds.

For this experiment the owner checks the two failed children against the actual
image-commit query before replying and at observed termination, requires127 then126,
and confirms collection/reclaim before the next fork. The three-parent workload
must finish the fifteenth slot2 lifetime without widening the existing bound.
Native producer qualification and nine semantic cases pass;
[verified independent userland acceptance](evidence/failed-exec-acceptance-review-2026-09-29/README.md)
now closes EXEC-SESSION-01–06 for this private profile. The parent-stderr closure control requires wrapper141 from the
unchanged failed-close path, with eight confirmed reclaims. This contract is not
shared SDK adoption or independent consumer acceptance. SI-07's versioned sustained
consumer bootstrap/binaries remain a separate dependency.
