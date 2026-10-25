# Private stdio write candidate (UL-067)

The host-only [vector gatherer](vector.c) is a candidate building block for the
[SDK audit's writev gap](../../docs/research/TOYBOX-NATIVE-SDK.md). It is not a public
writev implementation, musl replacement, native adapter or source patch. Native
CAT-04/05/06 remain NOT RUN. Logical sinks0/1 mean output/diagnostic, not native FDs.

Caller supplies a zeroed shared state, at most two valid immutable byte vectors,
a synchronous transport callback and an admitted logical sink. All borrowed
objects must remain valid/disjoint for the call. The implementation validates the
entire vector list before copying: null nonempty buffers fail, total length must
fit PTRDIFF_MAX, and unsupported vector count or sink fails locally. Non-null bad
pointers cannot be safely probed. Callback must enforce actual liveness/rights;
a logical sink index proves neither. Re-entry is supported only through tv_write;
callbacks must not otherwise change state, vectors or payload.

Gather at most16 bytes into private stack storage, in vector order, and issue
exactly one callback. Return a validated short positive count unchanged. There is
no internal retry or retained cursor. The future musl adapter must advance its
vectors by that confirmed count, as __stdio_write already does. A zero result on
nonempty input becomes EIO, preventing an endless zero-progress stdio loop. Zero
length still invokes the callback to validate the actual sink; malformed arguments
do not. Empty writes therefore do not manufacture success for an invalid binding.

Known callbacks require known=1, count within the submitted size, and either
error0 or negative errno -1 through -4095 with zero count. Unknown or malformed
results poison the shared state; later calls cannot reach transport. Re-entry also
poisons it and makes the outer result unknown even if its callback reports success.
Unknown count0 means no confirmed progress, not proof that no bytes were committed.
Known failures do not poison by themselves; no retry is performed. No concurrency,
signal safety, remote recovery or descriptor cleanup is claimed.

## Private libc integration proposal

A later separately reviewed __stdio_write replacement would convert a known count
to ssize_t, a known negative errno to -1/errno, and unknown to -1/EIO while preserving
the poisoned connection. It must use the same poison/ownership state as scalar
command I/O and finalization. Separate per-sink states must not permit a diagnostic
write after shared-channel uncertainty. The current host tf_state/tv_state are not
that integrated transport state; composing them remains explicit work.

Bind FILE output and diagnostic descriptors only after complete owner-approved
bootstrap. Do not register ambient stderr or widen the syscall header globally.
Keep the underlying musl write loop, F_ERR/error handling and partial-vector
progress visible in tests. Retain UL-044's evidence as a different descriptor
fixture; this candidate deliberately contains no file-open/seek policy, counters
or transport from that fixture. Reader vectors and buffered-input seeks remain
outside the candidate.

The [actual musl callback fixture](STDIO-LOOP.md) now exercises the narrow
replacement in Linux reference. Before native integration, compose its shared
poison state with finalization. Verify split
vectors, partial progress, zero progress, known failure and lost acknowledgement,
including an attempted later diagnostic on the same poisoned state. Keep the
uninstrumented control and exact source/patch/link identities. Then qualify actual
native roles, poisoning and cleanup with an immutable owner-produced bundle.

## Process-mask proposal and host candidate

Toybox calls umask(0), saves the previous value and restores it. The current SDK
forwards umask through an unsupported native operation; returning0 unconditionally
would conceal this missing state. Recommend a process-owned mask initialized once
by reviewed startup policy, with a proposed initial value0077 for the bounded
fixture. This initial value is a proposal, not an accepted boot default or new
wire field. No process-mask value confers native authority.

The [host candidate](MASK.md) now returns the previous permission-mask value
and replaces it with the requested low nine bits. Native integration is not implemented. Its storage belongs to the process
context, not a global shared service or a per-thread copy. Under the current
single-thread fixture, no concurrency primitive is implied. Future threads must
share the same process state; spawn/exec inheritance, reset and lifecycle require
explicit owner decisions before widening the scope. Failed/unvalidated bootstrap
must never expose a fabricated initialized mask.

Test save/restore, repeated calls, high-bit filtering, two isolated process contexts
and generation reset with exact before/after oracles. There is no file creation in
the stdin-only cat scope. Before any creation API is offered, the namespace owner
must define where the requested creation mode is combined with this mask and
native grants; a local setter alone cannot qualify those semantics. Keep open,
chmod, login identity and package installation outside this experiment. No new
shared normative requirement or kernel operation is allocated here.

## Reproduction and evidence

```sh
python3 -B experiments/toybox-reference/check-vector.py
```

Run from repo root with pinned Clang21.1.8 and Python3.12+. The driver uses private
build roots, strict C17 warnings, UBSan, pinned format and owned60-second commands.
Help/version use stdout0; usage errors stderr64. Source/plan/tool identities and
raw output are retained in [evidence](../../docs/evidence/toybox-vector-2026-09-06/summary.json).

36,992 scenarios combine all two-buffer sizes0–33, both sinks, eight callback
outcomes and recursive/nonrecursive calls. Independent flattened-byte expectations
check order and exact size. Eight boundary controls cover invalid trailing vector,
overflow, null/count/sink/callback/state failures and an empty call. Three compiled
mutants suppress zero-progress error, clear poisoning or overwrite the gathered
prefix; assertion oracles reject each. This is host C evidence, not actual libc,
authority or native performance evidence. Owner and independent review remain open.
