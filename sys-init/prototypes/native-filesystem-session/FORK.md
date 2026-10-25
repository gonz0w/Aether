# Selected opt-in fork frames and owner admission

Decision0224's matched home owner uses both delegated greetings and an owned FILE
event under the existing mixed-channel gate. The synchronous exec Request borrows
the already decoded local Plan exclusively through execute; no process memory is
reread after capture, and the borrow cannot outlive the closed callback. This
avoids repeated Plan stack copies. The terminal shutdown tail is a separate
non-inlined method so its close scratch does not overlap live polling frames;
all shutdown operations and their ordering remain. Old AF07/AF08 selections keep
their protocols and source behavior; actual current fits and tests are recorded
in [the owning record](../../docs/decisions/0224-home-owner-fit.md).

## Current native refusal and fit follow-up —decision0211

Use `Owner::resolve_native_refusal` for raw supervisor-side cancellation results:
only callback Ok(0) settles the known refusal. Return the raw value unchanged.
The kernel separately resumes the parent with-11; that is not the supervisor
result. Preserve the original copy errno in the correlated negative disposition.
Wrong phase/sequence never invokes cancellation; failed/unknown/positive results
retire and callback unwind keeps Resolving closed. Settle staged holdings/native
reservations explicitly first;0 alone proves neither a parent acknowledgment nor
endpoint/child/backing reclamation. The older resolve_refusal API still accepts
its explicitly supplied parent-side observation and retains its existing tests.

`Native::cancel_freeze` uses0x23005, the actual owned source in rdi and observed
freeze token in rsi, with other operands zero. Labels supply no native authority.
Actual root disassembly shows one trap and the raw zero test; no VM ran.

Private compact FILE selectors preserve all13 descriptions; a shared operation
boundary preserves frame/pending/delivery lifetime. Same prior code18176 vs18768;
expanded cancellation/routing/construction/copy/publication/settlement roots18384
exceed16384. Target gate2240+workspace4096 use6336/8192;1856 remaining bytes are
not complete resident/peak-stack fit.50 consumer tests, seven semantic omissions,
two borrow denials, producer36/15 and direct affected consumers pass. The attempted
direct decoder is rejected for larger code/stack; original decoder/router sources
stay exact. [Review](../../docs/decisions/0211-owner-structural-fit.md),
[results](../../../docs/evidence/owner-structural-fit-2026-10-22/README.md).
Older measurements below retain their scopes; no quota/pin/default flag change.

## One mixed-channel routing admission —decision0210

`owner_dispatch::dispatch` owns the joined FILE/fork/stream receive path. Its trusted
caller supplies one current Peer, authenticated identity/parent/file generation,
the existing4096-byte workspace and a bounded poll counter. `Owner::route` enters
Receiving BEFORE any prefix read. Exact AEFD0001 continues to the complete64-byte
header and shared real FILE exchange. Exact AEFORK01 continues to304 and the
unchanged full decoder; only its actual nonzero increasing sequence transitions
to Capturing. Selected32-byte stream/pipe/wait shapes require an explicit owner
callback which validates actual sources/holders/rights and completes its reply.
No default handler, guessed exec opcode or fallback to old fork83/64.

An initial EAGAIN with zero consumed bytes returns no work without waiting or
source effects. The owner may scan other peers, then use its existing observed
event sequence/park to avoid missed wakeups. After any prefix byte, finish under
the same closed gate and fixed poll/watchdog bounds; never treat partial input
as idle. Partial-client stalling can still fail-stop this POC owner, not establish
per-client availability. The new budget covers prefix/fork/stream I/O; FILE bodies/
replies retain the existing bounded Framed per-frame transport. Wall-clock limits
are unchanged and still need the complete owner watchdog.

The same workspace holds nonoverlapping304-byte fork raw/scratch, then clears on
every return/host unwind. Only a64-byte header is automatic; no second framing
cache or per-peer queue. Ordinary completion reopens only with an active source;
fork stays closed. Parse/transport/handler failure retires source and selected peer
once, preserving separate raw source(-9,-5)/peer(-7,-8) results in tests. Wrong
already-closed admission performs no I/O or implicit cleanup. Host unwind remains
closed but does not prove native abort cleanup or native obligations settled.

