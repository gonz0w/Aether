# Native home producer — UL-007/081/082

## Selected scope — 2026-10-24

The maintainer requested continued service/client integration until blocked.
Following [completed activation](FS-HOME-ACTIVATION.md#observed-integration-and-continuation),
this record owns one offline native producer: fixed diagnostic home/file
bootstrap, retained bootstrap observations, matched native entry/launch carrier
and C import/lifecycle consumption. Owner: userland/system integration agent.
Selection base `252d6936ffa97142cd0d9887e74ea659b78f4faa`; target
`codex/consolidate-system`; use `codex/fs-home-native` after reviewed documentation
closure and record its exact base before source changes. Main stays unchanged.

Apply root PROJECT/METHOD/STATE, selected Codex routing, DEVELOPMENT, component
guidance/quality, Foundations O/I/E and scoped CE/CD/CR/CA/TD/SE. Existing pins,
seals, old wires/layouts and execution dispositions stay exact. No guest is
selected. Full engine/helper/image composition follows this finite producer;
installation, login, initial CWD, libc/routed writes, rollback, durable replay,
packages, Zsh/ISO and release qualification remain outside it.

## Fresh host qualification input routing

[Issue64](https://github.com/gonz0w/Aether/issues/64) owns current producer/helper
qualification. Run the maintained producer and helper checkers on frozen current
source; a historical qualification does not cover changed client or descriptor
implementations. These host checks select no guest or complete engine build.

The producer reuses the exact retained AF07 compiler recipe as provenance. Its
live product includes must select this checkout's maintained headers. The one
historical service-delivery source include selects the maintained filesystem
service directory. Only the two exact disposed per-run resource/allocation
overlays may be omitted. Other missing inputs, foreign aliases, unknown path
flags and changed compilers fail before header compilation.
The exact historical freestanding empty-sysroot operand uses a verified empty
directory under the checker's owned workspace. Record that route; do not mutate
the retained SDK or accept another missing or nonempty sysroot.

Dependency paths use the existing explicit retained-root declaration and its
fixed allowlist. Source ROOT remains this checkout. Keep the original receipt,
recipe and macro-prefix-map output values unchanged; fresh evidence records both
requested and routed compiler prefixes and the exact omitted overlays. No SDK,
old seal or general source-migration catalog is rewritten.

From the system root, first run the routing regression checks, then each selected
qualification under its owned runner and source/input/tool freeze:

```sh
python3 -B -m unittest discover -s tests -p test_home_native_c_prefix.py -v
PYTHONOPTIMIZE=1 python3 -B userland/experiments/filesystem-service/check-home-native.py
PYTHONOPTIMIZE=1 python3 -B userland/experiments/filesystem-service/check-home-probe.py
```

Each qualification retains its 300-second aggregate, at most 180 seconds per
child, 4 MiB streams and owned cleanup. Keep each failure and record the fresh
host SDK selection and actual tool identities; old host/SDK observations do not
qualify the current environment. A complete engine construction, native fit and
execution disposition remain separate prerequisites.

## Required behavior before implementation

Select `fs_home_native` explicitly, requiring matching home policy/wire/activation,
runtime, mixed, directory and metadata dependencies. Old defaults retain their
symbols and72-byte service/136-byte launch layouts. New private symbols and
integer-only C carriers must never be interpreted as those old layouts.

The trusted entry opens the same exclusive writable SPA/context and constructs
one Owner with trusted labels1000/1000. It uses the authenticated existing endpoint
identity, distinct source/recipient sessions and an administrative source grant
with rights15 (no metadata16). Fixed components `home` then `probe` are diagnostic
fixture names under `testpool_zstd/x86_64`, not an installed filesystem layout.

Call MakeDirectory(home) once, retain its observation immediately, look up home
with rights15 and validate actual non-root directory identity before Create(probe).
Handle inequality cannot establish node inequality. Factor/share attach_home's
existing validation in a narrow `validate_home_source`; preserve old attach_home
error precedence. Then Create once, retain its observation, verify an empty regular
file lookup and close that temporary handle before existing home activation.
Existing names fail; no reuse-as-success, rollback, delete, retry or reconnect.
Root3/home15 remain authoritative. Four retained handles/two connections leave12
of16 after temporary verification close; no new authority table or grant policy.

Provide selected `namespace_observed` sharing the existing namespace body. It
returns its unchanged `Result<Completion, Error>` plus the original typed
`Backend::mutate` result, captured immediately after return and before Owner
normalization/refresh/retirement; None means no provider invocation. This is not
raw C-byte retention: the bridge has already decoded its provider. Preserve
successful provider completion separately when parent refresh returns WriteFailed,
and malformed typed completion separately from InvalidCompletion. Observation is
transient copied diagnostic output, not an Owner field, authority or budget.

This new finite selection enforces nine TOTAL provider mutation attempts through
the existing Owner counter, including two bootstrap operations, and96 service
requests. Capture final mutation count before Owner shutdown into a selected Rust
Report field. Do not reset counters during context reuse or bootstrap-to-loop
handoff; failed/unknown provider calls count, pre-provider denials do not. Existing
runtime usize::MAX and old8/64 selections remain unchanged. Test tenth mutation
before effects and97th request before receive/dispatch. Historical nine/96 workload
bounds are not claimed to have been existing library constants.

## Private output and cleanup contract

New `BootstrapReceipt` is96 bytes/alignment8: provider disposition, returned
disposition, error kind, signed error value, returned completion(error,TXG,staged,
state), original typed completion(same four64-bit fields). Provider0/1/2 means
not invoked/reported completion/Lost; returned0/1/2 means unreached/success/error.
An unreached slot is allzero. Inactive completions are zero; returned success or
WriteFailed carries returned completion, provider1 carries exact typed fields
even malformed. Diagnostic malformed fields never become successful authority.

`HomeResult` is320 bytes/alignment8: seven64-bit words(version1,bytes320,failure
phase,error kind,signed error value,flags,total provider attempts), two receipts
at56/152, unchanged ServiceResult72 at248. Error kinds1..16 map in order to
Invalid,Denied,Stale,Full,Closed,NotDirectory,IsDirectory,InvalidMetadata,
InvalidCompletion,Backend,Clock,WriteLimit,Poisoned,Uncertain,WriteFailed,Unsupported.
Backend retains its signed code; other error values zero. WriteFailed retains
completion fields. Phase0 success,1preflight,2open/setup,3admin attachment,4mkdir,
5home lookup/validation,6create,7probe verification,8temporary close,9activation.
Ordinary loop failures retain existing ServiceResult semantics, not invented
bootstrap errors. Stop::Provision retains its exact Error in the header.

Flags1 activation_called,2ordered_required,4endpoints_accepted,8close_attempted,
16callback_entered,32entry_entered. All are monotonic within this one invocation.
Calling activation is distinct from entering its request loop; Report.ready and
requests describe actual transfer/loop progress. Accepted/attempted flags never
claim successful native settlement. Readiness uses existing independent RuntimeUtc
check and ready syscall after both per-operation UTC checks. Readiness/syscall
failures stay in existing reply-loss status; no remapping of the original status.

`HomeLaunchState` is384 bytes/alignment8: existing six-word launch prefix48,
HomeResult320, startup close results at368/376. New symbols are `aether_fs_home_run`, `aether_fs_home_launch_serve`,
`aether_fs_home_engine_run` and `aether_fs_home_engine_import`. Their private
`home-native.h` types are distinct; Rust shares integer carriers in
`home-native-result.rs` between its selected entry and launch sources. Reject wrong version,
size, unknown flags/tags and contradictory inactive fields. The selected service
ABI takes SPA,dataset,length,reader,writer,uid,gid,out,out_bytes (nine arguments);
admin rights are fixed15. Output extent must be320. The trusted caller initializes
version1/bytes320 and every other field zero once in place. The callback accepts
only that canonical initial output, latches16 before calling the entry, and rejects
reentry before any output reset or effect. Entry accepts canonical flags0 or16,
latches32 before ordinary preflight and never reinitializes the carrier. Repeated
entry rejects before acquisition or overwriting prior evidence. Service-result
projection must never overwrite bootstrap receipts. Do not zero Rust Option/Owner
or allocate a large carrier temporary.

Set accepted4 before constructing the endpoint owner or making any backend call;
set close_attempted8 before attempting both closes, and retain their actual results.
At a valid service entry, ownership of both endpoints transfers exactly once;
all normal returns retain both actual close attempts separately from SPA/context
Drop and export. Launch startup closes only endpoints known not transferred.
Contradictory evidence never authorizes a second close or inferred reclamation.
Invalid output storage/extent returns EINVAL without acquiring endpoints; trusted
caller retains them. A canonical unaccepted preflight outcome has no receipt,
service, count, order or close evidence and retains the explicit phase/error.
Launch may startup-close only its own known pre-call rejection or a fully validated
canonical unaccepted outcome. The C SERVICE phase bit means callback entry, not
endpoint transfer. Missing/malformed/contradictory outcome cannot prove handback.
Preserve existing nonzero-token/alias checks. Panicabort is not cleanup or
durability evidence.

All FFI pointers are aligned/live/exclusively borrowed, output disjoint from
SPA/dataset, dataset1..255 bytes plus NUL, and code/SPA resident through synchronous
return and original ordered drain/export. No concurrent/reentrant mutation,
teardown or retained pointer. Native holder checks remain authoritative.

Derive a monotonic ordered obligation from both receipts: only no invocation or
canonical reported unassigned failure(error1..4095,state0,TXG0,staged0) establishes
no assigned effect. Any completed/committed, Lost or malformed typed result
requires the original ordered oracle. An earlier obligation cannot be cleared by
a later unassigned result or ServiceResult.TXG0. Activation follows two successful
bootstraps and always requires ordering. First-operation canonical unassigned
may skip that oracle, which itself requires completed work. After actual export,
invoke it whenever required, even on bootstrap-only failure. Preserve bootstrap,
service, export/order and cleanup errors independently. EXPORTED means actual
export plus required ordering succeeded; no false clean/reclaim conclusion.
C consumption validates/recomputes obligation from both receipts plus activation,
not flag2 alone. Unknown tags/malformed/contradictory carriers or a cleared required flag
retain a protocol error and conservatively require ordering after actual export;
they can never select the no-order path. Reentry rejection preserves all previous
callback/entry/accepted/close evidence without resetting it.
Canonical provider Lost/returned Uncertain is valid typed uncertainty requiring
ordering. It is not an unknown tag. If protocol invalidity and export/order failure
coincide, preserve the exact original carrier bytes and separate engine error/phase;
protocol invalidity remains recomputable by the same validator. Return EPROTO on
protocol failure after successful lifecycle; otherwise existing export/order error
priority remains. There is no second stored protocol-code field or overwritten
bootstrap diagnostic. Only canonical entry preflight flags32/direct or48/callback,
phase1/Invalid1/value0/all other fields zero proves unaccepted handback. Callback
validation rejection without entry is missing transfer evidence, not handback.

Keep original common C sources and old hash pins unchanged. Generate the new
selected lifecycle/importer from hash-pinned original bodies with exact unique
checked replacements for header/types/symbols and the ordered predicate. Retain
recipes and reject changed anchors/hashes. Share existing lifecycle logic, not a
parallel policy model. Never cast384 as136 or overload service TXG with bootstrap.

## Resources, security and simplicity

Protected state is the sole Owner ledger/provider lifetime and ordered export.
Requests cannot select bootstrap authority, labels or names. Preserve stale,
partial-effect, malformed-result, clock, exhaustion and cleanup failures without
replay. Receipts survive normal teardown only; process crash recovery is outside
this experiment. No new dependency, native capability, service, worker or channel.
Preserve owner49152 code/8192 resident/8184 usable stack/128 backing pages,
engine8192 pages, seven domains/twelve channels/35MiB, writer60s6000 ticks,
reader30s3000 ticks. No Runtime field growth; prior owner stack margin24 bytes is
not permission. Measure changed final consumers; object frames are not native peak.

Simpler alternative: call run_home and use the old single service completion.
It loses irreversible bootstrap effects before greeting or on parent refresh,
and can skip ordering. Reuse existing namespace/delegation/activation/dispatcher
and original C lifecycle; add copied observations and distinct private carriers.
No general provisioning, recovery framework or second mutable budget. No obsolete
sealed path can yet be removed; preserve it until a scoped replacement consumer.

## Verification selected before code

Write tests before production and retain actual compiler red without claiming
semantic execution. Focused real Owner tests exercise original/returned outcomes,
no-provider failures and root-identity substitution; actual native entry with real
bridge and typed C substitutes exercises bootstrap, two retire/reopens, publication,
greeting loss, closes and retained receipts. Extend the selected non-root context
fixture honestly. Actual C selected importer/lifecycle bodies run under host
instrumentation; compile original provider against pinned OpenZFS/native headers.
No host substitution is actual ZFS execution or native authority qualification.

Cover first unassigned; successful mkdir followed by unassigned/committedTXG0/
completed-but-failed/Lost/malformed create; refresh failure retaining both views;
clock before either op/ready; alias-root/type/empty/probe-close handling; both
greeting/publication failures; capacity and nine/96 caps; old profiles/defaults,
missing selections and wrong header/layout/symbols. Require compiling named
controls for overwritten first receipt, lost uncertainty, skipped ordered check
and quota bypass. Test temporary handle release by real capacity, not invented
production failure hooks for unreachable close errors.

Use Rust1.98/2021 fixture Rustfmt/strict Clippy and reviewed unsafe boundaries;
new C17 strict Clang21.1.8/UBSan/format; target object/layout/local-frame evidence.
Register before execution the root command
`PYTHONOPTIMIZE=1 python3 -B userland/experiments/filesystem-service/check-home-native.py`.
Use pinned owned-process runner,300-second bounded unit suite, frozen inputs,
compact all-attempt receipts and owned-output cleanup. Changed final Owner/service
consumers require activation190 and home-owner891 gates once on final core bytes;
focus new tests during iteration. Full engine handoff later requires broad checks,
actual complete fit and matching intake; current objects do not substitute.

Update component README, Experience CLI scope, quality inventory, workflow and
STATE; scoped CLI/pin/inventory/link checks and separate contract/source/control/
evidence/reader review before normal-hooks consolidation integration. No source
change during qualified runs. Actual SDK/tool absence blocks relevant coverage.
Full matched engine/helper/image preparation is the continuation, before a concrete
new guest disposition; no previous approval is renewed by this record.

## Status

Implementation branch base is `23fabc8aa8bae4f260c447347f86379df48b8074`,
tree `707a58222d5564216d8f5552484f2e56cb90d73f`, integrated with normal hooks
and fast-forward target readback before any source/test changes. Branch is
`codex/fs-home-native`; target matches that base, main remains78c13fc5.

Contract prepared before source/test changes. Separate read-only temper_reviewer
contract/reader review found no remaining blocker after the monotonic ownership
flags and C recomputation rules were added. It checked source contracts, closure
identity,18 links/anchors, workflow budget, whitespace, all four retained quality
children/cleanup and pinned simplicity inputs. This is ordinary peer examination,
not implementation or native acceptance. Requested reviewer gpt-6.1-sol/high;
provider role/model/effort metadata unavailable, so routing remains unverified.
Requested/observed routing remains unverified as in AT-002; record each bounded
assignment. At that pre-code checkpoint no tests, C layout qualification or
implementation acceptance existed. Current implementation status follows below.

[Selection checks](../evidence/filesystem-home-native-2026-10-24/selection-checks.json)
retain workflow41/37/191, coordinator output/owned-output removal and a failed
simplicity-manifest path discovery. Its incorrect receipt-name filter lost child
records; [corrected receipt capture](../evidence/filesystem-home-native-2026-10-24/selection-checks-02.json)
retains all four passing reference children/three pins before owned removal. The corrected
documented inputs/SHA256SUMS and four members match the pinned digest. No product
test or implementation claim follows from those checks.


## Implementation checkpoint — 2026-10-24

Two bounded implementation assignments requested the recorded temper_implementer
mapping gpt-6.1-sol/high, fresh agents home_native_entry and home_native_c. The
lead owns shared Owner/service policy, tests/checker, records and integration;
entry agent owns new native/launch/carrier/typed fixture/check module, C agent
owns the new header/source selector/host lifecycle fixtures/check module. No
recursive helper, guest, main or permission change. Actual provider model/effort
and role-discovery metadata remains unavailable; no routing verification claim.
Separate temper_reviewer is read-only and did not author implementation.

Attempts01/03 retain missing policy API compiler red.01 overlapped creation of
unrelated new test files and does not establish a whole-closure freeze;03 was
repeated with both implementers held. Frozen02 retains absent new native/launch
source and C-header compiler red: their new tests were not compiled or executed.
04 passes five real policy methods/host-target builds.05 passes those plus strict
Clippy and two controls, then the quota mutant fails the matching service limit
const guard; this is not a semantic pass.06 retains a passing companion-guard
control; [exact focused inventory override and companion identity](../evidence/filesystem-home-native-2026-10-24/focused-policy-invocation.json)
make its scope explicit. Final control instead omits only the namespace quota
branch. One inline-coordinator unmatched-parenthesis setup failure is retained in
that note; it ran no child. No production expectation was weakened.

07 passes22 selected original C lifecycle cases, an actual compiling skipped-order
control, target layout and original importer/provider-header builds.08 is a new
meaningful semantic red: contradictory inactive attempt count incorrectly skipped
ordering, rejected by HOME_ORDER_ORACLE before header tightening.09 first whole
producer attempt passes policy and47 C cases/control, then fails because the lead
supplied nonexistent zpl-namespace.c for Create. Actual provider is zpl-mutate.c;
keep09 failed and fix only that input selection. All named attempts retain input
verification and complete owned-output removal, with their own scope/rows.

Entry local attempts are retained separately as entry-local-attempt-01..12.json.
They include Clang DYLD contamination, wrong host trap target, strict Clippy,
fixture EOF/disconnect expectations, control-marker interception and fixture close
injection failures. Passing local12 has14 entry/three launch methods and compiling
controls with UBSan/strict target builds; later callback guard/fourth launch test
still require the final common gate. These are focused local results, not whole
producer qualification. Review replaced an output-field raw pointer that survived
whole-output mutable borrows with a safe scoped optional field borrow, armed only
after bootstrap; early closes set the carrier flag explicitly before either trap.
No panic-abort cleanup claim follows.

Existing namespace C bridge always returns typed Ok(Completion), including C error
status. Therefore real-bridge C negative status is tested as malformed typed
completion; genuine typed Lost is tested through real Owner's Backend seam, the
actual receipt converter and C consumption. No fake production Lost hook/API is
added. Caller receipts explicitly stop at the typed bridge boundary.

Source review also requires C/Rust to preserve the existing service state3 unknown
failure sentinel, reject unknown states/oversized staged counts, and enforce no
requests before ready and total attempts no greater than two plus requests. Final
actual Rust-to-C carrier-consumption tests and malformed service cases are being
added before final qualification. Full affected owner/activation checks, final
source/evidence/reader review and normal-hooks integration remain pending.


## Final offline results — 2026-10-24

[Canonical attempt13](../evidence/filesystem-home-native-2026-10-24/attempt-13.json)
passes156 owned child outcomes under one300-second suite. Five actual policy
methods,19 native-entry methods, four launch methods and69 C lifecycle cases
pass, with eight strictly compiling semantic controls and explicit packed-layout/
legacy-pointer compiler denials. Strict Rustfmt/Clippy, instrumented C17/UBSan,
host and target libraries/objects/layout/symbols pass. The actual entry's carriers
are consumed by the actual C header validator, including both bootstrap results,
clock/greeting failures, known service Unknown3, malformed progress and byte
preservation. The separate converter/Owner/C Lost coverage remains accurately
scoped above. Actual original mkdir/Create/metadata providers and selected importer
compile with196 recorded native importer/provider dependency inputs (190 headers,
six C sources), with pinned SDK/resource headers checked. Host substitutes do not
execute OpenZFS.

725 frozen input-map entries comprise723 retained inputs plus two disposed generated
C bodies, exactly reconstructable from unique hash-pinned recipes. Eight pinned
tools, three native Rust libraries, UBSan and resource headers verify. Local target
stack observations are object scope, not a complete engine or native peak proof.
No production/test/checker changes follow13. Owned generated roots are absent.

Whole11 first passed147 child checks. New semantic red10 reproduced rejection of
the existing service Unknown3 diagnostic before its fix; red12 reproduced accepted
contradictory progress before the final finite state rules. C EPROTO in those host
fixtures is the host errno constant (100), not a claimed native errno witness.
13 preserves valid committed state1/TXG0 failure, completed state2/nonzero TXG,
and known Unknown3 failure; state0 requires zero progress, any nonzero progress
requires ready/request, and inconsistent ready/count/limit/state fields reject.
Rust diagnostic retention of malformed original typed bootstrap fields is distinct
from C's conservative protocol-error/ordering decision. All prior failed attempts
remain failed; successful compiler-red02 is a successful negative reproduction,
not a failed suite or semantic execution. Earlier untracked prototype host-wrapper
bytes are not replay artifacts; compact command/hash/failure records remain.

Affected final consumers pass once on these final core bytes:
[activation attempt08](../evidence/filesystem-home-activation-2026-10-24/attempt-08.json)
passes190 children including old profiles/entry guards;
[complete owner attempt23](../../../sys-init/docs/evidence/home-owner-fit-2026-10-24/attempt-23.json)
passes891 children. Its actual complete owner is47384/49152 code,
3688 Runtime+4096 workspace=7784/8192 resident, and8160/8184 conservative stack.
Event224/Exchange192 alignment8, old AF07/AF08 fits and all input/cleanup checks
pass. The24-byte modeled stack margin belongs to sys-init's fixed owner; this
new engine entry uses its existing separate engine stack. No native interrupt/
peak, complete engine, guest, recovery or release conclusion follows.

[CLI/quality attempt01](../evidence/filesystem-home-native-2026-10-24/cli-quality-attempt-01.json)
passes six CLI/shared-runner scenarios plus workflow41/37/191, and four component
quality children/three offline pins. The operational/blocked scenarios explicitly
inject failures into the unchanged shared runner, not the product callback.
All owned CLI/quality output is removed; preexisting quality roots remain. The
small CLI driver/recipe is retained for peer readback before its removal. No
unrelated full suite was repeated; broad checks remain selected for the following
actual engine/helper/image integration handoff.

Separate temper_reviewer source/checker/control/evidence review has resolved all
identified findings. It verified156 outcomes,723 retained inputs, reconstructed
two generated C bodies/eight mutant recipes, tool/library identities and cleanup.
Final consumer/updated-reader review and source/target integration readback remain
before normal-hooks consolidation integration. This is ordinary peer examination,
not human/specialist/native or affected release-owner acceptance.


## Integration readiness

Final separate peer source/control/evidence/reader review passes with no unresolved
finding. [Lead-persisted peer receipt](../evidence/filesystem-home-native-2026-10-24/peer-review-checks.json)
SHA256 `3b30fe12272cff1a72e8c94a9112986fbbf74e904650c046b568b5bf77985632`. It binds producer13, owner23, activation08 and
CLI/quality01;29 links/anchors and the final corrected reader claims verify.
No suites were repeated by the reviewer. Requested reviewer/model/effort versus
unavailable actual routing metadata remain explicit. The CLI driver was read/hash-
verified against its retained recipe, then removed. Final workflow41/37/191 and
whitespace pass after the reader corrections. Exact staged source blobs, target
identity, normal hooks and fast-forward readback follow before observed closure.

307 qualified repository source blobs from the producer and both consumer maps
match the staged Git bytes. Integration target still equals the reviewed base;
main is unchanged. No generated SDK/source/object bundle is staged.


## Observed integration and continuation

Normal hooks and fast-forward integration completed at
`37be3401b3961769cab026449737a021e3e78b28`, reviewed tree
`be41161894bea5bf09663bf7fa68fdef82018274`. Consolidation readback matches;
main remains `78c13fc5f5329bb590c2ab4772f2e1e2372dc067`, checkout clean.
This finite offline native producer is complete.
[AF09 engine/helper/image preparation](FS-HOME-PREP.md) owns the next selected
offline composition, actual resource fit and independent reader inputs. No guest
was run and no earlier execution disposition is renewed.
