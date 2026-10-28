# Change review outline

2026-10-23 UL-007/081/082 canonical root paths: requirement, authority/resource/
cleanup/simplicity review and test selection precede code in
[FS-ROOT-PATHS](../proposals/FS-ROOT-PATHS.md). Actual Client/Remote consume the
operation only under fs_paths; default APIs/wire and fields remain exact.52 host
tests, five compiling controls and native libraries pass; two harness failures
remain retained. No new unsafe boundary/dependency/permission or quota. Technical
review by implementation agent; independent/native/whole-owner review pending.
Current Python passes; unavailable minimum runner remains explicit missing coverage.
Maintainer writable-home policy does not grant system-root writes.

2026-10-22 UL-007/081/082 checked-disconnect integration: scoped pre-code review
and unsafe/resource/simplicity obligations are in sys-init decision0212 in this
system repository. The existing client closes immediately after ack; the new
exclusive callback permits real native export/channel verification first. It
keeps one source, all live-view guards, once-only raw closes and old APIs; no new
authority, wire, allocation, concurrency or limit. Test valid/malformed ack,
callback error/order/no replay, unsettled views and failed close receipts, with
a compiling callback-error omission. Native owner/stack/exec/readiness and actual
export acceptance remain open; source review is by the implementation agent,
independent reader/owner review pending. Root STATE/evidence own current results.

For contributors preparing experimental changes after UL-060. Copy into the UL
record before behavior work; replace prompts with actual facts, not approvals.

- Requirement/UL ID, exact source/plan identity, purpose and supported scope:
- Applicable standards clauses and affected owner/consumer contracts:
- Ownership, lifetime, authority, bounds, concurrency and failure/cleanup review:
- Language/compiler/flags, dependencies/provenance/licenses and resource budget:
- Test IDs, family/layer/stage, commands, tools/platform, deadlines and isolation:
- Independent success/denial oracles, fault controls and expected cleanup:
- Documentation surfaces changed, canonical references and inventory updates:
- Evidence for every attempt, expected/observed results, hashes and retention:
- Reused evidence identity/impact review; freshness and invalidation triggers:
- Missing coverage, defects, suppressions, risk, compensation and expiry:
- Actual technical reviewer and separate reader walkthrough evidence, or pending:
- Final scope, unresolved follow-on UL IDs and completion decision:


For substantial design changes, include the adopted simplicity questions here
(SE-01–05; local snapshot linked from PROCESS.md):

1. What is the simpler alternative?
2. Why is it insufficient for this requirement, or why are we choosing it?
3. What complexity can this change remove? "None now" is valid with a reason.

Name the current requirement and, when borrowing, the specific idea, needed
mechanisms and deferred scope. Assess responsibility, control flow, state,
failure/cleanup and whole-system cost, including protocols, dependencies and
operator steps. Reuse this record; routine small fixes need no separate document.
Do not trade away correctness, authority or bounds to reduce code or meet a metric.


## UL-082 namespace implementation review — 2026-10-19

Requirement and pre-code authority/resource/FFI/simplicity review are in
`docs/proposals/FS-SERVICE-TRANSPORT.md`, “Namespace service implementation contract”.
The new private variant composes existing policy/provider/transport; a generic VFS
or expanded replay API is unnecessary for the one-attempt requirement. It removes
no qualified compatibility profile. Explicit bootstrap identity/MUTATE_DIR,
all-connection remove-alias rejection and consuming retirement before response
keep mutable authority scoped. Old exported wire/entry remain separate variants.
No dependency/pin, memory, worker, I/O, transaction or watchdog increase.

Review performed by implementation agent, not independent owner/reader sign-off.
Actual-entry tests and five compiling semantic omissions pass; exact target object,
original C partial definitions and all18 controller variants pass. Original9
controller binaries are exact; new namespace controllers3020/3036/3020 bytes fit
4096 without writable statics. Original default/lifetimes regressions pass.
Clippy's internal nine-field FFI-entry arity exception is local and documented in
the proposal; unsafe policy/service code remains forbidden. Initial failures,
commands/hashes/short logs are retained by Aether, owned outputs disposed. Native
execution, independent consumer/reader, complete stack/peak memory, operational
mixed lifetimes/idle/executable/provisioning/readiness/shutdown and R1 remain open.
The old native-consumption checker is intentionally tied to its prior25-member
receipt; the new namespace candidate cannot inherit its native acceptance.


## UL-082 approved mixed lifetime implementation — 2026-10-19

Maintainer approved exactly8 total attempts (4 namespace/4 writes16), AFSRPC03,
rights15/trusted UID/GID1000 and success-only typed namespace0/service16 retirement.
The pre-code sequence/security/FFI/simplicity contract remains in the transport
proposal and Aether OPENZFS-FEASIBILITY. Implementation reuses the consumed-context
bridge and counter; it never resets failed history, replays an unknown result or
adds a generic VFS/journal. No qualified legacy path is removed. Root-only policy
refreshes all directory aliases after mutation; rename retains valid file handles;
remove rejects every live alias; write updates sizes and preserves original
state/errno/TXG even when0. This adds no kernel authority, clock policy or dependency.

New unsafe boundaries retain exclusive SPA/provider borrow, typed live context,
serialized access, consuming/null close and no unwinding; typed0/16 retirement
checks original sync/pin/graph/epoch history before reopen. Failure remains consumed.
Checker `python3 -B experiments/filesystem-service/check-namespace.py --mixed`
passes10 actual-entry tests/7 compiling semantic omissions, Clippy/rustfmt and
target72-byte ABI/import/export/object checks. Default namespace8/5 and old
default/eight-write service regressions pass unchanged. Every frame prefix, reply
loss prefix, close errors, cached-root/file aliases, aggregate exhaustion and
original failed progress are covered. Failures and command/tool/source hashes
are retained in Aether docs/evidence/fs-service-mixed-2026-10-19.json.

Exact41-member candidate seal e07aeeff522094d4994c90ec63ea68c6fb2ca2f6163d994c6e8a54a3f43181a9
is immutable. Object37c280c2f2d4dcb1f58990743d260c9f61426e795992bf5a9b35ea3832b3cb1d.
No released standards/SDK pin changes. Implementation-agent review only; independent
owner/reader acceptance, original-engine native matrix, operational idle/executable/
provisioning/readiness/shutdown and persistent Zsh/packages/ISO remain pending.
Static resource fitting is not full-stack/peak-memory evidence. Aether owns the
matched engine/retirement/block harness; sys-init retains activation policy.


## Fixed mixed producer consumption result — 2026-10-19

The sealed41-member candidate now passes matching Aether original-engine native
qualification on7 images admitted before12 fresh guests. Normal/partial/close
complete8 total attempts,795/805; lost-first-create788/798, empty p. Independent
original/new file/namespace/allocation/metadata/ACL/EOF/recovery/media/export/
drains/all cleanup pass. Writer31.15–48.21s<=60s6000/readers30s3000; controller<=4096,
observer7596/8192 and other limits fixed. Frozen inputs/old seals/baseline bytes
pass, all VMs join/owned outputs removed, no native failure/retry. Aether final
broad720-method checkpoint and pins/workflow pass. Receipt
`../Aether/docs/evidence/fs-service-mixed-native-2026-10-19.json`, SHA256
`8e925cb74fc6c1a7289006374a3afbb89e095019b874c17d430ccea90b5d5991`.
Producer evidence is separate from independent userland acceptance; no old sealed
OWNER/member bytes or checker pins were rewritten. Current finite8/16-byte/
64-request candidate has no operational executable/ABI/provisioning/idle/larger-
transfer/readiness/shutdown delivery. See Aether OPENZFS-FEASIBILITY's remaining
operational handoff. Those contracts, matching engine/profile composition and
init/runner/packages/Zsh/ISO remain UL-082/M3/R1 gates, not another write-count
matrix. Existing authorization allows scoped implementation here; new explicit
resource-ceiling changes still need their own maintainer decision. No change to
sys-init/pkg-mgr/standards, SDK/released pins or independent owner/reader sign-off.


## UL-082 mixed-wait transport implementation — 2026-10-20

Requirement and pre-code review are in FS-SERVICE-TRANSPORT, “ABI26 writable
primary-wait adoption”. Reuse existing service/frame/typed retirement logic with
one cfg-selected result-bearing direction-aware readiness hook. Void yield
cannot retain wait errors or endpoint direction. No new allocation, service
boundary, queue, dependency, grant, pointer ABI or limit. Old profiles and sealed
objects remain available for their known consumers; no broad refactor or pin
change. Wait0x24004 has scalar retained-holder input and no kernel buffer borrow;
existing transfer pointer/serialization/consume-close obligations remain.

Host13 actual-entry tests/11 compiling controls, both-direction short progress/
backpressure/spurious/error and committed-outcome/cleanup checks, strict Clippy/
rustfmt/native symbols/typed ABI pass. Existing mixed, namespace and default/
eight-write service selections pass. New43-member seal/object are in experiment
README. First header-format failure is retained in Aether's compact implementation
receipt; no native guest launched for that failure. Actual four waiting Aether
controllers4059/3020/4091/4059 fit4096, with all old23 bytes unchanged.

Implementation-agent review only; independent owner/reader acceptance and actual
native writable waits/recovery are pending. Operational executable/provisioning/
readiness/shutdown/larger transport/lifetime and persistent Zsh/packages/ISO are
UL-082 follow-ons. Static fitting is not peak-memory/full-stack assurance.


