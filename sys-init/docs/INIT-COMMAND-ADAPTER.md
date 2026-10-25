# ABI9 command adapter: BG-067

2026-09-08. Producer intake is available locally in
[evidence](evidence/init-command-intake-2026-09-08/README.md). BG-067 is active,
not externally blocked on the role/startup handoff. Independent sys-init owner
implementation and acceptance remain unfinished.

## Accepted integration boundary

The [frozen producer contract](evidence/init-command-intake-2026-09-08/NATIVE-INIT-COMMAND.md)
selects AENMX001/ABI9, three worker images, six channels, 8192-byte supervisor code
and a separate 4096-byte stack. Sys-init replaces the reference supervisor; the
command/file protocol retains its separate responsibility inside that address
space. It is not another isolated service or a port of the ABI16 readiness binary.
Runner slot 0, backend slot 1 and command slot 2 select distinct image grants.
Backend launches first and its handle greeting precedes runner startup publication.
The frozen contract supplies exact argv, AERUN001/AERIO001 carriers and rights.
No package identifier or carrier integer independently confers native authority.

The reference owner occupies 7808 bytes (empty 7784, fault 7824); its remaining
368–408 bytes are not a measured allowance for our implementation. Measure the
composed owner before requesting capacity changes. Preserve the 4 KiB stack and
retain native execution evidence; code size cannot prove stack headroom.

## Required ownership adaptation

Source review of the frozen `user/native-connections/supervisor.rs::launch` and
`user/native-command/success.rs::run` identifies the concrete work:

- Retain request reader/writer and reply reader/writer independently as each
  channel is allocated. A second-channel failure must preserve the first pair.
  Launch failure retains both transfer endpoints and both local endpoints.
  Successful launch transfers request reader/reply writer exactly once; only
  then clear those local ownership entries and publish the worker handle.
- Separate image role, worker slot and current instance generation. Preserve
  first/latest errors, finite attempt budgets and closed unknown outcomes as in
  the existing service owner. Do not replay ambiguous launch or consuming close.
- Keep terminal observation free of cleanup side effects. Client termination,
  protocol reference retirement/readback, endpoint closure and native reclaim
  remain separate facts. A stopped/faulted client must not fabricate normal exit.
- Once clients are terminal and protocol references/readback are settled, close
  the backend request writer explicitly. Retain that completed close while
  waiting for backend EOF termination; then close its reply reader and reclaim.
  A retry must not close the request writer again or reclaim a live backend.
- Reuse the current-state ownership principles. The ABI16 Service/Pair's single
  readiness channel and unconditional terminal-before-close cleanup do not express
  this boundary. Do not hide additional effects in `terminal`, or disguise two
  fallible allocations as one atomic `channel` call. Review a narrowly scoped
  paired-connection owner before wiring it to the existing protocol implementation.

Required host checks cover failure at each allocation/launch/close/reclaim step,
known versus unknown outcomes, stale/foreign instance denial, delayed terminal
and backend EOF-before-terminal ordering. New native owner cases must preserve
real positive/empty output, exact fault kind/status and cleanup, wrong-role and
omitted-close denial. Producer negative cases have zero reclaims and do not prove
recovery. Add partial-admission/cleanup controls to the consuming owner rather
than treating the reference owner's assertion exits as product error handling.

## Simplicity review

Current requirement: run the actual bytecount workload under sys-init lifecycle
ownership. Simpler alternative: substitute the existing Service/Pair directly.
It is insufficient because it cannot retain four independently acquired endpoints
or express backend EOF before termination. Choose a small explicit connection
record and staged cleanup, reusing protocol code and current-generation rules.
Complexity removed now: none; avoid a second command broker, extra domain, generic
journal, parser framework and changes to the already-qualified ABI16 fixture.
Any later common-core extraction must justify compatibility and actual savings.

Foundations O-01/03/04, I-01/03–06 and E-01/04–08 apply to roles, transfer,
partial errors, bounds and exact evidence. Distribution boot transport and service
JSON candidates remain separate profiles. SE-01–05 applies through this review;
no new exception, shared standard or released pin is introduced. Original source
notices and SDK terms are preserved. Independent reviewer approval is not claimed.

## Validation and next action

Intake verifies the pinned 38-file producer manifest, all 196 source and 218
artifact archive members and the SDK archive digest. Fresh execution uses the
producer's five existing images and exact terminal/cleanup oracles; it is neither
a source rebuild nor sys-init policy acceptance. Local checks and raw replay logs
are retained in the evidence bundle. The archived failed producer attempts remain.

