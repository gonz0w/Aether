> Current review2026-10-20: [consumer evidence](../evidence/filesystem-native-consumption-2026-10-20/README.md)
> verifies Aether's exact normal/negative/recovery producer matrix for this sealed
> candidate. Original not-launched/build-rejection statements below describe the
> handoff at delivery time. One-write/context and the immutable delivery remain
> unchanged; repeated service use needs a matched small-write retirement profile.
> Retained evidence review is not fresh native execution or operational acceptance.

# Private filesystem service transport handoff — UL-082, 2026-10-19

Status: implemented and host/object tested here; **not selected, launched or
accepted natively**. This is an affected-owner proposal, not a new shared standard,
SDK pin or sys-init policy. Aether's current recovery/eight-write receipts clear
the historical callback/30-second gate. They do not qualify this new service.

## Entry and provisioning

The new delivery is `build/service-deliveries/filesystem-service-2026-10-19-v1`.
Its `SHA256SUMS`, source, inputs and build records bind one ELF64 relocatable
`objects/filesystem-service.o`, exporting `aether_fs_service_run`. This object
includes the Rust policy, bridge, connection and native adapter. It needs the
original C engine, shared UTC and native runtime dependencies; it is **not a
standalone executable**. Do not substitute it for the sealed write-probe delivery.

`native-service.h` declares the exact entry and72-byte result. The trusted importer
supplies a uniquely borrowed live writable/accounted SPA, an immutable1..255-byte
dataset plus NUL, retained request-reader and reply-writer bindings, and explicit
rights1..7 (LOOKUP1/READ2/WRITE4). Request bytes cannot call this entry. The native
kernel enforces each endpoint holder and direction; token shape checks do not
authenticate a caller. The request token is the nonreused generation and peer
binding. The sole client receives only the counterpart holders before admission.
Invalid scalar/name/rights provisioning returns22, with stop4/error-22 and close
fields-9 meaning no close attempted; those endpoints remain caller-owned.
After validation, the entry consumes both endpoint obligations on every return.

UTC must already be established and retained. One unused original ordered
transaction slot is reserved. No external SPA mutation/teardown, concurrent entry,
context reset, observer recycling or automatic replacement after uncertainty.
The C context closes before both endpoint closes. Failed endpoint closes remain
failures; closure is not revocation/reclaim/device quiescence. The importer keeps
engine/code/UTC resident through original ordered drain/export/kernel_fini.

## AFSRPC01 frames

Every request/reply is64 initialized bytes, little-endian64-bit words. Bytes0..7
are ASCII `AFSRPC01`. Word1 is request opcode or signed reply status (0 success,
negative error); word2 is the trusted service generation. Word3 is a service-local
handle token. Tokens never select C objects, are never reused within the instance,
and remain scoped to its one authenticated connection. Ready is a complete greeting
with status0/token1/kind1/root size; it means transfer completion, not supervisor
readiness acceptance. All unused fields and payload tails must be zero.

| Opcode | Word3 | Word4 | Word5 | Bytes48..63 |
| --- | --- | --- | --- | --- |
| 1 lookup | directory token | attenuated rights | name length1..16 | name, zero tail |
| 2 read | file token | offset | requested length0..16 | zero |
| 3 close | token | zero | zero | zero |
| 4 disconnect | zero | zero | zero | zero |
| 5 write | file token | offset | length0..16 | data, zero tail |
| 6 stat | token | zero | zero | zero |

Lookup/stat/greeting success: word3 token, word4 kind1 directory/2 file, word5
size. Read success: word5 count, initialized payload and zero tail. Write success:
word4 assigned TXG (0 for empty), word5 staged length, word6 state2 (0 empty),
word7 zero. Empty writes do not consume the provider budget. There is at most one
nonempty provider call per context, including a known unassigned error. Later
nonempty writes return-28; closing/reopening handles does not restore this budget.
No arbitrary create/resize/rename/remove, client UTC or general POSIX API is exposed.

Errors: invalid-22, denied-13, stale/closed-9, capacity/write budget-28,
not-directory-20, is-directory-21; positive engine errno becomes negative;
clock/poison/invalid-completion/uncertainty become-5. These private mappings are
not a POSIX conformance claim. Most failure fields are zero. Committed write errors
retain word4 TXG/word5 staged/word6 state1; malformed/unknown completion uses
word6 state3. Neither state2 nor a transferred response promises durability.

## Lifecycle and failure

One connection,16 total policy handles,64 complete requests. Each frame transfers
chunks<=16 with at most100000 polls; EAGAIN yields. This count is not a wall-clock
or scheduling guarantee; the existing outer native watchdog remains necessary.
Partial input/EOF/error cannot dispatch a request. A reply is never retransmitted.
Any failed receive/send or exhausted request budget revokes all references and
consumes the context before attempting both endpoint closes. Assigned/unknown/
malformed completion retires policy immediately and ends the loop after at most
one response attempt; a lost response also ends it. No next request can replay.

