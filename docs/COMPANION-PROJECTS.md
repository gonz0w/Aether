# Companion projects and integration boundaries

Since 2026-10-22 these implementations live in this checkout: `../userland/`,
`../sys-init/` and `../pkg-mgr/`. The ownership contracts below still define runtime
responsibility; old repository handoffs describe historical checkpoints, not
permission barriers for current implementation. Aether-standards remains separate.
Use [REPOSITORY](REPOSITORY.md) and root STATE for current integration work.

## BG-072 producer handoff: bounded ABI30 owner data — 2026-10-22

Sys-init0205's capture/placement158-member packet and21 closures/674 members
verify. Aether supplies the separate [AENFS004/ABI30 contract](native-fs-owner-data-v1.json),
SHA25613e4f5bc308a5fc24cdfb9a510cdc968da9ba66feaeb526cb23bc6db081d6d01,
and actual opt-in mapping/startup code. Owner6 receives8192 private zeroed RW/NX
bytes at0x900000, drawn from its existing128-page backing partition; entry binds
rdi30/r10base/r11size. Old ABI28/29, code/stack/backing/channel/worker/time limits
and allocator denial remain unchanged. No syscall or writable image statics.

Host mapping/zeroing/permission/binding controls and older-profile denials pass;
Debug/ReleaseSafe kernels build and exact AF07/TLS structural geometry is admitted.
[Evidence](evidence/fs-owner-data-2026-10-22.json) is build/host scope, not native
hardware enforcement or whole owner fit. All owned outputs are removed. The old
2072-byte activation owner is only a structural size placeholder, not a dispatcher.

Sys-init can now implement the matching ABI30 entry capture, one exclusive checked
initialization/placement boundary and complete transaction/settlement/readiness/
shutdown. Its gate2968+workspace4096 leave1128 of8192 bytes, not complete peak fit;
reuse transient buffers and measure remaining state/code/call frames. Aether then
qualifies matching native permission/zeroing/isolation/continued-parent/failure/
cleanup/readback under fresh scoped disposition. The existing runner intentionally
does not select ABI30 yet. No sibling edit/message or independent acceptance.

## TLS and authoritative stream consuming handoff — 2026-10-22

The corrected userland TLS85 shell is accepted by Aether's unchanged ELF/layout/
backing parsers. Sys-init0204's sealed FILE/stream gate, actual SESSION pipe cores
and child-ready holder activation pass fresh consuming host tests and generic
native-library builds. [Results](evidence/fs-af07-stream-tls-intake-2026-10-22.json)
verify213 packet members,23 deliveries/840 members, old linked580 and native876.
Fifteen component tests, four compiling semantic controls, two borrow denials and
two actual geometry tests pass. Geometry uses the old activation owner only as a
size placeholder; it is not a matched shell dispatcher or complete resource fit.

Sys-init's live0205 capture work is in progress and excluded from this sealed0204
qualification. Complete actual copy/refusal/unknown/startup/ready/parent transport,
terminal/endpoint/holder settlement, application readiness/shutdown and whole
executable/resource placement remain its deliverables. The selected owner has
one4KiB stack and no dynamic allocation grant: its4KiB RPC workspace needs an
explicit safe placement, not a code-tail/peer-memory or quota workaround. Aether
will review the matched composition and any concrete placement request under
current limits before another native campaign. No sibling changes/messages,
native execution, pin/limit change, independent sign-off or R1/ISO acceptance.

## Stage/gate consuming handoff: correct TLS image and native composition — 2026-10-22

New userland [fork stage](../userland/docs/proposals/FS-FORK-STAGE.md)
now includes actual __aether_fork_stage/one-shot child construction and a fully
linked experimental shell (stage81/seal7923584cb093e2c459ae45468ca1021dd92054e771d2de569ebcee15b3c143fe).
Sys-init [0202](../sys-init/docs/decisions/0202-serialized-fork-gate.md) selects
Aether ordering, frame69, retained source labels and stricter no-child refusal
semantics, and supplies a local serialized gate. Userland [file-view18](../userland/docs/proposals/FS-FILE-VIEW.md)
(sealbce3ead4e8a1583ef88e85eb494bb9f1d0d71167205e80b85c7e49cd121043a2)
now supplies BG-071's pure authoritative FILE presence/cloexec masks. These
components exist; do not keep requesting their generic implementation.

[Aether consuming intake](evidence/fs-af07-fork-stage-gate-intake-2026-10-22.json)
verifies full136-member sys-init packet,20/656 existing source closures and new
81/18, unchanged old linked580 and native876. Fresh new-library31 process tests
and six actual sys-init gate tests pass, with three compiling semantic denials.
Host storage/copy/stream doubles only; no actual holder/native copy/TLS or full
owner acceptance. Frame5847/stage1008 producer claims stay attributed, not rerun.

Concrete new compatibility blocker: exact stage ELF279256 bytes/hash
bbad8594bfeab70135a9b153dec88030278dfcfd423c2646103889ba00e21413
is rejected by Aether's actual ELF parser: **PT_TLS is absent**. Old v2 has a
4-byte session_tls/PT_TLS; the new link omits old runtime's live TLS definition.
The [failed admission](evidence/fs-af07-fork-stage-loader-failed-2026-10-22.json)
is retained, with19 prior passing commands. Separate actual-loader/composition
triage denies new stage and accepts an old-image control from the same geometry
writer. Geometry's small activation owner is explicitly a size placeholder;
no complete matched-owner image or whole fit is claimed. Nominal page counts
cannot override rejection. No patched ELF/fake TLS header or weakened loader.

Userland next: separately sealed actual-TLS relink compatible with the native
loader, preserving old artifacts/pins and pinned child auxv/TLS/__post_Fork order.
Include actual native-parser consumption before handing off the replacement;
link success and generic ELF checks did not catch this contract mismatch. Do not
link old full runtime with duplicate libc/greeting exports just to acquire its TLS.

Sys-init next: BG-071 consumes available file_view_v1 under begin/capture, derives
both complete masks from tagged FILE entries and compares exact authoritative
values before native copy. Bits mean remote FILE selectors3..15, not logical
indices; low bits/hole flags/omissions/extras all reject. Also compare actual stream
holdings/rights/generations/history. Sole gate must enforce all these restrictions,
including bypass callers; no destructive exec/flag probe or second mirror ledger.
Then compose actual native copy/reservation/refusal/thaw/unknown handling, fresh
startup/context-ready/parent disposition and real terminal/endpoint/holder cleanup,
readiness/shutdown. A positive native copy cannot produce a known negative parent
reply in the selected stage; retain obligations/fail-stop on post-copy uncertainty.

All old kernel/user/scripts runtime inputs and current resource/time limits stay
fixed. Both owned roots removed; all processes complete, no archive/SDK/source-tree
copy, binary bundle, sibling edit/message, guest or broad suite. After corrected
ELF plus complete owner and measured code/stack/heap/backing/channel fit, Aether
qualifies exact native commands/errors/continued-parent/wait/cleanup/readback.
Immutable exec/public dup2/writable-path-package/Zsh/TTY/persistent ISO and
independent owner/reader acceptance remain open. Handoff is local/unsent; STATE
owns authoritative progress.

## Previous intake: linked v1 must correct boot parent — 2026-10-21

Sys-init [decision0193](../sys-init/docs/decisions/0193-af07-native-consumption.md)
independently accepts Aether’s exact eight-guest AF07 activation/readback/failure
handoff; its complete33-member sealed consumer review matches receipt a63ba3ef…
and locally replays all eight selected oracles. No new guest or raw-media replay.
The old missing consumer-review gate is closed in this bounded scope.

Userland now supplies fully linked parent/helper ABI29 artifacts, not only objects:
`../Aether-userland/build/session-deliveries/filesystem-abi29-linked-2026-10-21-v1`,
outer seal66d8ec0f8353563a270d2f7ae2fbb9e288be2287ff08ff566e16dc4a3491a468,
nested bundle6265a3eb21f110f4888572987f4bc4420c9b2f6c932810567ecc369512a47c3b.
Complete580/574-member closures verify. Parent ELF b65cb3c896ce54689346fa2361a87ac4cce4889391e3078e56b78b0a13a93e50
fits73/128 pages; helper5727299d1a937c6fea20a781a076b54506bd2bbd49a3cd0a58faf82572ddb4d2
fits24/128 under actual kernel host parser/layout/backing. No peak stack/heap,
native startup or persistent FD/path/exec/Zsh claim follows from static fit.

Blocking compatibility: boot owner6 generation0 is PID7, not14. The exact linked
client decoder rejects genuine native-shaped PPID7 for all three shell generations.
Its old14/21/28 allowlist cannot be satisfied by relabeling: supplied14/observed7
also rejects, correctly. Kernel branch/source regression confirms owner7, shell9/
parent7 and copied child10/parent9. This does not add a native PID measurement.
[Local intake/results](evidence/fs-af07-linked-client-intake-2026-10-21.json) and
[sys-init correction handoff](../sys-init/docs/research/ABI29-BOOT-PARENT.md)
identify the exact mismatch; earlier object arithmetic review was not startup
acceptance and did not establish owner generation.

Userland: provide a separate corrected linked startup/client delivery preserving
native observation equality and child-parent validation; do not patch the old seal.
Sys-init: use that matched input for shell1/children2–4 startup/descriptor/copy/exec/
wait dispatch. Userland retains AF07 FD/path/immutable-executable and Zsh/TTY work;
Aether supplies native admission/qualification once matched inputs exist. No kernel
PID/generation workaround, lifetime reset, ambient grant or interim shell image.
All current limits, native engine/owner bytes, old pins and876 native inputs stay
fixed. No sibling edits/messages, new VM or full-suite repetition.

## Matched AF07 sys-init native handoff — 2026-10-21

Aether’s approved eight-guest qualification now passes with sys-init decision0192’s
exact2072-byte AF07/ABI29 owner,16KiB ceiling/1096-byte scoped stack, and separately
sealed v5 engine (guest ELF equals selected v3). Native readiness/dependent launch,
clean disconnect/export/ordered reclaim/halt and fresh original-file readback pass.
Five fixed failed peers hit exact semantic rejection with unchanged pristine media,
no unsafe engine reclaim or successful halt. Host confirms all eight VM stops.

Consume [native receipt](evidence/fs-af07-init-native-2026-10-21.json), SHA256
 a63ba3ef2f25789e8ae887b59d22c31fb91a8c9a8a34cc1cf64672f21c48b7d2,
with the existing [preparation/review](evidence/fs-af07-init-review-2026-10-21.json).
Eight retained oracles replay; eight actual-record corruptions reject. Owner/engine
and all non-ISO payloads equal prepared bytes; individual ISO hashes are retained.
876 frozen inputs/actual eight QEMU commands;292.974223s within900, writer1820ticks
and every existing native limit fixed. Full host checkpoint now passes910 Python tests plus Zig/pin/workflow checks;
all876 native inputs and exact owner/engine intake still match.
[Verification/handoff](evidence/fs-af07-init-native-review-2026-10-21.json). No additional guest under the consumed approval, no old-timeout fix,
independent sys-init sign-off or shell acceptance. All generated outputs removed;
current dependency/notices remain. No sibling file/message or released-pin change.

Sys-init’s next step is its own exact consumer review, then matching ABI29 shell/
process/descriptor dispatch work. Userland still supplies full client CRT/libc/
component/ELF/stack fit, AF07-backed FD/path/exec and Zsh/TTY. Its29-member identity
object candidate is verified but is not a promoted SDK or native shell. Actual
persistent runner/packages, modes/promotion and assembled boot-to-Zsh remain open.


## AF07 operational Rust owner delivered; consuming integration active — 2026-10-21

Consuming checkpoint: the separately approved corrected-capture sequence now
passes all three guests at796/806. The exact AF07 operational Rust owner/service
runs behind the C engine in AENFS002/owner28/engine26, with96 requests/nine mutations,
process exec/wait, full fresh-recovery namespace/data/metadata/media checks and
2-role ordered cleanup. All retained oracles replay; the904-test host checkpoint
and Zig/pin/workflow checks pass. [Native receipt](evidence/fs-af07-operational-native-2026-10-21.json),
[review and compatibility check](evidence/fs-af07-operational-native-review-2026-10-21.json).
The previous incomplete capture remains failed; no old-timeout fix or independent
consumer approval is claimed. No additional guest under the consumed approval.

Read-only inspection now finds userland's separate18-member
filesystem-af07-owner-2026-10-21-v1, manifest
`a5113edeb55d6ae38905bca047cbf6c290dc0ff25ab958556840194586a5b052`;
shipped Rust object
`10e401f8f5aaf7c33ce70081abb5cec2a310598ec17811325728c4c0c2604b7b`.
Its exact dependency is the existing77-member AF07 service, seal98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8.
The missing-owner prerequisite below is historical. Current Aether results and
exact executable/proposed guest identity are recorded in [STATE](../.planning/STATE.md).
The sealed owner selects metadata/root31 and preserves launch state136/result72,
readiness/SPA/endpoint/drain/export; eight host cases and the exact shipped object
are independently checked here. No producer packet commands/checkers are executed.

Aether composes a separate operational AF07 executable from that exact owner,
service and original C engine/provider/import/runtime. Structural link/intake is
separate from operational native acceptance and sys-init adoption. Existing AF06
seals/defaults remain fixed; no reinterpretation of old rights15 or wire handles.
The explicit new AENFS002 eight-KiB SESSION witness reuses current limits and
independent recovery checks; it is not an actual sys-init shell or ISO.

Matched consuming input now available: `.deps/fs-launch-af07-2026-10-21-v3`,
manifest e28d249b97d2e0a94c376190ec3f3839d50b6c1426cf788bab8f303fdb4084ac,
ELF9039e7b1d9a488076e3f8329b3666f39d85385f294d89954dd03df7c2df1753a,
5196832 bytes/1329 loader pages/four load segments. Same engineABI26, inherited
auxv0xa004 request-reader/0xa005 reply-writer, scoped block0xf101 and existing
region grant; original launch-state136/result72/all8191 cleanup obligations.
AFSRPC07 explicitly selects METADATA16/root rights31; handle IDs, metadata,
paths and digests remain data, never native authority. Preserve live readiness,
full greeting/framing checks, one clean disconnect and confirmed engine/native
settlement before reclaim; no replay or inferred cleanup after unknown outcomes.

Read-only inspection now finds sys-init decision0192’s separate AF07/ABI29
owner in `../sys-init/docs/evidence/filesystem-af07-owner-2026-10-21`. Its complete
seal is8f99308958df2552b527bc6abf07a78ea6b8a8bb670fd706139d1cab5c5ddd96;
raw620939e5218df104586ff38ce843776696c70814efdd2180c0244e7defae08a7,
ELF87598149c7a33307fffd3dc393f4cb87a04f635b40276f079943f93a904ebc03.
The2072-byte owner/scoped1096-byte stack and all120 admitted packet/source/tool/
engine identities pass Aether’s separate intake checks. Four actual host policy
tests pass here. Its selected v3 engine remains unchanged. A current harness build
must additionally pass full intake and equal that exact guest ELF; record both
manifests rather than edit the sibling pin. Aether now prepares a separate
`--metadata-sys-init-checks` selection using the existing AENFS003/ABI29 limits.
Actual matched native activation/readback/five-peer acceptance and sys-init’s own
consumer review remain open. The old AF06/default selectors remain unchanged.

Userland also delivers the29-member source/object ABI29 client candidate in
`../Aether-userland/build/session-deliveries/filesystem-abi29-client-candidate-2026-10-21-v1`,
seal4bd1290f28fb38b14554003b804d6dc5992606cef5c64785fdcfeab961c8c3ce.
All members, four x86-64 relocatable objects, three tools and its SDK header
manifest match read-only inspection. It proposes AEFSH001 startup, shell1/children
2–4 and actual seven-domain PID/PPID/memory checks. This is not a linked SDK,
matched dispatcher, persistent descriptor/exec adapter or Zsh delivery. Userland
still owns full CRT/libc/component/ELF/stack fit, AF07 FD/path/exec and Zsh/TTY;
sys-init separately owns the matching process/startup/descriptor dispatcher and
activation policy. Do not turn source/object success into native shell acceptance.
Persistent loader/runner/packages, modes/promotion and independent reviews remain
open. No sibling edits/messages or released-pin changes.



## AF07 consuming prerequisites pass; matching operational owner required — 2026-10-21

Aether's selected positive, transport/context, metadata reply-loss and original
four-provider gates now pass. The latest approved provider matrix passes12 fresh
guests at 796/806 with complete bounded oracle replay, full file/metadata/media/export/
reclaim checks and unchanged limits. [Receipt](evidence/fs-af07-metadata-providers-native-2026-10-21.json),
[current state](../.planning/STATE.md). The major host checkpoint passes 889 Python
tests plus Zig/pin/inventory checks.
[Review](evidence/fs-af07-metadata-providers-review-2026-10-21.json) records exact
approval, all 12 oracle replays and unchanged read-only companion input hashes.
Prior timeout receipts remain preserved and root cause unknown; the passing batch
is bounded producer evidence, not independent acceptance or operational adoption.

Read-only reinspection finds the same object candidate and an AF06 operational
owner calling aether_fs_directories_run with rights15. Aether-userland can now
supply its separately sealed AF07 operational Rust owner/executable, with:

- Exact 77-member filesystem-service-metadata-2026-10-21-v1 dependency, manifest
  98a9fd12db4ecd1c736fe3ce332c9b69c631e043d4d87313827145675ba230a8,
  object b5729862346409392064045af6f953484d3d6fbf9cad2b279840907003222f7b.