48 consuming tests include the prior34 plus nine real-library mixed-route and
five legacy FILE cases.464 short prefixes, file offsets/CLOEXEC then fork capture,
actual pipe creation and stale-history denial before copy, idle parent/active
copied child, malformed/unknown frames, errors/unwind/clearing and no replay pass.
Three routing omissions fail exact assertions; scoped channel escape and routing
reentry compile-deny. Publication's three existing omissions remain. Host storage/
native observations are injected; no complete native owner/entry or ISO follows.

The explicit unified-route roots measure18768/16384. Safe ICF18768 and disabled
jump tables18664, machine outlining18544 and outlining/no-jump18424 do not
close the gap; no alternate flag is adopted. The
older independent17440 roots omit this actual routing join and are not comparable
as a runtime regression. Complete owner/entry/native transactions/exec/wait/
terminal/readiness/shutdown and whole code/resident/peak-stack fit remain BG-070
work. All limits and released/sealed pins remain unchanged.

## Current publication transport — decisions0208/0209

`fork_transport::publish` runs only after actual positive copy and local FILE
publication in the matching Bound PID/sequence. Its trusted caller supplies the
child's exact startup plan and owned direction-correct native endpoints; numeric
labels never authenticate them. It encodes/sends304-byte AEFDB001, receives and
checks32-byte AEFKC001, activates the actual staged pipe holders, then sends the
correlated positive32-byte AEFKR001. Only complete parent delivery reopens the
gate. Context-ready is distinct from application readiness. Wrong gate admission
returns before I/O without retiring an unrelated Idle owner.

`refuse` is the complementary known-no-child path, selected only after the gate
records successful reservation reconciliation and actual token-matched raw thaw-11.
It delivers the original copy errno and reopens only after full correlated output.
It never performs another thaw, native rollback or replay. A positive copy cannot
enter this path.

Both paths share the existing <=16-byte short/EAGAIN transport and one caller poll
budget. Wait consumes that budget too. Caller owns one304-byte scratch, cleared
on return/host unwind and reusable from capture; no automatic4KiB buffer, queue,
ledger, worker or allocation. Native waits still need the outer watchdog. Partial,
malformed, raw-error or failed activation after admission retires source/gate once;
actual child/endpoint/holder obligations remain. Host unwind leaves admission
closed; native abort does not establish cleanup. No negative reply after copy,
implicit native close, retry or inferred reclaim.

34 actual owner/library tests and three compiling omissions pass. Tests use real
FILE/AF07 policy and pipe cores with injected storage/native channel observations;
they are not native authority/execution evidence. Full owner entry/copy/exec/wait/
terminal/shutdown and peak stack remain unqualified. The optional pinned musl
comparison fixes the old constructor-only size gate (16008/16384), but the expanded
positive/refusal roots are17440/16384. Same-root compiler-builtins cost17976.
These independent roots are not a theorem about a coherent complete executable.
All limits and old sealed inputs stay fixed; see [system results](../../../docs/evidence/fork-publication-2026-10-22/README.md).

Decision0202 selects Aether's serialized owner-admission contract, separate
serialized-copy17 v1 API, exact AEFORK01/AEFKR001/AEFKC001 frame69, retained source
labels/history and stage's bounded refusal rule for the next candidate. No old
API/owner/default/released pin is changed. The actual stage81 delivery is verified
separately; its full-link/native-entry claims are producer evidence, not a new
sys-init executable or native execution witness.

## Admission API

fork_gate.rs owns exactly one ProcessFiles and one stream-state value. Fields are
private. All normal requests (including direct callers, other file views, streams,
finish/exec and another fork) must enter through `admit`. No out-of-band source/
stream alias may bypass it. An unsafe/malicious owner or shared external source
is outside this safe-Rust ownership argument; this is not remote authentication.
The wrapper adds phase/sequence, not a queue, FD ledger, source handle or lock.

`begin(sequence,capture)` closes the gate BEFORE snapshot admission. Sequence is
nonzero and strictly increasing per fixed channel generation; gaps are allowed,
UINT64_MAX is usable once, no reset/reuse/wrap. Capture/validation has exclusive
ledger and stream access. After return only `copy` may advance; normal requests
remain closed. Snapshot bytes must stay immutable, and the actual parked native
parent/token/target/channel observations remain caller-owned requirements.