Disconnect succeeds only after its complete reply and both successful closes.
Result records ready, request count, stop (0 disconnect/1 receive/2 reply loss/
3 budget/4 provisioning/5 retired), both close outcomes, raw transport/setup error
and last known write TXG/staged/state. Invalid output pointer returns22 without
an output write. Nonzero returns do not imply no filesystem effect; preserved
successful progress after reply loss must never be interpreted as retry permission.

## Required owner integration and acceptance

Current pinned `openzfs_volume.build` rejects `pool_fs_bridge` with
`namespace_ipc`, and also rejects `pool_zpl_write` with IPC. Its existing bridge
intake pins the old18-member probe seal and adapts only
`aether_fs_policy_write_probe`. The new checker executes the isolated actual guard
and confirms rejection before any builder/import/native launch. No guard bypass,
local copy of kernel/init policy or sibling edit is proposed here.

Aether owns a separately selected matched build/profile that links this entry,
provisions authenticated counterpart holders/client workload and retains the
original writable import/accounting/UTC/drain/export, full-file hash/metadata/EOF,
outside-grant guards and fresh readonly recovery oracles. Request fixture: greet,
lookup`zstd` WRITE, lookup`zstd` READ alias, one16-byte overwrite at37 with byte
`(i*17+91)%256`, alias read/stat/EOF, disconnect. Native negatives must include
foreign holder/direction, partial request EOF, lost reply after write and failed
endpoint cleanup, with stop/no replay/context retirement and actual owner cleanup.
Preserve current watchdogs/grants/workers/transaction/observation limits; any new
resource/call-bound contract requires explicit owner review. No automatic native
retry after an uncertain failure. Current static object checks are not whole-stack
or peak-memory proof.

After matched owner qualification and independent consumption, sys-init owns
launch/order/readiness/shutdown acceptance for the exact executable and package
owner retains installation/trust policy. This proposal does not fulfill those
gates, general service uptime, persistent runner/packages/Zsh/ISO, or R1. Finite
eight-write producer evidence does not authorize continuous transaction history.


## Separate approved eight-write candidate — 2026-10-20

Run `python3 -B experiments/filesystem-service/check-service.py --lifetimes`.
This adds strict cfg-specific host/actual-entry, semantic omission, native object/
import and ABI checks; it never launches a VM. Owned build outputs must be removed
after recording compact results. The default one-write profile stays unchanged.
The separate27-member `filesystem-service-lifetimes-2026-10-20-v1` delivery has
manifest `0eddb895d8a8d6276834a0d4ec58aa77e13e44be882d5eab46695cf716ff825c`.

The approved variant accepts exactly sixteen-byte writes and at most eight
aggregate attempts, consuming the C context, checking original successful result
retirement and reopening before the next accepted write. Failures never reset
history or replay. Post-write readback/retirement/reopen errors preserve state2,
original TXG/staged bytes and retire aliases. Dataset/SPA lifetimes cover every
context; owned error outputs are consumed exactly once. Lost/partial replies and
endpoint cleanup retain outcomes. Seven actual-entry cases and four compiling
omissions pass, plus default regressions and x86-64 imports/ABI checks. Aether’s
native matrix remains pending; a host candidate is not a launchable service or
whole-system uptime/R1 acceptance. Namespace operations and operational lifecycle
remain required. See Aether `docs/evidence/fs-service-lifetimes-integration-2026-10-20.json`.


## Eight-write native producer gate passed — 2026-10-20

Aether's new exact27-member candidate/profile passes12 fresh guests with seven
images admitted before launch. Normal, partial-request and final-close-failure
complete eight16-byte calls with last795/fresh805; lost reply stops after one
788/fresh798 without replay. Full independent780248-byte final file/hash/metadata/
EOF, original ordered export/drains, all21 cleanup boundaries/three terminal0/
live0/reclaims3, recovered whole media/outside guards pass. Controller4096,
observer8192, writers60s6000/readers30s3000 and other bounds stay fixed. Sources/
tools frozen, all VMs joined/owned output removed.699-method Aether integration
checkpoint passes. Exact service reports are checked in-engine; retained numeric
observations are not a complete72-byte report or general failed-close proof.

Producer receipt: `../Aether/docs/evidence/fs-service-lifetimes-native-2026-10-20.json`,
SHA256 `cac88f4ff8faa4c86a4e2361d20ece087519008fa997687df3099e0ad6b54e4e`.
The retained old checker remains explicitly pinned to the old25-member receipt;
it does not verify this new result. This is producer evidence, not independent
userland native execution/human sign-off. Compact retention hashes repeated
unmodified dependency scans/source-context catalogues; no full archive/replay claim.
Old sealed candidate/default policy, SDKs and released standards pins stay unchanged.

