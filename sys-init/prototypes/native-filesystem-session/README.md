# ABI29 dispatcher startup and child/wait core

Decision0224 selects the private `fs_home_owner` composition with matching
home/in-place/FILE-write dependencies. Gate and Runtime consume both AF09 grants
in final storage through `connect_home_in_place`; old constructors remain scoped
to older profiles. The router returns a complete owned FILE event even after
admission/delivery failure. Runtime retains its exact native index/identity/context
generation and Exchange before fail-stop; `last_file()` is a read-only outcome,
not authority, crash durability or permission to replay. `source_cleanup()`
projects the current sole-source raw closes separately from the original receipt
and FILE cleanup; it implies no native settlement. See
[the owning record](../../docs/decisions/0224-home-owner-fit.md) for current fit,
checks, review and continuation. Run from the system root:
`PYTHONOPTIMIZE=1 python3 -B sys-init/scripts/check-home-owner.py`.
This runs host/no_std checks and concrete complete offline owner measurement;
no guest or engine/home/C-provider activation is selected.

Current decision0211: same prior roots shrink to18176; expanded concrete native
cancellation plus routing/construction/copy/publication/settlement roots18384
still exceed16384. Target gate2240+workspace4096 uses6336/8192.50 consumer tests,
36 producer tests/15 controls, seven semantic omissions and two borrow denials pass.
The native cancellation API preserves supervisor0 separately from parent-11 and
copy errno. [Review](../../docs/decisions/0211-owner-structural-fit.md) and
[results](../../../docs/evidence/owner-structural-fit-2026-10-22/README.md) supersede
older dated measurements below. No complete owner/VM/Zsh/ISO acceptance.

## Current mapped-owner checks

From the system repository root:

```sh
python3 -B userland/experiments/filesystem-service/check-process-descriptors.py --in-place
python3 -B sys-init/scripts/check-broker-init.py --libraries PRINTED_OWNED_OUTPUT --compact-compare --unified-route
```

The optional compact comparison consumes one unchanged pinned musl1.2.6 leaf from
the existing SDK; see [decision0208](../../docs/decisions/0208-owner-compare-fit.md).
Without this flag the compiler-builtins selection remains. The separate
`--unified-route` measurement replaces independent FILE/capture wrappers with the
actual mixed-channel router and retains construction/copy/publication/settlement
roots.48 component tests, six compiling publication/routing omissions, two borrow
denials and selected C ordering/boundary controls qualify host/link behavior only.
Exit2 explicitly reports code-fit failure after passing host checks; composed
compact roots18768 exceed16384. No complete runnable owner, peak
stack, VM or ISO acceptance. [Publication contract](FORK.md) and root STATE govern
the remaining integration; older handoff paragraphs below are dated context.

[Decision0194](../../docs/decisions/0194-abi29-dispatch-core.md) consumes corrected
userland v2 and prepares the transport-independent part of the next dispatcher.
This is host-tested policy, not a linked native init/shell dispatcher. It is not
wired into any accepted owner/default and no guest runs here.

startup.rs validates canonical admission bookkeeping for shell1/children2–4 and
returns exactly32 AEFSH001 bytes before the client's FD-table/binding exchange.
It requires real boot parent7 for shell generations1–3, the actual shell PID for
copied children, epoch1–15 and seven-domain PID/memory labels. Invalid/spare/engine/
owner roles, malformed generations/handles and forged fields produce no frame.
Its caller must own the real kernel-admitted instance and authenticated live
channel; a canonical number is not a grant or evidence that admission occurred.

children.rs preserves the existing three-child ledger: native-observed admission,
terminal, one reserved wait reply, confirmed transport delivery, holder disposal
and native reclaim remain separate. Short/unknown reply delivery cannot free the
record; generations cannot reset or skip, stale observations cannot settle a new
instance and a syntactically valid PID alone cannot create membership. Only the
PID encoding changes from6 to7 domains; Default delegates to the same empty
constructor. The original ABI24 dispatcher and all AF06/AF07 owners stay fixed.

[Evidence](../../docs/evidence/abi29-dispatch-core-2026-10-21/README.md) records
six host Rust tests, three compiling guard omissions and actual Rust-produced
frames accepted by the exact sealed v2 C decoder:138 identities and1803 malformed/
forged-observation rejections, with unchanged failed decoder outputs. Strict C17/
UBSan, Rust1.98.0/2024/default Clippy/format and x86-64 no_std object generation
pass. Object generation does not prove native stack/loader/transport enforcement.

## Reproduce the Rust checks

With the compiler/tool identity in the retained preparation and a fresh private
output directory:

```
rustc --edition=2024 --test -Dwarnings prototypes/native-filesystem-session/lib.rs -o out/my-abi29-core/tests
out/my-abi29-core/tests
rustc --edition=2024 --crate-type=lib --target=x86_64-unknown-none -Dwarnings -C opt-level=s -C panic=abort --emit=obj prototypes/native-filesystem-session/lib.rs -o out/my-abi29-core/core.o
```

The evidence retains exact format/Clippy and interoperability commands, the pinned
consumer header, producer/consumer test sources and serialized frames. On macOS,
set the compiler-adjacent DYLD_LIBRARY_PATH for Rust tools only as in the AF07
guide; do not pass it to LLVM/C compilation. No setup/download or sibling code
execution is needed for the Rust checks.

## Remaining integration gate (local handoff, unsent)