`copy` calls actual copy_inherit_serialized_v1 while exclusively borrowing the
ledger and stream state. Callback has only stream-state access for actual native
copy/holder work; safe callback reentry into normal admission is compiler-rejected.
It must return authenticated actual results, not expected target labels. Matching
copy clones real description aliases/flags/offsets before returning Bound. No
parent or child ordinary mutation is admitted while Bound or Ready. Exact child
context-ready advances Bound->Ready; only complete matching positive parent
reply delivery advances Ready->Idle. Context-ready is not application readiness.
Unknown/partial handshake must retire the gate, not reopen based on a local send.

Known private refusal keeps gate closed. `resolve_refusal` exclusively gives the
owner stream state to perform actual staged-holder cleanup and exact token-matched
thaw. It returns the complete raw Result; only Ok(-11) permits RefusalSettled. Then
complete correlated negative reply with the same original error may reopen. A
negative reply after positive copy is forbidden by the selected stage; post-copy
failures retain obligations/fail-stop. Invalid refusal, preflight error, unknown or
unbound child retire source and gate conservatively. No automatic cleanup/thaw/
rollback/retry or native settlement. Retired stream reconciliation is explicit
and cannot reopen admission; raw source cleanup stays inspectable.

Host callback unwinds leave Dispatching/Capturing/Copying/Resolving closed; copy
library also retires source on unwind. Explicit retire preserves no-replay. Native
panic-abort does not unwind or prove cleanup; actual owner watchdog/fail-stop is
still needed. Neither enum transitions nor callback return values authenticate
native outcomes. All holder/native endpoint/child settlement remains owner work.

## Frame API

fork_frames.rs rejects incompatible exact16 headers and full304 requests against
actual trusted parent Identity/PPID7 and expected file-channel generation. It uses unchanged startup encoder to validate
all map/source/history/reserved bytes in caller-owned304 scratch, without another
automatic304/4096 buffer. Returned Plan is inert, not admitted authority. Scratch
is private temporary storage; caller clears it on failure/retirement. Preserve full
CLOEXEC on fork, distinct file/pipe selector domains and exact source labels. The
same owner-issued source denotes shared console/pipe backing in child; copying its
label alone creates no grant. Fresh child file generation and actual new distinct
channels are still required. No new AF07 greeting/Owner/SPA.

`disposition` emits32-byte correlated canonical-child/private-negative output;
`ready` checks exact context-ready bytes/sequence/PID/zero tail. Trusted owner
proves observations, delivery, no-child/refusal settlement and all admission gates.
No transport, native-copy call or packet authenticity is supplied by these pure
codecs. Do not silently accept old83/64 or use any old startup reader as fallback.

## Evidence and current blocker

[Evidence](../../docs/evidence/serialized-fork-gate-2026-10-22/README.md) records
six actual ledger/AF07 service tests with synthetic storage and abstract stream
state, three strictly compiling omissions and actual borrow-reentry denial. Rust/C
interoperability covers135 child/startup pairs,1080 malformed requests,4095 private
refusals and reverse C-ready validation. Strict Rust/Clippy/format, C17/UBSan and
generic native libraries only; no actual stream-driver gate, native copy/TLS,
complete executable, full resource fit or native acceptance.

## Authoritative FILE comparison — decision0203

The additive file-view18 candidate is now consumed. `copy` requires the complete
captured `[Binding;16]` in addition to the existing identity/native arguments.
The trusted caller supplies the private immutable Plan.bindings produced by
`fork_frames::request` under `begin`; never reread resumed parent memory. Normal
admissions cannot run between capture, comparison, actual copy and local clone.

At copy admission the gate validates binding-domain shape and derives both u16
masks from all bindings: bit n is remote FILE selector n3..15, regardless of the
logical slot. Console/pipe selectors are separate domains. Duplicate FILE
selectors, malformed flags/holes/unsupported kinds and invalid selectors reject.
Compare both entire masks against actual `ProcessFiles::file_view_v1(parent)`;
omitted/extra FILEs, wrong flags and stale/retired keys cannot invoke copy.
The gate queries the authoritative ledger immediately before the synchronous
serialized-copy borrow; no file mutation or user callback intervenes.

A preflight error moves to Rejected, keeps normal and further copy admission
closed and returns Mismatch or FileView(actual ProcessError). It does not alter
parent flags/positions, send source requests, close the source, thaw the parent,
release holders or fabricate a negative parent disposition. Explicit owner
reconciliation/fail-stop remains necessary. This small phase is not a recovery
or retry framework. A source already retired stays retired.