The next UL-082 delivery must specify authenticated namespace mutation authority
and alias/POSIX rules, zero-staged mutation progress/retirement, idle/reply-loss
behavior and an exact executable/ABI/provisioning/readiness/shutdown contract.
Existing Aether `zpl-mutate.h` (bounded create/same-directory no-replace rename/
remove) and `zpl-resize.h` (bounded shrink) are private serialized engine-owner
interfaces, not client authority. Do not infer mutation permissions or silently
reuse16-byte retirement for zero-staged operations. Aether matches that new
candidate/profile; sys-init owns lifecycle and pkg-mgr installation. These gates
still block operational service/runner/packages/Zsh/ISO/M3/R1 assembly; finite
eight-call evidence is not general uptime or permission to reset history.


## Namespace service implementation contract — 2026-10-19

Requirement: carry the existing bounded original-engine create/rename/remove
operations through authenticated Rust service policy, the next concrete UL-082
step toward persistent Zsh/packages. This is a separately selected private
`fs_namespace` build, mutually exclusive with `fs_lifetimes`; old sealed deliveries,
AFSRPC01/default semantics, SDKs and released pins remain unchanged. One provider
mutation attempt per engine (shared with the old nonempty write budget), no
observer retirement/reuse/reset, no transaction/memory/time/channel increase.
The existing original C mutator serializes a live writable/accounted SPA/context.

Authority: add explicit MUTATE_DIR8 only to the new profile, distinct from
file WRITE4. Require both LOOKUP1 and MUTATE_DIR8 on an authenticated directory
handle before namespace effects. UID/GID are bounded trusted bootstrap labels,
not request fields or authority; no default ambient identity. Resolve victim IDs
inside the provider after checked leaf names. Remove rejects any live file alias
in any connection before dispatch (no open-unlink); create is empty0600 regular,
rename same-directory/no replace, remove single-link/no external xattr/<=1MiB.
No directories, links, replacement, cross-directory move, ACL inheritance or
arbitrary POSIX semantics. Keep native object/generation identities out of client
replies. Old profiles reject bit8 and the new wire/version.

Private AFSRPC02 keeps64-byte initialized frames and16-byte payload,64 complete
requests/bounded polling. Opcodes1..6 retain their field layouts. New7=create,
8=rename,9=remove: word3 directory token; word4 zero; word5 source-name length in
low32 bits and destination length in high32 (rename only); bytes48..63 contain
source then destination, with zero tail. Names each1..16 bytes; combined<=16;
reject empty/dot/dotdot/NUL/slash and all unused bits/fields. No raw victim IDs,
credentials or client clock. Success returns only assigned TXG in word4,0 staged
in word5,state2 in word6. No newly allocated client handle is published.

One actual namespace provider attempt permanently retires all policy aliases and
consumes the C context before one response attempt, then both endpoint closes.
A clean transferred success ends with explicit stop6/namespace-complete; this is
not disconnect/readiness/durability. Known unassigned errors also consume the
attempt and terminate; committed errors retain exact state1/TXG (including0),0
staged and positive errno. Malformed/lost progress becomes unknown/retired, never
replayed. Denied/malformed/preflight failures do not mutate or spend the attempt.
C close must consume/null; owned factory error outputs close exactly once.
Never pass zero staged bytes to the16-byte or4096-byte retirement entry. The new
trusted `aether_fs_namespace_run` entry adds explicit UID/GID bootstrap inputs and
keeps the72-byte result, with no export of the old entry in this build.

Simplicity SE-01..05: a generic POSIX VFS, replay journal or expanded recycling
API is unnecessary to test these existing primitives. Reuse existing policy,
bridge and framed transport with a small explicit variant; ending the connection
after the one attempt avoids inventing cache/directory alias recovery. None of
the existing qualified profiles can be removed yet. This finite experiment is
not the operational service; mixed-operation record lifetime, blocking idle,
executable/provisioning/readiness/shutdown and consuming owner gates remain.

FFI/security: serialized Rust mutable borrows cover initialized exact slices,
C output structs and the retained SPA/dataset; no input aliases outputs, no
unwind or pointer retention, and backend Drop precedes endpoint close. Trusted
bootstrap IDs<=INT32_MAX and UTC come from owner policy. Preserve failed attempts,
freeze source/tools during qualification, keep compact hashes/commands/short logs,
remove joined owned outputs. BSD-2-Clause original Rust/C tooling; original CDDL
engine and notices remain unmodified. No sys-init/pkg-mgr/standards edits/messages.