The verified linked parent/helper v2 inputs have outer seal
`e559c2ef5a0675c6c243aa3cc517bf5c34fd78ae5ef90a8ca3f3e99b04999081`
and standalone bundle seal
`70f87686d4d7ef7f23f6f53fd6ca1632e524eeefd75345321e0806c4cbe43942`.
All580/574 members match; old/new bundle changes are exactly README and identity
header, with572 unchanged. Corrected startup removes the former parent7 blocker.
Linked images and producer initial73/24 backing-page results are inputs, not
native shell, complete dispatcher or peak stack/heap acceptance.

Userland still owes the matched AF07 FD/path/immutable executable translation:
exact private directory/FD/binding/read/exec messages, generation/rights/lookup
and partial/error/unknown semantics, authorized immutable image admission, bounds
and failed-exec parent/descriptor preservation. The existing private RAM directory/
scratch/exec selectors cannot stand in for that contract. Pkg-mgr owns persistent
package bytes/records; Aether owns native loader and authority mechanisms.

Sys-init still owes full startup/FD-table/binding/ready/copy/exec/wait/endpoint
transport integration with these corrected cores, plus AF07 readiness/shutdown
composition and code/stack/heap fit. Aether must then execute the exact assembled
owner/client with positive/denial/partial/unknown/cleanup and fresh-readback
witnesses. Do not wire guessed filesystem references into the old1246-line
six-domain dispatcher or widen lifetimes, slots, channels or memory. No generic
service machinery, interim RAM-only shell ISO or shared SDK/release promotion.

The next [AF07 transport endpoint slice](AF07-TRANSPORT.md) now consumes the
separately sealed read-only client and prepares actual native channel methods,
with host Client/Framed tests and object/disassembly evidence. This narrows the
old transport dependency, but does not deliver shared FD/path/immutable exec or
wire the full dispatcher. Existing lib.rs/core and accepted owners stay fixed.

## Proposed descriptor startup

[The AEFDB001 producer](STARTUP.md), decision0200, now matches userland's new
single-consumer startup proposal. Pure checked304-byte encoding and host exact
C-consumer interoperability are prepared; the old identity/core and accepted
owners stay fixed. Selected shell/native startup/child copy/exec/fit remain open.

## Serialized fork admission

[Gate and selected frames](FORK.md), decision0202, consume the separate serialized
file inheritance API and proposed fork client. Host ownership/frame compatibility
is prepared. Decision0203 consumes file-view18 and enforces authoritative complete
FILE presence/cloexec comparison at copy admission (BG-071 resolved locally). Actual
stream/source/history capture and full transaction/readiness/shutdown/fit remain
BG-069/070 work; native shell witnesses separately need a corrected real-TLS ELF.
Older APIs/accepted owners/default and released pins stay fixed.

Decision0204 now requires the full Plan and an explicit stream implementation.
The [owned stream component](FORK.md) compares actual pipe holders/history and
console/source records before copy and activates staged holders on exact child
context-ready before parent success. Fifteen host tests/four compiling controls
pass; corrected TLS85 also passes our fresh actual Aether parser host tests.
Remaining work is full native owner/transport/settlement/fit and target witnesses,
not missing stream metadata or missing TLS input. No old owner or release pin changes.

Decision0205 adds [gated transport capture](FORK.md) before wire sequence decoding;
partial input/unwind cannot enable copy.20 host tests/four compiling omissions and
native libraries pass. Full owner composition now needs [bounded writable placement](../../docs/OWNER-PLACEMENT-HANDOFF.md)
(BG-072): actual gate2968+RPC workspace4096 exceeds the current one-page writable
owner stack. FILE/stream/TLS inputs remain resolved; no limit/pin change is made.


Decision0206 consumes the new AENFS004/ownerABI30 placement contract and verifies
all producer sources; the old missing memory-contract input is resolved. Entry,
MaybeUninit-backed single-owner partition and fieldwise gate initializer pass
four host tests/four omission controls and20 existing regressions. Complete native
construction now encounters [BG-073](../../docs/BROKER-INITIALIZATION-HANDOFF.md):
existing opaque ProcessFiles.connect exceeds the stack under selected size builds;
measured opt3/isolated alternatives exceed code. Need a bounded in-place producer
constructor, then full local owner/fit/native witnesses. See [API/evidence](FORK.md).

## Mapped broker initialization

Current integration: [decision0212](../../docs/decisions/0212-complete-native-owner.md)
supersedes code-quota optimization for the new owner. Add `--compact-compare
--unified-route --compose-owner` to the checker below to link the concrete ABI30
entry/control/owner and measure actual resident state and conservative stack.
This selection disables target jump tables for inspectable direct-edge analysis;
old selections stay unchanged. Exit2 with `blocked-owner-stack` is a real missing
fit gate after passing host tests, not native admission. Immutable exec and initial
readiness remain incomplete; no new code budget is chosen from this partial image.
The checked-disconnect callback verifies engine terminal and same-endpoint EOF/
EPIPE before closing channels and reclaiming. No new VM/runtime profile is admitted.

The opt-in `fs_in_place` owner composes userland's safe in-place constructor in
its final private FILE field, then moves streams and publishes initialized state.
[Decision0207](../../docs/decisions/0207-in-place-file-broker.md) records cleanup,
measurements and limits. From the system root run the exact two-command sequence
in [FS-BROKER-INIT](../../../userland/docs/proposals/FS-BROKER-INIT.md); the second
command takes the first check's printed owned library directory. At decision0207 it reported
versioned JSON and code-fit exit2 for constructor-only roots16544/16384. Tests and
no_std builds do not imply complete fit or native admission. Keep current limits.
