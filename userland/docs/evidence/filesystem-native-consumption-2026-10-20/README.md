# UL-082 native handoff consumption review

Requirement: verify the exact Aether producer receipt for the delivered Rust
service before changing userland runtime policy. Scope is retained producer
evidence consumption and blocker reconciliation, not a new VM run, independent
human sign-off or UL-082/R1 completion.

Applicable clauses: Foundations O-01/O-04/O-05, I-03/I-04/I-05/I-06,
E-01/E-04/E-05/E-06/E-08; local quality TD/TE and Python CP rules.
Read only the explicitly selected receipt after its fixed digest verifies; do not
execute sibling code or follow mutable sibling defaults. Check the four current
cases,12 guest roles, actual retained cleanup/terminal tails, command/profile
bounds, object provenance, target/media linkage and failure/coverage corrections.
Reject semantic tampering with named controls. The72-byte service report is
checked by the engine adapter but not completely projected in retained logs;
consumer review cannot reconstruct it or attest discarded binaries/full serials.

Ownership/bounds: Aether keeps engine/block enforcement and exact native profile;
userland keeps Rust client/context/UTC/POSIX and uncertain-result policy. Sys-init
activation and pkg-mgr installation remain separate. No service code, wire,
provider-call/transaction count, watchdog, memory, observer or capability changes.
New checker is offline Python3.10+ standard library, bounded2MiB inert JSON, no
execution of paths in input, no runtime dependency or source-tree/SDK/archive copy.
BSD-2-Clause for original tool/docs; existing seals/notices/pins stay unchanged.

Tests: exact current receipt and in-memory semantic corruption controls; CLI
help/usage/failure streams and syntax on actual installed interpreter; local
quality gate and links/whitespace after integration. No full runtime/VM suite
for this host consumer/doc-only slice. Preserve all failed attempts compactly.

Simplicity: manually reading the status alone would miss contradictory trace,
profile or artifact evidence. A small one-receipt verifier uses retained owner
data without copying the engine/harness or adding a new framework. No existing
runtime path is obsolete or removed. No numerical guard is relaxed.

Critical next compatibility finding: current private producer
aether_pool_lifetime_retire accepts exactly4096 staged bytes after consumed C
context; current AFSRPC01 service writes at most16 bytes and forbids observer
recycling. The private lifetime profile and service profile are exclusive. A
matched producer/consumer contract and fixed native workload must precede lifting
userland one-write/context; simply removing write_used or resetting history is
forbidden. Further implementation/owner decisions remain separate.

Technical review: contributor self-review; independent human reader and native
consumer execution pending. Existing deferred reader review does not become a
new local coding gate. Completion means only this retained-evidence review.

## Result and remaining profile boundary

The exact producer receipt SHA256 is
`93126506aa78231106b73f93c0f5f954179ed28c82bd291078d35d3a43dd05b4`.
All12 retained guest roles qualify: normal/lost-reply/partial-request/injected
close-failure, each pristine/writer/fresh reader at788/798. Consumer checks bind
the service object and original C origins, per-role60s/6000 or30s/3000, fixed
controller sizes, whole-file/media linkage, and all21 actual retained cleanup
lines/three successful terminal records per guest. Exact retained QEMU-command
JSON hashes are recomputed. This verifies retained producer evidence; full images
and serial logs were deliberately disposed, so neither byte rebuild nor a fresh
independent native run is implied. Source/ABI policy remains unchanged.

Run offline with the explicitly selected exact producer receipt:

```sh
python3 -B experiments/filesystem-service/check-native-handoff.py ../Aether/docs/evidence/fs-service-native-2026-10-19.json
```

The tool reads at most2MiB, verifies the fixed digest before parsing, rejects
JSON duplicate keys, executes no input paths and creates no outputs. Help/results
use stdout, invalid usage64/errors1 use escaped ASCII stderr. No new JSON output
schema or boot markers.19 named semantic corruption controls must reject on the
expected reason. See `summary.json` for actual commands, attempts and source hash.

