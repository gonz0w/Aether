# Home service activation — UL-007/081/082

## Selected scope — 2026-10-24

The maintainer requested continued service/client integration until blocked.
Following [the integrated home owner](../../../sys-init/docs/decisions/0224-home-owner-fit.md),
this record owns the next finite producer seam: explicit AF09 activation around
an already provisioned home handle, with real service/client host tests and target
libraries. Owner: userland/system integration agent. Original base
`77901cba77142cc6404b537505ea65472a483dbc`; intended integration target remains
`codex/consolidate-system`, with an exact implementation base recorded before code
following documentation closure. Use branch `codex/fs-home-activation`.
Main integration, push, guest and release remain unauthorized.

Apply root PROJECT/METHOD/STATE, the selected Codex routing profile, DEVELOPMENT,
userland guidance/quality, Foundations O/I/E and local CE/CD/CR/CA/TD/SE. Existing
release pins, old profiles/wires and sealed artifacts remain exact. This is one
usable next task: the dependent owner can start receiving two valid grants after
trusted readiness publication, including explicit failure outcomes. It is not a
runnable matched native image or native readiness acceptance.

Read-only continuation analysis by separate `temper_analyst` found no required
installed-layout/login/admin decision blocking this seam. Requested fresh mapping
was gpt-6-astra/high; actual role/model/effort metadata was unavailable. No code,
tracker, build or VM change was delegated. The real current native fixture has no
home; this scope consumes a live source handle supplied by its trusted caller.

## Contract before implementation

Add an explicit `fs_home_activation` selection requiring matching AFSRPC09 service
bytes. Old selections retain their existing root-only `run`; unselected wrappers
still reject AF09 with their existing diagnostic. Selected home activation rejects
old service dependencies and exposes a home-specific operation, not the old root
activation API. The actual native entry remains unmatched and must fail to compile
if accidentally paired with the new wrapper; do not silently activate it.

The new wrapper accepts the existing Owner/channel, authenticated source peer,
opaque live source Session/home Handle, recipient peer/nonreused epoch and one
bounded native-ready callback. Forward directly to existing service::run_home and
Owner::attach_home. Never duplicate grant derivation, storage policy, request
parsing or the service loop. Root3/home15 remain enforced by the authoritative
Owner; paths, UID/GID and copied handle labels supply no new authority.

Both grants must be attached successfully before publication. Preserve publication
BEFORE the first greeting send: a64-byte greeting cannot fit in the native32-byte
queue until the dependent client starts. On first send validate exact magic,
zero status, nonzero matching epoch, root token1/directory kind and reserved words;
publish exactly once before calling the channel. Validate the second greeting as
home token2 with the same header constraints before forwarding. Do not buffer two
greetings or delay publication until the second send. Both grants are typed and
attached before either send; validation of the second frame happens when it is
emitted. Native readiness denotes prepared attachment, not completed greeting
transfer. Report.ready remains false until BOTH complete sends. A retained ready
bit after loss is not a live/current client; consumers must still validate native
liveness and both grants. No second publication, replay or rollback is inferred.

Latch every malformed greeting, callback error and send error. Return original
negative callback/send errors; normalize only unsupported positive callback status
to-5 as the existing wrapper does. A latched wrapper rejects later sends without
callback or transport effects. After both greetings, ordinary reply bytes pass
unchanged, with the same failure latch. Receive/close delegate existing obligations;
Report cleanup contains actual channel closes, distinct from backend/native
settlement. Source provision failure/epoch0 has no publication, send or request.
The consumed Owner still owns all source/recipient handle teardown and backend
Drop. No source grant is revoked by closing an independent alias.

Callers retain the existing bounded/nonreentrant/non-panicking callback and UTC/
readiness policy obligations. This generic wrapper adds no native trap, clock,
FFI, unsafe code, global state, heap, worker, channel or service. The actual native
caller will later preserve its existing RuntimeUtc check and ready syscall. Keep
its old entry/phase/result ABI and flags untouched now.