[Current evidence](../../docs/evidence/authoritative-fork-file-view-2026-10-22/README.md)
adds nine actual-library gate tests and six compiling omission controls with
synthetic storage/native outcomes. FILE3..15 flag bits, logical-slot reordering,
pipe3 versus FILE3 and inherited shared offsets/independent flags are covered.
No native execution or complete stream comparison is established.

## Authoritative streams and child activation — decision0204

The current `copy` takes the complete captured `Plan`, rather than only bindings,
and requires the explicit `ForkStreams` implementation. It first performs the
same complete FILE comparison, then calls read-only `validate_fork` before any
native copy callback. Validation errors enter Rejected with `Streams(actual_error)`;
no file/source/pipe mutation, implicit cleanup/thaw or copy invocation follows.
Normal admission and retry remain closed.

`fork_streams::State` owns two actual SESSION pipe cores and three optional live
parent console source records. It is the actual dispatcher state, not a snapshot
mirror of another live dispatcher. `new` moves cores and checks console source
shape/duplicates. The owner supplies console records only after actual endpoint
ownership is established. `console_closed` records a confirmed actual close;
unknown closure retains the record and requires fail-stop. Native grants/console
closure observations remain independently authenticated by the eventual owner.

From all sixteen captured bindings, validation derives at-least-one local alias
per stream (CLOEXEC retained). It compares complete live console records, both
pipe parent endpoint holdings, full source reference/selector/rights/bound and
each pipe's retained creation history. History is checked even for an inactive
pipe with no emitted source. A terminated pipe parent is an error, not empty state.
FILE selectors do not count as console/pipe holdings. Actual alias counts and the
client logical FD table remain client-owned; these are authoritative source/holder
checks, not an invented second client FD ledger.

The candidate `fork_pipe.rs` selects the existing SESSION core production prefix,
with one pure parent view, two unused aliases removed and one equivalent nested-if
collapse for scoped Clippy. See fork-pipe-provenance.json and retained diff. Its ring,
holder/EOF/EPIPE/staging/generation algorithms are retained. The original ABI24
source/owner/provenance stays byte-identical. State holds two existing256-byte
rings plus core/source metadata, seven temporary usage booleans and bounded loops;
no clone of either ring for validation, heap, extra service or native operation.
Whole executable/frame/stack/heap/channel fit is still required.

Only while holding normal or copy/reconciliation admission may the owner obtain
`pipe_mut`. Its requests are existing local0x7800-core frames; the eventual owner
must route/check tagged0x7900 frames using the established two-pipe protocol.
This API does not silently reinterpret an external frame or grant native rights.
Safe borrowed pipe access cannot escape the gate callback; retained compiler
probes reject escaping references and callback reentry. Trusted owners can still
misuse ownership or invent observations: this is not a sandbox for owner code.

After exact authenticated bound context-ready, `context_ready` now enters
Activating and calls `child_ready(pid)`. The concrete State maps canonical ABI29
child slots2..4/epochs1..15 to existing pipe peers1..3 and requires matching staged
holders in both cores. Only successful activation permits Ready, then complete
parent disposition permits Idle. Activation error retires; unwind leaves Activating
closed. Partial activation retains actual state for native settlement and cannot
publish parent success or fabricate a no-child refusal. Application readiness
remains distinct. This closes the earlier gap where the gate could not activate
holders before parent delivery. The nine FILE/admission tests explicitly use a
labelled stream double; six new tests exercise real State/core integration.

[Current evidence](../../docs/evidence/authoritative-fork-stream-view-2026-10-22/README.md)
records15 tests, four compiling omission controls, borrow denials, strict
format/default Clippy and host/native no_std library builds. Actual native copy,
console operations, startup/ready transport and complete owner are still unwired.