The initial owner positive's inherited small-image flag remains unqualified;
the current matrix restored the actual denial. Both build-only failed batches
remain in the producer record and launched no guests. The first consumer test
incorrectly hashed argv alone; producer native_smoke.py writes a complete command
object with indent2/newline. The checker now recomputes those actual bytes. That
host-only failure is retained and never triggered a guest or changed engine code.

UL-082 remains active. The current old selector/timeout notes are superseded by
this exact review, not by updating the immutable candidate. Next Aether work is a
matched small-write retirement producer contract/profile; next userland work is
safe repeated-context/provider integration retaining actual progress even if close,
retirement, reopen or response fails. Do not reset observer/error history, retry
uncertain mutations or infer quiescence from endpoint closure. Namespace operations,
service idle/lifecycle delivery, matching sys-init and persistent Zsh/packages/ISO
remain open. Reader sign-off and source/full-native/whole-stack/power-loss coverage
are explicitly pending, not inferred from this checker.


## Approved lifetime service implementation,2026-10-20

The maintainer explicitly approved the separate fixed eight16-byte native profile.
New fs_lifetimes build selection spans policy/bridge/service/entry and retains the
AFSRPC01 frame and72-byte native result. Default one-write builds and old sealed
delivery remain unchanged. Count eight provider calls monotonically; no client or
handle close can restore that budget. Every successful bridge write verifies its
16-byte readback, consumes/nulls its C context, passes original progress to the
trusted16-byte retirement hook, and opens a fresh context before admitting another
write. The immutable dataset now outlives its derived context. Post-write read/
retire/reopen failure returns overall positive errno with original SYNCED TXG/
staged/state retained; policy retires immediately, attempts at most one error
reply, then endpoint cleanup. Never retry unknown effects or clear observer history.
Failed C writes do not retire or reopen. Reopen-owned error outputs are consumed;
void-close nulling violations fail stop. Existing grants/workers/32 observations/
8192-page backing/controller4096 and writer60s6000/readers30s3000 bounds stay fixed.
Actual typed-C/Rust fault and omission checks precede native selection; original
full-file/export/media/fresh-reader/cleanup oracles remain required separately.
No native execution, service publication, independent reviewer or R1 claim yet.


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


Namespace host/object result2026-10-19: the separate36-member candidate manifest
is `9d504603cac15be48e6a45dd266baae27c23b1851477a5fa1d27e44a4e0dc7d3`;
object `d54182a8758b0e153c6f056460987497e6397c74c6b51c284b148e86fcdf8bdc`.
All8 actual-entry tests/5 compiling omissions, strict formatting/Clippy, target
export/import/ABI checks pass. Old default/lifetimes checker passes on changed
shared sources. Initial environment/Clippy failures and an aborted host FFI mutant
are retained compactly in Aether's `docs/evidence/fs-service-namespace-2026-10-19.json`.
The final fixture records consume-before-reply rather than panicking across C FFI.
All owned host builds are disposed; current sealed candidates remain dependencies.
Native acceptance remains pending, distinct from unchanged25/27-member receipts.


Namespace native result2026-10-19: Aether's exact36-member selection passes13
fresh guests with all9 images admitted before launch. Create788/798,
rename804/814, remove820/830; fresh lost-reply and injected-close create788/798.
Independent original780248-byte file/namespace/allocation/metadata/ACL/EOF, original
export/drains/all21 cleanup/terminal0/live0/reclaims3, fresh media/guards pass.
Frozen source/tool/intake audit passes; baseline engine/controller exact, all
joined owned outputs disposed. The compact producer receipt is Aether's
`docs/evidence/fs-service-namespace-native-2026-10-19.json`. It is distinct from
independent userland/reader acceptance and does not generalize the old25-member
checker. Native partial-request, operational mixed lifetime/idle/executable/init,
persistent Zsh/packages/ISO remain open. A separate fixed eight-transaction mixed
profile has now been approved; its own qualification is still required.


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