Prefer a small selected module with one explicit greeting/failure state and no
persistent frame buffer. Preserve old activation implementation and its direct
cases. Mirror service::run_home's seven explicit source/grant parameters plus the
existing readiness callback; a single local Clippy arity exception, documented at
that function, is acceptable to preserve this direct producer correspondence
instead of introducing a parameter framework solely to meet an argument count.

## Resources, security and simplicity

The existing tested source root/home plus recipient root/home consume four of16
handles and two of four connections; this leaves12 handles in that arrangement,
not a capacity increase or a claim about every later native bootstrap. No owner
Runtime field changes: its exact previous24-byte conservative stack headroom is
not spare permission. Preserve49152 owner code/8192 resident/8184 usable stack,
128 owner backing pages,8192 engine pages, seven domains/twelve channels/35MiB,
writer60s/6000 ticks and reader30s/3000 ticks. This library check measures no full
engine or native peak/interrupt stack. The subsequent complete native composition
must measure actual selected bytes again.

Protected state is the actual Owner's grant/session ledger and readiness ordering.
Untrusted requests cannot choose source handles or invoke administration. Failure
before attachment must not publish readiness; loss after publication must not
claim greeting completion, replay an effect or hide actual cleanup. Host callbacks
are injected facts, not native authority/timing proof. Native service remains
trusted and bounded; this does not provide per-client availability or crash recovery.

Simpler alternative: keep the AF09 rejection or reuse root-only activation. The
first cannot start the matched home owner; the second skips the second greeting
contract. Reuse existing delegation/dispatcher and add one private selected send
state; do not redesign readiness or add a general activation framework. Remove no
old path while current sealed consumers still require it. The only new state is
local callback/greeting progress, with no second mutable authority table.

## Verification selected before code

Write actual missing-API tests first and retain compiler red before production.
Use the real Owner/service and Client with synthetic storage and bounded host
channels. Test successful two-grant exchange and real home write/readback while
system writes remain denied; no request before both greeting transfers. Cover
invalid/stale/insufficient/non-directory/root source and epoch0 with no publish,
first/second greeting loss and malformed fields, original callback errors,
positive-status normalization, exact cleanup/backend drop, post-greeting reply
loss, one publication and latched repeated sends. Do not hold fixture locks during
assertion failure/Drop. Join nominal service threads and retain owned-process
cleanup for all controls.

Named strictly compiling controls must reject publication before attachment,
wrong second-token acceptance and lost failure latching; add other focused controls
when required to distinguish a concrete failure. Require exact semantic markers,
not compiler/watchdog/abort failure. Compile selected host/no_std and strict
Rust1.98/2021 fixture Clippy/Rustfmt with unsafe forbidden. Existing metadata FFI
and native-entry library builds keep their audited unsafe allowances; no new one.
Run old activation's three direct methods on AF07/AF08, missing-flag/dependency/API
and unmatched actual-native-entry denials, and the affected home-wire producer
suite. Do not repeat unchanged891 owner checks solely because the source inventory
grew: activation is outside that owner closure. Document this impact/reuse; the
next full engine/image handoff must build and measure its actual complete closure.

Register before execution, from system root:
`PYTHONOPTIMIZE=1 python3 -B userland/experiments/filesystem-service/check-home-activation.py`.
Use the existing pinned owned-process runner, one300-second cumulative deadline,
frozen source/tool/native-library inputs, all-attempt compact results and exact
owned-output removal. Preserve actual commands/failures/control recipes and small
logs, not full source/build/SDK/binary bundles. Shared CLI keeps stdout JSON/help,
escaped stderr and0/1/2/64 exits; no palette/native marker changes.