Tests before native: policy authority/attenuation, cross-peer/stale handles,
malformed names/frames, missing identity, all remove aliases, spent write budget,
UTC/lookup/factory errors, original committed/unknown/synced outcomes, no second
attempt, close-before-reply, partial/lost replies and both endpoint close errors.
Compile actual Rust entry with typed C header fixture, strict Rust1.98/Clippy/
rustfmt edition2021 and Clang21.1.8; native relocatable imports/ABI and original
C definition origins, compiling semantic omissions and old/default/lifetime
regressions. Matching native selection must preserve original full-file/namespace/
metadata/allocation/EOF/fresh-reader/media/export/21-cleanup oracles. Writers60s/
6000, readers30s/3000, controller4096, observer8192, backing8192 pages/two channels/
three generations/32 observations and worker/I/O limits stay fixed. Fit or unexpected
native failure stops for triage; no automatic retry, larger bound or publication.

Scoped Coding exception: only fs_namespace internal `entry` mirrors the nine-field
private C ABI and allows Clippy too_many_arguments with that reason. Public wire,
other warnings and unsafe-op checks stay strict. No generic argument framework.
Identical rename names are rejected before provider dispatch in this new variant;
the original C API’s validated unassigned no-op remains unchanged.


## Approved next mixed-operation profile — 2026-10-19

After the13-guest namespace gate passed, the maintainer approved the fixed proposal
in Aether's OPENZFS-FEASIBILITY (“Proposed mixed-operation service lifetime gate”):
create p, two16-byte writes, rename p to q retaining the file handle, another
16-byte write, close/remove q, recreate p with a fresh identity, lookup/write16.
Exactly eight total attempts, one authenticated connection/64 requests/16-byte
payload; separate AFSRPC03/entry and trusted directory rights15. Old profiles,
candidates and released pins remain unchanged. Native writer60s/6000, reader30s/
3000, observer8192, controller4096,8192-page backing/two channels/three generations/
32 observations and all other worker/I/O/authority/verification/cleanup limits
remain fixed. No further approval needed for that same scope.

Typed namespace0 and service16 success-only retirement must consume the original
context before checking progress, all original observer graph/pin/request/wait/
epoch/permanent-error invariants, then reopen. Preserve file aliases across
rename and coherent root/file metadata across context replacement; remove still
rejects all live file aliases. Any actual failed/unknown result, retirement/reopen/
root refresh failure or lost reply permanently retires the owner with retained
original committed progress, never replay. Native fixture mutations stay at its
provisioned root. Full original/new file and namespace/allocation/ACL/metadata/EOF,
fresh recovery/media/export/drain/all cleanup oracles remain mandatory. Normal,
lost-first-reply, final-partial-input and final-close-failure variants require
matching evidence. This is a finite lifetime gate, not operational idle, larger
file transport, executable/provisioning/readiness/shutdown or persistent Zsh ISO.
Simplicity: extend the established consuming success-only mechanism for the exact
0/16 cases; do not reset flags, introduce a replay journal or silently widen a
qualified profile. FFI ownership and serialization remain as reviewed above.


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

## ABI26 writable primary-wait adoption — 2026-10-20

Maintainer requested matching writable Rust integration after Aether's read-only
wait qualification. Scope is a separate explicitly selected mixed-wait candidate,
not a silent upgrade of old sealed AFSRPC03/ABI25 objects or an operational ISO.
Retain eight total mixed mutations,64 complete requests,16-byte payload,100000
transfer attempts, one connection, two channels, three native generations and all
original context/outcome/identity/rights/cleanup checks. Writer60s6000, readers
30s3000, controller4096/no writable statics, observer8192 and all other resource
limits stay unchanged. Exact private AENBD004/ABI26 supports primary waits while
OpenZFS helpers remain schedulable; no runtime or released standards pin changes.

Add a result-bearing direction-aware readiness operation to the selected framing
path. After EAGAIN, wait0x24004 on the retained request-reader or reply-writer,
then rescan only the remaining range. Kernel borrows no pointer while parked.
Zero means hint, negative wait errors remain exact and unexpected positive means
EIO. Clear complete frame on every failure/exhaustion, close both endpoints once,
retain original committed outcomes and never dispatch an incomplete request or
replay a mutation. Untrusted clients acquire no ambient authority or new grants.
No new dependencies/allocations/unsafe pointer ABI. Scalar wait uses the existing
trap with its current memory/register obligations and synchronous transfers.

First gate is compilation of all four actual waiting controllers within4KiB.
Then actual-entry/typed-C mixed/backpressure/spurious/error/partial/lost/close
controls, compiling wait/offset/clear/error omissions, strict rustfmt edition2021
(existing scoped fixture convention), Clippy/native symbols/typed ABI and exact
candidate/selector checks. Native matrix only after complete matched admission;
independent file/media/recovery/export/drain/cleanup checks remain mandatory.
Keep compact failed/final commands/hashes/logs; join and dispose owned outputs.
Userland local quality gate is required. No independent reader sign-off claimed.