## ABI26 writable-wait producer result — 2026-10-20

Separate43-member candidate now passes Aether7-image/12-guest native matrix,
567 balanced primary wait/wake pairs (182/30/174/181), full original/final file,
namespace/allocation/metadata/ACL/time/EOF/media/guards/export/drains/all21 cleanup
and three terminal0/live0/reclaims3 per guest. Complete795/fresh805; lost-first-
create788/798/empty p. Controllers4059/3020/4091/4059<=4096, observer7596/8192;
all other limits fixed. Writers31.01–42.49s including post-run checks<=60s6000;
readers30s3000. Old candidates and baseline engine/controller exact, new writer
unchanged across isolated legacy metadata-position repair. SDK/Rust/service
inputs audited, joined generated outputs disposed. Host728 checkpoint plus final
six wait/three namespace bridge repair checks pass; unchanged results reused.

Producer receipt: ../Aether/docs/evidence/fs-service-mixed-wait-native-2026-10-20.json
SHA256 1f4625bbd014775f06dab230ea08f34ba15592a6f920bcf10a9bd3161ad181cf.
It is producer evidence, not independent userland/reader acceptance. Temporary
helper retained the wrong VM command filename; source-derived argv templates are
explicitly not captured commands, boot/tool observation has noted post-run limits.
The next data gate must capture native-qemu-command.json and emulator/boot hashes
before disposal. Independent/full E-01/release acceptance stays open. Old sealed
OWNER/member bytes remain capture-stage statements and are not rewritten.

Maintainer approved the separate4KiB data profile in Aether OPENZFS-FEASIBILITY.
Next implement AF04 header/body framing and length-checked success-only retirement
under unchanged other bounds; keep all qualified old profiles. Operational
executable/provisioning/readiness/shutdown/lifetime, directory/layout and POSIX/
runner/packages/Zsh ISO/R1 remain open. No new sibling edit/message authorization.


## UL-082 checked lifetime producer qualification — 2026-10-20

The separate55-member AF04/ABI26 aether_fs_runtime_run candidate now passes
Aether's7-image/12-guest native9-mutation/96-request matrix. Complete796/806 recovers
p8192 in two independent blocks; lost/partial788/798 recovers empty p. Full original/
new file/metadata/namespace/media/export/drain/cleanup and5294 balanced primary
waits pass. All engine/controller pairs and six older seals stay exact. The only
subsequent code change is Aether's narrow page-fragment channel-copy fix, qualified
by actual-body/four compiling omission checks, full757 host checkpoint and four
legacy native channel guests. Writer60s6000/readers30s3000, authority/memory and
all other limits unchanged. Initial timeouts, monitor launch/retention errors and
host implementation failures remain; generated outputs are disposed.

Producer receipt: [Aether native result](../../../docs/evidence/fs-service-runtime-channel-fixed-native-2026-10-20.json)
SHA256 695b1ee0a7bf537a6d42a976507dccce4b74ddd7fa83f7f799af4f5828c671a7.
This is finite producer evidence, not independent owner/reader acceptance or an
operational service. Keep UL-082/M3/R1 open. Next deliver the exact operational
executable/entry/resources/dependency/notice closure, authenticated block/dataset/
endpoint provisioning, generation-bound usable-namespace readiness and explicit
admission-close/drain/export/quiescence/reclaim contract. Sys-init's existing
persistent-boot intake requires those inputs before direct lifecycle wiring.
Preserve failed/uncertain outcomes; no reset/replay, new production service ABI
or shared PS adoption is inferred. Directories/layout/metadata/persistent loading,
runner/packages/Zsh/TTY and wider serial-session composition remain. No sys-init,
pkg-mgr or standards edit/message or SDK/released-pin change.


Review scope: implementation-agent producer review only, with no independent
sign-off. Checked counters preserve old profiles and permanent failure/epoch
semantics; no new Rust/C/unsafe change after sealing the runtime candidate.
The later kernel fix stays in Aether. Reuse unchanged actual-entry18/16 omission,
MAX/258-mutation/object/typed ABI/Clippy/format/legacy results; matching native
execution now supplies producer target evidence. Final local documentation/process
gate is selected for this handoff update; no unrelated host/native rerun.
The earlier pre-code simplicity/ownership/FFI review remains in the service
proposal and Aether OPENZFS-FEASIBILITY. No blanket standards/release conformance.


## UL-082 private activation preparation — 2026-10-20

Pre-code authority, ordering, failure/resource/FFI and simplicity review is in
FS-SERVICE-TRANSPORT and Aether OPENZFS-FEASIBILITY. Reuse the existing retained
ready bit rather than a control channel or supervisor framework. The wrapper
publishes after validated root and a checked userland UTC read, before the
64-byte greeting can block on a 32-byte queue. Failed publication never dispatches;
output failure latches, consuming teardown preserves both endpoint outcomes.
Exact live-instance observation is required even when a terminal bit stays set.
No new authority or time policy, heap/static, dependency, public ABI or PS adoption.

Selected focused checks pass: actual entry21/wrapper3, 21 compiling omissions,
strict host/native Rust and Clippy, C ABI/packed rejection/counters, existing
runtime18, three scalar consumer tests and three compiling consumer omissions.
Legacy non-bitcode bytes match; embedded LLVM bitcode differs, so no complete
object/LTO reproduction claim. The old sealed objects remain immutable inputs.
Initial missing-module/header-format/test/UTC-precondition issues and the
Rust-only legacy comparison are retained, not relabeled passes.

The actual 4,181-byte controller fails the unchanged 4 KiB linker ceiling.
A separate 8 KiB proposal is pending maintainer approval before any native
activation profile/admission. No native activation, operational executable,
shutdown, independent reviewer/reader, peak-memory or R1 acceptance is claimed.
The implementation agent performed this scoped review. Full native/host checkpoint
is deferred to the separately approved integration gate; no broad kernel changes.


## UL-082 activation qualification and package-name capacity stop — 2026-10-20

Exact58-member activation producer passes7-image/12-fresh-guest recovery matrix;
[qualified final-byte/host review](../../../docs/evidence/fs-activation-qualified-2026-10-20.json)
records the original EAGAIN assertion, bounded activation-only fixture repair,
semantic controls, unchanged old controllers and all output disposal. Owner source,
seals, released pins and current limits remain fixed. This is not independent
acceptance, operational executable or R1 completion.

Next package-path review identifies64-hex blob names versus the current16-byte
wire/mutation limit. The actual parser/policy rejects before effects. The separate
255/component510/rename proposal requires a maintainer decision; it reuses4096
scratch/framing, keeps all other workload/authority/memory/time/cleanup limits,
and changes no package format or sibling policy. Scope/tests/forbidden outcomes
are recorded in FS-SERVICE-TRANSPORT and Aether OPENZFS-FEASIBILITY. No code is
implemented without the decision. Operational entry/provisioning/shutdown,
directories/layout/metadata/loading/runner/packages/Zsh/sys-init remain.


## UL-082 approved separate name profile — implementation scope, 2026-10-20

Maintainer approved255-byte components/510 combined rename bytes. Requirement:
pkg-mgr needs64-hex blob names; the actual selected AF04 rejects them. Implement
separate fs_names/AFSRPC05/aether_fs_names_run with existing activation and9/96
native workload. Old code/seals/pins stay fixed; same4096 scratch reused, no new
memory/static/channel/authority/ABI26 operation or timeout. Complete padded name
body before effects; malformed framing consumes/stops, no reset/replay after
partial input, uncertain result or lost reply. Current owner/rights/epoch/token
and success-only retirement stay authoritative. Scope/schema/unsafe and test
selection are in Aether OPENZFS-FEASIBILITY approved section and transport proposal.
Actual entry/parser/policy/typed C mock, strict Rust/Clippy/format/ABI/object and
compiling omissions precede matched native fit/recovery. Missing target/independent
review stays missing; this does not close executable/provisioning/shutdown or R1.
Simplicity: reuse framed bodies instead of changing pkg format or building a name
broker. None of the old compatibility paths can be removed yet.


## UL-082 AF05 package-length producer qualified — 2026-10-20

Exact61-member AF05 now passes Aether's7-image/12-fresh-guest matrix on64-byte
names differing at the last byte. Full796/806 recover8192 bytes; lost/partial
788/798 empty, no replay. Original/new file/metadata/namespace/EOF/media/export/
drain/all cleanup and5473 balanced waits pass. Old seals/pins and baseline/
independent controllers stay exact; frozen inputs pass and owned trees disposed.
[Native receipt](../../../docs/evidence/fs-service-names-native-2026-10-20.json),
SHA25644125fdce33a0b06638e2a94e9ef281cfae768c0a3ab0c0ca48a83570353880d.
Entry29/wrapper3/26 omissions/legacy21/18/strict ABI and772 integration checks pass.
Every other resource/authority/workload/time/cleanup limit stays fixed. This is
producer evidence, not independent acceptance, operational executable or ISO.
Maximum255 is host/engine-contract coverage. The FFI still creates regular files
only and mutation policy is scoped to the provisioned root. Next operational
entry/resources/provisioning/shutdown and directory/hierarchy/layout/metadata/
loader/runner/package/Zsh/sys-init/TTY work remains; UL-082/M3/R1 stays open.
Do not reinterpret prior pending-native paragraphs as current STATE or lift any
bound from this result. No package-format workaround or RAM-only ISO.