Next implement and qualify the paired-connection ownership boundary above, then
compose it with the frozen command protocol and measure code/stack behavior.
Sustained execution (<3000 tick fixture watchdog), idle/wait behavior, operator
shutdown input/final action, full dash and persistence remain separate gates.

## Paired owner component — 2026-09-08

`prototypes/native-supervisor/connection_owner.rs` now implements the bounded
ownership portion above, with one immutable role, one identity/generation,
four independently retained endpoints and one worker. Channel allocation is two
explicit backend calls. Only confirmed launch transfers request reader/reply
writer. Known failures preserve outstanding handles; unknown outcomes close the
owner against all automatic replay. First/latest errors remain inspectable.

`backend_eof` closes only the backend request writer and records that progress
before observation. An explicit stop acknowledgment is recorded separately from
EOF intent, so an unsuccessful EOF close cannot suppress a later stop request.
Terminal detail/kind is cached unchanged through cleanup. Protocol code must
settle file references and readback before authorizing EOF/cleanup; this core does
not invent a second file-reference owner or enforce unimplemented protocol policy.
The borrowed I/O handles do not transfer cleanup responsibility to callers.

Eight host tests and two semantic omission controls exercise this contract.
[Evidence](evidence/connection-owner-2026-09-08/README.md) retains the required
Rust gate and full local checks. The original single-channel owner and Pair remain
unchanged. No new dependency, allocation or unsafe code is introduced. This is
host component evidence only; the module is not imported by any native entry point.

The existing simplicity review applies: four endpoint slots are necessary to
represent independently fallible acquisitions, and separate stop acknowledgment
prevents conflating EOF intent with a completed effect. No obsolete runtime path
is removed while the new adapter is unqualified. The next work is ABI9 trap and
protocol wiring, including actual partial-admission/error controls and linked
code/stack measurement within the unchanged profile. BG-067 remains active.

## Native composition reaches the code limit — 2026-09-08

The candidate in `prototypes/native-command/` now connects the paired owner to
real ABI9 channels, role-based launch, terminal observations and reclamation. It
reuses the frozen protocol source, replacing its lifecycle calls; backend EOF
is explicit before its terminal/cleanup loop. Three owners persist across two
generations. Successful transfer releases only request reader/reply writer.

All three bounded links reject at the unchanged 8192-byte limit. Sizing-only
builds measure8608/8640/8688 bytes for positive/empty/fault; no new image was booted.
Nonzero handle representation reduces the earlier positive8832-byte image; bounded
compiler/factoring trials do not fit. Existing native sources/pins are unchanged.
[Retained attempts](evidence/command-owner-capacity-2026-09-08/README.md) distinguish
link failures, measurement-only outputs and earlier tool setup errors. The adapter
is candidate code, not fresh target acceptance; stop/partial error/stack validation
still remain. Close/reclaim errors conservatively retain Unknown ownership.

SE review: retain the current owner and established protocol as the simplest
composition to test first. Using nonzero handles removes avoidable representation
cost without removing authority/error checks. Do not remove semantic oracles or
borrow ABI16's allowance to fit this ABI9 build. BG-068 now owns a scoped code
capacity/design decision before further native execution; it is not authorization
to modify Aether. No common framework, extra domain or shared standard is added.

## Capacity resolved and native owner exercised — 2026-09-08

BG-068 is complete. Symbol review identified575 bytes in the linked compiler
byte-comparison implementation. A scoped freestanding scalar memcmp replaces it
for this command image; current code is8016/7992/8080 bytes for positive/empty/fault.
All enforced links pass the original8192-byte assertion. No kernel, profile, stack
limit or lifecycle/authority/error check was removed. Earlier size failures remain
historical evidence and are not rewritten.

The helper compares unsigned bytes and returns the sign of the first difference.
Its unsafe C boundary requires readable len-byte ranges (overlap/unaligned allowed),
no concurrent mutation, and accesses neither pointer for zero length. Volatile
reads prevent recursive lowering into memcmp. It is for ordinary memory, not MMIO
or constant-time secret comparison. Three host tests and two omission controls
cover its exact contract; native symbol export is restricted to target_os=none.
Native inventory records the new unsafe sites. This is a deliberate small-runtime
tradeoff: lower code cost in exchange for scalar comparison, with no speed claim.