- Actual aether_fs_metadata_run/AFSRPC07 selection, METADATA16 attenuation and
  root rights31; no silent reinterpretation of AF06 handles/wire or backend IDs
  published as authority. Same nine trusted arguments/72-byte service result,
  existing 136-byte launch state and authenticated inherited endpoints.
- Existing sole live SPA/dataset/UTC borrow, context/endpoint consumption,
  readiness and ordered drain/export/block quiescence/runtime/reclaim handoff.
  Preserve explicit unknown-outcome failure and no automatic restart/write replay.
- Actual owner tests, native object/import/size/stack/link origins and reproducible
  input closure. Aether must separately link/intake/qualify the new operational
  owner; sys-init consumes its matching provisioning/readiness/shutdown input.

The AF07 object delivery itself is already present. Do not duplicate userland's
owner in Aether or treat finite conformance as a launchable service. Keep current
AF06 executable/seals selected until matching replacement qualifies. No sibling
edit/message or released-pin change. Modes/promotion, persistent runner/packages,
ABI29 shell/PID/FD and real Zsh/TTY ISO remain open, with snapshot/rollback post-R1.


## AF07 retirement diagnostic passes; provider acceptance still pending — 2026-10-21

The approved single diagnostic sequence passes writer796/fresh recovery806 with
full file/metadata/media/export/reclaim and complete bounded oracle evidence.
Relocated D/J distinguish eviction wait from export, and both complete. The old
unrelocated provider timeout remains unexplained; diagnostic success cannot
qualify that original profile. [Current state](../.planning/STATE.md),
[receipt](evidence/fs-af07-retirement-native-2026-10-21.json).

All generated media/images were removed. Existing limits, operational AF06 seals
and released pins remain unchanged. No sibling edit/message. Aether's next step
is renewed disposition for the unchanged four-provider matrix; matching AF07 Rust
operational owner/sys-init adoption and persistent runner/packages/Zsh ISO remain
later requirements. The metadata object itself is already delivered.


## AF07 failure qualification: Aether retirement blocker — 2026-10-21

Transport/context and metadata header/body loss pass18 guests with clean export,
full fresh recovery and complete bounded oracle replay. The malformed-nanoseconds
provider writer then times out after target796/S; all further persistence guests
are paused for renewed human disposition. No recovery/remaining provider ran;
VM stop confirmed and generated outputs disposed. See [current state](../.planning/STATE.md)
and [immutable attempt](evidence/fs-af07-metadata-providers-attempt1-2026-10-21.json).
Exact stall/root cause and writer cleanup/durability are unknown. A bounded
retirement-stage diagnostic is host/build-only prepared without changing any limits.

The AF07 object candidate is delivered; this is Aether qualification work. A
matching operational Rust AF07 owner/executable and sys-init adoption remain later
handoff requirements. Keep AF06 operational selections/seals. Persistent runner/
packages, shell/PID/FD and Zsh/TTY ISO are not yet qualified. No sibling source
modification or messaging is needed for this triage.


## AF07 positive disk and capture gate passes — 2026-10-21

The approved corrected-capture sequence passes native pristine/writer/recovery
at796/806 with unchanged guest payloads and bounds. Complete compact oracle rows
now independently reproduce the live terminal, cleanup and persistence checks;
the previous writer capture gap is closed for this new run only. All VMs stopped
and generated outputs were disposed. [Current state](../.planning/STATE.md),
[receipt](evidence/fs-af07-capture-native-2026-10-21.json).

Remaining Aether qualification is the AF07 partial/lost-reply/failed-close/
malformed-provider matrix. Full native qualification and independent intake still
precede a matching Rust operational AF07 owner/executable and sys-init selection.
Current AF06 seals remain selected. Do not call the positive candidate a missing
metadata delivery, an accepted operational replacement or R1 ISO. Modes/promotion,
filesystem-backed runner/packages, ABI29 shell/PID/FD and real Zsh/TTY remain open.
No sibling sources or messages were changed/sent.

## AF07 diagnostic live pass; operational handoff still pending — 2026-10-21

The approved fresh metadata-service diagnostic passes pristine/writer/recovery
with the actual AF07 object and original provider, complete file/namespace/media
checks, clean writer export and all domain reclaims. [Current results and trace
limitation](../.planning/STATE.md), [unchanged receipt](evidence/fs-af07-diagnostic-2026-10-21.json).
The writer's bounded retained selection overflows; its prefix plus tail replays
the acceptance oracles but does not preserve complete timer/wait history. A scoped
capture correction passes host checks only. Full AF07 failure-path qualification
and independent intake remain before operational adoption; the current blocker
is not missing metadata source delivery or an observed engine/runtime failure.

Read-only reinspection finds the same object-only AF07 candidate, with no matching
Rust launch owner/executable. After qualification, userland must supply that exact
entry/magic/METADATA-rights owner; sys-init consumes its provisioning/readiness/
drain/export handoff separately. Existing AF06 executable/seals remain selected.
Modes/promotion, ABI29 shell/PID/FD, filesystem-backed runner/packages and Zsh/TTY/
ISO remain open. No sibling modifications or messages.

## AF07 delivered; native consuming failure under triage — 2026-10-21

Userland's77-member AF07 candidate is received and exact intake passes. It supplies
the previously missing authenticated metadata policy/backend/reply boundary.
The private integration builds the actual new object/provider within current
bounds. First pristine reader passes; writer stops at supervisor401 before engine
terminal/export/reclaim, so recovery and AF07 adoption remain unqualified.
[Current disposition and next diagnostic](../.planning/STATE.md),
[failed receipt](evidence/fs-af07-attempt1-2026-10-21.json). Do not report the old
metadata-delivery absence as the current blocker. Host fixes and a bounded
numbered-check controller are prepared; another guest awaits renewed human
disposition under the existing unknown-cleanup rule. No sibling edits/messages,
owner sign-off, default refresh, launchable replacement or ISO acceptance.

## Qualified metadata input and service boundary — 2026-10-21

