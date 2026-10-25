# Selected opt-in fork frames and owner admission

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

Aether requires comparing the full request against actual parent file view before
copy. Current ProcessFiles exposes current key/position/flag mutation but no pure
exact file-slot/cloexec validation. Source proof is retained in evidence. Positions
cannot reveal flag mismatches; destructive exec-close or normalizing parent flags
is not a valid read-only preflight. A second mirror ledger would violate this
composition's single authoritative-view rule. BG-071 requests a small separately
versioned pure validation/metadata seam, such as exact presence/cloexec bitmasks for
13 file selectors under an opaque current key. No public name is invented here.

BG-069/070 remain active; the gate/frame components are prepared, not the full
native transaction. After BG-071 input, wire snapshot comparison plus actual stream
holdings/history, native freeze/copy/refusal/child greeting/context-ready/parent
disposition and terminal/endpoint/holder/readiness/shutdown. Use verified stage81
and measure complete fit, then fresh Aether positive/refusal/unknown/continued-
parent/wait/cleanup/readback. Immutable executable/failed-exec/public dup2/wider
shell/TTY/packages remain separate. No sibling edits/messages, guests or quota
expansion. Old owner/source/evidence/default/release bytes stay fixed.