[Five fresh Aether cases](evidence/command-owner-native-2026-09-08/README.md) pass
with sys-init lifecycle ownership and the frozen protocol/application inputs.
Positive/empty/fault complete two generations/six reclaims; wrong-role/omitted-close
retain their precise rejection and zero-reclaim semantics. The existing4 KiB stack
suffices for these executions; peak usage and other schedules are not measured.
A linker-library environment failure occurred before boot and is retained.

Next BG-067: add native partial-allocation, rejected-launch and cleanup/stop error
controls for the new adapter. Host component controls and producer negative cases
do not qualify those real failure paths. No external capacity handoff is now
needed. Sustained boot, operator shutdown, full shell and release remain open.

## Native failure boundary qualified — 2026-09-08

[Eight final native probes](evidence/command-owner-failures-2026-09-08/README.md)
exercise actual first/second channel EBUSY, invalid-startup EINVAL, missing-handle
stop EBADF with retry, and conservative Unknown after close/reclaim errors.
Deliberate external handle consumption tests retained ownership state; it is not
a supported competing-owner operation. Two native omission controls reject missing
partial cleanup and replay past Unknown. The normal three command owner variants
remain byte-identical, including the shared positive image used by both existing
command negatives. No runtime/profile pin, unsafe site or sibling changes.

An initial oracle confused decoded controlled-stop detail143 with raw observation
144; the failed run is retained. The native owner correctly reports143/kind3.
Controlled stop does not produce an ordinary worker-exit serial line, so the driver
uses actual in-image terminal checks plus exact supervisor/reclaim/panic outcomes.
These probes remain bounded allocation/stop/cleanup experiments, not actual
command-protocol cancellation or recovered unknown cleanup. The public policy
and original error classification are unchanged.

SE review: use a separately selected small probe with direct native calls and one
denied-stop routing flag; reuse the paired owner and existing real images. This
avoids extending the protocol state machine merely to arrange allocation failures.
No current production path is removed. New cfg selection compiles away from normal
images; the three compatibility builds verify that claim. Next BG-067 exercises
controlled stop during actual command exchange and settles file-reference policy.

## Actual command-stop candidate: link blocked — 2026-09-08

The separately selected `success_stop` candidate stops at the first complete
command read before any backend effect or reply. It reuses actual terminal
observation, abnormal file-alias retirement and runner collection; the proposed
oracles require143/kind3, runner1, unchanged input/empty output and six reclaims.
The retirement omission control is prepared, not executed.

[Retained capacity attempts](evidence/command-owner-stop-capacity-2026-09-08/README.md)
all fail the original8 KiB assertion. Final sizing-only output is8336 bytes; no
stop image was booted. Normal three supervisors remain byte-identical. Next
BG-067 resolves this144-byte code gap through scoped layout review before native
qualification; do not infer a need for new kernel mechanisms or relax checks.
BG-068's prior successful command-size resolution remains historical and valid.
No released pin, sibling file, new unsafe site or accepted ABI changes. SE review
is in the linked evidence: reuse current state/cleanup; no additional machinery.

## Controlled command stop qualified — 2026-09-08

[Seven fresh native cases](evidence/command-owner-stop-2026-09-08/README.md) pass:
first-read stop, missing-retirement rejection and all five existing command cases.
Borrowing completed frames and consuming decoded terminals directly removes
redundant copying/zeroing and raw encoding. Stop/control each link at8176 bytes;
all original profile bounds and semantic checks remain. Normal image bytes changed
and were freshly tested. Earlier link failures remain historical evidence.

The stop point consumes a complete request before any backend effect or reply.
Actual143/kind3 precedes reference retirement, runner collection/status1, backend
readback/EOF/status17 and six reclaims. This does not qualify interruption after
an effect, sustained idle, graceful shutdown or operator poweroff. The control-only
black_box keeps retained aliases opaque to optimization; ordinary checks reject
missing retirement at1403/reclaimed0. No new normal-path state or unsafe site.

SE review and applicable O-04/I-04/I-05/E-01–08 evidence are in the linked record.
The bounded BG-067 command slice is now qualified; next review a matching sustained
wait/watchdog and authorized shutdown handoff. The frozen producer packet leaves
those explicit gaps. Current sibling signal work does not authorize an ABI9
terminal-kind extension. No sibling change or request, pin update or larger code
profile was needed.