Corrected TLS85 is now selected as a candidate input: seal
f14badab992cf50de4b3443093ccd4b65aa01b1ba1bcf4fa7447672d26b962d4,
ELF279568/SHA366287d33cff71c33db24247fb214dd6099bcb6359d28b3f6866e9de11dc2b96.
We verify its complete closure and independently run the unchanged actual Aether
parser: all seven host tests pass, including actual TLS positive, old stage81
no-TLS denial and malformed TLS/WX controls. Missing TLS is no longer an input
blocker. Parser acceptance is not native execution or complete peak fit. Old
stage81 and default/released pins remain unchanged. Remaining local work is full
native holder/copy/refusal/greeting/ready/parent/terminal/endpoint/readiness/shutdown
composition, whole fit and fresh matching Aether witnesses under BG-069/070.

## Gated transport capture and placement boundary — decision0205

`capture(decode)` enters Receiving before callback I/O and validates/reserves the
actual decoded nonzero increasing sequence on complete return. Sequence remains
unreserved during input. Invalid/old sequence or decoding error enters Rejected
without implicit source cleanup/thaw; host unwind stays Receiving. Copy is legal
only after completed capture in Capturing. Known-sequence begin now also uses
Receiving during its callback. No predicted wire sequence or second queue.

`fork_transport::receive` owns this acquisition order and uses existing Kernel
transfer/wait, authenticating endpoint/parent observations externally. It reads
exact16 header bytes before any body; unsupported header consumes no body. It
assembles exact304 bytes with short transfers bounded to16 and a shared caller
poll budget, preserving raw errors and rejecting EOF/overcounts/positive wait
statuses. Poll budget bounds calls, not wall time inside a blocked native wait;
actual owner watchdog/fail-stop remains separate. RAII clears both caller-owned
304-byte buffers on success/error/host unwind. Parsed Plan owns its data. Native
panic-abort has no unwind cleanup guarantee; retain actual native obligations.
No request memory is reread after parent resumes. Extra bytes are left for the
next framed admission; this decoder makes no claim to authenticated transport.

Twenty actual-library/core/capture host tests/four compiling omissions pass, with
304 truncated prefixes, malformed input, sequence gaps/replay/zero/final value,
short/EAGAIN, raw wait/count/budget failures and closure/clearing on unwind. Native
libraries build, but no full native owner/transport execution is claimed.

Native placement is now blocked: the concrete gate2968 and required4096-byte RPC
workspace need7064 resident bytes; current owner has only a4096-byte stack page,
RO code and no supervisor allocation. See [placement handoff](../../docs/OWNER-PLACEMENT-HANDOFF.md),
BG-072 and exact target/source evidence. An opt-in8192-byte zeroed RW/NX mapping
within existing owner backing is requested; no new quota, guessed memory grant,
writable code, second FS owner or old input change. Full native wiring/fit and
matching target witnesses follow the exact placement contract. Earlier FILE/
stream and corrected TLS85/parser inputs remain resolved.


## ABI30 placement and constructor boundary — decision0206

The selected AENFS004/ownerABI30 contract supplies8192 private zeroed RW/NX bytes
at0x900000 within existing backing. Entry bridge captures r10/r11 before its first
call; original six grants stay unchanged. No owner_main/native boot is supplied
by the bridge. owner_region.validate returns inert Binding; unsafe claim requires
actual unique one-time boot authority. Safe from_storage accepts exclusively
borrowed MaybeUninit<u8> storage, initializes it, validates bounds/alignment and
partitions a single typed slot plus4096 workspace/spare without overlap. Native
claim checks initial zero bytes before any typed write. The original storage must
remain MaybeUninit because valid T writes can invalidate padding. No automatic
Drop/settlement, general allocator or restart is implied.

Owner.initialize writes each field in its uninitialized destination before creating
its first Self reference; its concrete local construction frame is56 bytes,
excluding caller inputs/callees. Four new actual-library placement tests/four
compiling omissions and20 prior regressions pass. Native builds/disassembly are
not actual permissions/zeroing/entry or full-stack/whole-owner acceptance.

BG-072's missing mapping input is resolved. The existing opaque FILE broker's
by-value connect still reserves6504 bytes in size-z (5328-byte noinline callee),
above4096 stack. Opt3 and isolated constructor alternatives exceed the code bound
for measured subsets. [BG-073 handoff](../../docs/BROKER-INITIALIZATION-HANDOFF.md)
requests a narrow safe in-place constructor with explicit partial-failure/resource
semantics. Old APIs/bytes/pins stay fixed. This is a selected construction blocker,
not a whole-owner minimum-size theorem. Full routing/transaction and native
qualification remain sys-init responsibilities.