## UL-082 delegated directories — 2026-10-20, implementation review

Requirement: package installation needs real directory hierarchies and mutations
relative to delegated parent handles. Aether's OPENZFS-FEASIBILITY operational
review defines the matching mkdir0700/empty-rmdir/directory-refresh C extension.
Implement separate fs_directories selection, retaining immutable AF05 and older
seals/pins. LOOKUP|MUTATE_DIR, trusted uid/gid and UTC remain mandatory. No raw
client object IDs, ambient path, widened rights, recursive deletion, symlink,
cross-directory rename, reset/replay or invented success. Refreshed parent
identity/type and every alias must agree; a mismatch permanently retires. Only
successful synced zero-staged namespace results may retire/reopen; context close
precedes reuse and original observer checks remain authoritative. Live directory
aliases prevent rmdir. Directory entry counts belong to the mutated parent,
never a refreshed unrelated root. Same name255/rename510/data4096, handles16,
sessions4, worker/channel/memory/time and9/96 native limits remain fixed.

Tests: actual policy+typed bridge nested create/write/rename/remove, mkdir/rmdir,
attenuation/peer/stale/alias/clock denial, corrupt refresh/result and failure/no
replay, strict no_std/unsafe/ABI/import/format checks. Native qualification must
separately prove real hierarchy, link/entry counts, ACL/metadata, complete file/
media, ordered export/drain and reclaim within fixed budgets. Host results are
not operational executable/sys-init or ISO acceptance. No published API or new
shared standard. Preserve failed receipts, remove owned generated outputs.

Simplicity: precreated directories cannot implement package mkdir/state/stage.
Reuse existing Owner tables and serialized bridge; add identity-checked refresh
and two typed mutations. No new service/allocator/path framework. Nothing removed
now because old consumers are still pinned. Real operational entry must propagate
service failures rather than fixture expected-error conversion. Admission close,
context/endpoints, ordered drain/export/block quiescence and native reclaim remain
separate obligations; an entry return does not discharge engine lifetime.


UL-082 directory implementation result:15 entry/3 wrapper/27 compiling omissions,
strict typed C/ABI/object/Clippy/format and18 legacy behavior tests pass. Scope is
AF06 plus exact67-member candidate, without old seal/pin changes. Active legacy
object bytes differ after source/panic-site changes; no byte-equality claim.
Aether785 checkpoint passes. First native preparation stopped before guests on
reader misclassification; actual requirements/map control and49 focused final
checks repair it. A fresh source-frozen complete native matrix remains required.
All finished host/first-preparation outputs disposed, compact failures retained.
The new namespace method shares the existing policy rather than duplicating it;
no new service/allocator/state table. Runtime/independent/R1 claims remain open.

### UL-082 kernel idle handoff status — 2026-10-20

Documentation-only reconciliation of Aether's exact native lifetime result and
remaining producer obligations. Sources/seals, authority and runtime unchanged;
no copied SDK, binary or evidence archive. STATE remains progress authority,
README/transport proposal route to it. Root794 host/159 Zig plus one approved
three-guest qualification are producer evidence; they are not independent
userland acceptance or an operational executable. Local quality/pin check selected
for these status edits; no repeated unchanged native suite.

### UL-082 launch owner before implementation — 2026-10-20

Requirement/authority/unsafe/cleanup/resource/test review is in Aether's
OPENZFS-FEASIBILITY, Launchable filesystem owner implementation review. One Rust
main consumes the existing AF06 producer and exact kernel-provisioned endpoints;
Aether owns engine/block calls. All limits/seals/pins stay fixed. A real failure
never becomes terminal0; startup closes unconsumed endpoints once, service owns
them after entry. Native stop/reclaim and independent disk recovery remain
separate from engine/export/provider/runtime flags. No sys-init/package policy
or generic framework. Simpler reuse of the test owner is unsafe because of its
expected-error normalization and fixed layout assertions. Reuse original calls
and typed ABI instead; retain old paths for existing consumers. Focused actual
Rust entry/FFI failures and semantic omissions, native object/typed header/strict
format/Clippy, actual C lifecycle/import stages, then resource-aware ELF link/intake.
No further120s attempt is authorized by the consumed one-off qualification.


### UL-082 launch owner implementation result — 2026-10-20

Implemented original BSD-2-Clause `launch-owner.rs` and typed host fault tests;
exact existing AF06 seal remains unchanged. Main imports the fixed trusted
provision, delegates native engine lifecycle to Aether and calls the actual sealed
entry. It preserves service failure/progress and separate cleanup stages; it does
not normalize negative fixture outcomes, infer readiness from entry or require a
fixed workload. Private borrow layout136/service72 is checked across C/Rust.
Read-only and many-request host cases, failed startup/endpoint ownership, invalid
bootstrap/context, false-zero/partial-cleanup/service errors and five compiling
omissions pass; the writer-close omission initially survived and exposed missing
test coverage, then failed after that case was added. Strict Rust1.98 native object,
Clippy, unsafe-operation lint and format pass. Aether links and checks the actual
ELF against its kernel parser, including the required TLS guard; its initial
embed-path and missing-TLS failures are retained. Native owner/sys-init and broad
uptime remain unrun coverage, not waived acceptance. Source remains in userland;
Aether's current sealed ELF is a dependency, not a per-run binary evidence bundle.

No shared/released pin, old library member, kernel grant or runtime quota changes.
The CLI/build and full bootstrap/partial-shutdown contract are maintained in Aether
NATIVE-C; userland README documents the owner and focused commands. No sys-init,
pkg-mgr or canonical standards modifications. Existing storage/SESSION composition
is explicitly rejected; a matched separate profile/resource budget and consuming
owner review are required. Metadata/promotion and persistent runner/packages/Zsh
remain active. The previous794-host/159-Zig kernel checkpoint is reused for unchanged
kernel/shared mechanism inputs after scoped review; affected owner/build/intake and
existing runtime/pair checks are selected here. Documentation adoption check remains
required; sandboxed first attempt could not create its owned build temp directory,
so the already-authorized sibling check is retried with the required sandbox access.


Final documentation adoption check passes: the authorized quality checker removes
its owned temporary process-test directory, then verifies Foundations25, Distribution30
and Experience14 pinned files/cases plus review snapshots/inventory. Runtime/source
reader/publication gates remain explicitly unrun. The linked ELF retains only the
original static-link LOCAL HIDDEN _DYNAMIC sentinel, not a dynamic loader/import.
No full archives or duplicate ELF directories remain. Further combined-profile
implementation waits for the explicit domain/channel/backing decision documented
in Aether; no existing runtime limit or released pin has changed.

## UL-082 private metadata binding review — 2026-10-21

Requirement: preserve the original engine's136-byte metadata record in Rust for
package inspection. The Aether-side plan is docs/OPENZFS-FEASIBILITY.md, section
“Metadata Rust binding and disk qualification plan”. This separate module does
not change AF06, existing sealed inputs, service rights, wire formats or defaults.

Apply O-01–05, I-01–06, E-01–07, CE/CR/TE and SE-01–05 through the existing local
process. Only an unsafe trusted engine owner can call read on a borrowed view and
resolved object/generation. No safe raw-object frontend, fabricated credentials,
partial error output, integer truncation, retained pointer/state or automatic
retry. Preserve high owner labels, special mode bits and signed seconds. Caller
retains/excludes conflicting SPA/view/dataset/property/export/teardown access.
The136-byte copied snapshot is not cross-call atomic or a POSIX stat contract.

No dependency or allocation is added. BSD-2-Clause original Rust, pinned1.98.0,
edition2024, warnings/unsafe-op warnings denied, no_std native panic=abort; host
Clippy/rustfmt plus actual C layout/error/edge-value and semantic omission tests.
Aether's separate read-only qualification retains30s/3000ticks,32MiB engine,
4KiB controller,3 generations/full file/media guards/21 cleanup boundaries.
Existing9-mutation/96-request service and all writer/authority limits stay fixed.

Simpler alternative: defer all metadata until a new wire variant. Insufficient
for qualifying this already-prepared engine prerequisite. Choose a small borrowed
module; no new protocol/owner/service/lifetime wrapper. None of the old sealed
paths can yet be removed. Client metadata adaptation, policy translation, chmod,
promotion, actual filesystem runner/Zsh/sys-init assembly remain separate work.

Run Aether tests/test_fs_metadata.py plus existing engine tests as relevant and
python3 -B docs/quality/check.py here. Freeze qualified inputs, retain all attempt
results/commands/tool hashes/short logs, remove owned generated output after joins.
Independent technical/reader acceptance remains pending; this record is a change
review, not owner sign-off, native acceptance or completion of UL-082/R1.

UL-082 metadata result2026-10-21: eight focused Aether host methods pass with
nine named compiling semantic omissions and two compiler negatives. Original
C/Rust layout/field/error controls, pinned Clippy/rustfmt and native object pass.
The separate Aether READ-only disk gate passes two metadata nodes/stale denial,
full file/hash/EOF, unchanged media and3 generations/21 cleanup boundaries;
generated outputs removed after VM join. Independent technical/reader acceptance
and metadata-capable operational service/backend/reply integration remain pending.
Aether STATE owns exact native/broad receipts; no duplicate binary/source archive.

## UL-007/081/082 ABI29 client candidate — 2026-10-21