Aether's additive `zpl-metadata.c/.h` and userland's separate
`experiments/filesystem-service/metadata.rs` pass the original-decoder READ-only
disk consumer, including root/file metadata, stale identity, full file/hash/EOF,
three-generation cleanup and unchanged medium. [Native contract](NATIVE-C.md#separate-rust-metadata-disk-selection--2026-10-21),
[receipt](evidence/fs-metadata-native-2026-10-21.json). This is an engine-owner
Rust binding input, not AF06 service adoption or POSIX stat/credential policy.
Original C record136 bytes preserves raw64-bit labels/mode/flags and signed
seconds; getters borrow an exclusive live view/SPA, release temporary SA handles,
return positive errno and zero valid C output on error. Rust discards failed or
contradictory results. No pointer/state escapes. Values confer no authority.

The next operational userland delivery must bind this to its authenticated peer,
session and retained authorized handle before entering the unsafe backend. Define
metadata-read authority, a versioned reply/error contract fitting existing frames/
4KiB data, explicit raw-ID/time translation/rejection and reply-loss/cleanup
behavior. Do not accept raw client object/generation, silently reinterpret AF06,
expose backend pointers or infer chmod/chown authority from metadata or WRITE.
Freeze matching source/tool/artifact inputs and qualify rights/stale/malformed/
provider/reply failures and actual native consuming fit before selecting it.
Current AF06 and exact67-member dependency/30-member executable remain unchanged.

Further package operations need owner-defined ordinary-mode and cross-directory
promotion contracts before exposing them; current service explicitly lacks both.
The unchanged sys-init handoff also requires the ABI29 shell/client/PID/FD delivery,
filesystem-backed loader/runner and real Zsh/TTY. Pkg-mgr retains package identity/
layout/closure and install/run/reboot policy. SESSION's15 child lifetimes are still
a separate fixed limit and matched owner request, not permission to reset/widen it.
No replacement service/shell delivery was found during this batch. This records
the concrete next consuming inputs; it does not assign kernel privilege to paths,
metadata or packages, send requests to other chats, or claim the ISO is ready.

## Received sys-init review and next metadata input — 2026-10-20

Sys-init decision0191 now independently consumes the prior bounded first-activation
receipt and five complete retained failure spans. Aether verified its18 live-input
hashes and both producer receipt identities; no fresh guest or complete positive-
UART replay is inferred. Full ABI29 shell/client/dispatch/PID/FD and persistent
runner/package/Zsh/TTY inputs remain [the next matched handoff](../sys-init/docs/FILESYSTEM-BOOT-HANDOFF.md).

The separate unselected `zpl-metadata.h` now defines a read-only136-byte private
engine record for node/parent/links/raw uid/gid/flags and four timestamp pairs.
[Preparation contract](OPENZFS-FEASIBILITY.md#next-package-prerequisite-read-only-engine-metadata--2026-10-20).
It passes actual-C host fault/omission and pinned native-header checks; no new
AF06 RPC, service adoption or active engine seal exists for it. Userland owns
authorized handle lookup and checked POSIX/owner/ACL translation; metadata never
grants authority. General chmod/promotion and installed package loading remain
separate work. No sibling modifications/messages or namespace/policy duplication.

## First filesystem/init activation consuming witness — 2026-10-20

The exact separate sys-init2072-byte ABI29 owner and sealed Rust/OpenZFS executable
now pass actual activation/normal process settlement/export/quiescent halt,
independent post-export original-file/hash/metadata recovery and five native
hostile-peer rejection controls. [Receipt](evidence/fs-init-recovery-native-2026-10-20.json)
and [scope/limits](NATIVE-C.md#post-activation-recovery-and-fixed-failed-peers--2026-10-20).
The recorded first oracle failure is preserved and corrected; outputs are disposed.
This is Aether's bounded consuming evidence, not independent sys-init sign-off,
real OpenZFS fault recovery or full BG-067/UL-082/R1 acceptance.

Sys-init's delivered owner still runs one boot-image process; full ABI29 serial
dispatch/PID/FD policy remains its work. Userland owns package-required filesystem
metadata/promotion, filesystem-backed runtime/runner and Zsh/TTY delivery; pkg-mgr
and userland retain package identity/layout/closure and installation policy. Current
AF06 explicitly leaves general modes/cross-directory promotion unsupported. Native
engine/loader mechanisms here must follow those matched contracts and existing
limits. No replacement delivery was found; no sibling modifications, lock refresh,
messages or interim ISO. STATE records the next blocked assembly gate.

## Storage primary-wait mechanism — 2026-10-20

Separate AENBD004/ABI26 now supports primary-only waits without suspending storage
helpers. A read-only original-engine namespace guest passes actual balanced waits
and original full-file/media/three-generation cleanup checks. Host actual-code
and compiling omission controls cover helper scheduling and primary completion.
Old ABI25/session profiles and sealed candidates/pins are unchanged. Userland
still needs a matching Rust service adapter/candidate and operational executable/
ABI/provisioning/readiness/shutdown/transfer-lifetime delivery; this kernel mechanism
does not imply consuming owner acceptance or ISO completion. No sibling files or
messages changed. See STATE and the primary storage-channel wait contract.

## Mixed service native handoff — 2026-10-19

Exact41-member AFSRPC03 now passes the approved8-total mixed profile and all12
normal/lost/partial/close native guests on7 pre-admitted images. Target795/805
for full sequence; lost-first-create788/798. Original/new file, namespace/allocation/
metadata/ACL/EOF/recovery/media/export/drains/all cleanup pass. Limits/pins and old
candidates unchanged, frozen audit passes, joined owned outputs disposed.
[Native receipt](evidence/fs-service-mixed-native-2026-10-19.json),
[remaining operational handoff](OPENZFS-FEASIBILITY.md#operational-service-handoff-after-the-mixed-gate--2026-10-19).
The finite namespace/lifetime producer gaps are closed for this profile; operational
executable/ABI/provisioning/idle/larger transport/readiness/shutdown and independent
consumer/sys-init/pkg-mgr/runner/Zsh/ISO acceptance remain. Existing authorization
allows scoped userland implementation; no other sibling modification or messaging
is inferred.


## Namespace service integration scope — 2026-10-19

The authorized userland implementation now supplies a separate36-member AFSRPC02
candidate with explicit directory mutation authority and trusted bootstrap identity.
It covers one create/rename/remove attempt, retires all aliases and consumes the
C context before replying; remove rejects every live file alias. This supersedes
only the older statement that no namespace RPC candidate exists. Earlier25/27-
member receipts retain their exact meaning and their checker is not generalized.
[Contract](OPENZFS-FEASIBILITY.md#namespace-service-implementation-contract--2026-10-19),
[profile/command](NATIVE-C.md#separate-rust-namespace-service-profile--2026-10-19),
[implementation checks](evidence/fs-service-namespace-2026-10-19.json).
Native original-engine/fresh-recovery qualification now passes13 guests with9 images admitted first: create788/798, rename804/814, remove820/830; lost-reply and injected-close create788/798. Independent file/namespace/allocation/metadata/EOF/media/export/drains/all cleanup pass; sources/tools frozen and owned outputs disposed. [Native receipt](evidence/fs-service-namespace-native-2026-10-19.json). No mixed
operation observer lifetime, idle or executable/init provisioning/readiness/
shutdown contract is inferred. Userland owns those policies; Aether supplies native
engine/block/channel mechanisms, sys-init activation and pkg-mgr installation.
No sys-init/pkg-mgr/standards changes or messages; no operational delivery, independent
consumer acceptance or persistent Zsh/packages/ISO/R1 claim.

## Eight-write service native handoff — 2026-10-20

[Native receipt](evidence/fs-service-lifetimes-native-2026-10-20.json),
[host/object/integration record](evidence/fs-service-lifetimes-integration-2026-10-20.json),
[exact selection](NATIVE-C.md#service16-retirement-preparation--2026-10-20).
The separately approved27-member userland delivery manifest
`0eddb895d8a8d6276834a0d4ec58aa77e13e44be882d5eab46695cf716ff825c`, object
`35c950f9a8b49df81d85f81e112f99ff2b8215d90140f14985e598735e653c6f`,
is now bounded-native-qualified through the opt-in service-lifetimes selection.
Seven admitted images precede all12 pristine/writer/fresh-reader guests. Normal,
partial input and final-close failure perform eight16-byte calls through consumed
contexts and successful checked retirement/reopen, last795/recovery805; lost
reply stops after first788/recovery798 without replay. Independent final full-file
hash/metadata/EOF, original ordered export/drains, all21 cleanup/three terminal0/
live0/reclaims3, whole recovered media/guards pass. Report checks are in-engine,
not all72 bytes in retained observations. Writers60s/6000/readers30s/3000,
controller4096/observer8192 and all other limits stay fixed. Current699-method
broad checkpoint passes; sources/tools frozen, all VMs join and owned outputs
are disposed. Old four C objects/controllers and reviewed baseline/one-write
recovery engines stay exact; old candidate and released/SDK pins are unchanged.

This closes the16-versus4096 retirement compatibility gate for this finite service
workload, not operational delivery or independent owner acceptance. Userland's
existing retained checker remains pinned to the old25-member receipt; it does not
verify this new result. Next owner handoff must specify required namespace
operations (bounded create/shrink/rename/remove engine APIs already exist), directory
mutation authority/alias rules, mutation progress and zero-staged retirement,
blocking idle/reply-loss behavior, and exact executable/ABI/provisioning/readiness/
shutdown/drain delivery. Aether supplies the matching native engine/profile;
sys-init owns activation and pkg-mgr installation. These policies are not inferred
from AFSRPC01 or silently added to the eight16-byte selector. Native assembly
awaits that contract/delivery; no general uptime, crash/power-loss, Zsh/packages/
runner/ISO/R1 or independent consuming/human sign-off follows.

## Userland filesystem service native handoff — 2026-10-19

[Producer receipt](evidence/fs-service-native-2026-10-19.json),
[selection/commands](NATIVE-C.md#userland-filesystem-service-native-selection--2026-10-19),
[reviewed contract](OPENZFS-FEASIBILITY.md#userland-service-native-intake-contract--2026-10-19).
Aether now natively consumes the exact25-member userland delivery
`build/service-deliveries/filesystem-service-2026-10-19-v1`, manifest
`5dd5f492dd2ab2c57321a8fd610f1f6fa488dece4c4b40466a37236bf24144c4`,
object `dab564abbcc70ca93cebec7fec8d6017c569367dde8419abbf2d2701401150b1`.
The sealed relocatable Rust entry is linked into the original accounted writable
OpenZFS engine, separately selected over existing authenticated AENBD003/ABI25.
The sibling proposal's old build-rejection/native-not-run statements are superseded
for this exact producer selection; no sibling document or acceptance was changed.

After an initial positive sequence, all12 guests in a fresh normal/lost-reply/
partial-request/injected-close-failure matrix pass. Each case performs one16-byte
overwrite at37, assigns788 and recovers798 in a fresh reader. Full780248-byte
hash/metadata/EOF, original writer ordered export/drains, all21 cleanup boundaries per
guest/terminal0/live0/reclaims3, whole recovered media and outside-grant guards
pass. Lost reply retains synced progress without replay; partial EOF never
dispatches its incomplete frame. Trusted close injection consumes the original C
context first, then proves actual failed reader-close and successful writer-close
reporting. This is scoped fault qualification, not general failed-close quiescence.
The exact72-byte report is checked in-engine, not fully projected in observations.
Native holder/direction/stale/image-denial/exhaustion checks pass. All six distinct
images/twelve roles are sealed before any guest. Controllers3868/3292/3900/3868
fit4096, other bounds unchanged; writers60s/6000/readers30s/3000. One broad checkpoint
including686 harness tests passes on current bytes. Sources/tools and normal C/
reviewed baseline/recovery artifacts stay exact; joined outputs are disposed.
Two pre-guest build/admission failures and the initial positive trace-coverage
correction remain in the receipt; current matrix includes the actual image denial.

This closes Aether's requested bounded native producer matrix, not operational
service publication or independent consumer acceptance. The delivered protocol
still allows one nonempty provider call/context,16-byte payload, one connection,
64 complete requests/bounded polling, and no create/resize/rename/remove requests.
It forbids observer recycling. Do not reuse contexts, replay uncertain writes,
replace the old bridge silently, or infer sustained service from eight-write C
producer experiments. Userland must define and deliver the next operational
contract using those producer results: sustained write/context lifetime, necessary
namespace operations, idle waiting and retained uncertain/lost-reply outcomes.
Userland retains authenticated clients/UTC/credentials/aliases/POSIX policy.

Assembly also needs the exact executable, matched runtime/profile and capability
provisioning, readiness semantics and shutdown/drain outcomes, then sys-init's
consuming witness and pkg-mgr/runner/Zsh integration. The private ABI25 producer
cannot be silently substituted into a different pinned session profile. Sys-init
owns activation/readiness/shutdown; pkg-mgr owns installation/trust policy. These
are the next owner gates, with no sibling edits/messages, SDK/released-pin change,
independent sign-off, general uptime, power-loss or persistent ISO/R1 claim.

Follow-up source review2026-10-20 identifies a precise cross-owner compatibility
gap before sustained service adoption: the trusted lifetime-retire hook in
`user/storage/openzfs-volume/pool-lifetime.inc` requires4096 staged bytes after
consumed context, while the AFSRPC01 service write payload is16 and its selected
single-write profile does not link that hook. Aether must supply a matched
small-write producer contract/profile; userland must preserve progress and
uncertainty across consumed close, successful retirement/reopen and reply loss.
Do not remove the current call guard or reset history. Native engine retirement
qualification alone does not satisfy this service boundary. The
[consumer review batch](proposals/ul082-native-consumer.patch) is now applied to
userland under the maintainer's explicit approval. Its12-role/19-control verifier
and local quality/pin/inventory gate pass. [Applied receipt](evidence/ul082-native-consumer-applied-2026-10-20.json).
This is retained-evidence review, not fresh native execution or independent sign-off.
The [fixed16-byte retirement preparation](NATIVE-C.md#service16-retirement-preparation--2026-10-20)
passes actual observer/body host controls and preserves the original4096 API.
The maintainer explicitly approved eight16-byte service writes. The separately
sealed27-member userland candidate and opt-in Aether integration now implement
success-only consumed-context retirement/reopen without resetting aggregate
attempts/history. The subsequent twelve-guest qualification is recorded above; operational and
independent consumer acceptance remain separate. [Integration receipt](evidence/fs-service-lifetimes-integration-2026-10-20.json).

## Native successful-record lifetime handoff — 2026-10-19

[Producer receipt](evidence/zpl-write-lifetimes-2026-10-19.json) qualifies the
[private retirement contract](OPENZFS-FEASIBILITY.md#continuous-write-record-lifetime-contract--2026-10-19):
one successful-TXG record reused across eight4096-byte appends in one live engine.
Shrink788/798 and initialized extension804/814 precede final102403-byte content,
last assigned827/fresh recovery837. Independent full intermediate/final hashes,
identity/metadata/two EOF, consuming context close/checked retirement/reopen,
original ordered I/O/export/all21 cleanup per guest/terminal0/live0/reclaims3,
whole recovered media and guards pass. Seven prepared-before-launch guests join;
owned generated outputs are removed, actual commands/hashes/short logs retained.
The writer takes37.24s within60s/6000; readers stay30s/3000. One broad
`zig build test` checkpoint passes, including674 harness tests. No native retry.

The selected combined observer uses7596/8192 bytes with one304-byte record.
Retirement excludes record borrows, verifies exact original successful progress,
seven phases/wait and no graph/request/operation references. Monotone epochs and
retired/completed summary survive reuse; failures/device identity/global counters/
first target/operation generations never reset. Host64-write and deterministic
concurrent-pin/old-token/old-wait/failure/overflow/omission checks are scoped tests,
not all races or native uptime. Existing append-only modes, original C APIs, eight
old probe objects, native shrink/extension/recovery engines and supervisors remain
exact. Frozen native/tool inputs match; static frames are not full-stack proof.

This trusted-owner callback releases an observation record, not a client response
or complete pool/device/DMA lifetime. Rust's one-call/context policy and its
retained uncertain/lost-reply outcomes remain unchanged. The current userland
transport proposal expressly excludes observer recycling; adopting continuous
writes requires a separate matched owner contract and service witness.

Read-only inspection now verifies all25 files in userland's new private
`build/service-deliveries/filesystem-service-2026-10-19-v1` against manifest
`5dd5f492dd2ab2c57321a8fd610f1f6fa488dece4c4b40466a37236bf24144c4`.
Its `aether_fs_service_run` object is build-only, not a standalone executable or
native witness. The [transport proposal](../userland/docs/proposals/FS-SERVICE-TRANSPORT.md)
requires matched writable+IPC selection, authenticated endpoint provisioning,
client/partial-frame/lost-reply/cleanup controls and original full-file/fresh-reader
oracles. Those are the next Aether integration work, then exact launchable service
and sys-init acceptance. The older bridge-only delivery statement below records
its earlier inspection. No sibling changes/messages, SDK/released-pin adoption,
Rust budget lift, public service, persistent Zsh/package/runner/ISO or R1 acceptance.

## Native eight-write engine producer handoff — 2026-10-19

[Compact producer receipt](evidence/zpl-eight-writes-2026-10-19.json) qualifies
seven prepared-before-launch guests: shrink788/798, initialized extension804/814,
and eight4096-byte appends in one live engine, final102403 bytes/last827/fresh837.
Independent original-zdb/Python full intermediate/final hashes, identity/metadata/
two EOF after every write, consuming close/reopen, original ordered I/O/export,
all21 cleanup boundaries/terminal0/live0/reclaims3 per guest, exact whole recovered
media and outside-grant guards pass.215 focused methods, six bit-exact default C
objects, unchanged native shrink/extension engines/all supervisors and frozen
sources/listed C tools pass. All guests join and generated outputs are disposed;
actual commands, hashes, observations and short host failure logs remain.

The separately approved fixed eight-record/10240-byte observer uses9704 bytes;
ninth admission permanently poisons capacity, no reset/recycling/retry. Old two/
8192 profiles, writers60s/6000/readers30s/3000 and other limits remain unchanged.
The preceding652-method full checkpoint is before this isolated extension; focused
affected checks were used here. Static C frames are not whole-stack/peak-memory
proof. This is eight finite original-C operations, not general service uptime,
a Rust call-bound change, public SDK/API, consumer acceptance or R1 qualification.

These results supersede the historical owner30s/selector blocker in userland's
old bridge proposal. Its six-call bridge is still the sole delivered artifact;
operational authenticated transport, UTC/credentials/aliases/POSIX policy and
lost-reply/context retirement remain userland-owned work. Exact launchable service,
provisioning/readiness/shutdown delivery and matched sys-init consumption gate
Zsh/package/runner/persistent ISO assembly. Safe bounded observer retirement needs
its own contract before continuous service; do not solve uptime by resetting
history or repeatedly increasing the finite limit. No sibling edit/message,
released repin, service adoption or Rust policy change is inferred.

## Native file-size engine producer handoff — 2026-10-19

[Compact receipt](evidence/zpl-file-sizes-2026-10-19.json) qualifies nonzero shrink
780248->65539, initialized4096-zero extension->69635 and two4096-byte writes in one
engine->73722, with fresh independent recovery after each. Assigned/fresh targets
are788/798,804/814,last821/831. Independent original-zdb/Python full hashes,
identity/metadata/two EOF, original ordered export/all21 cleanup per guest, exact
whole media and guards pass. Seven prepared-before-launch guests,202 affected host
methods and a652-method integration checkpoint pass. Sources/tools unchanged,
reviewed baseline/supervisors unchanged, all VMs joined and owned outputs disposed;
actual commands/hashes/observations and short failed host attempts remain.

[Private initialized-growth interface](../user/storage/openzfs-volume/zpl-extend.h)
reuses unchanged original shrink/write/context/progress semantics; growth<=4096,
regular file/exact generation, same-size checked no-op, reject shrink, original
signed time/size/readonly/flag checks. Assigned failures retain actual progress;
retire/stop/investigate, never replay uncertain effects. No public SDK/wire or
POSIX/sparse/ACL/alias policy is defined here. Static local frames are not whole-stack
or peak-memory proof. The two-record witness is not sustained-service acceptance;
the separately approved eight-record result is recorded in the current handoff above.

Userland owns operational authenticated Rust service, trusted UTC, aliases,
credentials/ACL/POSIX and lost-reply retirement. Read-only delivery inspection still
finds only the bridge fixture. Exact launchable service/provisioning/readiness/
shutdown and matched sys-init consumption remain the assembly gate. No sibling
edits/messages/acceptance, released repins or assembled Zsh/package/runner/ISO claim.

## Native namespace mutation producer handoff — 2026-10-19

[Compact producer receipt](evidence/zpl-namespace-mutations-2026-10-19.json)
qualifies the private original-engine subset: empty0600 SA create, same-directory
exact-identity/no-replace rename, and single-link/no-external-xattr remove. Fresh
VMs recover each result at TXGs798,814,830 after assigned788,804,820. Root counts
and exact object inventory prove allocation/reclamation; original780248-byte file
hash/EOF and xattr objects remain. Each guest has all21 cleanup boundaries,
terminal0/live0/reclaims3; ordered export, exact recovered media and guards pass.
Seven images precede all VMs; later seeds require exact qualified stopped media
and successful fresh readers. Writer60s/6000, readers30s/3000, one transaction each.
193 focused methods plus the broad checkpoint (640 harness tests) pass. Generated
outputs are disposed; actual commands/hashes/observations/short failure logs remain.

The first seeded writer stopped before import with873 due to the pristine-label
selector mismatch. Compiled798 old/new-label regression and fresh corrected batch
pass. That failure and missing first-attempt actual QEMU-command retention remain
recorded; corrected commands are retained. Earlier Rust-reader873 is a separate
unattributed history, not retrospectively fixed by this result.

[Private C contract](../user/storage/openzfs-volume/zpl-mutate.h) and
[scope/command](OPENZFS-FEASIBILITY.md#create-rename-and-remove-engine-batch-contract--2026-10-19)
are Aether engine-owner prerequisites. No new public SDK/wire or live aliases,
replacement/cross-directory/directory/open-unlink semantics are delivered. Assigned
errors may have partial effects; retire/stop/investigate, never replay or treat
bytes_staged0 as no effects. Numeric UID/GID labels grant no authority.

Aether-userland retains operational Rust service/authenticated transport, trusted
UTC, credential/ACL/FUID/project and alias/POSIX policy, lost-reply retirement and
public error/durability contracts. Current read-only delivery inspection still
finds the bridge fixture alone. Next integration gate is launchable service plus
exact executable/provisioning/readiness/shutdown delivery and matched sys-init
consumption. Aether retains independent nonzero shrink/extension, sustained IO,
nonempty-remove and broader engine qualification. No sibling edit/message/signoff,
pin update, assembled Zsh/package/runner/ISO or R1 acceptance is inferred.

## Native UL-082 callback and recovery writer-window handoff — 2026-10-19

[Current matched producer receipt](evidence/recovery-writer-window-2026-10-19.json)
passes176 focused methods and pristine READ1, supplied Rust-policy/bridge WRITE7,
independent full file/hash/metadata/EOF, ordered target788/export and fresh READ1
at TXG798. All three guests complete21 cleanup boundaries/three terminal0/live0/
reclaims3; recovered whole media unchanged, guards exact, VMs joined, outputs
removed. Reviewed baseline/writer engines and all supervisors are unchanged.

The recovery acceptance window now matches the selected writer watchdog: fixed
UTC base1791290040 through30s by default or60s for approved extended writers,
inclusive. Reader execution remains30s/3000; writer60s/6000 and all other limits
are unchanged. Canonical default reader bytes and immutable bridge/C/UTC inputs
remain fixed. The preceding873 remains unattributed; matching the interval does
not prove its historical cause. Exact default/profile and source-hash rejection
checks pass. Old receipts and failed attempts remain retained, without archives.

This opens bounded callback evidence to userland consumer review and authenticated
filesystem transport/reply-loss retirement. The mutable sibling still records an
older selector/timeout blocker; that is not current producer status. No sibling
edit/message, owner acceptance, silent repin or deterministic/sustained/operational
service claim. Aether has also qualified the bounded native truncate-to-zero path below;
userland owns filesystem/POSIX/UTC policy and Zsh/TTY, init/package owners retain
assembly/install policy. Remaining mutations, persistent runner/packages/ISO and
R1 remain open.

## Bounded native truncate-to-zero producer result — 2026-10-19

[Mutation receipt](evidence/zpl-zero-2026-10-19.json) passes184 focused methods and
fresh pristine baseline/original shrink writer/readonly recovery. One free+SA
transaction, actual target788, consuming close/reopen and exact post metadata/two
EOF pass; fresh READ1 importsTXG798 and independently verifies size0, fixed empty
SHA256, identity/flags/time and EOF at0/former780248. Ordered export,21 cleanup
boundaries per guest, whole-media equality/guards and VM stop pass. Generated
outputs removed. Writer60s/6000; readers30s/3000; baseline engine/all supervisors
unchanged. This qualifies zero only, not nonzero-prefix/extension zero-fill,
sustained IO, create/rename/remove, a public API or consumer acceptance.

The existing private zpl-resize.h ownership/progress contract applies; userland's
Rust bridge needs its own safe consumer and policy/alias/lost-reply qualification.
No callback call-bound lift or package/service-policy transfer. Sys-init's current
BG-067 intake still awaits an exact launchable authenticated filesystem service,
provisioning/readiness/shutdown delivery from userland. Kernel fixtures do not
supply it. Package-owner native install/run/reboot acceptance also remains open.
This producer result is available for matched owner review; no sibling write,
message or independent sign-off occurred.

## Matched Rust writer passes; recovery acceptance remains open — 2026-10-19

The [source-bound native bridge result](evidence/rust-fs-bridge-2026-10-19.json)
qualifies supplied UL-082 Rust policy/FFI for one16-byte writer operation with full
independent C file validation, ordered export and all21 cleanup boundaries. The
fresh READ1 reader returns873 after import/OAMT and remains unqualified. All VMs
stopped; whole media equals the stopped writer with exact guards; outputs disposed.
Current failure disposition gates another guest. A stale30-second writer UTC
predicate is a plausible cause, not yet proven. Aether is preparing error-only
reader-stage attribution without weakening it. The standing writer ceiling is
60s/6000, readers remain30s/3000; no new budget decision is pending.

This is producer evidence for the exact frozen composition, not independent
userland acceptance, authenticated WRITE transport, sustained service or R1.
Userland owns further filesystem/UTC/alias/POSIX policy and native transport;
Aether retains original engine mutations/block producer work. No sibling edit,
message, pin update or transfer of ownership is implied.

## Zsh boot target reaffirmed — 2026-10-19

The maintainer requires persistent OpenZFS and interactive Zsh for the bootable
VM image; no RAM-only interim substitute. Userland's existing UL-008/009 and
PROJECT already name Zsh as the interactive destination. Its TTY/ncurses/source/
build/startup, editing and jobs require actual consumer qualification; existing
dash coverage remains process/system-shell evidence. Aether owns engine/block
mechanisms, userland the Rust filesystem service and Zsh/TTY, sys-init boot policy,
and pkg-mgr package/install policy. No sibling edits, source pin or owner acceptance
is implied by this local alignment. Snapshot/rollback remains post-R1.

## Bounded engine repeated-write/recovery gate passes — 2026-10-19

[Current producer receipt](evidence/zpl-writer-tick-budget-2026-10-19.json) closes
the repeated-write timeout in its explicitly approved6000-tick/60s writer scope.
Separate READ1 baseline, two checked advancing writes/full file+metadata/EOF,
clean export/drain/retirement/all21 cleanup boundaries/three terminal0/reclaims3,
and fresh READ1 import/full independently predicted file/metadata pass. Recovered
whole media remains exact and all VMs stopped. Normal30-second qualification is
false; one-off consumed, no userland one-call bound lift or general sustained IO.

UL-082's private Rust bridge is the next live consumer. Read-only preflight verifies
18 delivery members, eight tools/three Rust libraries, five C/header/owner-probe
inputs and UTC header; two captured Aether builder hashes differ. No C ABI break is
inferred, but current source-compatible adoption/matching selector and frozen
consumer/producer closure (or refreshed owner handoff), plus explicit next writer
budget, must precede native composition. This producer result resolves the prior
timeout prerequisite, not actual Rust callback/stack/authority acceptance. No
sibling edits/messages or silent repin. Real-media shrink/other mutations, sustained
IO, operational service, Zsh/TTY and persistent runner/packages/ISO remain open.

## Kernel fixture budget identified; persistence handoff remains open — 2026-10-19

[Exact assertion result](evidence/native-tick-assertion-2026-10-19.json) confirms
nativeTick's3000-tick fixture ceiling immediately before the generic panic. All
three engines/supervisors match the prior run; pristine baseline passes and writer
again reaches two checked synced writes/full readback, target789 and pre-export S.
No export/guest cleanup/fresh-reader recovery qualifies. The consumed diagnostic
leaves a proposed writer-only6000-tick/60s bound pending maintainer decision; no
internal-limit increase or speculative OpenZFS fix is implemented. All VMs stopped
and owned outputs disposed. No production service/SDK or consumer acceptance,
sibling edit or owner transfer follows; persistent Zsh target remains unchanged.

## Engine write/readback progresses; export handoff still blocked — 2026-10-19

The [sync-stage receipt](evidence/zpl-sync-stages-2026-10-19.json) records a passing
pristine baseline and the consumed single60-second diagnostic. Writer reaches two
checked synced writes and full post-readback/hash, target789 and pre-export S, then
generic kernel assertion. No clean export, guest cleanup or fresh-reader recovery
qualifies. An independent unchanged3000-tick kernel fixture ceiling applies, but
actual assertion attribution remains unknown. Disposition/call-site identification
precedes another guest; no service or SDK handoff. Owner boundaries above remain;
no companion edits, inferred acceptance or interim-image substitution.

## Separate pristine baseline passes; transaction sync still blocks — 2026-10-18

[Compact result](evidence/zpl-separated-baseline-2026-10-18.json) records197 focused
methods and three prepared native images on frozen sources/tools. Pristine READ1
checks the full780248-byte file, metadata/EOF, Rust ownership and21 cleanup
boundaries, leaving exact whole guarded media. The generated worker WRITE7 probe
omits the duplicate baseline stream, retains fixed independent full-file/recovery
oracles and original helper/sync/order/export/cleanup, and reaches first-target
binding, quiesce return and unlocked sync worker (`BIUVWLPOAMTbqs`). It hits30s
before ordered-root/wait return, target/terminal/guest cleanup. Actual spa_sync
entry and the cause remain unknown; no application persistence or sustained writes
qualify. QEMU stopped; no recovery reader/retry; owned outputs disposed.

The next producer diagnostic requires human disposition, then narrows original
sync entry/open-I/O/configuration/dataset-convergence progress within the same
limits. Aether-userland still owns the operational Rust filesystem service,
client/alias authority and POSIX/UTC policy; init/package owners and post-R1
snapshots remain unchanged. No sibling, SDK/ABI/pin/right/quota or consumer handoff.

## TXG worker diagnostic has no native worker observation — 2026-10-18

[Compact receipt](evidence/zpl-txg-worker-diagnostic-2026-10-18.json) retains225
checkpoint methods, final16 worker/link +4 intermediate +66 runtime checks, two
pre-guest link failures and the repaired final images with exact readonly bytes.
The only actual writer VM reaches `BIUVWLPOAMT` then30s watchdog, with no target
binding or worker marker/result/terminal/guest cleanup. Earlier commit/wait-entry
evidence belongs to a different artifact and cannot fill this trace. No worker
cause or successful sync/durability is established. QEMU is joined, no reader or
guest retry, and owned outputs are disposed.

Operational persistence remains blocked. Next refine the fixed-fixture workload
within the same limits and independent oracles after human disposition, rather
than speculate about a worker fix. Userland's operational Rust service/authority/
alias/POSIX work, init/package policy and the post-R1 snapshot boundary remain
separate. No sibling, kernel/SDK/ABI/pin/right/quota change or consumer acceptance.

## Native first write reaches sync wait; producer still blocked — 2026-10-18

[Approved narrower diagnostic](evidence/zpl-first-write-diagnostic-2026-10-18.json)
passes161 affected host methods and both native builds, with exact readonly ELF/
supervisor bytes. One writer observes assignment return, original commit return
and sync-wait entry, then the unchanged30s watchdog without wait return, TXG/errno
output, terminal or guest cleanup. This does not establish successful sync, durable
write or a deadlock. Original quiesce/sync worker progress is the next observation
boundary; no speculative fix or retry. QEMU stop is confirmed, no reader launches,
and generated outputs are removed. Human disposition gates another guest.

Operational persistence remains blocked. Existing one-write/fresh-reader scope and
userland's Rust service/authority/alias/POSIX work remain separate. No sibling,
kernel/SDK/ABI/pin/quota/right change or consumer acceptance; sys-init/package
policy and the post-R1 snapshot boundary remain fixed.

## Approved write-stage diagnostic; producer still blocked — 2026-10-18

[Compact diagnostic](evidence/zpl-stage-diagnostic-2026-10-18.json) records the
approved same-budget attempt.148 affected host methods pass; both images build,
and readonly ELF/controller bytes remain exact. The writer reaches writable open,
full pristine baseline hash and UTC validation, then first-write entry before the
unchanged30s watchdog. No checked first completion/second entry, TXG/errno result,
terminal or guest cleanup. Assignment/commit/wait and error-path closure remain
unresolved; a partial stage trace is diagnostic only. QEMU stop is confirmed,
reader never launches, outputs are disposed and no retry/limit increase is made.

Human disposition gates another native attempt; the next useful probe is within
that first-write interval. This does not unblock operational persistence or claim
consumer acceptance. Aether-userland can continue its existing Rust service,
authority/alias/POSIX contract work; kernel/SDK/pins, sibling repos and init/package
policy remain unchanged. Prior bounded one-write/fresh-reader success retains its
scope. General mutations and assembled persistent shell/packages remain open.

## Engine mutation preparation; repeated-write target blocked — 2026-10-18

[Current batch](OPENZFS-FEASIBILITY.md#shrink-and-repeated-write-engine-batch-contract--2026-10-18)
adds private original-engine shrink and two append-only transaction observations.
504 host methods and wired Zig/pin checks pass, followed by expanded focused wait/
provider denials. Both native images build and the reader/controller bytes remain
exact. The one repeated-write writer hits its unchanged30s watchdog after OAMT;
no TXG result/terminal/guest cleanup, no reader launch and no native retry. QEMU
stop is confirmed; outputs are disposed with a compact failure receipt.

This does not qualify sustained writes, real-media shrink or a writable service.
The earlier one-write/fresh-reader result remains scoped. Human disposition gates
the next persistence guest; Aether-userland may continue its operational Rust
service/authority/alias contract work from the existing producer handoff. No sibling
edit, consumer acceptance, SDK/pin/ABI/rights/quota or package/init policy change.


## Filesystem owner and native write prerequisite — 2026-10-18

The maintainer assigned the operational Rust filesystem service to
**Aether-userland**. Aether supplies the native OpenZFS engine/block contracts and
producer qualification; current Rust namespace implementations here are private
conformance fixtures. Userland owns service-side authority, handles, alias coherence,
POSIX adaptation and UTC policy. Sys-init retains startup/supervision and pkg-mgr
retains package records/install/trust policy. This records explicit direction, not
acceptance or implementation by those repositories.

The [bounded native write/fresh-VM readback](OPENZFS-FEASIBILITY.md#native-existing-file-write-and-fresh-readonly-vm-pass--2026-10-18)
now passes after diagnosing873 as write-stage ENODEV and selecting the original
trusted writable vdev lifetime. Writer assignsTXG788; fresh readonly VM recovers
TXG798 and the complete independent file/metadata oracle. Both VMs stop and pass
three-generation cleanup; reader leaves all media unchanged. Initial failures and
all checks remain in the [compact receipt](evidence/zpl-native-pair-2026-10-18.json).

[The producer handoff](OPENZFS-FEASIBILITY.md#filesystem-service-owner-and-producer-handoff--2026-10-18)
identifies current source/FFI/authority contracts and the consumer work that can
start. Public WRITE, sustained transaction observation, general mutations and
persistent shell/runner/package assembly remain open. The private readonly wire
is unchanged; no new SDK, pin, protocol allocation, sibling edit or owner sign-off.
Snapshot/rollback follows R1. Earlier progress entries retain their historical scope.


## Rust/ZPL read-only component qualifies in QEMU — 2026-10-18

[Current producer result](OPENZFS-FEASIBILITY.md#rust-zpl-composition-contract--2026-10-18)
passes complete real-file SHA verification through Rust-owned handles and original
C ZPL, local authority/reuse/epoch denials, both contexts closed, original pool
retirement and all three owner generations reclaimed. Whole guarded media is
unchanged; VM stop/frozen inputs/tools/artifacts match. Full418-method host
checkpoint and byte-exact default storage comparisons pass; outputs are removed.
This has no published filesystem endpoint or authenticated consumer traffic yet.
Peer/epoch labels are private test inputs. Next kernel-authenticated namespace
request/reply binding and generation ownership, then real ZPL writes/transaction/
recovery and persistent runner/package/sys-init composition. Userland keeps POSIX
adaptation, pkg-mgr package/install policy and sys-init lifecycle policy. No sibling
change, public SDK/ABI/pin update, new companion handoff or R1 acceptance is implied.
Earlier progress entries below retain their historical scope.

## Capacity and checksum prerequisites qualified — 2026-10-18

[Two private pairs](evidence/openzfs-storage-batch-run-2026-10-18.json) pass original
dataset-reservation ENOSPC/property-data preservation/fresh baseline readback, and
original SPA ENXIO6 rejection after16 declared uberblock checksum-bit changes.
Healthy guests complete full cleanup; the corrupt importer remains unqualified for
guest reclaim and is stopped through confirmed VM teardown. Both import disks stay
unchanged during their readers; canaries and169 frozen inputs/13 tools/artifacts
match. [Preparation](evidence/openzfs-storage-batch-preparation-2026-10-18.json)
records141 focused checks, compatibility scope and preserved failed attempts.
Generated outputs removed; no new shared ABI/SDK/UTC/pin/rights/quota or sibling
change and no filesystem-service handoff. Next is actual OpenZFS namespace/file
porting plus the Rust service/consumer boundary. Full write-ENOSPC, payload/parser
safety, physical durability and persistent runner/package/sys-init/R1 remain open.

## Dirty uncommitted update preserves persistent baseline — 2026-10-18

[One private pre-commit recovery pair](evidence/openzfs-uncommitted-run-2026-10-18.json)
now passes: original baseline TXG6/data/strict ordered completion, dirty assigned
TXG7 held before commit, confirmed host writer VM teardown, then fresh ACTIVE-only
READ import of baseline TXG6/complete record. Reader drains/retires with all21
cleanup/three terminal0/final-live0/100/reclaimed3; entire import disk unchanged,
canaries intact. No writer guest reclaim/clean export or candidate acknowledgment.
151 frozen inputs/13 tools/QEMU/prepared artifacts match. [Preparation](evidence/openzfs-uncommitted-preparation-2026-10-18.json)
passes129 focused methods and both after-sync/new build-only pairs; qualified
after-sync engines, readonly importer, supervisors and runtime remain exact.
Owned outputs/temporary files removed after compact retention. No sibling, public
SDK/ABI/UTC/pin/rights/quota or supervision/package policy change or new handoff.

This is one held-transaction schedule, not arbitrary before-ack/after-commit recovery,
physical power-loss/cache-loss durability or a mounted filesystem. Full-media/deeper
corruption, Rust filesystem service and persistent runner/package/sys-init assembly
remain next; R1 boot-to-serial-shell is open. The prior full host result is reused
only for unchanged infrastructure; changed direct consumers have focused/native
coverage. Next broad checkpoint is filesystem-service integration or shared risk.

## Controlled interrupted-data prerequisite qualified — 2026-10-08

[One private after-sync/pre-export pair](evidence/openzfs-interrupt-run-2026-10-08.json)
passes original assigned TXG6/data/strict ordered completion, closed writer borrow
and the planned parked checkpoint before export or guest reclaim. Confirmed host
VM teardown precedes fresh ACTIVE-only READ1/global READ import on exact same
media. Reader recovers the identical record/target, drains/retires and completes
all21 cleanup checkpoints/three terminal0/final-live0/100/reclaimed3. Entire
import disk unchanged/canaries intact; frozen inputs/tools/artifacts match.
[Preparation](evidence/openzfs-interrupt-preparation-2026-10-08.json) passes114
focused methods and preserves healthy defaults; [full host checkpoint](evidence/openzfs-interrupt-host-2026-10-08.json)
passes362 Python methods plus wired Zig/pins/workflow. Owned generated output and
temporary logs removed; compact evidence retained. No sibling, SDK/ABI/UTC/pin,
rights/quota or supervision/package policy change and no new companion handoff.

QEMU termination may drain host caches. This does not provide physical power-loss
durability, public commit acknowledgment, before-ack recovery or live writer
reclaim. Before-ack/full/deeper corruption, Rust filesystem service, persistent
runner/package/sys-init integration and R1 boot-to-serial-shell remain open.

## Interrupted-pool intake prerequisite prepared — 2026-10-08

[Preparation](evidence/openzfs-active-label-preparation-2026-10-08.json) adds a private
object-only ACTIVE-label profile that preserves the real state, with default
EXPORTED intake byte-identical.107 focused methods and both native-header objects/
identical23 imports pass; default healthy data engines/supervisors/runtime remain
exact through one build-only pair. Frozen inputs/tools/format/workflow checks pass
and outputs are disposed. Two corrected host test setup/oracle failures remain.
No native active import, SDK/ABI/pin/kernel/rights/quota or sibling change.

Next is the actual interrupted writer/confirmed VM-stop/same-media guard and fresh
READ-only recovery. This is no filesystem, runtime or companion handoff. Interrupted/
full/deeper corrupt-media recovery and Rust filesystem/runner/package/sys-init
integration remain required; R1 stays open. Earlier sections are historical.

## Malformed label header control qualified — 2026-10-08

[One private negative pair](evidence/openzfs-pool-corrupt-labels-run-2026-10-08.json)
passes normal data writer/export/full cleanup/VM stop, then exactly four label
encoding-byte mutations and fresh READ-only pre-import rejection. Import disk
unchanged/canaries intact, both VMs stopped, exact healthy native artifacts and
144 inputs/13 tools preserved. Importer873/401/reclaimed0 and only cleanup1/2 are
expected denial, not guest reclaim or recovered data.103 focused methods and
build-only/pin/process checks pass; generated outputs and temp logs removed.

The healthy data prerequisite below remains qualified. No sibling or public
filesystem/service/SDK handoff is made; interrupted/full/deeper corrupt-media
recovery and Rust filesystem/runner/package/sys-init integration remain required.
R1 boot-to-shell is still open. Earlier sections are historical.

## Assigned-data prerequisite qualified — 2026-10-08

[The approved corrected pair](evidence/openzfs-pool-data-drain-run-2026-10-08.json)
passes original assigned TXG 6/data validation/strict ordered writer export, confirmed
VM stop, fresh READ-only matching data/TXG readback and original readonly retirement
after queued-user drain. Both guests pass all 21 cleanup checkpoints, three terminal
zero owners/final-live zero/supervisor100/reclaimed3. Whole import disk unchanged,
canaries intact and both host finally waits returned; all prepared artifacts and
138 sources/13 tools match. READ1/global READ/30s/82-context/32MiB and SDK/ABI/UTC/
pins remain fixed. Generated outputs are removed; prior failures remain unqualified.

This is one graceful private single-leaf data prerequisite. [The full host checkpoint](evidence/openzfs-pool-data-drain-host-2026-10-08.json)
passes 341 Python methods and wired Zig/pins/workflow on 413 frozen inputs/13 tools.
Recovery/full/corrupt media and a mounted Rust filesystem are still
required before persistent package/runner/sys-init handoffs. No sibling or consumer
acceptance, production durability or R1 boot-to-shell readiness is claimed. Earlier
sections below are historical.

## Native assigned-data gate — 2026-10-08

[One data pair](evidence/openzfs-pool-data-pair-run-2026-10-08.json) passes writer
TXG6/strict ordering/export/full cleanup. Fresh READ-only importer reads the same
record/target6, then returns873 before readonly retirement; importer reclaim and
the pair remain unqualified. Both VMs stopped, entire import disk unchanged and
canaries intact; generated outputs removed. Native qualification is stopped under
the accepted recurrence rule, with no retry or companion handoff.

[Correction preparation](OPENZFS-FEASIBILITY.md#assigned-data-readonly-retirement-drain--2026-10-08)
adds only original async-user eviction wait after closed borrows/outside locks;
actual references still reject. [Final build-only preparation](evidence/openzfs-pool-data-drain-preparation-2026-10-08.json)
passes99 affected host methods/original wait origin and structural limits. Default
metadata, passing writer engine/data supervisors and private runtime stay exact;
all138 frozen inputs/eight SDK tools match and five host-tool hashes verify. Outputs
removed; no corrected guest. Renewed human disposition precedes
another native pair. Metadata-only bytes, READ1/global READ,30s/82-context/32MiB,
SDK/ABI/UTC/pins and sibling ownership stay fixed. Recovery/filesystem/package/
sys-init integration and R1 remain open. Earlier sections are historical.

## Native storage runtime integration gate — 2026-10-07

[Assigned dataset helper preparation](OPENZFS-FEASIBILITY.md#assigned-dataset-data-probe-preparation--2026-10-07)
now passes51 focused methods and strict native object/build-only engine closure.
Original dataset ownership/assignment/getter/identity join/commit/wait and readonly
record guards are prepared, with all64 single-byte corruptions and named omissions.
No new guest or filesystem/SDK/ABI/sibling handoff. The helper is not native-selected;
next wire writer/fresh readonly reader and require matching original assigned target,
actual ordered provider/root completion, drain/export and fresh data. Generated
outputs removed; current metadata pair below remains its unchanged bounded scope.

The [corrected native pair](evidence/openzfs-readonly-retirement-run-2026-10-07.json)
now passes creator nonforce export, confirmed VM teardown, fresh readonly original
SPA/MOS5000 readback and original private pool retirement on the same owned disk.
Both guests complete all21 cleanup observations, three terminal0 owners/final-live0,
supervisor100/reclaimed3 and native block marker. Entire import disk unchanged;
canaries intact and both VMs stopped. READ1/global READ/30s/82-context/32MiB fixed;
importer retirement means in-memory eviction, not on-media clean export.
The [single full host checkpoint](evidence/openzfs-readonly-retirement-host-2026-10-07.json)
passes329 Python methods plus wired Zig/pins/workflow on frozen inputs. Generated
outputs removed; original failed attempts and unknown earlier timeouts retained.
No SDK/ABI/UTC/pin/sibling change or companion action/handoff. Next is assigned
application data transaction/fresh readback with actual TXG/provider ordered-flush
closure; transactions/recovery, filesystem/package/sys-init and R1 remain open.
Earlier preparations/results below are historical, not execution authorization.

[Final cleanup diagnostics](OPENZFS-FEASIBILITY.md#final-cleanup-boundary-diagnostics-preparation--2026-10-07)
are now host/compile prepared. Default-off kernel scalar observations leave
engine/supervisor/runtime bytes, limits and sibling contracts fixed.43 focused
checks and actual trace-on/off kernel builds pass; the broad host classification
failure is retained and its scoped fix verified. Root cause/final native reclaim
remain unknown. No guest or import ran; renewed human disposition is pending for
one create-only diagnostic. No companion action or handoff is implied.

Latest [paired import attempt](OPENZFS-FEASIBILITY.md#readonly-fresh-vm-import-preparation--2026-10-07)
is blocked on creator final completion: three terminal0 owners, but no supervisor
success/reclamation/pass marker before the watchdog. Import never started; host VM
teardown is confirmed.49 focused host methods and both build-only profiles pass,
but native readonly MOS readback remains unqualified. The recurrence stop/report
rule is active; local boundary investigation/review and renewed human disposition
precede further execution. No sibling action, SDK/ABI change, filesystem delivery
or pkg/sys-init/R1 acceptance is established. The following checkpoints are
historical and do not qualify this changed creator composition.

The [corrected native checkpoint](OPENZFS-FEASIBILITY.md#corrected-native-pool-creation-and-export-checkpoint--2026-10-07)
now passes original pool creation/export, three clean owner reclamations and two
storage-denied replacements. The actual attached disk changes with intact outside
canaries; host teardown confirmed. This closes the bounded creation checkpoint,
with full `zig build test` passing once (302 Python harness tests). Fresh
import/readback, assigned transaction/TXG/provider closure, recovery and the Rust
filesystem service remain; no maintained SDK/ABI/sibling contract change or
filesystem/pkg/sys-init/release owner acceptance is inferred.

Latest [worker-sized checkpoint/harness review](OPENZFS-FEASIBILITY.md#worker-sized-checkpoint-and-harness-correction--2026-10-07)
reaches first-owner create/export and terminal0, but401/reclaimed0 prevents completed
ownership acceptance. A raw diagnostic C/resource-row mismatch and wrong pool-media
snapshot path are corrected in host/build preparation (39 checks;2299-byte native
supervisor). Historical pool snapshots hashed unused seed media; guest final bytes
were already compacted and remain unknown. Engine/runtime/SDK contracts unchanged;
no sibling action or acceptance follows. Native runs stopped; renewed disposition
and corrected reclamation/media witness come next.

The [bounded measurement](OPENZFS-FEASIBILITY.md#measured-live-worker-admission-failure--2026-10-07)
now identifies original pthread11/EAGAIN and actual live-worker admission at82
against82 capacity, with matched caller identity. Selected-source review corrects the earlier upstream-default estimate: globals
already use1/1 workers, and the conservative complete selected steady budget is83.
A single pool FREE throughput floor32-to8 change prepares59 steady/62 including
one-leaf helper allocations. Source/queue-progress and resource review belong
here; native create/export/drain and memory-pressure acceptance remain. Native125 and
uncertain retirement are reported; execution stopped and current approval consumed.
QEMU stopped and final media matches seed, without flush/quiescence proof. New
[worker preparation](OPENZFS-FEASIBILITY.md#one-core-pool-worker-policy-review--2026-10-07)
passes59 focused host checks and build-only composition; no native retry. Generated
outputs are removed after compact receipt verification. No kernel/runtime ABI, maintained SDK
or sibling action requested. FS/pkg/sys-init and assembled R1 remain unqualified.

The [approved diagnostic attempt](OPENZFS-FEASIBILITY.md#diagnostic-attempt-and-coverage-correction--2026-10-07)
also returns125 after creation entry with no site marker and no confirmed
export/engine/runtime retirement. QEMU is stopped; final media matches seed with
intact outside canaries. Execution stopped/reported; one-run approval consumed.
Eight omitted assertion/time exits are corrected in a44-site private diagnostic
build, with234 checked time consumers and bounded assertion line/caller evidence.
Focused host/build-only checks pass; renewed disposition precedes another native
run. No kernel/userland ABI, runtime delivery, owner contract or sibling change;
no filesystem/package/sys-init handoff or acceptance follows.

The [approved corrected-input checkpoint](OPENZFS-FEASIBILITY.md#approved-corrected-input-checkpoint--2026-10-07)
returned generic125 at creation without confirmed export/engine/runtime retirement.
Final whole-disk hash matches the seed and outside canaries are intact; no flush or
quiescence claim. Aether immediately notified the maintainer and stopped further
pool/persistence execution. The next local work is failure-site localization;
no sibling delivery/contract change or owner acceptance is established. The one-run
approval is consumed; further affected execution requires renewed disposition.

The [first pool creation checkpoint](OPENZFS-FEASIBILITY.md#native-pool-creation-resource-checkpoint--2026-10-07)
returned872 before successful creation, with unconfirmed export/engine/runtime
retirement and unknown final media effects. Aether stopped native persistence
qualification and notified the maintainer. A concrete version-property defect is
corrected in preparation; original errno and failure-media diagnostics are added,
with host/build checks only. Renewed human disposition is required before another
pool run. This is a local experiment blocker: no sibling SDK/contract change or
filesystem/package/sys-init owner acceptance is requested or inferred.

[Original open-probe/copy investigation](OPENZFS-FEASIBILITY.md#original-open-probe-observation-scope--2026-10-07)
locates long successful provider calls and removes per-byte page-record scans in
native sector validation/copying. At most two checked fragments preserve complete
validation-before-effects and stable IF=0 borrows.24 native cases and238 host
checks pass: C cross-page/no-mutation denials, Rust block consumers, paired open
checkpoints, physical controls and revoked ZIO. Engines remain byte-identical
between paired/prequalified cases. The measured context supports a concrete copy
bottleneck, not replay or complete attribution of an earlier failed schedule.
Aether's [minimal writable-pool contract](OPENZFS-FEASIBILITY.md#writable-pool-preparation-contract--2026-10-07)
now separates provider/leaf flush completion from upstream parent-wait success,
partial writes from durability, and owner close from device quiescence. Host body
checks cover real callback/provider propagation and synthetic bypass/error cases;
the [physical write/flush experiment](OPENZFS-FEASIBILITY.md#native-physical-write-and-flush-scope--2026-10-07)
now passes all six native cases plus the unchanged read regression. Actual provider
completion, fresh-VM readonly readback and exact media/callback/lifetime controls
are qualified for raw disposable media only. Next local work is pool-create/import/
TXG runtime and resource closure. Original v2 UTC cause remains unknown; human
disposition now permits the bounded disposable v3 experiment under the conditions
below. Persistent service/release acceptance remains separate. No new sibling
delivery blocker, public SDK promotion or filesystem/service handoff is established.
The [pool dependency audit](OPENZFS-FEASIBILITY.md#pool-dependency-and-resource-audit--2026-10-07)
now links18 original pool/DMU/TXG roots and accepts their static image structure
without running a pool. Newly required DSL/TXG/MMP/auxiliary workers, cache/stack
pressure and export drains still need native measurement. It changes no companion
contract or readiness claim; technical pool and broader acceptance gates remain.
The [bounded UTC assessment](OPENZFS-FEASIBILITY.md#utc-timeout-evidence-assessment--2026-10-07)
now has the maintainer's [accepted human disposition](OPENZFS-FEASIBILITY.md#required-independent-disposition)
for disposable corrected-v3 QEMU pool experiments after technical prerequisites.
Original v2 root cause remains unknown. An unexpected v3 missing terminal/stall, unmatched
completion or uncertain cleanup stops affected qualification and is reported to
the maintainer in this chat immediately, with compact failure/teardown/effect
facts; reopen investigation before further affected persistence acceptance.
No new sibling delivery, production/valuable-data use or release approval follows.
No companion is changed or messaged. Defaults, pins, ABI, rights and budgets stay
fixed; all owned outputs are removed after compact receipts.

Earlier bounded qualification follows:


[Physical stage qualification](OPENZFS-FEASIBILITY.md#physical-read-stage-observation-scope--2026-10-06)
now passes actual512-byte provider/callback/wait/data/borrow and vdev/SPA/engine
teardown with66 final origins,18/3/3 observation rows and3 clean reclaims. The
four-case target group passes positive plus exact861/862/860 rejections. Separate
closed-grant ZIO propagates actual ENXIO, preserves the entire destination and
tears down cleanly; whole readonly media stays identical. Root regression retains
three full engine lifetimes and its previous byte-identical ELF. Healthy-open867
checkpoint passes again; it remains unclean evidence.

An earlier missing-callback timeout stops at C before healthy-open O/read Q;
identical engine/supervisor bytes later pass. Open variability is unresolved,
not an established maintained-runtime defect or new delivery blocker. Aether owns
that next bounded open/probe/child-taskq investigation. Prior UTC attribution and
independent reader acceptance remain open before persistent pool/service handoff.
237 host/Zig/pin checks pass. Candidate defaults/pins/ABI/quotas/watchdogs remain
unchanged; no companion is modified or messaged. All owned build/run outputs are
removed after compact receipts, including failures.

[Actual empty SPA activation/root ZIO qualification](OPENZFS-FEASIBILITY.md#empty-spa-activation-and-root-zio-scope--2026-10-06)
now passes on opt-in corrected elapsed/UTC v3. Original SPA state transitions,
real synchronous completion and cleanup retain57 actual origins, three normal
owner generations/live0/reclaims, exact857/858 controls and unchanged readonly
media. This closes the bounded empty activation/root-completion producer step;
it does not qualify physical I/O, a pool, public SDK, filesystem service or owner
sign-off. The raw8MiB region cannot meet the unchanged64MiB device minimum. Aether
can continue real-vdev/physical-ZIO work locally; no new userland/sys-init delivery
blocker is established. Prior UTC terminal attribution and independent reader
review remain open before persistent acceptance. No companion repository is changed.

[Producer scope](OPENZFS-FEASIBILITY.md#scoped-resource-binding-scope--2026-10-06)
and [compact qualification](evidence/openzfs-resources-arc-2026-10-06.json) close the
private checked resource and ARC-pressure prerequisites:28 final native cases,
26 unchanged resource regressions and188 host tests pass. Existing query0x22000
returns free pages in RAX and total grant in R8; require the exact memory selector,
zero reserved inputs and checked signed/byte arithmetic. One eligible CPU follows
the pinned-owner profile, not host topology or a CPU reservation. Private legacy
physmem/boot_ncpus labels carry these scoped meanings; public sysconf does not change.

Userland has now delivered its corrected opt-in service-runtime-v0 supplement,
seal `101001e0edefb8471546ebc85d9aea6ffa759529243c8507abe288ddb84d0ba1`.
[Independent intake](NATIVE-CLOCKS.md#maintained-runtime-intake-scope--2026-10-06)
verifies282 delivery members,240 unchanged guarded-base members and an identical
source rebuild. Aether's independent native client qualifies lifecycle/capacity,
long conditions, busy/final shutdown and stop/replacement, plus disabled804/early802.
The supplement is retained once in `.deps/native-service-runtime-v2`, separate from
the unchanged `.deps/native-current/sdk`. The **SDK delivery gate is cleared**;
default/public SDK pins and independent human/reader acceptance remain separate.

The old engine adapter exports mapping/basic I/O only and must be omitted when
linking this supplement. Strict whole-engine link passes with replacement and
rejects retained old adapter overlap. The [empty-engine native admission](OPENZFS-FEASIBILITY.md#empty-engine-native-admission-scope--2026-10-06)
now executes actual startup/fini with all selected providers and explicit metadata:
three large-owner generations, exact reclaims/stale rejection, bounded detached
retirement and final zero-live finish pass. Omitted-fini224/finish225 and missing
entropy125 reject. No parallel production libc or maintained-SDK fork is created.

[Actual file-vdev/Rust volume qualification](OPENZFS-FEASIBILITY.md#readwrite-startup-and-vdev-binding-scope--2026-10-06)
now passes open/size/reopening/close, positioned partial-I/O/flush and all four
disposable-disk cases with31 origins and three successful owner reclaims. Select
`--engine-volume` for the complete sequence; use `--engine-native --case write-mode`
for independently qualified mode3 empty startup. Default kernel_init(1) is READ,
correcting earlier WRITE scope wording without rewriting old receipts. The Rust
provider is private in-process glue, not a public SDK or full storage-service API.
This default elapsed profile adds no calendar policy. The separate opt-in UTC
intake below supersedes its earlier missing-delivery gate; the confirmed
maintained-reaper defect now requires a fixed owner delivery. Actual ZIO/pool/transaction/reboot and production
sys-init launch/regrant/recovery remain separate acceptance.

[Real taskq volume worker lifetime](OPENZFS-FEASIBILITY.md#queued-volume-helper-lifetime-scope--2026-10-06)
now passes queued C/Rust/native I/O, read-only and parked-before-I/O revoke/drain,
with actual inline-dispatch846 rejection. `--engine-volume-workers` selects its
three cases, retaining38 origins and exact owner/reclaim semantics. The current
default volume ELF stays identical. This producer fixture adds no SDK/service API
or sys-init policy; issued-device cancellation, actual ZIO/pool and production
regrant/recovery remain open. No shared UTC delivery or owner acceptance is inferred.

Source-bound producer command for independent owner intake:

```sh
python3 scripts/service_runtime_smoke.py --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2 --engine-native
```

Append `--case no-fini`, `--case no-finish` or `--case no-entropy` for a
lifecycle/provider control. The
[compact receipt](evidence/service-runtime-empty-engine-2026-10-06.json) pins tools,
inputs, sources and measured target admission. This closes the producer's empty
engine checkpoint, not independent userland acceptance, a production Rust/FFI
handoff or general pool/persistent filesystem behavior.

Userland can independently consume these source-bound producer commands:

```sh
python3 scripts/service_libc_clock_smoke.py --openzfs-arc --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
python3 scripts/service_libc_clock_smoke.py --openzfs-resources --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

The base input manifest SHA256 remains
`0521371de06c44489426635890c4bb96bc820912ac7200c4294ff7eaea081d95`,6458 members;
the receipt pins final112 sources, tool and executed artifact hashes. Current
sources are `user/native-memory` plus the selected builder and owned OpenZFS ports
in `user/storage/openzfs-elapsed`; entry/transform/compile commands are in the
maintained runner. Generated binaries/source trees are disposed, not delivered as
archives. Independent intake must rebuild matching inputs and preserve the same
authority, deadline/error, TLS/TSD/origin/retirement and stop/reclaim semantics.
Kernel operation changes require Aether review; public SDK/source integration and
independent consumer acceptance remain userland-owned.

[Private segmented long waits](NATIVE-CLOCKS.md#segmented-long-wait-scope--2026-10-06)
now supply the scoped two-second prerequisite without enlarging native admission:
real/repeat/early331/old-bound341 qualify; default image bytes remain unchanged.
[Expanded long sleep/stop](NATIVE-CLOCKS.md#service-long-sleep-and-stop-scope--2026-10-06)
now qualifies82/two-worker two-second sleep and confirmed stop during its second
chunk, including fresh replacement and actual old-backend384 rejection. Shared
conditions remain900ms; final producer ELF identity and unchanged default image
are checked. Userland can run the same service command with `--long-waits` in
place of `--openzfs-arc`, or supported `--case timeout|spurious|stop|old-bound`.
Do not combine long mode with OpenZFS modes: that composition is not qualified.
This earlier private producer evidence remains distinct from the maintained
supplement intake above. Neither qualifies82 application-worker long conditions
with an additional reaper or30-second production linger. The new consumer uses
81/one application workers plus the charged reaper and real long conditions.

Required production configuration/volume, truthful UTC and pool/
helper/281-lifetime/ARC/entropy budgets remain explicit native/provider work. The
new ARC headroom target is not reservation or reclaim, and its32MiB floor remains.
No actual ARC growth, dirty transaction, persistent
filesystem, package/reboot or R1 acceptance is claimed. Empty engine lifecycle
passes; scoped volume/UTC gate the next persistent pool experiment locally.
Userland delivery no longer blocks the next implementation. Sys-init retains
supervision policy and pkg-mgr package policy; no sibling changes or sign-off.

[Large-service region primitives](NATIVE-BLOCK.md#large-service-region-composition-scope--2026-10-06)
also compose existing ABI14 block grants with service backing under an explicit
selection. Actual unchanged Rust clients qualify bounded writes, reboot readback,
attenuation, close/fault/replacement denial and wrong-profile rejection; small
region and maintained-runtime regressions pass. This uses the guarded base and
existing minimal adapter, independently of the engine/runtime composite. It does
not deliver engine vdev I/O, pool persistence or a production Rust filesystem API.
The maintainer assigned shared UTC establishment/policy to Aether-userland on
2026-10-06. Aether owns raw source observations/enforcement; calendar conversion
and source trust remain userland work. No separate daemon or qualified UTC SDK
is implied by that decision.
[Raw source intake](NATIVE-CLOCKS.md#raw-rtc-intake-scope--2026-10-06) now passes
explicit-date/leap-day, replacement and disabled-source cases. The same reference
records concrete shared UTC delivery requirements; affected-owner intake remains
pending and no sibling has been modified.
The newer [shared UTC engine intake](OPENZFS-FEASIBILITY.md#shared-utc-engine-intake-scope--2026-10-06)
supersedes the missing-delivery blocker: userland's sealed native-utc-v2 is
independently rebuilt, with four final native cases passing actual engine/SPA/
taskq time and closure plus source/policy denials. It stays opt-in and provisional:
one prior missing-terminal observation requires native/runtime liveness diagnosis
and owner review, not a guessed calendar fix or wider quotas. Aether owns native
wait/scheduling and engine composition; userland owns maintained runtime/UTC.
The later [detached reaper witness](NATIVE-CLOCKS.md#result-and-maintained-owner-handoff)
confirms a lock cycle in the exact maintained backend inherited by UTC; it does
not attribute that first stall. That handoff is now superseded by the
[corrected v3 independent intake](NATIVE-CLOCKS.md#corrected-candidate-intake-result):
new294/343-member elapsed/UTC seals rebuild identically and pass overlapping
retirement, serial/busy/stop/exhaustion and all six actual engine UTC cases. The
reaper delivery blocker is cleared for this opt-in candidate; real SPA/ZIO and
persistence qualification resume from that base, with reader sign-off still open. Eight actual UTC SPA/taskq reuse cycles
per owner pass, with the short847 control; those passes do not waive the defect.
No sibling is modified or signed off. Actual activation/ZIO/pool persistence and
production service/recovery remain separate.

[Maintained runtime/region composition](NATIVE-BLOCK.md#maintained-runtime-and-volume-scope--2026-10-06)
now passes actual worker reads, write/flush, same-disk fresh-VM verification,
read-only denial and corrupt-data rejection under existing82/two-worker limits.
One exact first-generation owner receives the region; peers/replacements deny.
No vdev/file provider, service-recovery factory, UTC or filesystem API is delivered.
The next persistent-engine timestamp gate requires the assigned userland UTC
provider and checked consumer intake; remaining Aether vdev/service work stays open.

OpenZFS allocation prerequisite,2026-10-06:
[scope/result](OPENZFS-FEASIBILITY.md#bounded-allocation-failure-scope--2026-10-06)
qualifies the private malloc fallback's one-attempt fatal NOFAIL and DEFAULT
constructor-error cleanup under native grants, composed with elapsed/entropy.
Twenty-two native cases and15 unchanged regressions pass at82/two-worker scale.
All198 selected inline-header consumers rebuild; full-engine relink remains
build-only. Fatal125 routing uses the private probe adapter; default/public SDK
and full-engine runtime acceptance remain separate. This measures a smaller
fixture, not ARC/full-engine fit. Existing query exposes total grant quota; no
SDK/shared interface change is made. Simulated ARC pressure and unchecked host-wide
resource/CPU assumptions remain local engine-entry work. Userland owns its SDK,
sys-init supervision policy and pkg-mgr package policy. No sibling/owner acceptance
or persistent filesystem/release claim is made. Compact evidence only.

Selected OpenZFS entropy binding,2026-10-05:
[scope/current command](NATIVE-ENTROPY.md#selected-openzfs-binding-scope--2026-10-05)
binds actual libzpool init/fill/fini to the existing delegated entropy grant,
replacing random-device opens and the non-progressing read loop. Actual82/two-worker
draws share the4096-byte lifetime quota; permanent close, stop and replacement
are qualified in the private producer profile. Userland's public getentropy/SDK
and future scoped /dev remain separately owned/unimplemented. No sibling change,
independent consumer acceptance, entropy-quality or full-engine budget/startup
claim is made. Required resource/CPU/identity/configuration/volume providers,
native heap/ARC/helpers, longer waits and UTC remain before persistent storage.
STATE links compact results; generated outputs are disposed without archives.

Selected OpenZFS elapsed port,2026-10-05:
[private command/scope](NATIVE-CLOCKS.md#openzfs-elapsed-caller-scope--2026-10-05)
now calls actual libzpool CV/mutex/delay functions with actual musl/native waits.
Monotonic conditions, retained absolute deadlines and exact lbolt tick conversion
pass at82/two-worker scale, including spurious/broadcast/stop/replacement and named
early/old-domain failures. Full-engine relink changes only two reviewed upstream
objects; no engine startup or public SDK adoption is claimed. Lib tpool block
probes are distinct from pool lifecycle. Userland retains SDK ownership; scoped
provider identity/resources/configuration, production long waits/UTC and engine
startup/fini/restart remain before persistent storage. No sibling change or new
owner sign-off is implied. STATE links the compact result; generated builds are
disposed after success and failure without archives.

Expanded actual-musl timing,2026-10-05: [compact producer result](evidence/service-libc-clock-2026-10-05.json)
qualifies82/two actual pthreads through original-deadline condition retries,
broadcast/contended relock,200ms relative/absolute sleep and timed stop/replacement.
Actual TLS/TSD/destructor/join/retirement and existing quotas remain intact; nine
fresh cases and five smaller regressions pass with named381/380 controls. This
supersedes the expanded-musl private-prerequisite gap in the earlier notes below.
Userland still owns maintained SDK integration and independent consumption. Aether
next binds selected OpenZFS elapsed callers/providers; UTC, scoped resources and
actual engine lifecycle remain open. No sibling/default SDK/released pin change or
assembled R1 acceptance is made. New builds use current pinned inputs and compact
receipts, never disposed historical archives.


Worker-clock composition,2026-10-05: [producer result](evidence/service-clock-2026-10-05.json)
qualifies existing absolute waits on82 bare service workers/two peers, including
simultaneous expiration, exact wake/requeue/pins and stop/replacement. The private
build incompatibility is removed without new grants, operations or quotas. This
supports the next actual expanded musl timed-wait trial; userland still owns
maintained SDK integration. It does not supply UTC, production pthread semantics,
full engine providers/resources or successful OpenZFS startup. No sibling or
released-pin/default SDK change is made.


Private musl timed backend,2026-10-05: [native contract](NATIVE-CLOCKS.md) and
[compact producer result](evidence/libc-clock-2026-10-05.json) provide actual
musl1.2.6 monotonic timed conditions and elapsed sleep over the existing explicit
thread grant. The local checked `__timedwait_cp` patch preserves absolute deadlines
and errors; actual mutex cleanup, spurious retry and sleep/early-completion controls
pass. Userland owns maintained SDK integration and independent acceptance. This
fixture does not alter its guarded/default SDK or supply UTC, shared waits,
interruption, expanded filesystem-worker timing or full engine startup. Historical
bulk archive replay remains retired; source builds use current verified inputs.


Guarded SDK intake,2026-10-04: [Aether independent qualification](evidence/openzfs-sdk-guards-intake-2026-10-04/README.md)
verifies userland's sealed error-guard delivery and all1349 libc object occurrences.
Only clock_gettime/sysconf change; corrected actual ENOSYS/unchanged-buffer behavior
and old-library240/241 native controls pass. This closes Aether's bounded independent
guard intake, superseding waiting for that delivery. No default SDK/pin, sibling or
kernel change. Userland still owns production SDK/provider bindings and other
sysconf review; Aether defines scoped native primitives/configuration/resources.
Real providers and engine startup are absent; this does not close filesystem,
package, continued-shell or assembled R1 acceptance.

ABI24 dispatcher correction,2026-10-03: [producer patch and native proof](evidence/session-poll-terminal-2026-10-03/README.md)
confirm a terminal/transfer race shared by Aether's fixture and sys-init's borrowed
dispatcher. Re-observe the exact held task after EOF/EPIPE before existing terminal
settlement; live-peer closure still fails. Canonical-client immediate/delayed/wide
compositions and all11 old serial cases pass. Sys-init must explicitly apply the
scoped producer patch without changing its owned entry/policy, inspect resulting
code/stack and consume it in matched normal/negative qualification. No sibling
change or owner acceptance is performed here; the original uninstrumented failure
is not independently localized to this call site.

ABI24 matched intake,2026-10-03: [canonical runtime and actual sys-init entry delivered](evidence/abi24-companion-intake-2026-10-03/README.md).
All sealed packet/artifact members and actual ISO component identities verify.
A fresh normal delayed boot completes the real shell and ten-reclaim halt;
wrong-ABI/busy-halt controls reject. Normal immediate boot reproduces sys-init's
retained failure after the final helper, before parent completion. Diagnostic
success does not resolve it. The missing-runtime/entry blockers below are
superseded; next diagnose the dispatcher's possible terminal/transfer timing
window, then qualify the matched producer/consumer fix. No sibling changes,
owner sign-off or assembled R1 acceptance.

ABI24 private client progress,2026-10-03: [Aether's wait-enabled fixture](evidence/session-client-wait-2026-10-03/README.md)
now survives35-second real dash prompt idle and completes commands/ten-reclaim halt.
The extracted ABI23 runtime remains userland-owned and unchanged. Canonical runtime
adaptation must consume009/0x24004, retained partial offsets and explicit ambiguity/
signal policy, with independent matching consumer qualification. Actual sys-init
entry/boot policy remains separate; no sibling changes or owner sign-off.

SI-07 companion intake,2026-10-03: [six snapshots verified](evidence/si07-handoff-review-2026-10-03/README.md).
Userland independently replayed nine matched producer and seven sys-init loop cases.
Sys-init delivers quiescent shutdown, six commands/18 reclaims and four partial/
Unknown error controls. Its source export matches all35 current kernel files; a
fresh owner rebuild is byte-identical. Missing-input/fixed-five blockers are closed.
Native child-bootstrap/malformed/stale/foreign schedules, wider waits and useful
shell-session composition remain local work; no external blocker is established.
These checks do not claim production recovery or full SI-07/R1 acceptance.
Earlier pending handoff wording below is superseded by this verified delivery.


SI-07 update,2026-10-03: the v2 transport and runner/bytecount delivery has arrived.
[Matched native integration](evidence/si07-native-2026-10-03/README.md) passes five
useful command generations, actual idle/wake,15 reclaims and authorized halt,
plus cohort-cleanup and pre-admission epoch-exhaustion controls. Seeded native
255/256/65534/65535 commands and both parent-carrier mismatch directions pass with
cleanup/halt; this is not65535 sequential cycles. Legacy regressions pass. Kernel-owner code/grants and userland inputs remain separate; sys-init must
supply/qualify its own policy owner against this closure. Full SUSTAIN-01–06,
native child-mismatch/malformed/foreign/partial coverage and independent consumption
remain open. Next gate is userland technical replay and sys-init consuming policy.

SI-07: [Aether's private v2 protocol reconciliation](evidence/si07-v2-review-2026-09-29/REVIEW.md)
is complete. The proposed AERIO002/NIO2/0x7b closure fits the existing enforcing
mechanisms with full-width cohort checks and finite epoch retirement. That review originally awaited userland bootstrap/transport and rebuilt payloads;
the2026-10-03 delivery above supersedes the missing-input status. Sys-init owns policy, approval and eventual independent consumption;
no runtime adoption or owner approval is inferred from the host/design review.

Current handoff: the [scratch-session producer](evidence/scratch-session-2026-09-29/README.md)
consumes userland’s frozen SESSION-SCRATCH workload and seeds without sibling
changes. It supplies the owner/client source, matched regressions, exact negative
oracles and linked resource inspection. [Verified independent acceptance](evidence/scratch-acceptance-review-2026-09-29/README.md)
now closes SCRATCH-SESSION-01–06 for the private volatile profile. The [real serial-session input](evidence/serial-session-2026-09-29/README.md) has qualified producer delivery and
[verified independent acceptance](evidence/serial-acceptance-review-2026-09-29/README.md)
for SERIAL-SESSION-01–06:169 fresh native cases,11 comparisons and151 checker
controls. Userland UL-081's boundary assessment is complete and
[verified locally](evidence/session-sdk-intake-2026-09-29/README.md).
Userland now records explicit maintainer ownership assignment and supplies the
sealed bounded runtime candidate. Its [local review](evidence/session-runtime-review-2026-09-29/README.md)
verifies delivery and rebuilds identical native-tested worker ELFs. Actual independent
technical/reader findings and SSDK-01–06 consumer/owner disposition remain pending.
Aether retains native ABI/grant and fixture-owner responsibility. SI-07 bootstrap/transport and rebuilt runner/bytecount are now delivered; the
matched replay checkpoint above awaits independent consumption. Shared SDK and R1 assembly
remain separate. STATE is authoritative; earlier handoff notes below are historical.

The [dash recovery producer handoff](evidence/recovery-native-2026-09-25/README.md)
now supplies the unchanged RECOVERY workload and controls for userland replay:
three parent lifetimes,24 exact terminal/reclaims,128 capacity cases and five
non-pipeline command regressions pass. Independent RECOVERY-01–06 acceptance is
pending. This closes the missing early-reader-composition input dependency only.

Additional [SI-07 authority/wake checks](evidence/sustained-controls-2026-09-29/README.md)
pass six real worker lifetimes, foreign-owner denial and actual idle/serial wake on
unchanged kernel bytes. They do not replace the blocked userland sustained contract.

SI-07 now has an [experimental serial implementation and concrete consumer dependency](NATIVE-INIT-COMMAND.md#current-si-07-integration-dependency--2026-09-25).
The kernel idle/wake/reuse/halt probe passes, but the real runner rejects generation
3 after two successful bytecount cycles. Userland's role-carrier, admission-result
and native-I/O decoders are pinned to generations 1/2. A versioned sustained
contract and rebuilt inputs are needed before completing SI-07 and sys-init's
independent consumption. No decoder was weakened here; current sibling bytes match
the frozen inputs. This is not a completed producer handoff.


[Verified SESSION consumer acceptance](evidence/session-acceptance-review-2026-09-25/README.md)
now closes the independent replay gate for the
[composed producer handoff](evidence/session-native-2026-09-25/README.md).
Userland accepts SESSION-01–06 for private AENMX007/ABI21 after 910 native cases,
115 Python/configured Rust/Zig checks and independent semantic controls. The
receipt binds the exact sealed producer; neither sibling nor prior evidence changed.

After recovery replay, the next dash step needs new userland-owned failed-exec,
scratch and real-serial composition bytes and oracles. Keep the accepted script/helper pins unchanged.
Shared SDK/runtime, full UL-007/M3/R1, TTY/general signals, persistent filesystem,
packages and sys-init assembly remain separate gates. SI-07 sustained sys-init is
an independent queued producer task and does not depend on SESSION acceptance.

[Serial forwarding evidence](evidence/shell-streams-2026-09-24/README.md) removes
script-specific capture buffers from AENMX006 stdio. Long stdout/stderr commands
before and after a parent pipeline pass; the host now rejects corrupted output
after successful guest cleanup. Final 105 capacity cases and 110 Python tests plus
Zig/Rust pass. This is a prerequisite, not a SESSION-01–06 delivery. The packet pins
userland’s composed-session proposal and unchanged inputs; the one-parent
repeated-job producer is now supplied above; consumer acceptance is now recorded above. Kernel/ABI, sibling repositories and released pins remain unchanged.

[Interactive pipeline evidence](evidence/pipeline-serial-2026-09-24/README.md) now
qualifies a real serial parent-created pipeline, returned prompt and builtin/exit
follow-up across three shell generations. AENMX006/ABI20 grants UART only to the
bootstrap owner; parent/copies retain scoped stream authority. All898 native checks
and host checks pass. This new private profile still needs consumer review; the
earlier12/12 script acceptance does not cover it. Compose accepted serial paths into
the shared SDK/runtime before claiming a full interactive filesystem shell.

[Parent-driven dash evidence](evidence/pipeline-parent-2026-09-24/README.md)
now runs unchanged pipeline.sh and early-reader.sh through actual parent main/jobs,
with unchanged helper bodies, inherited environment, scoped descriptors and child
collection. Both positives and five semantic controls pass in the101-case suite.
Final matching358 connections and431 runner cases also pass on287 runtime inputs;
all attempts and replay inputs are retained in the sealed packet. Userland independently accepted12/12 on2026-09-24 in its sealed
`docs/evidence/dash-parent-consumer-2026-09-24` receipt; the local
[receipt review](evidence/pipeline-serial-2026-09-24/consumer-review.json) records
that evidence. No sibling has been modified or accepted on its owner’s behalf.

The new profiles enable native public signal actions/copied dispositions. Older
copied-main packets only linked musl signal calls; their broader signal-operation
wording is narrowed here without changing sealed evidence. Exact scripts, expected
output, source snapshots, tools, artifacts and failed attempts belong to the packet.
The fixed helper/env/private owner is not a published SDK or an interactive shell.
Next close shared runtime/SDK integration and serial-shell
assembly. General signals/TTY, persistent storage/OpenZFS and package/init composition
remain separate R1 acceptance requirements.

[Retained exec replacement](evidence/pipeline-exec-state-2026-09-23/README.md)
now covers snapshot/freeze, admission/publication, grants and fragmented readiness.
All66 native cases pass, including basic exec under the old envelope; clients remain
unchanged. The outer driver is still sequential. Exec/I/O overlap and independent
consumer qualification remain next; no full-shell handoff is claimed.

[Private supervisor code capacity](evidence/pipeline-owner-budget-2026-09-23/README.md)
now qualifies AENMX005 at24 KiB while retaining004's16-KiB ceiling and the same
ABI19/grants. All65 native cases pass; all81 prior client/owner binaries are unchanged.
This is a private integration prerequisite, not a new consumer handoff or full dash.

[Resumable exec request handshake](evidence/pipeline-exec-progress-2026-09-22/README.md)
passes54 native cases and105 host tests. Partial request/reply state and canonical
rejection are qualified; the driver and later exec phases remain sequential.
Full exec/I/O overlap and independent consumer acceptance are still open.

[Exec transaction boundaries](evidence/pipeline-exec-boundaries-2026-09-15/README.md)
now separate bounded validation/admission/commit from blocking transport, preserving
cancellation and authority checks. All54 native cases and104 host checks pass.
This is an integration prerequisite; exec/I/O interleaving remains next.

[Direct wait dispatcher intake](evidence/pipeline-wait-probes-2026-09-15/README.md)
qualifies wait-any, live WNOHANG, scoped denial and once-only collection across
fragmented replies. All54 native cases and104 host checks pass; wrong errno and
recollection controls reject. Exec/I/O integration and interrupted wait recovery
remain open; this is not full-dash or independent consumer acceptance.

[Parent wait alongside I/O](evidence/pipeline-wait-io-2026-09-15/README.md)
now retains a live blocking wait while child I/O advances, with once-only collection
and partial replies. Final51 native cases and104 host checks pass; early zero
completion is rejected. Ten build/size attempts are preserved. Broader wait-state
qualification, exec multiplexing and independent consumer acceptance remain open.

[Autonomous pipeline children](evidence/pipeline-autonomous-2026-09-15/README.md)
now initiate I/O without a separate dispatch-release token. All49 native cases
and104 host checks pass; obsolete-token injection is rejected. Parent/peer release
and sequential owner phases remain; interleaving parent waits with child I/O is next.

[Copied-child dash builtin](evidence/pipeline-copied-builtin-2026-09-15/README.md)
now runs printf directly in the forked writer, preserving live FD ownership and
excluding writer replacement through per-slot admission counts. All47 native cases
and104 host checks pass; all66 prior images are identical. Coordinated execution/
data/wait handling is next; sequential owner phases and dispatch release remain.

[Actual dash builtin pipeline](evidence/pipeline-dash-builtin-2026-09-15/README.md)
now runs pinned printfcmd/flushall in the replacement writer, with exact output
and wrong-byte rejection. All45 native cases and104 host checks pass; all62 prior
images are identical. Direct copied-child builtin execution and coordinated
execution/data/wait remain next; this is not full shell or consumer acceptance.

[Child-requested pipeline exec](evidence/pipeline-exec-request-2026-09-15/README.md)
now initiates replacement through a private public-execve shim, verifies denied
request rollback and retries with live snapshots. Forty-three native cases and104
host checks pass. Owner handling remains sequential; actual dash builtin execution
and execution/data/wait scheduling remain open.

[Inherited stdin and stderr](evidence/pipeline-stdio-2026-09-15/README.md)
complete the bounded fixture's inherited standard-stream path: actual libc input/
EOF, independent output/diagnostic captures and checked closure. Forty-one native
cases and104 host checks pass; retained input authority and dropped diagnostics
are rejected. Actual dash scheduling and consumer intake remain open.

[Inherited pipeline stdout](evidence/pipeline-stdout-inherit-2026-09-15/README.md)
now carries parent-granted output through actual forks, validated exec/CLOEXEC
revocation and independent parent closure. Thirty-eight native cases and104 host
checks pass; deliberately retained writer authority is independently rejected.
Inherited stdin/stderr and actual dash execution remain open.

[Pipeline final stdout grant](evidence/pipeline-stdout-2026-09-15/README.md)
now carries actual libc output into an explicitly granted bounded capture; forged
caller, malformed grant and dropped-output controls are checked. Thirty-six native
cases and104 host checks pass. This is post-exec output authority, not full inherited
stdio or console integration; actual dash/child-driven execution remains open.

[Multi-child wait-any intake](evidence/pipeline-wait-any-2026-09-15/README.md)
now exercises musl wait3/wait4, live WNOHANG, scoped PID rejection and once-only
terminal collection. Thirty-three native cases and104 host checks pass. Early
false completion is rejected; the discovered channel backpressure defect is fixed.
Actual dash streams, child-driven execution and concurrent scheduling remain open.

[Interleaved pipeline construction](evidence/pipeline-interleave-2026-09-15/README.md)
now supports pipe creation and parent close between successive native forks, with
reduced live inheritance. Thirty-one native cases and 104 host checks pass; a false
close acknowledgment rejects before another copy. Actual dash wait-any, standard
streams, child-driven execution and unchanged scripts remain integration work.

[Client pipe creation and child collection](evidence/pipeline-parent-ops-2026-09-15/README.md)
now exercises two requested pipes, public parent close and musl waitpid backed by
observed terminal records. Twenty-nine native cases and 104 host checks pass;
repeat collection returns ECHILD and a false status is independently rejected.
Fixed owner phases remain; actual dash orchestration, unchanged consumer scripts
and independent intake are still open. No full-dash handoff is claimed.

[Live libc fork/exec snapshots](evidence/pipeline-live-fds-2026-09-15/README.md)
now capture actual fcntl-created aliases and exec flags through the shared facade.
Twenty-seven native cases and 104 host checks pass. Initial pipe grants and exec
scheduling remain fixture-controlled; actual dash pipe/fork/wait orchestration
and independent intake remain open.

[Public musl fork pipeline](evidence/pipeline-public-fork-2026-09-15/README.md)
now creates all three children through public fork with copied libc repair, then
runs the libc exec/I/O path. Twenty-five native cases and 104 host checks pass.
Actual dash-driven pipe/fork/wait orchestration and independent intake remain open;
this fixed-snapshot witness is not a full-dash handoff.

[Seven-binding libc replacement I/O](evidence/pipeline-libc-2026-09-15/README.md)
now uses the shared descriptor adapter and actual musl read/write/close after exec,
including dup2, CLOEXEC aliases and EOF. Twenty-three capacity cases, twenty-one
legacy pipe cases and 104 host checks pass. Actual dash multi-child orchestration,
copied libc rebind and independent intake remain open; no full-dash handoff yet.

[Interrupted pipeline exec cleanup](evidence/pipeline-exec-stop-2026-09-15/README.md)
now cancels parked-admission and partial-table schedules after exact participant
terminal observation, with three-generation reuse. Twenty-one native cases and
104 host checks pass. Actual libc/dash integration and independent intake remain
open; scheduled cancellation does not establish arbitrary lost-receipt recovery.

[Copied pipeline replacement exec](evidence/pipeline-exec-2026-09-15/README.md)
now passes distinct-image startup, atomic CLOEXEC holder removal and exact pipe
I/O through three generations. Eighteen native cases and 104 host checks pass.
Validated fixture tables do not install libc descriptors; interrupted-exec cleanup,
actual dash scripts and independent intake remain open. No new full-dash handoff.

[Native copied pipeline workers](evidence/pipeline-copy-2026-09-15/README.md)
now inherit both pipes through actual freeze/copy and complete three generations
with fifteen reclaims. Sixteen native cases and 104 host checks pass. This is a
private snapshot/copy fixture; replacement exec, libc descriptor installation,
unchanged dash scripts and independent consumer handoff remain open.

[Native early-reader EPIPE](evidence/pipeline-epipe-2026-09-15/README.md)
now passes explicit close and exit-with-holder schedules through both pipe stages,
including fragmented error replies and three-generation cleanup. Fourteen native
cases and 104 host checks pass. Actual dash fork/exec, SIGPIPE composition and
independent consumer intake remain open; this is private AENMX004 coverage.

[Interrupted pipeline writer cleanup](evidence/pipeline-stop-2026-09-15/README.md)
now preserves exact effects and EOF after confirmed stops at partial-request and
partial-reply boundaries, including three-generation reuse. Eleven native cases
and 104 host checks pass. Actual fork/exec pipelines, ordinary EPIPE delivery and
independent intake remain open; this is no new full-dash handoff or sibling change.

[Native two-pipe transport](evidence/pipeline-dispatch-2026-09-15/README.md)
now passes writer/relay/reader data and EOF with fragmented channel traffic across
three generations. Eight native capacity/dispatch cases and 104 host checks pass.
This verifies initially admitted workers; actual dash fork/exec, ordinary pipe
errors and interrupted-peer cleanup remain before full-dash handoff. No sibling
or public SDK contract was changed; STATE records the next action.

[Native pipeline capacity](evidence/pipeline-capacity-2026-09-15/README.md)
now runs five workers simultaneously through three lifetimes with ten scoped
channels, exact stop/reuse and fifteen reclaims. Actual musl PID calls exposed an
unused-register validation bug; that kernel check is corrected. The capacity
fixture and rejection controls pass, but the full-dash handoff remains open until
native multi-pipe dispatch and actual pipeline/early-reader qualification. No
sibling repository or released pin was changed; STATE records the next action.

[Seven-binding transition preparation](evidence/pipeline-descriptors-2026-09-15/README.md)
now validates descriptor counts and both objects' live holdings before publishing
local fork/exec changes. Failed second-object updates preserve the first object;
CLOEXEC filtering and exact readiness/terminal cleanup have host witnesses.
The 104 host checks and 21 existing native pipe regressions pass. This is private
adapter preparation; native multi-child dispatch and full matching consumer
qualification remain open. No sibling was edited. STATE records the next action.

[Two-pipe routing preparation](evidence/pipeline-routing-2026-09-15/README.md)
now separates equal-generation pipe references and validates their descriptor
bindings while retaining each object's participant authority. All 42 combined
Rust tests and 104 host tests pass; target compilation is recorded. This adapter
is not yet imported by a native profile. Seven-binding fork/exec integration,
larger native capacity and actual pipeline/early-reader qualification remain
before full-dash intake. No sibling or public SDK contract was changed; STATE
records the next action.

[Pipeline participant preparation](evidence/pipeline-participants-2026-09-15/README.md)
adds a bounded parent/three-child pipe core while preserving the existing
parent/one-child interface. All 34 Rust tests, 104 host tests and 358 existing
native connections cases pass. Four-participant native execution is not yet
wired: two-pipe routing, seven descriptor bindings and an opt-in larger worker
profile precede the unchanged pipeline/early-reader workloads. This does not
complete the full-dash handoff or unblock independent consumer intake. STATE
records the next action; no sibling or released pin was changed.

[Consumer substitution integration](evidence/dash-consumer-substitution-2026-09-15/README.md)
now passes unchanged substitution.sh and the real helper: quoted arguments and
environment survive exec; eight pipe bytes become the checked shell variable;
exact substitution ok newline and helper0/parent0/backend17 repeat twice with six
reclaims. All 358 connections cases and 104 host tests pass. Wrong arguments and
skipping the helper reject premature EOF with zero reclaims. This is bounded
producer coverage; multi-stage pipeline/early-reader, matching runner and
independent SDK/userland intake remain before full handoff. No sibling was edited;
persistence, package execution and sys-init R1 assembly remain separate work.

[Dash denied-redirection integration](evidence/dash-denied-redirection-2026-09-15/README.md)
now passes the unchanged consumer script: backend EACCES, child2/parent0/backend17
twice, exact denied ok newline and six reclaims. All 355 connections cases and
104 host tests pass. Wrong errno and missing stdout reject with zero reclaims.
This completes the bounded non-exec subshell denial path, not the public SDK or
full-dash handoff. Exact consumer substitution, pipeline and early-reader workloads,
matching runner and independent acceptance remain. No sibling was edited;
persistent filesystem, package and sys-init R1 assembly are separate work.

[Dash redirection integration](evidence/dash-redirection-2026-09-15/README.md)
now passes the unchanged redirection workload: duplicated writes, inherited file
readback, exact AB output, helper0/dash0/backend17 twice and six reclaims. All 352
connections cases and 104 host tests pass; all 671 older images are unchanged.
Lost-write, retained-stdin and skipped-helper controls reject explicitly.
Denied redirection, remaining consumer workload reconciliation, matching runner
and independent SDK/consumer acceptance remain before the next handoff. This is
volatile scratch producer evidence; persistence and R1 assembly remain separate.

[Dash scratch leak integration](evidence/dash-scratch-dispatch-2026-09-15/README.md)
now passes the unchanged fd-leak-control workload through actual fork/exec/wait:
helper95, dash22, empty stdout and six reclaims over two lifetimes. All348
connections cases and104 host tests pass; all661 pre-existing images are unchanged.
This producer evidence covers volatile scratch descriptor inheritance and cleanup.
Writable redirection/readback, matching command-runner evidence and independent
SDK/consumer acceptance remain open before a new handoff. No sibling was edited;
persistent filesystem and R1 assembly are separate work.

[Failed-exec producer evidence](evidence/failed-exec-native-2026-09-14/README.md)
now passes the unchanged missing127/denied126 script and five semantic controls,
with exact output, preserved rollback state and four real reclaims. All 322
connections and 431 runner cases match final sources/SDK/tools. Independent userland
intake and public SDK review remain open; the new source set supersedes prior
producer inputs for this workload. Writable descriptor/redirection workflows are
next. No sibling was edited and no persistent filesystem or R1 claim is made.

[Current bounded background-wait replay intake](evidence/suspend-runner-2026-09-14/README.md)
qualifies 431 command-runner and 316 connections cases on identical frozen
sources/SDK/tools. Actual unchanged dash wait.sh, both ordering controls,
stop/reuse, stale-parent isolation and failed-frame retry have producer evidence.
Restored runtime/support host checks pass. The earlier runner timeout remains
preserved; the completed retry closes the unmatched-suite gap.

Userland has already accepted 13 focused cases on the preceding stale-parent set.
The two new recovery controls, full matched replay and UL-081 SDK review remain
separate. The
handoff supplies pinned archives and commands, not stock-libc installation or
owner sign-off. Default termination during suspension, nested delivery and
eventual unblock remain gaps. Writable filesystem workflows, consumer integration
and release assembly remain open. Sibling repositories and released pins are
unchanged. Historical phase-one receipts below retain their original scope.

[DASH-fd-closure producer coverage](evidence/dash-consumer-closure-2026-09-13/README.md)
now runs the unchanged consumer script/helper through actual dash exec/wait, with
exact output, inherited-descriptor checks and cleanup. All 290 connections cases
pass; independent userland acceptance remains separate. The null dependency identified at that stage is now partially covered above;
the consumer leak control still needs writable /scratch.


The [corrected matched phase-one producer set](evidence/dash-phase-one-native-2026-09-13/README.md)
now passes431 command-runner and287 connections cases on identical sources/SDK.
It supersedes the original replay handoff's failing runtime source set with one
bounded code-size correction; use its new source archive and the original pinned
support/SDK archives. Startup/syntax now match argument/signal qualification.
Independent userland replay and UL-081 SDK boundary acceptance remain open.


The [phase-one replay handoff](evidence/dash-phase-one-handoff-2026-09-13/README.md)
pins the argument/signal producer set, archived SDK and missing replay support.
Restored host checks pass. Startup/syntax remain historical command-runner coverage
until that suite runs on the same final sources. Independent userland acceptance
and UL-081's supported SDK integration boundary remain open; no sibling was changed.

[DASH-signal-table and corrected consumer environment](evidence/dash-consumer-signal-2026-09-13/README.md)
now have producer evidence: actual substitution/USR1 trap, exact backend readback,
scope/dropped-post controls and six reclaims. Both argv and signal-table use the
manifest environment, with all287 connections cases passing. Next consolidate the
phase-one matched handoff for independent userland replay. No SDK or sibling
changes; remaining workloads and R1 filesystem/package/sys-init assembly stay open.

[Unchanged DASH-argv](evidence/dash-consumer-argv-2026-09-13/README.md) now passes
producer-side execution through real dash and the pinned userland helper, with
argument/environment preservation, independent backend output readback and six
reclaims. Three semantic controls and all 284 connections cases pass. No sibling
or SDK changes were made. Next qualify unchanged DASH-signal-table before the
adapter handoff; independent acceptance and the full consumer workload gate remain.

[Serial external substitution](evidence/pipe-exec-serial-2026-09-13/README.md) now
qualifies two externally executed substitutions in one serial shell and a clean
replacement shell, with six actual reclaims and second-generation rejection
controls. All280 connections regressions pass. Next qualify the unchanged
DASH-argv and DASH-signal-table inputs before an adapter handoff. This private
producer packet does not update the SDK or mark independent userland acceptance;
filesystem/package/sys-init R1 assembly and general pipelines remain open.

[Native external substitution](evidence/pipe-exec-native-2026-09-13/README.md) now
qualifies actual dash executing a separate writer ELF through an inherited pipe,
after denied admission preserves descriptors. CLOEXEC, pipe bytes/EOF, real wait
status and six reclaims pass with two controls and complete connections regressions.
This dedicated producer profile is not yet serial adoption or an installed SDK
delivery; independent consumer acceptance and general pipelines remain open.

The [pipe execution boundary](evidence/pipe-exec-boundary-2026-09-13/README.md)
adds host-checked five-binding CLOEXEC preparation and local pipe-holder commit.
Existing native regressions pass, but native executable replacement with live
pipes is not wired yet. This is not a new SDK delivery or consumer unblock.

[Interactive serial pipe substitution](evidence/dash-pipe-serial-2026-09-13/README.md)
now has bounded producer evidence for two substitutions entered at returned prompts
and a fresh second shell. The owner validates stdio bytes and EAGAIN handling; the
UART backend survives both sessions and its replacement lacks the grant. This is
separate from the serial exec profile: combined exec/pipe support, installed SDK
handoff, independent consumer acceptance and R1 assembly remain open.

[Repeated actual dash substitution](evidence/dash-pipe-repeat-2026-09-11/README.md)
now has producer evidence for two pipe/child generations within one shell, with
EOF/wait acknowledgment before retirement and reclaim. This is a bounded stream
backend profile, not a serial substitution or installed SDK handoff. Existing
serial exec/redirection evidence remains separate; independent userland acceptance
and combined consumer delivery are still required.

The [native pipe producer probe](evidence/pipe-native-2026-09-11/README.md) adds a
private copied-process FIFO/EOF experiment. Its packet distinguishes current run
status from installed SDK or independent userland acceptance. Public pipe/SIGPIPE,
actual dash substitution and release assembly remain separate work.

The [native SIGPIPE adapter](evidence/pipe-sigpipe-2026-09-11/README.md) records
selected real signal-delivery schedules for the private producer. This is not an
installed SDK handoff: public pipe(), serial-dash adoption and independent consumer
acceptance still need completion.

The [interrupted-create cleanup probe](evidence/pipe-reply-cleanup-2026-09-11/README.md)
extends this producer boundary with reply EOF, no descriptor publication or retry,
and terminal-based teardown across three real replacement lifetimes. This does
not unblock consumers on public pipe/SIGPIPE or actual dash substitution; matching
SDK/consumer integration and acceptance are still required.

Read-only checkpoint, 2026-09-11: userland now records independent serial-dash
qualification through resumed prompts and exit0/7 in its
[consumer packet](../userland/docs/evidence/dash-serial-consumer-2026-09-11/README.md).
This review did not rerun its tests. Its current STATE requests the completed
repeated-child delivery next; Aether has sealed repeated-child and builtin
redirection packets, while independent acceptance of those extensions remains
separate. The [pipe design](NATIVE-SHELL-STARTUP.md#bounded-pipe-and-command-substitution-contract--2026-09-11)
is a local implementation plan, not an installed SDK or a new shared standard.

[Serial dash producer evidence](evidence/dash-console-2026-09-11/README.md) adds an
explicit native input configuration for independent SDK/userland review. It proves
interactive command input and child stdin in a private kernel harness; it does not
install an SDK, change sibling contracts or establish sys-init/R1 assembly.

The [ordinary dash command producer handoff](evidence/dash-command-config-2026-09-11/README.md#sdk-and-userland-handoff) binds the explicit native fork configuration, private process adapters and matched QEMU evidence for UL-007 review. This is a producer candidate; independent SDK/userland acceptance remains separate.

The [BG-067 command producer handoff](NATIVE-INIT-COMMAND.md) specifies the real
runner/bytecount profile, frozen inputs, capacity limits and cleanup obligations
for sys-init adapter work. Current acceptance and next action remain in STATE.

> Update 2026-09-05: the [five-artifact v2 handoff](../pkg-mgr/docs/BOOT-HANDOFF-V2.md) now passes current target smoke and pixel validation. Earlier pair/mismatch descriptions below are historical evidence; the legacy adapter remains unchanged.

> Shared-standards migration, 2026-09-05: [Foundations adoption](STANDARDS.md) now routes the canonical shared ownership, interface and evidence rules. Domain mechanisms and exact implementation contracts below remain owned by this project. Shared-rule changes belong in a new standards release; adoption does not change implementation status.

Reviewed working files on 2026-09-05. This records Aether's integration direction,
not acceptance or implementation on behalf of the sibling repositories. Their
working trees are changing; repository HEAD alone does not identify reviewed
behavior. No sibling files were changed. The sys-init positive client was rebuilt
and booted against current Aether as recorded below; full companion test suites
were not rerun.

## Ownership

| Project | Owns | Does not obtain implicitly |
| --- | --- | --- |
| [Aether](../.planning/PROJECT.md) | Kernel objects, capability enforcement, image/launch contracts, instance lifetime, IPC, stop/quiescence/reclaim mechanisms; native filesystem engine/block contracts | Filesystem service/POSIX policy, service restart/ordering policy or package trust policy |
| [Aether-userland](../userland/.planning/PROJECT.md) | Operational Rust filesystem service, scoped client/handle and alias state, POSIX adaptation and shared UTC policy; maintainer assignment2026-10-18 | Ambient block authority, lifecycle policy or package installation/trust policy |
| [sys-init](../sys-init/.planning/PROJECT.md) | Init/bootstrap policy, supervision, dependency ordering, readiness, service definitions, diagnostics and recovery policy | Ambient root authority, POSIX process semantics, or a language choice from Aether's fixtures |
| [pkg-mgr](../pkg-mgr/docs/ARCHITECTURE.md) | Package build/staging, artifact and ownership evidence, package records, eventual install/update/remove and trust policy | Capability grants, service enablement, or permission to start/restart services |

Package dependency graphs, service dependency graphs, and native capability
relationships represent different facts. Installing bytes is not activation;
a package/service name or hash is not authority. Sys-init owns descriptor syntax
and lifecycle validation. Keep package artifacts and definitions inert until
separately authorized operations consume them.

Read-only package prerequisite check,2026-10-20: pkg-mgr's
[native package prerequisites](../pkg-mgr/docs/NATIVE-PACKAGE-PREREQUISITES.md)
still require directories/cwd/enumeration, exclusive creation, truncate/append,
mode/owner inspection, controlled cleanup and publication/persistence ordering,
plus loading programs from authorized filesystem objects. AF04's bounded data
transport does not supply those operations or native package admission. Its STATE
still cites the earlier October7 pool failure; current Aether recovery receipts
supersede that engine result only. No pkg-mgr acceptance, contract edit or native
installation is inferred, and no sibling files were changed by this inspection.

## What exists in the companions

**sys-init:** independently accepted bounded ABI-6 interrupt-time observation,
supervisor-launched helper transfer and whole-domain fail-closed shutdown in
[decision 0017](../sys-init/docs/decisions/0017-native-init-consumer.md), then
accepted [sequential reuse](../sys-init/docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
and a bounded service/dependent workload. Its current
[decision 0042](../sys-init/docs/decisions/0042-reconciliation-evidence-review.md)
selects confirmed-result mapping (BG-058); unknown-result reconciliation remains
unsupported. It has not requested a new kernel API for that local step. Production
clocks, arbitrary delegation, replacement supervisors and SMP recovery remain
separate. These are inspected owner records, not fresh QEMU results from this review.

**pkg-mgr:** its current [STATE](../pkg-mgr/.planning/STATE.md) reports host
zlib/zpipe builds, mode-aware package records, binary transport, explicit recovery,
update preflight and retained replacement in private staging roots. These results
were not rerun by Aether. Native target installation, service activation and a
current multi-module boot handoff are not established by those host results.
Its boot adapter still accepts the older kernel/protection pair described below.

## Concrete boot-handoff mismatch

pkg-mgr's [recorded handoff](../pkg-mgr/docs/AETHER-HANDOFF.md) and
[adapter](../pkg-mgr/mk/aether-boot.sh) accept a pinned kernel plus one
`protection.bin` module. Their retained two-core evidence is valid for that older
pair. It is not evidence that the same bundle works with today's image builder.

Aether now requires this ordered set from one matching build (updated after the separate SMP supervisor slice):

1. x86_64 kernel ELF.
2. Immutable `protection.bin` flat image, 1–4096 bytes.
3. Immutable `display.bin` flat image, 1–4096 bytes.
4. `lifecycle.bin`: the validated 32-byte v1 supervisor envelope plus 1–4096 code bytes.
5. Immutable `smp-supervisor.bin` flat image, 1–4096 bytes.

The current consumer invocation is:

```sh
python3 scripts/image.py KERNEL OUTPUT_ISO PROTECTION_BIN DISPLAY_BIN LIFECYCLE_BIN SMP_SUPERVISOR_BIN
python3 scripts/emulator.py smoke OUTPUT_ISO --cpus 2
```

The image builder includes the four modules in that order; the kernel requires four.
Default smoke requires `AETHER FAULT RECOVERY PASS` and actual Rust-rendered pixels.
Protection/display/SMP-supervisor remain fixed unversioned images; the lifecycle client uses
the explicit v1 profile. Neither is a general loader or package ABI. Artifact hashes must bind
all five matching inputs; hashes alone do not prove compatibility or provenance.
Do not silently source an unpinned display, lifecycle or SMP-supervisor image from a cache or accept the old
pair as current. Updating pkg-mgr's bundle/receipt/tests belongs in that project,
followed by a new consuming Aether smoke test. No such updated handoff is claimed.

## Native lifecycle seam and remaining companion work

The [implemented v1 conformance profile](../.planning/M4-LIFECYCLE-V1.md) now supplies a replaceable supervisor image, scoped bootstrap, instance identity, terminal retention/acknowledgment and bounded failure behavior. Aether's client and sys-init's actual positive client pass the fixed nine-cycle workload. Sys-init accepts this bounded subset in decision 0001; this is not acceptance of general or SMP supervision.

Preserve this accepted narrow interface while the internal SMP experiment evolves.
Align it with sys-init BG-032 (lifecycle), BG-033 (bootstrap/recovery), and BG-034
(native integration experiment). The smallest first consumer experiment can be
single-core and fixed-image, reusing M2 mechanisms without requiring POSIX or a
general loader. M4's final cross-core restart/display demonstration still remains
required; this is implementation ordering, not a reduction of that milestone.

The coordination checklist remains (v1 answers a bounded subset, with explicit exclusions):

| Checklist | Aether obligation for the bounded experiment |
| --- | --- |
| AR-01/02: bootstrap and launch | Explicit fixture ABI/version, image identity/layout, entry/configuration handoff, initial scoped grants, resource bounds, and rejection/cleanup outcomes |
| AR-03/04: identity and observation | Instance generation distinct from service name and holder-scoped handle; inspectable terminal reason/status with a defined retention/collection lifetime |
| AR-05/06: progress and stop | Poll/yield or notification semantics, honest watchdog/time limits, and forced-stop completion distinct from a cooperative service request |
| AR-07/08: reclaim and grants | Stop, mapping removal, reference invalidation and zeroing before reuse; explicit initial dependency grants and replacement semantics |
| AR-09/10/11: readiness, owner failure, quota | No queue-test readiness claim; explicit supervisor-death outcome and resource ownership; predictable quota exhaustion without partial launch |

The original M2 result values and destruction ordering are reference evidence.
V1 separates the supervisor image and retains a factory-owned terminal record
through destruction/release until acknowledgment; the task-local inspection
value still disappears when its task capability is invalidated. M3 static namespace
handles are not M2 generational handles. Do not export these differences as a
coherent lifecycle API without resolving and testing them.

Aether may keep conformance fixtures to exercise its mechanisms. Actual init
policy and its language remain sys-init-owned. A copied/renamed Rust test
supervisor is not sys-init integration. Resume the companion's dependent native
work only once the documented seam and target evidence exist and its own
experiment requirements are met; do not change its pause state on milestone
names alone. Supervisor recovery, service readiness and SMP cleanup must each
have explicit limits rather than inferred guarantees.

## Current sys-init client consumption

Rebuilt the current sibling source without modifying it, then booted its supplied
envelope on the current one-core Aether kernel:

```sh
python3 ../sys-init/scripts/build-lifecycle.py "$PWD/zig-out/sys-init-client"
zig build smoke -Dsmp=false -Dlifecycle-image="$PWD/zig-out/sys-init-client/pass.bin" -p zig-out/sys-init-current --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The client emits the expected completion accepted by `AETHER LIFECYCLE V1 PASS`;
all nine cycles complete. The source SHA-256 is
`e9c9fb8274e85cc594c8451053a95495de4fdcb164ba1434e661502bad0cbe65`;
the 2,512-byte envelope SHA-256 is
`cf7fbc9ab62c310428442ad419771506e1238b363a0f05a1293f7392d8120382`.
Generated evidence is under `zig-out/sys-init-current` and may be overwritten.
The companion's own negative-client results remain its separately retained
[evidence](../sys-init/docs/LIFECYCLE-V1.md); they were not rerun here.

Aether's [SMP supervisor experiment](../.planning/M4-SUPERVISOR.md) now uses its
own separate Rust image and discards a queued old-generation result after
owner-confirmed stop, before reclaim/replacement. The [fault recovery extension](../.planning/M4-FAULT-RECOVERY.md) adds five
generations, two #UD faults and retained reason/detail records. Its bootstrap and control
operations are a different fixture, not an extension of lifecycle v1 or sys-init
SMP acceptance. General rootfs installation, production init, readiness and
POSIX execution remain later contracts.

### Recovery accepted; failed-exec composition delivered — 2026-09-29

The [verified intake](evidence/failed-exec-session-2026-09-29/README.md) binds
450 independent userland evidence members to Aether's recovery producer seal.
RECOVERY-01–06 is accepted for the private scripted profile. Userland's next
failed-exec workload is now pinned locally; its owner-backed lookup integration
and semantic controls pass137 capacity cases; userland independent replay is next.
Scratch and serial compositions remain
separate. SI-07 still lacks complete versioned bootstrap/transport and rebuilt
runner/bytecount; isolated sustained decoder checks do not supply those binaries.

### Failed-exec independently accepted — 2026-09-29

The [local verified receipt](evidence/failed-exec-acceptance-review-2026-09-29/README.md)
closes the pending EXEC-SESSION-01–06 consumer replay for private AENMX007/ABI21.
All492 consumer members,300 source bindings and17 rebuilt owner hashes match.
Userland's137 capacity plus five legacy cases and123 host checks pass. This does
not supply the next scratch/serial compositions or SI-07 sustained binaries.
Those remain the inputs needed for the next kernel/runtime integration; no sibling
implementation or released pin is changed by this intake.

### SI-07 bounded kernel dependency complete — 2026-10-03

The [local completion review](evidence/si07-completion-review-2026-10-03/README.md)
closes Aether's original sustained idle/reuse/authorized-halt kernel backlog against
sealed producer and actual sys-init-owned useful-cycle evidence. It does not close
sys-init BG-067, userland SUSTAIN-01–06, production init or shared SDK acceptance.
Captured companion dispositions remain partial for those broader scopes. No
sibling file/task is changed. The next shared boundary is explicit sys-init/serial-
shell composition; bounded ABI22 command and ABI23 SESSION payloads cannot be
interchanged. Persistent filesystem and package policy retain their owners.

### Serial boot composition direction — 2026-10-03

The [source-backed review](evidence/serial-boot-contract-2026-10-03/README.md)
selects a bounded next experiment with one boot-owner domain, actual sys-init
policy and explicit SESSION dispatch responsibility. An ordinary worker cannot
inherit supervisor process/UART authority. Co-location retains a shared TCB/failure
domain; it does not assign the existing Aether fixture to another owner or prove
independent service containment. Userland’s bounded runtime closure currently
admits008 only; a new selected lifecycle profile needs explicit matching delivery
and native consumption. Next kernel work reuses observe/park/halt while retaining
SESSION IDs/quotas and old profile behavior. No sibling/ABI/pin/runtime edit or
independent sign-off is made by the design review.


ABI26 writable Rust service qualification2026-10-20: separate43-member candidate
passes twelve fresh guests,567 balanced waits, full file/recovery/media/export/
drain/cleanup; old candidates/pins remain. Implementation is authorized in Aether
and Aether-userland only; no sys-init/pkg-mgr/standards edits or messages. See
STATE for exact receipts and command-recording limitation. Maintainer approved
separate4KiB framing/length-checked retirement next; operational handoff and
persistent Zsh/packages/runner/ISO remain open.


## Checked filesystem-service lifetime producer handoff — 2026-10-20

The55-member AF04/ABI26 service now has matching7-image/12-guest9-mutation/96-request
producer evidence after a narrow kernel channel-copy fix. All fresh full-file/
namespace/media/export/drain/cleanup and5294 balanced wait gates pass at unchanged
limits; full757 host checkpoint and four legacy native channel guests pass. Six
old seals/SDK/pins and engine/controller pairs stay exact. Failures retained,
joined outputs disposed. [Result](evidence/fs-service-runtime-channel-fixed-native-2026-10-20.json).

Read-only reinspection finds no operational service delivery. The next userland
handoff must include exact executable/entry/dependencies/resources, authenticated
provisioning, generation-bound readiness, admission closure/drain/export/quiescence/
reclaim semantics and matched consuming evidence. Sys-init's persistent-boot intake
already identifies those boundaries; use its existing direct lifecycle path after
agreement. The relocatable candidate does not allocate a production service API.
Directories/metadata/persistent loading/packages/Zsh remain; no companion owner
sign-off or persistent ISO acceptance follows. No sys-init/pkg-mgr/standards edit
or message, SDK promotion or released-pin update.


The filesystem executable's consuming contract is now specified in
[NATIVE-C](NATIVE-C.md#launchable-filesystem-owner-and-sys-init-intake--2026-10-20).
Aether-userland owns its Rust main/fixed policy; Aether owns direct native engine/
provider composition; sys-init owns dependent admission and shutdown ordering.
Exact local build/intake coverage is in STATE, separate from owner acceptance.
The separately approved AENFS002/owner28 and AENFS003/owner29 now compose storage
and SESSION roles with qualified filesystem/process/recovery witnesses; old
profiles remain incompatible unless that explicit composition is selected.
STATE records exact inputs and bounds. Sys-init's new separate2072-byte ABI29
activation entry now passes Aether's pristine-reader/actual-activation guests,
with selected process1, clean engine exit,14 ordered reclaim boundaries and
quiescent halt. [Matched result](NATIVE-C.md#first-actual-sys-init-activation-result--2026-10-20).
This first slice is not its full shell/dispatch/PID/FD adaptation. Aether's
[read-only owner inspection](NATIVE-C.md#read-only-init-owner-inspection--2026-10-20)
checks exact ELF/raw/stack before assembly but cannot establish ABI or lifecycle
compatibility. Do not treat structural fit or conformance-controller success as
independent sys-init sign-off, a boot shell ISO or permission to auto-restart.
