# Armed fork stage and child constructor — UL-007/081/082

The opt-in AEFD_FORK_BINDINGS client now provides a real __aether_fork_stage and
one-shot child constructor for Aether's proposed AEFORK01 profile. The complete
pinned dash/CRT/libc/public-fork/copy_rebind link succeeds. This is a build and
host-qualified client candidate, not a selected sys-init transaction or executed
native filesystem shell. Old startup APIs and the default binding path retain
their existing contracts; no old83/64 snapshot or successful fork stub is used.

## Storage, state and authority

One stable5040-byte aggregate contains the existing4952-byte startup/context and
88 bytes of compact arm metadata. Boot is first; no heap, second boot object,
second descriptor ledger or automatic304/4096-byte frame. Existing scratch304
holds the parent request; only the actual child uses its private workspace prefix
to retain that inert request while scratch receives its fresh greeting. Neither
normal callers nor an ordinary startup retry can reset an admitted/copied object.

Only current shell1 may arm, and only once at a time. The per-channel counter
never wraps or reuses a reserved sequence. Public struct fields are trusted
implementation storage, not an untrusted admission API. Native identity/channel
labels and the captured request are assertions to compare with authenticated
kernel/owner observations; they confer no process or source authority. The stage
only parks the caller with0x23003. The supervisor still owns actual freeze-token
observation, copy/admission, reservations, thaw and all native settlement.

| State | Allowed work |
| --- | --- |
| IDLE | Exact live shell preflight; sequence exhaustion rejects without native calls. |
| SENDING | Whole native/context guard held; capture and send full304-byte snapshot. Reentry cannot enter parent/child completion. |
| ARMED | Exactly one actual native park is next. Guard remains held. |
| PARENT | Consume one correlated owner disposition; no FD work or child-constructor reentry. |
| CHILD | Quarantine inherited context before any callback; only fresh-grant validation/rebind/startup permitted. |
| READY | New child context and context-ready transmission complete; upstream __post_Fork still precedes application return. Child cannot originate another fork in this bounded profile. |
| FAILED | No retry or ordinary startup/reset. Native entry exits directly, without libc finish on inherited labels. |

## Parent path

Under pinned _Fork's outer blocked signal mask, arm enters the existing whole
context guard, observes actual native PID/PPID, captures current full map with
cloexec preserved, exact source records and pipe histories into scratch, validates
against native observations and reserves a sequence before sending. It does not
reuse the original startup map as a live snapshot. The send and subsequent reply
share the existing16384-transfer-attempt budget,16-byte transfers and native wait
adapter. Attempt bounds are not wall-clock deadlines: native watchdog/stop remains
owner policy. An enforcing owner gate must precede snapshot admission; client
signal masks cannot exclude direct or queued owner requests.

The native x86-64 entry performs one actual int81 park and preserves rdi/rsi/rdx
child grant outputs before any C call. Positive parent return must match a complete
AEFKR001 owner disposition and exact sequence. Confirmed raw thaw-11 can return
the owner's validated private negative error; it cannot invent ENOMEM from EAGAIN.
Known completion restores mask and the prior cached mask field, clears scratch,
returns to IDLE and preserves the entire parent boot/context byte state. Counter
reservation remains consumed. No exec-cloexec or parent finish is copy rollback.

Partial/unknown/stale disposition, invalid raw result or partial request retires
parent transport once and requires direct exit116. This candidate rejects a
negative disposition paired with a positive native copy result even if an owner
claims post-copy settlement; that case fails closed rather than reporting a known
no-child errno. The matching owner must account for this bounded refusal policy.
No retry, compensating thaw, endpoint release or native reclaim is inferred.

## Child-only constructor and musl ordering

1. Only actual native child return0 enters the constructor from ARMED. It marks
   CHILD, boot phase4 and context state4 before any callback. No inherited context
   operation, finish/abort, mask-leave or channel close may execute. Exact request
   sequence must still match the arm; ordinary startup retry remains forbidden.
2. Native getpid/getppid must identify canonical child2–4/epoch1–15 and the captured
   actual parent. Copy-result memory must be the distinct canonical child memory
   grant; channels must be nonzero, distinct and disjoint from both parent channels.
3. The target rebind wrapper checks all three old auxv values against the captured
   parent and calls the pinned copy_rebind compiled with REBIND_LIBC_REPAIR. That
   helper validates the single-thread/TLS/list/lock conditions, bounded auxv table,
   memory ownership probe and channel directions, then updates the three actual
   grants. The wrapper checks the resulting auxv and output labels. No TID repair
   occurs here; target disassembly checks that the rebind object has no set-TID
   trap. No REBIND_SKIP flags are selected.