Update this record, component README/activation contract/Experience/quality inventory,
root workflow and STATE. Run focused pin/inventory/link/CLI checks and separate
peer contract/source/control/evidence/reader review before normal-hooks integration.
No missing runner or unexecuted target is a pass. No guest disposition is requested
by this library scope.

## Later native preparation gates

A separate matched trusted native-home entry and launch selection, real home/file
preparation, actual service/provider/full engine link and FILE/C helper preparation
remain. Existing AF07/AF08 intake/origin/geometry/seal guards must stay strict; use
a distinct reviewed AF09 preparation path. No real installed home path, initial CWD,
login/admin flow, libc/routed write, durable journal, packages/Zsh/ISO or release
acceptance is selected here.

Pre-greeting mkdir/create requires a separate exact provisioning-outcome contract.
The current names loop initializes last_write=None and records only request-loop
mutations; blindly creating before it would lose progress on greeting failure and
could skip filesystem-import.c's conditional ordered-TXG check. Retain bootstrap
completion/error/uncertainty through export, count all attempts within the unchanged
nine-mutation ceiling, and never retry assigned/unknown effects. This is concrete
implementation work, not a request to choose installed filesystem layout.

## Pre-code checkpoint

At that checkpoint, separate pre-code peer review (`temper_reviewer`) found no required policy or
contract blocker after reading actual activation/home/service/native-entry code.
It verified readiness-before-send, both attachments before publication, failure
latching, old selections, later provisioning receipts and unchanged resources.
No production or test code exists yet. Next write missing-API tests and retain
compiler red, then implement this bounded seam. Native execution, engine/C helper
activation and full source-matched qualification stay later gates.


## Implementation base and initial red

Exact code branch base/target is `9325e5a6e92e3a6695ff31a55f80494a8606cf3c`,
reviewed closure tree868537a3e86e055b8f0365b0a2326447aba167d4. The code branch is
codex/fs-home-activation; main remains78c13fc5. Six positive/failure test methods
are written before production. The current activation crate's deliberate AF09
rejection can stop the first selected build before those fixtures compile; retain
that actual compiler red rather than describing it as an executed semantic failure
or a literal missing-method diagnostic. No production code is changed yet.


Attempt01 retains the pre-production selected build red: E0080 from the existing
AF09 rejection and E0425 because root-only activation calls a service::run that is
absent under AF09. All inputs verify and owned outputs are removed; no host
semantic test execution is claimed. Implement the selected wrapper now.


Attempts02/03 retain fixture-only missing Rights import and Clippy ok().expect
issues, corrected without suppressions. Attempt04 passes all six host methods
and early-publication/home-token semantic controls, then the latch mutant fails
to compile because Failed becomes an unused variant. Keep an inert construction
in that omission so it compiles and exercises the named latch assertion; do not
count the compiler failure as a semantic rejection. Production remains unchanged.


Attempt05 passes all six cases/four compiling semantic controls and the preceding
home producer checks, then the checker tries the actual x86_64 native entry on
an arm64 host library build. Native trap registers correctly reject. Scope actual
entry positive/negative compilation to x86_64-unknown-none; keep host generic old-
API denials separately. Add no platform accommodation or warning suppression.
Wrapper host/no_std and old host tests remain required. This is a checker target
selection failure, not a semantic source rejection or a missing product runner.


## Current status and results — 2026-10-24

[Final attempt07](../evidence/filesystem-home-activation-2026-10-24/attempt-07.json)
passes190 owned child checks. All six real Owner/service/client host methods,
four strictly compiling activation controls, six inherited home-wire controls,
old AF07/AF08 activation's three methods each, old/default/sealed service/client
regressions and explicit selection/API/actual-entry denials pass. Strict host/
no_std Rustc, Clippy, unsafe denial and2021 format pass for the new wrapper/tests.
Old native entry positive/negative checks are x86_64 target-only; host generic
API probes independently establish absence without unrelated assembly failures.
All167 retained source inputs/three tools/three native Rust libraries verify
before complete owned-output removal. Selected/old generated activation-library
hashes are retained; bytes are disposed. No production source changes after06;
07 adds accurate scope wording and artifact identities to the checker.