Simplicity: a void yield hook loses wait errors and endpoint direction; add one
explicit result-bearing operation, reuse framing/service/engine lifetime logic,
and keep old selections for existing consumers. No new event service or wait
queue. Removal of old paths awaits consumer migration. Operational executable,
provisioning, readiness/shutdown, larger transfers and service lifetime are still
follow-on work; no uptime/Zsh/packages/ISO/R1 acceptance follows from this fixture.


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


## Approved AF04 data implementation contract — 2026-10-20

Maintainer approved Aether's concrete “Proposed next data gate:4KiB service
payloads” in OPENZFS-FEASIBILITY. Apply it before code as UL-082's next slice:
AFSRPC04/new trusted entry/candidate,64-byte headers and following64-byte data
frames,1..4096-byte reads/writes, zero last-frame padding and zero header data
area for data operations; namespace names stay within16 inline bytes. Fully
validate/receive write data before effects. Invalid data-bearing headers,
unknown opcodes and partial bodies end the connection without tail replay;
known header-only namespace denials retain canonical errors. Read errors carry
no body. All partial/lost output closes and preserves original mutation outcomes.

Reuse one4096-byte service buffer; no retained kernel pointer or new allocation/
grant. Use original consuming context/graph/pin/epoch/permanent outcome guards
with trusted length-checked success-only retirement1..4096 (native writes4096),
namespace0 separate; wrong expected count or failed/unknown history never reuses.
Old0/16 wrappers and candidates remain exact. Scalar primary waits and helpers
remain the qualified ABI26 mechanism; no new kernel opcode or ambient authority.

Native normal/close sequence stays8 total mutations,4 namespace/4 writes4096,
final p4096/q absent/original zstd unchanged. Lost first create reply leaves
empty p. Partial first write body sends16 bytes after create/lookup, then EOF:
no write dispatch, original create progress retained.64 complete requests,
100000 transfer attempts per64-byte frame (<=64 frames/body),60s6000 writer/
30s3000 readers, observer8192/controller4096/no writable statics/backing8192
pages/two channels/three generations/32 observations and existing worker/I/O/
authority/cleanup limits stay fixed. Fit or stop; no automatic retries/reset.

Test actual entry/framing,1/63/64/65/4095/4096 and reject4097/overflow/rights/stale/
padding before effects; partial bodies, read/write backpressure/spurious/wait
failures, original progress, aliases/budget, consuming cleanup; compiling omission
controls. Strict Rust fixture edition2021/rustfmt/Clippy/native symbols/typed C
ABI/original engine origins, old regressions/byte compatibility, full independent
native file/namespace/media/fresh-reader/export/drain/cleanup matrix required.
Capture actual VM argv and freeze all selected tool/boot identities. New unsafe
length scalar and slices require exact live bounds, exclusive SPA/context,
serialized access, consume/null close and no unwind, as at current boundary.

Simplicity: reuse bounded sequences of existing frames and backend4096 limit,
not a new variable-frame/shared-memory/multiplexing framework. One serialized
connection needs no stream IDs. Retain old paths for real consumers; remove only
after migration. This is the necessary file-data gate, not sufficient operational
service, package/session assembly or ISO acceptance. Review by implementation
agent only; independent reader/owner gates remain open. Source/commands/hash/
short failure logs stay compact; dispose owned outputs after joined processes.

## AF04 result and approved separate lifetime work — 2026-10-20

The exact49-member candidate now passes Aether's7-image/12-guest data matrix;
normal795/805, lost/partial788/798 empty p, close795/806. Original/new full file,
namespace/allocation/metadata/ACL/time/EOF/media/export/drains/all cleanup and3450
balanced primary wait pairs pass. Controller4075/3132/3564/4075, observer7596;
all guest bounds stay fixed.12 actual VM commands and frozen tool/boot/SDK/Rust
identities are retained; generated outputs disposed. See Aether STATE and compact
fs-service-bulk native/implementation receipts. Host16/15 controls, legacy checks,
broad739 and final8 affected methods pass; no independent acceptance inferred.

The maintainer now approved the separate lifetime proposal in Aether
OPENZFS-FEASIBILITY: aether_fs_runtime_run, same AF04/ABI26 and one serialized
connection; replace only the new candidate's artificial cumulative8/64 stops
with checked monotonic counters, retaining original observer epoch exhaustion
and all permanent-failure guards. Native workload exactly9 mutations/96 complete
requests, ninth append4096@4096/seed91, final p8192/q absent; old lost-first-create/
partial-first-body empty recovery and close injection after9 retirements remain.
Writer60s6000/readers30s3000, body4096, controller4096/observer8192/backing8192pages,
two channels/three generations/32 observations and other worker/I/O/authority/
cleanup bounds stay fixed. Fit/time failure stops, no retry or relaxed check.