4. Only successful native rebind permits a temporary borrow/guard of the new
   channels. Preserve the inert request in the child's own workspace, consume
   exactly one fresh304-byte startup in scratch, reject an incompatible header
   after16 bytes, and run full child correspondence checks. This candidate keeps
   exact FD entries/flags/source labels/history while requiring fresh file-channel
   generation/factory0 and actual child identity. Sys-init must select the exact
   source-label retention relationship; it is not an automatic owner acceptance.
5. Only after those ownership and correspondence checks, discard copied metadata
   without executing cleanup and explicitly initialize this child's private
   context. Internal map/client/workspace/native/adapters point to its own stable
   members; sequences, mask/close state and fresh generation are reconstructed.
   Transfer the one masked new-channel borrow into that context and invalidate
   the temporary metadata without leaving its mask or closing channels. This
   special constructor is not a public blanket reset or ordinary startup reentry.
6. Send exactly one correlated32-byte AEFKC001 context-ready receipt under the
   same remaining child budget, then publish READY/boot phase2 and leave the new
   guard. Return0 into the unchanged pinned __post_Fork, which repairs clear-TID,
   TID/list/locks before upstream restores the original signal mask. Context-ready
   is not application/service readiness and does not promise later child survival.

Any child failure closes only actually borrowed new channels once, retains both
raw close results in boot.closed and leaves state quarantined. Pre-borrow identity/
rebind failure closes no guessed or inherited labels. Scratch/workspace clear;
repeat constructor/startup cannot retry. The native entry exits directly114.
Existing mask-restore failure keeps fail-stop125 and once-only new-channel cleanup.
Owner must observe actual child terminal/endpoint/reference settlement before
releasing its holdings; these local receipts are not native rollback evidence.

## Qualification and exact limits

```sh
python3 -B experiments/filesystem-service/check-fork-stage.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/filesystem-service/check-fork-stage.py
python3 -B docs/quality/check.py
```

Run in repository root with pinned provisioned tools/SDK/source candidates. The
private recipe retains exact checker/source/input/tool hashes, argv/environment,
60-second compile/30-second suite bounds,16MiB output streams and process cleanup.
1008 armed stage/child host cases include every request/parent reply/child startup/
ready prefix, malformed startup bytes/early header rejection, native observation/
rebind/mask failures, source/flag/history/generation correspondence, reentry,
unknown/no replay, known refusal/exact parent preservation and child pointer/FD
continuation. A real host fork supplies private copied backing and verifies parent
aggregate preservation. This is a host copy witness, not native copy authority.
Seven compiling semantic omissions must fail assertions.

The same native-entry C body is host-tested by injecting only auxv, park grant
outputs and the rebind boundary. It exercises parent/child/known-refusal returns,
errno preservation and actual isolated host exits114/116/125. It does not execute
int81 or pinned musl TLS layout checks on macOS. Those remain separately pinned
source/object/native integration obligations; no host syscall stub is selected in
the target. Retained5847 frame and78 default libc cases pass. Default target BSS
remains4952; opt-in aggregate is5040. C17/format/UBSan pass.

Twenty production target units relocatably link. Actual native park disassembly,
pinned rebind flags/order, full static dash32/CRT/libc/public-fork/copy_rebind link
and required function symbols are checked. The ELF has four static load segments,
63 PT_LOAD pages, NX stack and no writable-executable load, interpreter, dynamic
segment or relocations. lld retains the same local hidden zero-valued UND _DYNAMIC
synthetic symbol as the pinned old static ELF. The checker verifies that exact
shape and baseline, with no ignored undefined symbols or newly unresolved runtime
reference.119 static frame reports/max664 exclude call chains/libc/interrupts/
whole code/stack/heap/backing/channel fit. These are build properties, not loader
acceptance, measurements of peak fit, native execution or POSIX conformance.

## Concrete next integration block

Current sys-init checkpoint0201 has no matching selected AEFORK01 transaction.
BG-069 must consume this stage and the separate serialized-inheritance API, select
exact framing/source-label/refusal rules and prove the enforcing file/stream gate.
BG-070 then composes actual freeze/copy/refusal/unknown handling, startup/ready/
parent disposition and terminal/endpoint/holder settlement, readiness and shutdown.
There is no authorized sibling implementation here. Aether subsequently qualifies
matched native commands/errors/continued-parent/wait/cleanup and fresh readback.

The old missing-stage link blocker is resolved for this opt-in candidate. Whole
resource fit/native integration is blocked on that matching owner. Immutable exec,
public dup2, wider shell/POSIX/Zsh/TTY/package/persistent ISO and full UL/M3/R1 remain
open. No profile/default/quota/release pin changes, installation or VM run. See
[evidence](../evidence/filesystem-fork-stage-2026-10-22/README.md); independent owner/
reader acceptance stays pending.
