# 0211: Reduce resident FILE state and separate operation from reply ownership

2026-10-22 / BG-070 and UL-007/081/082. Pre-code review.

Requirement: finish the actual native owner within the unchanged16384 code,
4096 stack and8192 mapped-data bounds. Decision0210's concrete composed roots
are18768 bytes. Rebuild the exact baseline to inspect symbol/call costs; prior
outputs were correctly disposed. No complete-owner lower bound follows.

The FILE broker has exactly13 shared descriptions but each descriptor stores a
machine-sized index. Use u8 for this private index with a compile-time capacity
check and explicit widening at indexing. Keep Option, separate close-on-exec and
all checked indexing, source/handle lifetime and one authoritative ledger. This
changes private layout only; no wire, rights, capacity, key, error or API change.
The existing fieldwise initializer still writes typed Option values, never assumes
zero is None, and must be remeasured/reviewed after the layout change.

Separate the cohesive FILE operation switch from Connection's frame validation,
pending/reply lifetime and delivery settlement. One private non-inlined operation
boundary returns value/body length and the unchanged structured error. Read/open
workspace clearing, source-loss rejection before replies, sequence advancement,
partial-delivery retirement and actual close outcomes must stay identical. No
handler default-success, unchecked index, error flattening or authority shortcut.
This is a source-level shared code boundary, not new alternate compiler flags.

Affected owners are userland's FILE broker/protocol and sys-init's single owner.
Untrusted requests remain authenticated/bound and fully validated before effects;
unknown outcomes stay retired. No new dependency, allocation, unsafe operation,
channel, worker or quota. Old APIs and sealed deliveries/pins stay unchanged.
No source is changed during a qualification. Host tests do not qualify native
mapping/abort/termination/reclaim or media export.

Select producer broker/description tests and all semantic omissions, current
consumer mixed routing/copy/publication/failure tests and borrow controls, strict
host/native builds/format/Clippy, exact symbol/code/resident/frame observations.
Exercise full13-description occupancy, aliasing/inheritance/close-on-exec and
source failure, and compare old/new protocol replies/effects in a differential
host test when splitting the operation switch. Use the same pinned compiler,
link/default flags and required roots. Keep all failed attempts/short failures,
compact commands/hashes/results; remove owned generated outputs. No VM before
complete native owner fit/admission and fresh scoped persistence disposition.

Simplicity: keeping current code is simplest, but it exceeds the current code
bound and stores a machine word for a13-value private selector. Direct bounded
representation and one explicit operation boundary avoid a new protocol/service,
shadow ledger, generic dispatch framework or allocator. Their benefit must be
measured; reject a change that only relocates complexity or weakens correctness.
No borrowed subsystem, new abstraction layer or broad runtime refactoring.
Full entry/boot/copy/exec/wait/lifetime/shutdown integration remains local work;
partial size measurements cannot justify a quota request or claim Zsh/ISO ready.

Differential reference is the exact prior committed AEFD0001 protocol at
4e32ff296, source SHA2567b8bd810d0cb4943f3e873db65592854fe0001d78afd7418005aa6839bbefc32.
Read it from local Git only, verify before compiling into an owned host-only
reference crate, and dispose the generated copy. No native or released consumer
loads that reference. Exercise success and errno/unknown/partial-delivery paths
against both actual implementations; compare reply bytes, workspace, source
effects and cleanup rather than calling a successful stub. No network fetch.

After the first final affected build: code18176, gate2240/workspace4096, compared
to baseline18768/gate2968. The remaining fork decoder currently re-encodes304
bytes merely to compare canonical reserved fields. Factor the existing full Plan
validator from encoding, share it between writer and decoder, and directly check
the exact fixed/reserved input ranges after parsing. One shared parser serves
both old request-with-scratch and the new scratch-free decode used by the router.
Keep the old request API and its regenerate/compare behavior, publication encoding
and all wire/error ordering. Only the router stops allocating the second304-byte
scratch slice. Check every single-byte mutation against exact prior decoder and
encoder sources from immutable Git, plus valid varied source/descriptor/history
plans and existing consuming schedules. This is current protocol implementation,
not a new wire variant, weakened validation or removal of safety checks. Keep
both old reference inputs host-only and dispose them after qualification.

The direct fork decoder experiment passes50 tests including155648 byte mutations
and54 valid plans against the previous codec, but increases the same-root code
from18176 to18368 and the largest fixed reservation from536 to968. Reject it:
restore the original codec/router sources exactly and remove the new codec API,
reference crates and experiment-only test. Retain compact attempt/input hashes
and results; no per-run source tree. Do not trade a removed scratch slice for
larger stack/code or retain an unneeded second decoder. No change is adopted.

Native integration review finds another exact contract distinction: successful
0x23005 cancellation returns0 to the supervisor and sets parent return to-11.
Old resolve_refusal accepts the parent-side observation, and must not receive a
raw supervisor result relabelled-11. Keep that API for its existing component
callers. Add an explicit native-result method accepting only callback Ok(0),
sharing the existing gated reconciliation implementation and returning the raw
callback result unchanged. Errors, positive/unknown or callback unwind stay closed.
Add a native scalar cancel_freeze method using the same reviewed syscall bridge
with rdi=owned source and rsi=observed token, other operands zero; no pointer is
passed or authority supplied by labels. A concrete measurement root must compose
this method with the gate, accounting for its cost. Test wrong phase/sequence/no
callback, actual0 success, original copy errno retention, raw-11 denial, other
errors/unknown and unwind. No repeated thaw, child rollback, resource reclamation,
parent-return observation or native acceptance is inferred from supervisor0.

The native refusal guard has a strict compiling semantic control: replace only
its expected supervisor0 with parent-11, rebuild the actual dependent gate/stream/
transport/router crates and fail the exact new raw-result test. A compile error,
missing test or timeout cannot satisfy that oracle. Existing six semantic controls
and two borrow denials remain. The total now is seven semantic controls.