This is a separate selection, not a silent upgrade, unbounded uptime claim,
standalone service, namespace/metadata expansion, supervisor readiness protocol
or R1 qualification. Preserve all old sources/sealed candidates/pins. New counters
must fail closed before wrap and never reset poisoned/unknown outcome history.
Use focused affected checks, actual-entry/body/alias/exhaustion/cleanup tests and
compiling omissions before matching native admission; compact evidence only.


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


## Private filesystem activation preparation — 2026-10-20

Requirement: connect the validated imported root to existing owner-local native
readiness0x20004 and supervisor observation0x20001, without adding a control
channel, kernel opcode or shared service standard. This is the next UL-082
preparation slice, not an operational executable or sys-init adoption.

A separately selected fs_activation entry/library first validates the locally
constructed AF04 root greeting (exact epoch/token/kind/reserved fields) produced
after backend open, root metadata and owner attachment succeed. Publish the native
instance ready bit once BEFORE attempting the greeting. The64-byte greeting cannot
finish on a32-byte queue until a client drains it: publishing after it creates a
startup dependency cycle. Failure to publish sends no greeting, dispatches no
request, consumes the context and attempts both endpoint closes. Greeting loss
AFTER publication can leave a retained ready bit on a terminal instance; the
consumer must require the exact admitted instance handle to be live AND ready,
never trust endpoint payload labels or terminal readiness. Existing asynchronous
liveness policy applies; no atomic observe-plus-admit claim or auto replacement.

Keep the72-byte ServiceResult and its ready field's greeting-completion meaning;
the kernel bit is separate. This local startup fact does not imply supervisor
acceptance, durability/export, shutdown, public discovery or PS adoption. Existing
AF04 disconnect and permanent failed/unknown outcomes remain unchanged.

Prepare a small scalar-only supervisor gate and compile the actual9/96 controller
with it before native integration. Preserve4096 controller bytes,8192 observer,
all grants/channels/workers/lifetimes/IO, writer60s6000/readers30s3000 and9/96
workload. A fit failure stops this native path for a concrete decision. No VM runs
or silent code-budget expansion during preparation. Old sealed candidates and
SDK/released pins stay fixed; legacy live-code comparison is selected.

Security: importer/SPA/dataset/UTC authority stays trusted and serialized; peer
frames never publish readiness. The new hook uses scalar int81 only, retains no
pointer, does not unwind and grants no authority. The wrapper validates BEFORE
notification or output, calls publication once, and never retries after error.
No new heap/static state; two booleans/callback-local state only. Caller-held
native instance identity scopes consumer observation; stale/foreign/terminal/
malformed readiness closes admission. Whole-system/peak stack remains unmeasured.

Tests: actual service run with typed C provider/native-trap substitutes, native
object/strict Rust/typed C ABI, malformed greeting/epoch/reserved, root/open/UTC
failure, publication failure, every greeting prefix loss, no effect/replay, both
endpoint-close errors and checked original outcomes; compiling omissions for
order/skip/retry/terminal readiness. Execute actual supervisor gate with scripted
native observations and compile the real controller for fit. Focused tests only;
matching native/independent consuming gates remain unrun until selected.

Simplicity: reuse the existing retained ready bit and direct lifecycle primitives;
a separate readiness channel or service broker adds authority, slots and recovery
states without a current need. Reuse current engine/service code through a tiny
selected wrapper instead of a second filesystem policy. Removes no old consumer
path now. Userland owns readiness semantics, sys-init activation policy; no
sys-init/pkg-mgr/standards edits or messaging. Operational executable/provisioning/
shutdown and persistent Zsh composition remain explicit work after this slice.


### Activation host result and next decision — 2026-10-20

The private preparation passes 21 actual-entry tests plus three wrapper tests,
21 compiling omissions and strict object/ABI/Clippy/format checks. The native hook
checks the existing UTC provider before publication; each later mutation still
checks time independently. Factory/root/UTC failures never publish, publication
failure sends nothing and consumes/closes, all 64 greeting prefixes preserve
no-request effects, and readiness remains distinct from completed greeting.
The wrapper latches output/publication errors; no automatic replay. The actual
scalar supervisor gate rejects terminal/stale/foreign/malformed observations and
shares the original poll budget with completion. Root validation cannot be
replaced by a client payload. Independent/native activation remains unrun.

Legacy runtime's 18 entry tests pass. Its actual object differs only within the
embedded LLVM bitcode section; every other file byte matches its immutable
prior object using the original Rust/Clippy emission sequence. The first
Rust-only comparison was not the original emission sequence and is retained as
triage. No LTO or bit-for-bit sealed-object reproduction is claimed.