Scoped pre-code review, exact contract and results are retained in
[the change evidence](../evidence/session-abi29-candidate-2026-10-21/review.md).
Explicit profile/framing and native identity observations avoid a numeric role
shift. Versioned startup symbols separate mixed application/runtime inputs.
New pure C17 decoder is strict/UBSan-tested with nine compiling semantic omissions;
retained inline-assembly runtime boundary receives native-object builds only.
Eight unchanged legacy object comparisons pass after retaining/fixing preparation
feature/header-order failures and an actual code-scheduling difference. Existing
legacy Boolean expressions remain intact. No new native link/fit/execution or
independent review is asserted; matched dispatcher, actual filesystem execution,
resource/lifetime and persistent shell/package/TTY acceptance remain open.

## UL-007/081/082 complete ABI29 client link — 2026-10-21

[Pre-code scope and assessment](../evidence/session-abi29-link-2026-10-21/review.md)
reuse the existing builder/runner/recipe, adding explicit four-compile selection
and actual45/8 link inventories. No kernel/supervisor policy or new builder stack.
Pinned runtime/musl fork/wait/rebind/helper builds and prebuilt CRT/libc/dash inputs
produce equal minimum/current ELFs; old ABI23/24 whole ELF identities remain.
Actual mixed links fail, resealed malformed recipes reject before effects, and
an omitted-memory link demonstrates why component admission remains mandatory.
Frozen kernel parser tests qualify initial73/24-page fit, not runtime/peak use.
The zero LOCAL HIDDEN _DYNAMIC sentinel is explicitly distinguished from a global
import/dynamic loader; an initial overly strict inspection and empty-directory
continuation failure remain preserved. Actual independent review remains pending.
Next filesystem FD/path/immutable loader and matched dispatcher/native witness
remain incomplete; no authority, lifetime, old seal or standards pin changes.

## UL-007/081/082 actual boot-parent correction — 2026-10-21

The [scoped pre-code review](../evidence/session-abi29-boot-parent-2026-10-21/review.md)
fixes a real consumer-discovered assumption: owner6 is generation0/PID7, rather
than14/21/28. Require7 and preserve supplied/native PPID equality, memory/PID,
roles/generations and copied-child parent validation. The actual old decoder
fails the positive regression; correction, denial/forgery controls and eleven
compiling guard omissions pass. Exact minimum/current linked clients and eight
legacy object pairs match; host parser/initial fit remains separate from native
execution/peak fit. New v2 seals preserve old incompatible inputs and evidence.
No kernel workaround, sibling code, new authority or lifecycle widening. Actual
independent consumer/native/reader review and full filesystem shell remain open.

## UL-007/081/082 read-only descriptions — 2026-10-21

[Scoped pre-code review](../evidence/filesystem-descriptors-2026-10-21/review.md)
implements a local descriptor/description split directly over the pinned actual
Owner rather than creating a backend/proxy framework. It requires one dedicated
context; it is not a live multi-client server wrapper. Independent/shared offsets,
capacity before effects, rights attenuation, error clearing, checked seek/read,
final alias close, per-FD cloexec and fail-stop cleanup have host controls. Native
generic-library type preparation is explicitly separate from executed/linked
runtime or peak-resource fit. First Clippy failure corrected without suppression;
all failures and subsequent semantic omissions retained. Actual AF07 transport,
fork/exec staging and native/independent acceptance remain incomplete. No old
source/seal, wire, supervisor, authority, lifetime or standards pin changes.

## UL-007/081/082 read-only AF07 client — 2026-10-21

Pre-code requirements, ownership/bounds/error/cleanup, test plan and simplicity
answers: [review](../evidence/filesystem-af07-client-2026-10-21/review.md). Reuse
existing sealed Channel/Framed/service; no alternate live Owner/SPA or changed
wire/authority/default/pin. Eleven host tests/eight compiling omissions pass
under actual minimum/current Python, strict Rust/Clippy/format and identical
native generic-library builds. No native execution/fit/security conformance.
Implementation-agent technical review only; independent reader/affected-owner
integration acceptance remains pending. Source-only delivery and retained failures
are in [evidence](../evidence/filesystem-af07-client-2026-10-21/README.md).
Next transport-backed shared FDs, process/path/binding/immutable exec contract and
matching sys-init/Aether native lifecycle. UL-007/081/082/M3/R1 remain incomplete.

## UL-007/081/082 shared transport-backed descriptions — 2026-10-21

[Pre-code review](../evidence/filesystem-remote-fds-2026-10-21/review.md) records
bounds/authority/error/cleanup and simplicity: one common algorithm for two actual
adapters, rather than two offset/lifetime implementations. Remote owns a fresh
client, creates no Owner/SPA and preserves both local close outcomes. Client abort
sends nothing; immutable old candidates/wires/pins stay fixed. Internal maintained
Failure::Policy becomes Source; original error identities remain exact.

Actual minimum/current Python client/local/remote12/12/8 tests and8/8/11 controls,
strict Rust/default Clippy/format and identical generic native libraries pass.
[Evidence](../evidence/filesystem-remote-fds-2026-10-21/README.md) retains initial
migration/unused-import failures and surviving zeroing omission before stronger
dirty-buffer assertions. No native execution/fit or invented review sign-off.
Implementation-agent technical review only. Authenticated process/path/binding,
fork/failed-exec/immutable image and full dispatcher/native acceptance remain
open in UL-007/081/082/M3/R1; independent owner/reader review still pending.

## UL-007/081/082 process descriptor views — 2026-10-21

[Pre-code review](../evidence/filesystem-process-fds-2026-10-21/review.md) covers
trusted after-admission/copy/settlement hooks,13 shared descriptions/four views,
exact keys/generation history, shared offsets/independent flags and all-view
last-close. Reuse pinned sys-init canonical identity code, existing AF07 client
and one descriptor algorithm. Canonical labels are not native authority; no
native admission/copy/reclaim or false failed-exec success. No old wire/pin/owner
or quota change. Source-only/native generic preparation needs concrete native fit.

18 process-profile/eight controls, local12/eight and remote8/eleven pass under
actual minimum/current Python; strict Rust/default Clippy/format and identical
per-suite native libraries pass. Initial extraction/test lint issues and strict
mutation-oracle attempts retained. Redundant epoch comparison removed in favor
of full stored-key equality; controls now test that real membership boundary.
Implementation-agent technical assessment only; independent owner/reader and
exact process/path/immutable exec/dispatcher/native acceptance remain pending.

## UL-007/081/082 AEFD0001 file RPC — 2026-10-21

[Pre-code review](../evidence/filesystem-fd-wire-2026-10-21/review.md) records distinct
file-only wire, trusted key binding, generation/sequence/header/body validation,
caller-owned workspace and pending reply/Drop/no-replay ownership. All opcodes
validate current process before effects/replies; persistent pending state covers
forgotten guards. No old bootstrap/console/pipe/exec frames or native profile changed.
The actual C codec is pure encoding/validation, not authority or native transport.

9 host/eight semantic omissions, C/Rust exchanges10, C header corruptions80/body
boundaries and borrow controls pass on actual minimum/current Python. Current
process18/eight rerun; strict Rust/Clippy/format/C17/UBSan and identical generic
native/wire bytes pass. Source v1 stale-unsupported defect remains superseded;
v2 corrected runtime and v3 expanded qualification remain separately sealed.
All setup/mutation-target failures and preceding guard versions retained. Review
by implementing agent only; affected-owner/reader, facade/native fit/authentication/
copy/immutable exec and full UL-007/081/082/M3/R1 remain incomplete.


## UL-007/081/082 C file-client transport — 2026-10-21

[Plan/review](../evidence/filesystem-fd-client-2026-10-21/review.md) covers trusted
C callback authority/lifetimes, short transfers/waits, bounded whole exchange,
exact shapes, sequence, complete output publication and once-only raw retirement.
Abort clears/releases borrowed storage before calling external cleanup. No libc
interposition, shell wire selection, native generation/quota or sibling change.

Minimum/current Python each pass1631 schedules/seven assertion-specific omissions,
strict C17/format/UBSan; exact prior wire exchanges and pinned host inputs retained.
Initial mutation-target mismatch and minimum missing-lzma setup preserved; plain
fixture copies retain original hashes. Implementing-agent technical review only;
independent owner/reader, actual facade/dispatcher selection, native fit/execution
and immutable exec/failed-exec remain open. Full UL/M3/R1 not complete.


## UL-007/081/082 typed file facade/live host exchange — 2026-10-21

[Plan/review](../evidence/filesystem-fd-facade-2026-10-21/review.md) records typed
private-errno C operations, unchanged caller output on failed/short read, trusted
C lifetimes and explicit file-only context. Actual host pipes connect the selected
C transport to the real unchanged Rust handler/process/AF07 policy with synthetic
storage; observed C child exit and source/request/cleanup counters are independent
oracles. No libc interposition, native engine/endpoint or shell route selection.

Minimum/current each pass74 live cases/six compiling semantic omissions, strict
Rust/Clippy/format/unsafe denial and C17 diagnostics/format/UBSan. Module-path
preparation error and explicit EOF backend-count oracle correction retained.
Source/runtime dependencies unchanged; independent owner/reader, matched shell
FD routing/dispatcher/native copy/immutable exec and full fit/runtime acceptance
remain open. Implementing-agent technical review only; UL/M3/R1 not complete.


