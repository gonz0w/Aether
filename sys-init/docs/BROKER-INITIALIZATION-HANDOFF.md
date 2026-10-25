# Bounded FILE broker initialization — BG-073

Current disposition, 2026-10-22: the additive constructor is implemented and
consumed locally in the consolidated repository. See the [current API](../../userland/docs/proposals/FS-BROKER-INIT.md).
The request below records its measured motivation and obligations. Construction
host/component checks pass; selected code16544/16384 blocks native admission.
Full composition/peak-stack/native acceptance remains open under BG-070/073.

2026-10-22. Local unsent request to the Aether-userland FILE broker owner.
No sibling repository was modified and no message was sent. Sys-init owns its
entry/mapped placement, full composition and whole resource-fit qualification.
Aether's new ABI30 mapping input is received; this is a separate constructor seam.

The existing sealed file-view18/serialized-copy17 ProcessFiles has private nested
ledger/source fields and only a by-value connect(channel,epoch) constructor.
Our gate now initializes its own fields directly, avoiding its extra2944-byte
stack temporary. However, constructing the actual ProcessFiles still generates
multiple intermediate aggregate copies under the pinned Rust1.98.0 x86_64 target.
Caller-owned destination storage alone does not remove those temporaries.

| Actual native subset experiment | Code bytes | Constructor finding |
| --- | ---: | --- |
| Direct constructor, size-s/fat LTO | 17016 |6536-byte fixed reservation before pushes/callees |
| Direct constructor, size-z/fat LTO | 16016 |6504-byte fixed reservation before pushes/callees |
| Direct constructor, opt3/fat LTO | 32008 |Smaller local reservation; code exceeds16384 |
| Noinline constructor, size-z/fat LTO | 16272 |5328-byte callee reservation plus2208-byte caller reservation |
| Isolated opt3/static-library constructor + size-z subset | 19072 |280-byte constructor reservation plus pushes/callees; code exceeds16384 |

The stack allowance remains4096 (4088 below entry); code remains16384. Experiments
retain actual native RPC, gated capture, copy/local inheritance, exact-ready,
parent-delivery, connect, settlement and disconnect paths, not boot/activation/
complete dispatch/shutdown. Callback observations are function parameters with
no caller. They are never executed and are not native acceptance candidates.
These numbers reject these arrangements, not a theorem that every full build
must have identical size. No larger quota, stack pivot, private-layout cast,
zero-as-valid-ProcessFiles, ignored undefined symbol or successful stub is chosen.
The final isolated variant links normally with a real fail-stop panic handler;
earlier missing raw dependency/panic-symbol links remain failed attempts.

Requested narrow additive candidate: safe initialization of the existing broker
directly in a caller-owned aligned MaybeUninit<ProcessFiles<Channel>> slot, including
its nested description/client state. Preserve the old by-value API and old sealed
bytes. Do not add another ledger, allocator, service or public protocol. Sys-init
will supply unique mapped storage and compose its own gate fields only after a
valid broker exists. A possible shape is connect_in_place(slot,channel,epoch) ->
Result<&mut Self,ConnectFailure>; spelling and exact error ownership are for the
producer contract, not an accepted API here.

Required contract/evidence: valid Self reference only after every field is valid;
zero bytes alone never count as initialized Rust state; no duplicate live owner;
one AF07 greeting/readiness consumer; original epoch/channel ownership preserved;
actual once-only raw close/cleanup results on failure, no replay or unwinding
assumption; partial initialization cannot leak a usable reference or unknown
obligation. Any supplied variant must explain success/failure/drop lifetime and
preserve direct versus source-side admission/authority boundaries.

Measure concrete Framed<Endpoints<Native>> construction and called routines with
the pinned x86_64 toolchain, selected size build and existing one-page stack.
Host tests must cover valid/malformed/lost greeting, failure after partial nested
initialization, epoch rejection, no second greeting, no double close and unchanged
failed output. Supply separately sealed source/tool/command/artifact identities;
old API regressions and strict checks remain required. No native guest is requested
by this handoff. Sys-init then consumes/reviews/tests and proves complete fit,
remaining transaction/transport/settlement/readiness/shutdown and fresh native cases.

[Decision0206](decisions/0206-abi30-owner-placement.md) and
[retained measurements](evidence/abi30-owner-placement-2026-10-22/README.md).