The unchanged Aether linker rejects the new actual controller at 4,181 bytes
against 4,096. The concrete separate 8 KiB/two-RX-page resource proposal in
Aether OPENZFS-FEASIBILITY is pending; no native profile, kernel envelope widening,
new seal or VM run is authorized by these host results. Existing seals, SDK and
standards pins remain fixed. Compact attempts and commands/hashes live in
Aether's fs-activation-host/fit receipts; owned host outputs are disposed.
Operational executable/resources/provisioning/shutdown and sys-init composition
remain separate UL-082 work; no PS API or ABI22/24 composition is invented.


### Approved activation controller — 2026-10-20

Maintainer approved the separate 8192-byte controller, same4096 stack and all
other limits. The 58-member activation candidate is sealed with the exact entry,
AF04/ABI26, selected cfgs and readiness contract in inputs.json. Aether supplies
selected loader/envelope/alias/tail enforcement and retained-instance gate; no
new shared PS API or kernel operation. Four actual controllers fit, and loader/
intake controls pass. Native qualification awaits the final kernel checkpoint
and full matched9/96 normal/lost/partial/close/fresh-recovery checks. No production
executable/shutdown or independent acceptance follows from sealing. The earlier
resource-pending proposal is superseded only by this explicit decision.


### Qualified activation producer; package-name proposal — 2026-10-20

The exact58-member activation candidate passes Aether's complete7-image/12-guest
matrix after an activation-only controller prefix progress fix. Owner code/seals
stay fixed; normal/lost/partial/close-error fresh recovery, ordered export/drains
and cleanup pass. This does not promote a production executable or service API.
[Native result](../../../docs/evidence/fs-service-activation-prefix-fixed-native-2026-10-20.json),
[final-byte review](../../../docs/evidence/fs-activation-qualified-2026-10-20.json).

