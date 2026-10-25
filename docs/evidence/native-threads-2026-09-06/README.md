# Bounded native threads — 2026-09-06

A native worker can now create one additional context in its own address space
using a separate boot-granted capability. Parent and child keep separate saved
frames, FS bases and floating-point state while sharing their domain's mappings
and authority. Explicit child exit retains status and clears its TID without
stopping the parent. Domain exit, child fault and supervisor stop quiesce both
contexts before reclaim/replacement. All live-context TLS/TID storage and the
child's designated stack page are protected against protect/unmap.

This is the opt-in AENATC01/AENSUP01 experiment described in
[NATIVE-C](../../NATIVE-C.md#bounded-shared-address-space-thread-contract--2026-09-06),
not libc pthread compatibility. The child has no libc TCB and does not call libc.
Its stack/TLS come from the domain's existing bounded memory quota. Child-slot
reuse, blocking waits and an engine-scale thread budget are not implemented.

## Executable results

- Seven thread cases pass in each of the 128-page and 2048-page memory profiles:
  shared-memory/TLS/FP positive, supervised replacement, parent exit with a live
  child, forced stop after child execution, child #UD fault with peer completion,
  deliberately omitted live-storage pins, and extension-disabled rejection.
- Within the positive, bad/foreign/missing/stale-generation grants, nonexecutable
  entry, malformed/unmapped stack, invalid FS/TID, failed-create atomicity,
  consumed creation quota, live stack/TLS/TID pins, retained child exit/TID clear,
  and release after exit are checked by the actual native producer.
- Existing default/large memory suites: 12 + 13 cases pass.
- Large static executable admission/replacement: nine cases pass.
- Two-core/framebuffer regression: seven cases pass.
- Host build/checks: 96 Python cases plus kernel and offline standards/workflow
  checks pass. Changed Zig and the new C fixture pass their pinned format checks.

The live-pin mutant must fail at assertion 194 in both domains; the disabled
extension at 182. The child-fault case requires vector 6 and domain status 134,
with a separate successful peer terminal and matching output summary. Harness
unit tests reject incorrect reasons, missing/duplicate records and false peer
completion. No timeout or generic panic is accepted as those semantic outcomes.

## Inputs and attempts

[Full attempt](final/results.json) records exact arguments, UTC command boundaries
and source digests. Its host, formatting, both thread profiles, both memory
profiles and image suite passed. M4 could not start: the sandbox denied QEMU's
private QMP socket bind. It remains an incomplete/failed overall attempt, with
its raw QEMU error retained; it is not rewritten as a pass.

Review then strengthened only `user/native-memory/threads.c`: shared coordination
uses C11 atomics, and the forced-stop case waits for a child context switch before
announcing readiness. Documentation records that refinement. No kernel, builder,
other producer or harness bytes changed. [Refined qualification](refined/results.json)
reran host/format, both complete thread suites and M4 with local QMP socket access;
all pass. The earlier memory/image results apply to their unchanged runtime and
producer inputs. [Triage](triage.json) identifies the two changed paths precisely.
The `final/` directory name belongs to the earlier wrapper, not an overall pass.

Initial attempts also retain a Zig method-placement formatting error and a C
string-index warning promoted to an error; both were corrected before target
qualification. `before.tar.gz`, `initial-edit.py`, contract and frozen source
archives preserve review inputs. No failed attempt was discarded. The initial
format error has a diagnostic transcription rather than a raw command log.

`target-attempts.tar.gz` retains every thread/memory/M4 attempt listed in
[target-directories.json](target-directories.json), including failed producers and
the denied socket run. `image-target.tar.gz` retains the nine image cases in
`zig-out/native-image-6hl_f8xz`. Producer receipts bind the supplied strict musl
archive, compiler/linker pins, source and ELF/envelope hashes; no sibling source
or consumer pin changed. [Formatter identity](formatter.json) records Clang
21.1.8 and its digest. `SHA256SUMS` covers the retained evidence packet.

## Limits and next work

One extra context per domain lifetime, one-page child stack, BSP-only ownership
and polling inspection are deliberate experiment bounds. They are not sufficient
for the OpenZFS runtime. Next are bounded blocking wait/wake semantics, followed
by libc thread adaptation, measured engine resource bounds and the native engine
port behind the Rust filesystem service. Shell/package release assembly remains.

Independent reader/consumer reviews, optimized target modes, stack-high-water,
extended stress and full draft-standard/release qualification remain open. The
wrappers record top-level UTC timing; inherited libc builders do not record every
internal command boundary. No consumer sign-off or release readiness is claimed.