Six cases exercise a real Client receiving both grants, home write/readback and
system-write denial; eight source/epoch failures without publication or transport;
both greeting losses;20 malformed-header rows; negative/positive callback statuses;
ordinary reply loss and failure latching/no second publication. Client cleanup0/0,
service[-7,-8] and backend Drop are checked distinctly. Nominal service thread
joins. Compiler failures02/03, noncompiling control04 and wrong-target05 remain
retained, not semantic passes. The separate reviewer found05's target-selection
problem; the corrected06/07 gates pass without production/platform changes.

The new wrapper uses one private four-state value and no frame buffer/unsafe/FFI/
Runtime field. Its direct eight-argument producer signature has only the declared
local Clippy exception. Existing root-only wrapper bodies are unchanged behind
old selection; neither new native entry nor old service/result ABI is activated.
The broad22 frozen inventory differs at activation.rs/new files; the actual
owner compile/link closure does not import activation, and its core sources/flags
are unchanged. Reuse only the unaffected owner component result after this impact
review, not a fresh all-input qualification.190 checks cover the changed activation
and its old/new guards; do not repeat891 solely for that broader inventory.
The later actual engine/helper/image preparation must build/measure its closure
and retain bootstrap mutations before any fresh guest disposition.

Source/control review by separate temper_reviewer found no production ownership,
readiness-ordering or failure blocker; its checker finding was corrected as above.
Final CLI/pin/inventory/link and separate evidence/reader review pass as recorded
below; normal-hooks integration into unchanged target9325e5a6e remains. No guest or new native
readiness/authority/peak/settlement/recovery/release claim is made.


## Final review and integration readiness

[CLI/quality attempt02](../evidence/filesystem-home-activation-2026-10-24/cli-quality-attempt-02.json)
passes six CLI children and four owned quality-reference children, including all
three offline pins and the documentation inventory. Attempt01 retained a capture-
wrapper error (StringIO has no binary buffer) after partial reference completion;
use a TextIOWrapper for the coordinator capture, without changing product code.
All exact newly owned CLI/quality roots were removed; older quality roots remain.
Workflow41 references/37 tools/190 groups and whitespace pass.

Separate peer temper_reviewer completed final source/control/evidence/reader review:
167 inputs, three tools/three native libraries,190 child outcomes, ten control
recipes, API/target guards, six CLI/four quality outcomes,24 links/anchors and
cleanup verify. [Receipt](../evidence/filesystem-home-activation-2026-10-24/peer-review-checks.json)
SHA256 `a32eba79c1046019e5d916d85c83fa085c6508b162ec37f6d86ce64da0c356cc`.
No unresolved finding remains after its wrong-target checker correction. It did
not implement this source or repeat suites; review is ordinary peer examination,
not human/specialist/native assurance. Requested reviewer gpt-6.1-sol/high and
actual unavailable routing metadata remain distinct.

No source/test/checker changes follow07. The temporary CLI script was read/hash-
verified with its recipe retained by the peer, then removed by the lead. Source
identity/target readback, normal hooks and local consolidation integration follow;
main, native authority and all resource limits remain unchanged.

## Observed integration and continuation

Integrated with normal hooks into `codex/consolidate-system` at
`252d6936ffa97142cd0d9887e74ea659b78f4faa`, tree
`afb6c6bf1387f12f641f6c449171b01db1108520`. Target/readback and clean checkout
verified; main remains `78c13fc5f5329bb590c2ab4772f2e1e2372dc067`.
This finite activation seam is complete. [Native-home producer](FS-HOME-NATIVE.md)
owns the next offline bootstrap/outcome/lifecycle integration. It must preserve
pre-greeting effects separately; this completion grants no guest execution.