**Decision required; no implementation or resource lift.** The current16-byte name
and combined-rename bounds cannot represent pkg-mgr's64-hex files/<digest> names.
The [actual-code probe](../../../docs/evidence/fs-package-name-compatibility-2026-10-20.json)
confirms AF04 lookup and namespace creation reject these before backend effects;
lookup policy/C engine already permit255-byte components. Do not alter package
hash filenames or reinterpret old frames. See the [concrete separate-profile
proposal](../../../docs/OPENZFS-FEASIBILITY.md#proposed-separate-package-name-profile--decision-required-2026-10-20).

If approved, the private owner candidate would accept1..255 bytes per name and
at most510 combined rename bytes. Lookup/create/remove use one name length;
rename uses two checked lengths with no new opcode. A separately versioned
header keeps the former inline-name bytes zero and follows with complete64-byte
frames and zero final padding. Receive and validate the full name body before
any lookup/mutation. Reject NUL/slash/dot/dotdot, malformed/partial/oversized/
overflowing bodies; no error, unknown outcome or lost reply replays. Review exact
wire magic/layout/entry and a fresh seal before producer selection; this text
allocates no public protocol or shared PS schema.

Reuse the existing4096 scratch body serially, no heap/static/new buffer/channel
or stack grant. Preserve4096 data,8192 controller/4096 stack/no statics,8192 observer,
engine8192 pages, two channels/three generations/32 observations, workers/I/O/
authority,100000 transfer attempts/shared1M polls,9 mutations/96 requests and
writer60s6000/readers30s3000. Old candidates/bytes and independent full-file/
metadata/media/export/drain/cleanup checks stay fixed. Host parser/policy/provider
bounds16/17/64/255/256 and rename510/511, partial/padding/rights/epoch/no-effect/
no-replay omissions, ABI/object/intake/four-controller fit checks precede bounded
native long-name recovery/interruption. Fit/time failures stop, never reset/lift.
Long names do not supply directories, metadata, production lifecycle, loaders,
runner/packages/Zsh or independent/sys-init acceptance.


### Approved AF05 name implementation — 2026-10-20

Maintainer approved separate255/component510/rename. Private fs_names requires
activation/runtime/bulk/wait/mixed; header MAGIC AFSRPC05, entry aether_fs_names_run,
same72-byte/nine-argument result. Named headers reserve bytes48..63 as zero;
word5 holds low32 source/high32 destination only for rename. Full64-byte padded
body is received in existing4096 scratch before effects. Invalid structure, epoch,
partial body or padding stops/consumes; lexical/policy denials may reply/continue.
NUL/slash/dot/dotdot names never reach a mutator. Nothing resets or replays.

Run `python3 -B experiments/filesystem-service/check-namespace.py --names`.
Actual entry29/wrapper3/26 omissions, strict Rust/Clippy/format/typed C/object,
legacy activation21/runtime18 and exact legacy non-bitcode object checks pass.
The separate61-member delivery is
`build/service-deliveries/filesystem-service-names-2026-10-20-v1`, manifest
99cb2e36ad13e108761ca513aed53cc4681ce9b8033aa4663c1faf0aec091e78.
Old seals/pins stay fixed; LLVM bitcode differs without a LTO reproduction claim.
A separate AF05 run shares original AF04 body/data helpers; a selected dead-code
expectation retains the old run verbatim for compatibility. No new buffer/heap/
static/channel/stack or kernel operation. All other resource/authority/9/96/time/
verification/cleanup bounds stay fixed. Native preparation is not executable/
provisioning/shutdown, directory/layout/metadata, persistent loading/runner/package/
Zsh/sys-init or independent acceptance. STATE links host and native progress.


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


## Delegated directories AF06 — 2026-10-20

Run `python3 -B experiments/filesystem-service/check-namespace.py --directories`.
The separate67-member current dependency is
build/service-deliveries/filesystem-service-directories-2026-10-20-v1, manifest
e01e269a91a96bac3a428fb1197dc862032838dcb94602c0c6042ef9e8e5c4fa. Entry
`aether_fs_directories_run` keeps nine trusted arguments/72-byte result, existing
activation/UTC and AF05 framing/data bounds; MAGIC is AFSRPC06. New named operations
10 mkdir0700 and11 empty-rmdir require LOOKUP|MUTATE_DIR on the actual delegated
parent, trusted uid/gid and shared UTC. No raw client object/parent identities,
slash/dot/dotdot/NUL traversal or widened rights. Live aliases prohibit rmdir;
failed/unknown/partial/lost outcomes never replay. Only exact synced zero-staged
namespace success can consume/retire/reopen, then refresh that parent and every
alias. The root cache changes only if it is that parent. No unrelated root lookup
substitutes for a child refresh. A provider lacking directory refresh fails closed.

Typed directory-bridge.rs binds Aether's exact zpl-directories.h functions and
validates mkdir output/type and refreshed identity. SPA/context/name/result borrows
remain exclusive/disjoint through synchronous FFI, with no pointer escape, Send/
Sync/reentry or concurrent teardown. Reuse the original tables, scratch and typed
retirement, with no new allocator/channel/kernel operation. All existing9/96,
60s6000/30s3000, code/stack/observer/engine/worker/I/O/authority bounds remain fixed.
Immutable AF05 and older dependencies stay unchanged. General modes, directory
rename/cross-directory promotion, recursive deletion, symlinks and open unlink are
unsupported. Ordinary backend mutation errors also retire the context; production
policy/error usability remains part of the operational handoff, not a retry API.

Host actual entry15/wrapper3/27 semantic omissions, strict object/typed ABI/Clippy/
format and legacy18 behavior checks pass. Active legacy source/panic locations
changed, so current objects are not claimed byte-identical to sealed old ones;
embedded bitcode/LTO reproduction and fresh legacy native acceptance are not claimed.
Aether785 host and actual controller5281/3845/4581/5281 fits pass. The initial
reader preparation guard failure is preserved with no guest execution; its fix
and49 affected checks precede a fresh native matrix. STATE records target results.
Directory support is not an operational executable, sys-init handoff, persistent
runner/packages/Zsh or ISO acceptance. The candidate OWNER.md states explicit
startup authority, readiness and shutdown obligations, preserving separate ordered
engine drain/export/block quiescence and native reclaim. Never use the fixture's
expected-negative conversion as a real clean service result.


AF06 producer qualification now passes all7 admitted images/12 fresh guests.
Full796/806 recover the renamed4096-byte blob and exact directory hierarchy;
lost/partial788/798 leave only empty files. Original/new data/metadata/inventory/
media/export/drain/all cleanup and2476 balanced waits pass;36 reclaims/live0.
Nine old seals/pins remain fixed and owned generated outputs are disposed.
[Final native receipt](../../../docs/evidence/fs-service-directories-reader-fixed-native-2026-10-20.json),
SHA256 dd54d56ccf97a774d3ed47099e1352312afe940419e3d6e0e9eaa74c6ecafae8.
This is a finite producer result, not an operational executable or independent
acceptance. STATE records the approved next separate120s/65s-idle lifetime profile;
all old bounds and all other resources/authority/workload limits remain unchanged.

## Separate kernel idle qualification — 2026-10-20

Aether's one120s writer and30s pristine/recovery readers qualify6500 delivered
idle ticks with post-idle mutation/read4096 on the exact67-member AF06 producer.
AENBD005 owner27 exposes self-event/park only; engine ABI26/wire and immutable
producer stay unchanged.9/96, all memory/authority/worker/I/O/cleanup bounds and
old profiles remain. STATE links exact sources/commands/results and compact failed
attempts. This is finite producer evidence, not the standalone executable or the
authenticated startup/resource/readiness/truthful shutdown handoff sys-init needs.
UL-082 remains active; do not infer launchability or independent owner acceptance.