## UL-007/081/082 tagged startup FD proposal — 2026-10-21

[Plan/review](../evidence/filesystem-fd-bindings-2026-10-21/review.md) covers the
file3/pipe3 collision, proposed fixed tagged snapshot, output publication, shape/
generation/uniqueness rules and pure class-preserving immutable lookup. Reuse
existing word codec/table geometry; no native authority, I/O/lifecycle, extra live
ledger, selected shell profile or sys-init implementation/API acceptance.

Minimum/current each pass65951 host cases/five compiling assertion-specific
omissions, C17 strict warnings/format/UBSan; all exact inputs/attempts retained.
Existing facade/live-service evidence reused only for unchanged original scope.
Implementing-agent technical review only; consuming-owner/reader reconciliation,
actual shell table/routing/mutations, native copy/failed-exec/immutable exec and
complete fit/dispatcher/runtime acceptance remain open. Full UL/M3/R1 incomplete.


## UL-007/081/082 tagged read dispatcher — 2026-10-21

[Plan/review](../evidence/filesystem-fd-routing-2026-10-21/review.md) covers borrowed
immutable table, source-class dispatch/no fallback, private workspace publication,
known semantic versus unknown stream results and file-only local retirement.
Actual stream/native settlement and authority remain trusted owner obligations.
No new live FD ledger, selected shell/mutations or native API change.

Minimum/current pass74 live host file-path cases/13 synthetic stream modes per
child/six assertion-specific compiling omissions; strict C17/UBSan/format and
unchanged Rust/Clippy/unsafe checks. Initial fixture strict assertion diagnostics
retained/corrected without suppressions or runtime-policy changes. Independent
owner/reader, selected startup/table/actual streams/mutations, native copy/failed
exec/immutable admission and full fit/dispatcher/runtime remain open.

Final routing receipt review corrected a checker flag initialized before live
launch; failed compile actually executed no live server. Preserved original record
and explicit disposition, reran both interpreters, kept production/candidate bytes
unchanged. Evidence summary selects final corrected-checker runs.


## UL-007/081/082 tagged table file operations — 2026-10-21

[Plan/review](../evidence/filesystem-fd-table-2026-10-21/review.md) covers one-map
logical/source allocation, true duplicate/final-close semantics, confirmed flag/
close commits, unknown-result preservation and conflicting-selector retirement
without unsafe rollback. No extra ledger/native authority or successful stream
no-op. Logical seek and local dup-full boundary added before final qualification.

Minimum/current pass269 live C/Rust host cases/six assertion-specific omissions;
strict C17/UBSan/format and Rust/Clippy/unsafe checks. All six passing runs across three scope stages
and intentional failures retained. Implementing-agent review only; independent
owner/reader, selected startup/shell, actual streams/mutations, native copy/failed
exec/immutable image authority and full fit/dispatcher/runtime acceptance open.


## UL-007/081/082 mixed stream aliases and observed close — 2026-10-21

[Plan/review](../evidence/filesystem-fd-streams-2026-10-21/review.md) covers one-map
stream aliases, independent C cloexec flags, class-aware final-close scan and
explicit complete/consumed/status outcomes. Known consumed error clears metadata;
unknown retires file admission with no inferred stream cleanup or replay. File
entries delegate to the unchanged source policy. No native grant duplication,
pipe creation/write, destructive exec, source/profile/SDK or sibling change.

Minimum/current each pass269 live C/Rust file cases/fourteen host pipe/completion
scenarios per child/six compiling omissions; strict C17/format/UBSan and unchanged
Rust/Clippy/format/unsafe checks. Initial control diagnostic mismatch retained;
checker-only correction followed by both interpreter reruns. Implementing-agent
technical review only. Owner/reader, actual native adapters and selected startup/
shell, native copy/failed exec/immutable image authority and whole fit/dispatcher/
runtime acceptance remain open; full UL/M3/R1 incomplete.


## UL-007/081/082 tagged stream output — 2026-10-21

[Plan/review](../evidence/filesystem-fd-write-2026-10-21/review.md) covers explicit
class dispatch, read-only file rejection, staged const input, known short/zero/
error progress and unknown physical output without replay. Same map/workspace;
no new table, runtime dependency, native grant, retry loop, pipe creation, wire
opcode or selected shell. Actual stream deadlines/cleanup stay owner-managed.

Minimum/current each pass18 output+unchanged14 stream scenarios per child,
269 live C/Rust file cases/six assertion-specific compiling omissions; strict
C17/format/UBSan and unchanged Rust/Clippy/format/unsafe checks. Earlier successful
scope retained; final fixture adds healthy-error continuation and precise stale
retirement control. Implementing-agent technical review only; owner/reader, actual
native adapters/selected shell, copy/failed exec/immutable image authority and
complete dispatcher/fit/runtime remain open. Full UL/M3/R1 incomplete.


## UL-007/081/082 paired pipe publication — 2026-10-21

[Plan/review](../evidence/filesystem-fd-pipe-2026-10-21/review.md) covers two-slot
preflight, actual source observation, ordered unused pair validation, class-aware
collision checks and paired map/output publication. Known errors preserve live
admission; unknown/collision preserves state and retires without retry/unsafe
rollback. No new ledger, source authority, wire opcode or native generation reset.

Minimum/current each pass22 creation+unchanged18 output/14 lifetime scenarios per
child,269 live C/Rust file cases/six compiling omissions; strict C17/format/UBSan
and Rust/Clippy/format/unsafe checks. Three prior passing19-case attempts and one
preparation-script failure disposition retained. Implementing-agent review only;
actual native adapters, coherent shell/startup/table/redirection, owner/reader,
copy/failed exec/immutable image authority and complete fit/dispatcher/runtime
remain open; full UL/M3/R1 incomplete. No sibling change or native readiness claim.


## UL-007/081/082 chosen-target stream replacement — 2026-10-21

[Plan/review](../evidence/filesystem-fd-replace-2026-10-21/review.md) covers stream
redirection, self/distinct flags, full-table aliasing and close outcome publication.
FILE crossings reject before effects; known consumed error leaves a hole, unknown
preserves map/retired admission. This is an explicit subset, not atomic POSIX dup2.
No extra ledger, native grant, temporary remote FD or new runtime dependency.

Minimum/current each pass19 replacement+unchanged22 creation/18 output/14 lifetime
scenarios per child,269 live file cases/six compiling omissions; strict C17/format/
UBSan and Rust/Clippy/format/unsafe checks. Initial18-case passing scope retained;
non-mutating patch-context failure recorded, final reruns select strengthened tests.
Implementing-agent review only; FILE/full replacement, actual native adapters,
selected shell/startup, owner/reader, copy/failed exec/immutable image authority and
full fit/dispatcher/runtime remain open. Full UL/M3/R1 incomplete.


## UL-007/081/082 descriptor integration batch — 2026-10-21

[Plan/review](../evidence/filesystem-fd-session-2026-10-21/review.md) groups startup,
one-context operations/flags/seek, inert full/cloexec projection and terminal cached
finish reporting. Borrow one map/client; no second ledger or native settlement
claim. Invalid startup publishes nothing; unknown stops close replay, both raw
transport errors and known leftovers remain visible. FILE replacement still -38.

Minimum/current each pass15 integrated+73 predecessor host scenarios per child,
269 live file cases/eight assertion-specific controls. Strict C17/format/UBSan and
Rust/Clippy/format/unsafe checks. Eight freestanding ELF x86-64 objects/relocatable
link,217 pinned header inputs, four explicit memory imports/41 static frames/max264
qualify build only. Two failures (mutation match/import expectation) plus earlier
six-control passes retained. Saved receipt/cache/seek controls strengthened before
final reruns. Consolidated repetitive README/architecture intros; module/evidence
contracts remain. Implementing-agent review only; owner/reader/full FILE/native
adapter/selected shell/copy/immutable/whole-fit/dispatcher/runtime gates stay open.


## UL-007/081/082 source-backed file/stream redirection batch — 2026-10-21

[Plan/review](../evidence/filesystem-fd-redirect-2026-10-21/review.md) groups actual
remote prepare, all-class target close/publication, rollback, unresolved receipts
and session entry. No new wire/Rust source policy/ledger; known failures clean only
confirmed fresh descriptors while live, unknown/collision never replay/rollback.
Remote capacity and consumed-target-hole limits are explicit; not atomic dup2.

Minimum/current pass482 live C/Rust cases+88 prior host scenarios per child/eight
compiling omissions;192 lost reply headers span all phases. Strict C17/UBSan/format
and Rust/Clippy/unsafe checks. Nine x86-64 objects/relocatable link,43 static frames/
max264 and exact217-header prior pin are build evidence only. Three passing attempts
retained; final checker strengthens header-set equality, production unchanged.
Implementing-agent review only; owner/reader, native adapters/linked shell/startup,
immutable copy/exec/failed-exec/full fit/dispatcher/runtime remain open, UL/M3/R1
incomplete. Prior stream-only replace API remains backward-compatible.

## UL-007/081/082 native descriptor adapter batch — 2026-10-22

[Pre-code plan and technical review](../evidence/filesystem-fd-native-2026-10-22/review.md)
groups native channel/stream/pipe adapters, generation history, once-only transport
close and whole-operation signal mask. No startup wire, greeting consumer, runtime
dependency or second logical ledger. Unknown source effects remain explicit; native
wait duration/settlement and coherent shell/owner composition remain unqualified.

