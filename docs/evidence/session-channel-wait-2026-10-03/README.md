# ABI24 channel waiting: implementation review

Before-code assessment, 2026-10-03. Requirement: the selected single-context
AENMX009 worker must be able to sleep while a channel transfer would return
EAGAIN, so an interactive shell can retain pending stdin without a polling limit.
Aether owns enforcement and private probes; userland owns the consuming runtime,
sys-init owns boot/session policy. This is an experimental additive ABI24 operation,
not a published SDK or consumer acceptance. Released standards pins remain unchanged.

Allocate `0x24004`: RDI is the caller's exact endpoint; RSI/RDX/R10/R8/R9 must be
zero. Only AENMX009 implements it; other profiles return ENOSYS (-38). Read endpoints
wait for bytes or writer closure; write endpoints wait for space or reader closure.
Return zero is a readiness hint, not a transfer or EOF. Retry read/write with the
original partial offset; wait never copies bytes or retains user pointers.
Invalid, foreign, closed or stale authority returns EACCES (-13). Reserved arguments
return EINVAL (-22) after authority validation. A pending unmasked signal returns
EINTR (-4) without dequeue/delivery; existing explicit signal processing remains
necessary. Authority loss precedes interruption, which precedes readiness. Masked or ignored
signals cannot wake a waiter, including ignored occurrences retained across exec. There is no timeout, wait set, cancellation grant,
automatic handler injection or SA_RESTART policy in this operation.

IF=0 serializes ready check, one domain-local registration and scheduler exclusion.
Recheck actual holder, full endpoint/generation, signal mask and stream state before
selection and scheduling. Read/write/close/transfer/terminal changes thus wake only
matching waiters. Stop/terminal clears registration before backing retirement; reuse
cannot inherit it. All blocked contexts enter the existing kernel HLT path. At most
one 8-byte wait record per domain, no allocation and bounded scans over six domains
and ten channels. This BSP-only profile does not establish cross-core ordering or
multi-threaded wait support.

Forbidden: ambient worker authority, lost readiness between check and park,
fabricated transfer/EOF, replayed partial data, stale grant resurrection, rewriting
another syscall's saved completion, wait state surviving teardown, old-profile
behavior changes or claiming healthy shell idle before a matched client exists.
Focused host state transitions cover readiness, close, transfer, generation reuse,
interruption and one-shot completion. Native probe must exercise actual blocked
workers, delayed owner wake, backpressure, peer close and stopped/reused waiters.
Selected legacy ABI22/23 and M4 scheduler regressions plus full host/pin checks are
required before qualification. Missing native interruption/consumer/reader coverage
must remain explicit. Document exact operation in NATIVE-CONNECTIONS and progress
in STATE; no new public script/profile or dependency is planned.

Simplicity (SE-01–05): the simpler alternative is continuing EAGAIN polling without
a counter. That burns a runnable context while the human is idle and cannot meet
the requirement. Borrow only the conventional atomic readiness-check/park/rescan
idea, using existing endpoints and scheduler; no separate event service or wait-set
API. Added cost is one bounded wait record and readiness scans. It enables later
removal of the selected client's arbitrary polling budget; no obsolete legacy path
is removed now. Existing pointer validation, ownership, finite quotas and cleanup
remain authoritative. Zig 0.16 formatting applies to touched kernel code; new Rust
private witnesses use Rust 1.98/edition 2024, abort on panic and documented synchronous
trap ownership. This review does not claim independent security assessment.

## Bounded qualification

Final `qualified.json`/`qualified-serial.log` passes seven actual worker generations,
3033 ticks/3023 idle and seven confirmed reclaims. The owner sleeps while a worker
is blocked for3005 ticks; then a real byte wakes it. Other cycles cover writer EOF,
full-queue writer wake after a read, owner stop while blocked then slot/backing reuse,
reader-close EPIPE under full backpressure, and a masked queued signal that leaves
read wait blocked. Unmasking produces EINTR twice without dequeue; installing ignore
then permits progress. Every worker checks foreign endpoint/factory-as-endpoint
denial and all five reserved fields. Owner stale waits reject after transfer/reclaim
and across subsequent channel generations. Exact terminal rows include generation4
stopped143; all other generations exit0. No client byte is supplied or forged by QEMU.

`negative-qualified` changes the worker's expected foreign-end denial to success.
It exits77 in generation1; owner fails before qualification/halt with the exact
failure marker and supervisor panic. This is an intentional failed invariant oracle,
not healthy shell acceptance. `verify.py` checks the retained final trace and rejects
12 named corruptions (missing/duplicate/wrong terminals, halt/idle/reclaim/marker
changes and panic). It is an offline aid, not an independent native replay.

Final regressions: `regressions-final/legacy-session.json` passes all11 fresh-owner
ABI23 serial cases using exact sealed worker payloads; `legacy-init.json` passes the
old ABI22 mechanism; `m4-final-command.log` records all seven M4 cases. Final host
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global` passes
132 Python tests, configured Zig/Rust tests, workflow and all released pins. Zig/
Rust scoped format checks, Experience and simplicity snapshot hashes pass. Actual
ENOSYS on009-disabled profiles is enforced by the dispatch guard; old regressions
do not separately invoke this new operation. No sibling or released-pin changes.

Private owner2184 bytes; ELF-derived raw bytes equal the native raw image. Scoped
stack aid estimates440/4088 bytes for the owner and88 for the worker function plus
24 conservatively charged for entry alignment/call (native worker stack64KiB).
Immutable GOT400880 points only to memset4007e0. The sole indirect jump is a local
five-cell immutable table400828: unsigned index check<=4 before dispatch, all targets
inside _start. `inspection.json`, assembly and constrained stack aids retain this
manual provenance. These are bounded inspection estimates, not whole-kernel stack
or security assurance. Final owner equals the earlier signal-test owner byte for byte.

Final frozen source map/export and exact build/QEMU commands live beside each run.
`environment.json` records tools, firmware, current-source equality and released
pin identities. Kernel surface grows by a readiness predicate/registration scan,
not by a privileged service; no allocation or borrowed user buffer is added.

## Retained attempts and limitations

`positive` rejected before admission because the probe used unpaired launch23000
with paired grants; corrected to23002. `positive-final` qualified six cycles, then
`positive-signals` qualified seven. Final rerun follows the ignored-after-exec fix;
old passing runs are retained rather than rewritten. `negative` and `negative-final`
are earlier intentional invariant controls. Preparation notes preserve the wrong
working-directory reads, unmatched exploratory wildcard and original stack-aid
failure (it assumed absent memcpy/memcmp symbols). The corrected aid admits only
the exact inspected memset call and checked local table. No failed target is counted
as a successful mechanism run. All newly owned temporary outputs are archived and
verified before cleanup; source exports and previous evidence remain intact.

This qualifies a private single-core/single-context mechanism, not a shell runtime,
public SDK or actual sys-init consuming result. Async peer signal posting while
parked, automatic delivery/restart, cross-core races, wider wait combinations,
independent technical/reader review and actual consumer adoption remain unqualified.
No external signal injector is added here. Next match userland's client/runtime to
wait on EAGAIN while preserving partial frames, handle EINTR through its actual
signal policy, and test a genuine dash prompt with delayed serial input. Persistence,
packages, assembled boot image and R1 remain open.

`artifacts.tar.gz` preserves596 file members from13 newly owned temporary
roots; every member was read back and SHA256-checked before deleting those roots.
`cleanup.json` records their exact paths. `kernel-review.patch` isolates this task
against the previous sealed producer source; the inherited working tree is retained.
