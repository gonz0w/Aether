# UL-007/081/082 C file-client transport review

Pre-code scope: add an opt-in C17 file-client transport using sealed AEFD0001
v3 codec. Existing linked ABI29 shell/startup/console/pipe/exec bytes are unchanged.
Sys-init/Aether current STATE still lack full dispatcher and immutable executable
admission. No sibling implementation changes, native campaigns or new authority.

Client borrows trusted callbacks/context and one dedicated caller-owned4096-byte
workspace for its lifetime. Callback read/write receives at most64 bytes and reports
actual count or private -11 would-block; wait direction matches the failed call.
No other error retries. Zero/oversized count, EOF, failed wait, malformed response,
partial completion or exhaustion retires exactly once and clears workspace. Both
raw close outcomes are retained; local closure does not imply native settlement.
16384 I/O attempts bound each entire request, with at most one wait per attempt;
callbacks must enforce their own deadline and actual native endpoint authority.

Only exact open-component/read/seek/duplicate/close/set-cloexec layouts or empty
unsupported opcodes are emitted. Locally invalid arguments cause no transport
calls. No next request until entire response header/body/padding is validated.
Known semantic negative statuses consume sequence and may continue. UINT64_MAX
is never sent. No replay, reconnect, fallback or libc symbol interposition.
No concurrency/reentrancy; callback/context/state/arguments/output/workspace must
remain valid and nonoverlapping, with unique client access through the exchange.
Caller consumes successful read workspace only after complete validated exchange.

Simpler alternative: expose pure codec and let every facade write its own loop.
Insufficient because partial transfers, budget, pending sequence and retirement
would then be duplicated at the immediate C consumer seam. Borrow the existing
AF07 fail-stop/short-transfer model, not a new asynchronous RPC framework. Remove
no accepted old protocol now; the new client centralizes the file-only loop before
explicit facade selection. No new runtime dependencies beyond the existing C codec.

Pin v3 source manifest and complete prior evidence manifest/archive before extracting
actual C requests/Rust replies for host callback tests. Do not execute archive code.
Use selected pinned Clang21.1.8/C17 strict warnings/UBSan, formatter and owned process
helper, clean environment,60s compile/30s tests,16MiB stream bounds. Record SDK
header closure/resource headers/runtime before compilation and recheck. Test all
short chunk widths, would-block directions, every response/request interruption
prefix, corrupt identity/status/body/padding, zero/oversized/error returns, failed
wait/budget, exhaustion, negative semantic error continuation and exactly-once raw
closure. Include compiling semantic omission controls. Native object/link/fit and
actual C-to-live-Rust invocation are distinct from replaying recorded Rust responses.
Run minimum/current Python, syntax/whitespace/format and local quality gate; retain
failed attempts. Independent review and full UL/M3/R1 remain open.

Qualification adjustment: the minimum Python lacks optional lzma and could not
open the prior xz archive; this failed setup is retained, not a passing test.
Current Python's verified streaming extraction is preserved as two plain fixtures
(704/832 bytes) with exact prior exchange hashes/provenance, allowing both
interpreters to consume identical bounded bytes without new external tools.
Abort now clears and releases its workspace pointer before external closure,
allowing safe repeated abort after the caller reuses that borrowed storage.

## Implementing-agent review and final outcome

The runtime uses one transfer loop with a single exchange-wide attempt budget;
requests are fully shape-checked before callbacks. Only would-block waits retry
at the exact current offset. Local argument errors preserve sequence/reply metadata
and emit nothing. Response decoding is followed by full padded body validation;
only then are sequence and output metadata published. Semantic negative errno is
not a transport failure and permits the next request. MAX-1 advances to MAX;
subsequent exchange retires before any transport call. No implicit reconnect exists.

Abort consumes live state before external close, clears then releases workspace
and retains both raw close outcomes. A later abort/exchange does not touch released
storage or repeat cleanup. This is ordinary C lifetime discipline, not a Rust-like
borrow proof or native endpoint enforcement. All callback/context/argument/storage
lifetimes, serialized nonreentrant access and callback deadlines remain explicit
trusted caller preconditions. No code/stack/heap/channel fit is inferred.

Final minimum3.10.21/current3.14.7 qualify identical source/checker inputs,1631
schedules and seven assertion-specific compiling omissions each. Strict C17
warnings, format and UBSan pass;105 SDK headers/resource headers/runtime are
recorded before compile and rechecked. Raw argv, environment, timeout, tool/binary
hashes, stdout/stderr and completed owned cleanup are retained for each command.
Recorded C requests/Rust replies match exact historical hashes. This experiment
uses scripted endpoint callbacks, not a live Rust service, native trap or OpenZFS.
Earlier dependency tests are reused only for their original unchanged-byte scope.
No new native object, link, stack/heap measurement or shell acceptance is claimed.

The initial target-string mismatch is a tooling failure, preserved with its exact
checker. The minimum Python's missing optional lzma is a pre-compilation setup
failure; hash-pinned plain fixture copies remove that optional tooling dependency.
Review improved workspace-pointer release; earlier passing predecessors remain
recoverable. Final tests were rerun after the correction; no warning suppressions.
The local quality gate passes with runtime/full-audit/reader/publication NOT RUN.

All six exact owned attempt roots were archived, every regular file hash/size read
back once in streaming mode, and only then removed:4437965 logical bytes removed,
253508 archive bytes retained. Physical reclamation was not measured. Immutable
prior wire v3/evidence manifests and all member hashes remain unchanged. The new
nine-member source-only candidate matches current source/contract and is separate
from all existing selected shell/SDK/native inputs. No unrelated roots, sibling
files, accepted owners, grants/limits/pins or historical evidence were changed.

Documentation updates cover contract, architecture, acceptance, work follow-ons,
current evidence, contributor inventory and scoped internal output exception.
Project intent did not change. Independent affected-owner/reader review, selected
facade/FD routing, startup/console/pipe/native copy/failed-exec, immutable image
admission, matching dispatcher, measured native fit and assembled runtime remain
open; full UL-007/081/082/M3/R1 are not marked complete.