Actual minimum/current Python qualification and preserved attempts are linked from
[the evidence](../evidence/filesystem-fd-native-2026-10-22/README.md). Implementing-
agent review only; independent owner/reader and full UL/M3/R1 gates remain open.

## UL-007/081/082 placed descriptor context batch — 2026-10-22

[Pre-code plan/review](../evidence/filesystem-fd-context-2026-10-22/review.md) groups
startup table/source cross-validation, context/workspace borrows, every-operation
masking and cached terminal reporting. Reuse exact native48/session/redirection
algorithms; no new wire, greeting, libc interposition or second logical ledger.
Negative controls drove removal of a redundant source check; missing/orphan cases
now test both directions of the single presence comparison. Full native startup/
shell/copy/immutable/failed-exec/placement/dispatcher integration remains open.

Actual qualification and retained failed/passing attempts are in
[the evidence](../evidence/filesystem-fd-context-2026-10-22/README.md). Implementing-
agent technical review only, independent owner/reader pending. Full UL/M3/R1 open.

## UL-007/081/082 single-consumer startup batch — 2026-10-22

[Pre-code plan/review](../evidence/filesystem-fd-startup-2026-10-22/review.md) groups
explicit304-byte owner proposal, native identity observations, sole consumer,
context admission/publication and terminal raw channel cleanup. Reuses pinned
identity/context/native implementations; no fallback/greeting competitor, shell
selection, allocation, new source authority or second logical table. Early16-byte
header rejection avoids waiting for an incompatible producer's nonexistent body.

[Evidence](../evidence/filesystem-fd-startup-2026-10-22/README.md) retains actual
minimum/current qualification and all attempts. Implementing-agent technical review
only; owner proposal acceptance/reader/full linked shell/copy/immutable/fit/native
integration remain open. Full UL/M3/R1 not complete; no sibling implementation.

## UL-007/081/082 libc FD / complete-shell link boundary — 2026-10-22

[Plan/review](../evidence/filesystem-fd-libc-2026-10-22/review.md) groups actual FD
symbols/hook, errno/variadic/bounds behavior, BSS startup context, old32-byte wait
and terminal exit/application entry. Public dup2 remains explicitly unsupported;
structured receipt redirect does not imply atomic POSIX replacement. Complete
pinned dash/public-fork link isolates only __aether_fork_stage. A matching128-map
native descriptor-copy/child-rebind transaction is absent; no fallback or stub.

[Evidence](../evidence/filesystem-fd-libc-2026-10-22/README.md) retains all attempts,
actual current/minimum qualification and concrete linker block. Implementing-agent
review only; owner/reader/native/full fit/UL/M3/R1 remain incomplete. Expected link
failure is a scoped boundary observation, not a passing complete-shell build.

## UL-007/081/082 tagged fork owner-status recheck — 2026-10-22

Documentation-only refinement after sys-init Decision0201. Read-only source hashes
and actual implementing-agent review are in docs/evidence/tagged-fork-owner-status-2026-10-22/.
Current kernel copy clears parent frozen before the library's required frozen
local-clone window completes. BG-069 agreement/BG-070 implementation are still
needed; no wire/precondition/child transition is selected here. No runtime or
source pins change; prior evidence is preserved. Risk is overstating readiness:
STATE explicitly retains exact fork-stage/full-native block. Applicable I-01/I-03,
E-04/E-05/E-08 and documentation/testing evidence clauses. Quality and diff checks
recorded with this review; affected runtime tests unnecessary for prose-only work.
Owner agreement and independent reader review remain pending; no UL completion.

## UL-007/081/082 serialized file inheritance v1 — 2026-10-22 plan

Requirement: resolve userland's local frozen-parent composition obstacle identified
by sys-init0201/BG-069 without selecting sys-init's wire or native dispatcher.
Add a separate versioned synchronous copy callback API to ProcessFiles: exclusive
mutable ownership spans preflight, callback and local clone. Existing frozen
inherited_child contract remains unchanged. Native authority/token/channel/stream
exclusion and matching child transition remain dispatcher obligations; labels do
not authorize copy. Source remains one AF07 ledger; no new fields/heap/handles.
Before callback validate parent/target/generation/capacity. Confirmed observation
must match reserved target and actual parent. Known refusal preserves file state;
unknown, unexpected confirmed child or callback unwind retires admission without
claiming native settlement. Guard Drop closes the uncertainty gap on host unwind.

Simpler alternative: relax the existing method's frozen precondition in prose.
Insufficient: callers could interleave FD mutations between copy and local clone.
Borrow Rust's existing exclusive ownership for this bounded local sequence; shared
validation avoids duplicate clone policy. No generic transaction framework, kernel
change, extra ledger or accepted path removal. Independent owner agreement pending.

Tests planned: actual Rust service/ProcessFiles fixture schedules queued parent
close/open/flags/read after copy; shared offsets/last close, all child slots/full
FD capacity, preflight no callback, refusal preserves parent/generation, unknown
and mismatched confirmation retire without replay, panic guard. Compile-fail
callback reentry proves borrow exclusion (not native synchronization). Retain old
18 tests/eight controls; add semantic omissions for retirement/target validation.
Strict Rust2021, rustfmt/default Clippy/-Funsafe-code, host tests and generic
x86_64-unknown-none rlib. No native/link claim. Actual minimum/current Python on
checker, local quality and whitespace. Preserve every attempt and pin sources,
tools and dependencies before execution; no sibling edits/messages. Evidence and
follow-ons recorded before any completion claim. Owner/reader review pending.

Actual review/results:26 process-profile host tests/ten compiling semantic omissions
and actual borrow-reentry compile rejection pass on Python3.14.7/3.10.21. Initial
passing internal-only qualifications omitted visibility of callback/result types;
review found the private-module export gap. Added explicit re-exports and external
no_std host/target consumers; both final qualifications pass matching sources.
Strict Rust2021/rustfmt/default Clippy/unsafe denial and generic native rlib pass.
Queued parent close/reopen applies after publication, shares retained descriptions
without retargeting child bindings. Refusal consumes no generation; unknown,
unexpected confirmation and unwind close admission with no fake native settlement.
No native synchronization, target monomorphized size/stack/fit or complete link
claim. Old process/libc evidence and source candidates verify unchanged. Evidence:
docs/evidence/filesystem-serialized-copy-2026-10-22/. Owner agreement/full staging/
child transition and independent reader remain pending; UL/M3/R1 remain open.

## UL-007/081/082 AEFORK01 frame qualification — 2026-10-22 plan

Aether now selects unchanged native copy plus serialized owner admission and
proposes exact304/32-byte frames. Implement only pure userland encode/validate,
sequence exhaustion and parent/ready correlation, with no new opcode, native call,
context reset or selected dispatcher. Pin exact Aether contract excerpt before
implementation. Existing startup identity/map/native-source validators provide
body checks; no duplicate file/source policy or ledger. Caller owns immutable
capture under the whole guard, authenticated endpoints, sequence lifetime and
unknown no-replay. Syntax/labels do not grant authority or prove child readiness.

Tests: all prefixes/extra sizes, each header/reserved byte, identity/native
observation mismatch, map/source/history correspondence, cloexec preservation,
sequence0/stale/wrap/exhaustion, parent native-return/owner disposition agreement,
private errno and canonical child PID boundaries, ready magic/sequence/PID/tail,
output preservation/clearing and deterministic byte fixtures. Strict C17/format/
UBSan, target freestanding object/import/stack-frame inspection; no native or
complete-shell execution. Actual minimum/current Python and pinned tool/dependency/
header closure, bounded owned execution and retained failed/passing attempts.

Simplicity: a successful fork stub is insufficient; a generic framing/transport
framework is unnecessary. Reuse existing validators and small plain C functions,
with caller-supplied304/32 buffers and a single monotonic counter. No allocation,
second context/ledger or old API removal. Native grant/auxv repair, armed child
constructor/stage, stream gate and matching sys-init wire/transaction remain open.
No sibling edit/message or affected-owner acceptance is authorized or inferred.

Actual implementation review/results:5847 pure C boundary cases/eight compiling
omissions pass on final minimum/current interpreters. Two earlier5099/six passes
predate child correspondence; one expanded attempt failed when an omission
survived malformed-only coverage. Added valid changed-cloexec/file-selector/extra-
FD cases, preserving production checks. Exact source-label equality is a proposed
owner relationship, not authority. Pure frame checks do not construct a context,
repair TLS/auxv, allocate grants or prove native readiness. All attempts/checker/
source/tool/process logs retained. C17/format/UBSan and target two-object ELF64
relocatable link/imports/static frames pass. Independent owner/reader, armed stage/
constructor, matching sys-init selection/composition/full native/UL gates pending.

## UL-007/081/082 armed fork stage/child constructor — 2026-10-22 plan

User explicitly requests armed stage/constructor through next concrete block.
Read current Aether ordering/rebind contract and pinned copy_rebind source. Add
one opt-in aggregate containing the existing single boot object plus compact arm
metadata. Reuse boot scratch304 for parent request/child greeting and child's own
workspace prefix for inert retained request after quarantine; no second ledger,
allocator or automatic4096/304-byte frame. Keep old startup API/bytes and default
bindings; conditional fork bindings use the new aggregate. One arm/sequence per
parent channel generation; only shell1 can originate. Whole context guard covers
live snapshot/send/park/correlated parent disposition. Known refusal preserves
parent state; unknown no replay/fail-stop. Child quarantines inherited context
before callbacks, validates actual grants/PID/PPID and pinned TLS/auxv rebind, then
reads one fresh greeting, validates exact fork correspondence and reconstructs
private pointers only after native ownership validation. No inherited leave/close.
Ready send precedes child return through upstream __post_Fork; no duplicate TID
repair. New-channel failure closes once with raw receipts and requires fail-stop.

Simplicity: reuse native adapters, frame validators, context initializer and pinned
musl rebind, not a process framework/second startup ledger. Explicit state guards
are necessary for one-shot quarantine and unknown outcomes; remove no old path.
Tests include real helper logic with host-injected native calls/rebind observations,
all child greeting/ready prefixes, guard/reentry/identity/grant/TLS mismatch,
known refusal/parent preservation, unknown/no replay, child pointer reconstruction,
read/FD continuation and real exit fail-stop witnesses where relevant. Preserve
prior5847/eight frame controls and78 libc scenarios; add semantic omissions at arm/
child boundary. Strict C17/format/UBSan, target objects/static frames/BSS, actual
complete pinned dash/CRT/libc/public-fork/copy_rebind link without stubs. Host and
link evidence do not prove native scheduler/owner gate or full resource fit.
Pin all inputs/tools/SDK before consumption, run minimum/current Python and local
quality, preserve every attempt and archive/readback exact owned roots before
removal. No sibling edit/message, guest, default/profile/quota/release-pin change.
Owner matching wire/source/gate/readiness and native acceptance remain separate.

Actual results/review: final1008 stage cases/seven semantic omissions plus5847
frame/78 default libc cases pass on minimum/current Python. Real native-entry C
body host tests inject hardware/auxv/rebind boundaries, preserve errno and observe
actual exit114/116/125; private host fork preserves parent aggregate byte state.
No int81, native TLS layout or owner gate execution is inferred.20 target units,
119 static frames/max664 and5040/4952 optional/default BSS; actual native park and
pinned rebind/no double TID repair verified. Full pinned shell links; static ELF
has63 PT_LOAD pages/NX/no WX/no dynamic binding or relocations. Exact inherited
zero LOCAL HIDDEN UND _DYNAMIC is checked against baseline, not ignored imports.
Initial setup/fixture/control-preparation/static-symbol-check failures retained.
Final review explicitly invalidates transferred temporary guard metadata and adds
that omission. No production warning suppression or success stub. Native transaction
selection, full fit and matching BG-069/BG-070 owner implementation/readiness/
settlement/native witnesses remain open. Scope/reviews/evidence in the dated
fork-stage packet; independent owner/reader and all full UL/M3/R1 gates pending.

## UL-007/081/082 authoritative file view v1 — 2026-10-22

Pre-code scope/authority/error/bounds/simplicity and validation review:
[review](../evidence/filesystem-file-view-2026-10-22/review.md).
Two pure u16 masks come from the sole private descriptor array; bit n=remote FD n.
No mirror/source/native effects or parent repair. Exact active opaque key required;
owner compares both complete masks while gate remains exclusive through copy.
31 actual process tests/13 controls, reentry compile denial, public host/native
library consumers and default remote regression pass. Initial process pass retained;
private helper then gated to process profile before final min/current/default runs,
preventing unused private code in baseline builds. No new suppressions.
Review by implementation agent; independent owner/reader pending. Full UL/M3/R1,
consuming pre-copy enforcement, actual streams/native transaction and fit remain.

## UL-007/081/082 real TLS relink — 2026-10-22

[Pre-code review](../evidence/filesystem-fork-tls-2026-10-22/review.md) records actual
Aether no-TLS denial, scope, lifetime/error/resource/simplicity and test selection.
Restore a live checked initialized four-byte C17 TLS canary in the opt-in module;
no production reset, fake header, old runtime or loader weakening. Initial greeting
and native fork/rebind paths validate without changing grants/error contracts.
1010 stage/nine compiling controls, frame5847, default78/opt-in78 libc scenarios
pass on actual minimum/current Python; C17/format/UBSan and complete link match.
Actual pinned unchanged Aether ELF parser accepts corrected shell under default
limits; old image and malformed TLS/WX remain denied, seven Zig tests total.
One test harness primitive-name compile failure is retained, corrected in our
helper only; initial successful C/link checks were not native acceptance.
Source review by implementation agent; affected-owner/reader acceptance pending.
Generic parser79-page accounting is not whole peak fit or native execution. Full
UL-007/082/M3/R1 and matching actual owner/native witnesses remain open.

## UL-007/081/082 file-view consumer status intake — 2026-10-22

[Scoped review](../evidence/filesystem-file-view-consumer-2026-10-22/review.md)
verifies every declared sys-init0203 evidence hash/size and exact file-view18 seal.
Update STATE because BG-071 is locally complete; full BG-069/070/native acceptance
is not. Documentation/evidence only; no source or test behavior changes, so no
unchanged experiment replay. Local quality required. Implementation-agent review;
owner/reader and full UL/M3/R1 remain open.

## UL-007/081/082 mapped FILE initialization — 2026-10-22

Pre-code requirement, unsafe/partial-failure and simplicity review is in
[FS-BROKER-INIT](../proposals/FS-BROKER-INIT.md). The existing by-value constructor
was measured beyond the one-page stack. Field projection initializes the same
private ledger/source in final storage, removing aggregate copies without a new
allocator, ledger, service or stack. One common greeting/cleanup path preserves
old APIs and once-only actual endpoint results. Default still denies unsafe code;
only the explicit initialization candidate admits documented projection blocks.

35 producer tests/15 compiling semantic controls and26 consuming owner tests pass;
default client/process regressions remain. Nonzero backing, all empty view records,
malformed/lost/wrong-epoch greeting, epoch0, once-only close/drop, mapped workspace
separation and stream drop on nested failure are covered. Strict tool/source hashes
and attempted alternatives are in the root system evidence. The selected source
is restored exactly to passing qualification hashes after the larger typed-array
comparison. Native code16544/16384 still fails fit, so no VM or full peak-stack
claim. Unsafe review is by the implementing agent; independent review is pending.

2026-10-23 explicit path-wire continuation: FS-ROOT-PATHS pre-code scope defines
AEFP0001, matching compile-time dependency selection and no fallback.11/10 actual
selected/default handler tests/eight compiling controls per selection pass; C17/
UBSan exact codec/C-Rust-C checks and native libraries pass. Existing component
wire/default/runtime grants unchanged. Implementation-agent technical review;
independent/native owner fit and minimum-Python execution pending. No new unsafe
boundary; caller-valid C ranges retain the existing borrowed codec obligations.

2026-10-23 path-owner/read-probe continuation: sys-init0221 records pre-code
requirements, unchanged authority/resource/unsafe/cleanup contracts and explicit
version propagation. Actual complete owner40640 code/7504 resident/8000 conservative
stack fits unchanged49152/8192/8184 limits. Two initial C mock failures remain
failed and retained; corrected bindings and ten actual fixed-helper outcomes pass.
Only current Python executed; source-matched native sequence/independent review
pending. Kernel/runtime ABI unchanged; path strings never mint home/system rights.

2026-10-23 exact-target FILE alias foundation: FS-FILE-REPLACE records pre-code
requirement, security/cleanup/capacity/simplicity/test selection.41/42 selected/path
cases and19 compiling semantic controls each pass with real sealed AF07 service
and strict host/target Rust checks. No unsafe, fields, quota/wire/C/libc/kernel
change. Initial fixture unused-field/duplicate-module failures remain failed;
reuse the existing fixture and inspect real storage. Technical review by the
implementation agent; independent/native whole-fit/public dup2 acceptance pending.
A separate16-alias proposal measures only actual type geometry (delta24 bytes),
retains13 descriptions/16 handles and is not implemented pending disposition.


## UL-007/081/082 approved16-slot FILE ledger —2026-10-23

Maintainer approval, pre-code contract, O/I/E and SE-01–05/security/resource/test
review are recorded in FS-FILE-REPLACE. Split alias geometry from the13-description
pool, reusing the actual reference scan/offset/retirement ledger. A spare-alias
workaround cannot support full mixed C16/FILE13 tables; no reference counters,
second source, handles, generic VFS or new authority are needed. No existing
qualified compatibility path is removed yet. Audit in-place initialization against
each actual array, not their formerly shared length. New view selectors0–2 do not
grant console rights; old protocol consumers are compile-time fenced before effects.

15 actual-entry cases/21 compiling controls each with/without paths pass, plus
old41/42 and19, old FILE protocol10/11 andeight, strict Rustfmt/Clippy/host/native
libraries and target layout assertions. Concrete test-Channel ProcessFiles adds24
bytes; complete selected owner code/data/stack fit still pending within existing
budgets. Four harness failures retained;11 owned trees removed. No new unsafe
boundary, fields, heap, dependency, pin, quota (except the explicitly approved
alias count), wire/native/C map/public dup2 selection. Current Python3.14.7 only;
minimum runner missing. Technical review by implementation agent; independent/
native consumer/owner acceptance remains open. Root STATE records next integration.


## UL-007/081/082 matched FILE/startup/public dup2 —2026-10-23

Pre-code O/I/E, bounds/authority/ownership/concurrency/error/unsafe/resource/test
contract and SE-01–05 review are in FS-FILE-REPLACE. Reuse one bounded ledger,
exact-target opcode and existing local mask/guard; spare-only replacement fails
at full capacity, while a second transaction service/cap pool is unnecessary.
No qualified compatibility path is removed yet. New explicit versions fence old
selectors/consumers; low FILE selectors never imply console rights. Known failure
preserves victim; unknown reply/close/cleanup actually exits public process141.
No new fields, unsafe/FFI boundary, allocator, authority, dependency or other limit.

Actual C/Rust/C, mixed/private/public errno/fail-stop, inherited full16 views,
startup/fork/exec/readiness/export and complete shell/helper/owner checks pass;
old regressions remain. Full owner41360/7528/7992 fits existing limits. Six harness
failures remain retained without suppressed warnings or weakened semantic gates.
Private inputs refreshed after source-hash drift; engine/activation executable
bytes exact. Bounded native probe has19 host outcomes; images/receipt prepared,
no VM. Generated host trees are disposed after compact readback; only pending
images/current dependencies remain. Current Python only; minimum/independent/native
coverage remains open. Implementation-agent technical review; no release sign-off.

## UL-007/081/082 directory-anchored path foundation —2026-10-23

FS-ROOT-PATHS records the pre-code requirement, forbidden root fallback/escape/
borrowed-base close/rights inflation, lifetime/cleanup/resource/simplicity review
and focused test selection. Reuse the existing rolling client walk for retained
service directories as the next real-CWD foundation; no new protocol, policy,
Client field, unsafe boundary, dependency, authority or native profile selection.
Current complete native dup2 witness remains frozen-source scoped. Root STATE
owns integration; whole-owner fit and process CWD/home/Zsh acceptance are separate.

Focused directory client30/13 and descriptor9/8 tests, eight compiling omissions,
actual selected FILE protocol15/ten controls and strict host/target checks pass.
Layouts unchanged; no new VM or complete-owner claim. Two harness attempts remain
failed in the linked compact evidence, corrected without runtime check changes.
Technical review by implementation agent only; independent/minimum runner remain
open. Current native pins/witness keep their exact frozen bytes. Public CWD/home
and persistent Zsh qualification remain integration work.

## UL-007/081/082 retained per-process directory candidate —2026-10-23

Pre-code scope and O/I/E/security/unsafe/resource/test/simplicity review are in
FS-CWD. Retain an actual directory handle per admitted record, share by the existing
four-record scan across fork, preserve through exec and release only after final
settlement. Reuse one checked FD publication path. No string-CWD cache, new source,
reference ledger, write authority or native profile. Existing public wires reject
selected CWD libraries before effects. Measure actual type size and keep complete
owner fit/public POSIX directory semantics/native/independent acceptance separate.

Retained-CWD results:27/50 tests and29/25 compiling controls for selected16/13
aliases pass; non-CWD16 regression15/21 and old public FILE consumers10/15 with8/10
controls pass. Host/target libraries reject CWD-selected old wires; strict format/
Clippy/unsafe policy, explicit new Option initialization and bounded layout96-byte
growth pass. Twelve CWD cases include shared-binding exhaustion and uncertain
lookup retiring every view. One semantic-control harness failure is retained;
asserting close order earlier fixes its oracle without production changes. No VM
or complete-owner claim. Technical review by implementation agent; minimum runner
and independent review remain open. FS-CWD links exact compact evidence.


## UL-007/081/082 public physical directories and owner —2026-10-23

FS-CWD records pre-code requirement, forbidden outcomes, authority/ownership,
compatibility, bounds/cleanup, unsafe/FFI and test/simplicity review. One original
SA/ZAP getter and one existing source/FILE extension satisfy current shell needs;
no path cache, VFS framework, kernel CWD syscall or second reference ledger.
C allocates one upstream-owned flexible ZAP attribute record per nonrecursive
step inside the existing engine backing and frees it on every exit. Rust retains
exclusive SPA/view borrows. Parent/path use existing rights3; public CWD context
changes do not grant filesystem mutation rights. Same runtime limits and release
pins, new explicit AF08/FILE03 candidate and opaque process-key binding only.

Focused host/target C/Rust/C, actual libc, entry, policy/transport/fork/exec/settlement
and original-getter checks pass, with9 compiling omissions/3 selection denials,
old FILE/metadata regressions and complete owner fit44968/7624/7992. The initial
undersized flexible-array assumption was rejected by the real-header build before
VM execution; corrected upstream allocation and faithful test double now pass.
Other runner/fixture/control-anchor failures are retained, not acceptance. Matching
engine/guarded inputs and exact images are prepared; no native run or independent
review/sign-off. Minimum-runner, symlink/non-root-native coverage, writable home,
persistent executable/package/Zsh/TTY/ISO and release gates stay open. Compact
[results](../evidence/filesystem-public-cwd-2026-10-23/README.md) describe commands,
hashes, failed attempts and pending exact receipt. Generated trees are disposed
after readback; no archives/copied SDKs. Implementation-agent technical review only.

## Issue #88 private created-identity core — 2026-10-28

The [pre-code contract](https://github.com/gonz0w/Aether/issues/88#issuecomment-6468880060)
and [accepted design](https://github.com/gonz0w/Aether/issues/87#issuecomment-6448937637)
preceded the additive API. Retain the identity already returned by the provider
rather than add a storage primitive or rely on an unenforced create/lookup
single-mutator interval. One synchronous Owner borrow reserves unpublished local
capacity, preserves raw mutation progress and publishes an attenuated handle only
after exact identity validation across reopen. Existing Backend/Completion/wire
APIs, fixed file mode 0600/directory mode 0700, profiles, resource limits, shared
standards and dependencies stay unchanged. Requested modes, umask and a public
mktemp/libc consumer are outside this private core. Existing retirement/no-retry
and alias/session teardown govern acquisition failure; no namespace rollback is
inferred.

Tests were defined before implementation. Missing-method compilation was not
counted as behavioral RED. The actual typed C fixtures and narrow Backend cases
cover success, collision, identity substitution/malformed output, pre-effect
rights/stale/quota/capacity/serial denial, truthful completed/committed/unknown
progress and descriptor admission/alias cleanup. Current mixed, directories and
default runs passed 17, 23 and 8 entry tests and rejected 11, 31 and 5 compiling
semantic omissions, respectively. All 78, 242 and 48 selected commands met their
expected outcomes, including strict format/Clippy/target/ABI checks and 18 legacy
runtime host tests in the directory selection. A host-only import of the complete
maintained descriptor ledger permits dead code only within that test module,
because unrelated ledger APIs are outside this composition. Production warning
policy is unchanged; fixtures retain explicit edition 2021 and Rust 1.98.0.

The selected actual Owner/Zpl no_std caller and minimal external non-LTO typed C
boundary passed both positive and no-create fit controls. Positive graphs retain
creation/reopen/validation edges; no-create graphs exclude reachable create/mkdir
edges. Mixed measures 10,576 code bytes, 3,096 conservative stack bytes and a
5,352-byte component envelope (1,112 Owner + 144 caller-owned context + 4,096
workspace). Directories measures 11,008 code, 3,128 stack and a 5,368-byte envelope
(1,128 + 144 + 4,096). Caps remain 49,152 code, 8,184 stack and 8,192 state plus
workspace. The Owner is stack-local; the external typed context's size is included
explicitly. Fresh construction and one create may fold known preconditions, so
these are selected-caller measurements. The workspace is budgeted, not actual
provider storage. This is no all-state worst-case, actual mapped-state,
full-provider/system/native or release qualification. The unchanged stack
inspector checks the actual entry-reachable graph and readonly load permissions.

The separate legacy bridge checker remains unavailable: exact historical input
and producer/baseline prerequisites are missing and may not be substituted or
resealed. Its unchanged default bridge algorithm is cfg-excluded from this change.
The available directory regression's 18 host tests passed, while both
`exact_object` and `non_bitcode_object_exact` were false. This provides no legacy
byte equivalence, bitcode/LTO reproduction or fresh legacy native evidence; old
sealed artifacts remain immutable.

Every failed attempt remains retained. Directory attempt 07 failed its native
Clippy stage on the new comparison against the runtime maximum counter. The
small equality-guard correction preserved checked-increment exhaustion, no-effect
and no-wrap invariants and passed separate source review before fresh runs.
Its failed compact outer receipt and complete failed inner receipt remain
separate; the later compact frontend did not relabel that failure as a pass.
The first three mixed fit attempts remain failed: a Rust library path sent to
Clang caused a pre-compilation loader abort; the next attempt rejected the ELF
without section facts; the diagnostic attempt proved one exact RX load with
SHF_WRITE in its .text section metadata. The corrected private oracle follows
actual load permissions, requires one exact .text extent and retains the section
flags, without weakening native mapping authority or increasing any cap.

Focused checks used pinned inputs and separately reviewed owned-child aggregate
runners. Final freezes, known child stops and owned generated-output disposal
passed for the successful selections; compact commands, hashes and short failure
logs remain. This three-document result reconciliation changes no compiled input,
helper, policy, dependency pin, profile or resource limit. No new maintained
checker, compiler or guest run was selected for this documentation-only patch.
[Issue #88](https://github.com/gonz0w/Aether/issues/88) is the sole live owner for
exact receipts, quality validation, separate final review and protected
integration; this note does not claim an unrun quality pass or a merged PR.
