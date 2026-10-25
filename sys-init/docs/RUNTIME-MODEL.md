# Deterministic runtime model

## Current journal/retirement composition — decision 0163

The suite has 287 tests. Seven integration tests compose the actual JournalRuntime,
CleanedAdapter, CutCoordinator and Retirement. Mixed Cleaned/Launched and
Cleaned/Terminal receipts retire only the Cleaned member. The other member's real
reserved reclaim obligation and synthetic pending position survive retirement and
old receipt replay. Sequential completion preserves the exact journal/history.
Pending release is required separately from successful model cleanup; retirement
reinspects resource disposition. Failed release/mark confirmation closes the
coordinator and retains Applied receipts, partial tombstones and journal state.
Two source controls detect omitted release prerequisites and retirement of a
Terminal member. No new runtime algorithm is introduced. Resource inspection,
pending positions and tombstone operations are still trusted synthetic callbacks.
Native integration/provenance, sustained reuse and recovery remain open.


## Current Cleaned adapter — decision 0162

The suite has 280 tests. Nine new tests connect Cleaned observations to the actual
Model.batch and EventJournal. The adapter retains the reclaim token emitted by
Terminal and checks its executed disposition separately from a fresh resource
inspection. All four resource positions must be empty, the inspection must match
the exact source, and no unresolved disposition may remain. Both members are
preflighted before model mutation. Successful cleanup relinquishes model ownership;
retry policy may schedule a later attempt but this fixed-time cut does not launch
it. Replay performs no new inspection. Failed inspection, callback reentry, stale
generation and missing transition close without claiming successful cleanup.
Two source controls omit journal-disposition and resource checks independently.
Resource inspections remain trusted synthetic inputs, not native disposal evidence.
Pending release/retirement integration and native provenance remain follow-ons.


## Current Terminal adapter — decision 0161

The suite has 271 tests. Eight new tests map bounded qualified-fact fixtures into
actual Model.batch terminal transitions and real EventJournal reclaim obligations.
Normal/fault/stop result collisions preserve kind and detail. Terminal requires
applied launch ordering and running owned generation; a busy journal denies before
mutation. Wrong post-transition kind or a missing reclaim obligation closes both
owners while preserving terminal/resource state and the diagnostic cut. Two source
controls detect result-only kind collapse and omitted kind/detail verification.
Facts remain synthetic registered inputs; this is not native raw capture or cleanup.
Historical readiness is retained metadata, not a readiness event.


## Current Launched adapter — decision 0160

The suite has 263 tests. Nine new tests connect CutCoordinator to the existing
JournalRuntime/Model/EventJournal for Launched observations. Explicit reserved
batches consume the actual pre-reserved journal ticket and block intervening
commands. Applying provider launch generates a real dependent launch obligation;
empty-effect application still has a bound journal serial. Exact replay does not
mutate lifecycle state or journal. Transition/capture failures close both owners,
with two adapter omission controls verifying the independent adapter boundary.
Source registration and launch-executed evidence remain model inputs, not native
worker provenance. Terminal/Cleaned and resource disposition remain follow-ons.


## Current pending/mixed-cut model — decision 0159

The suite has 254 tests. Eight new tests qualify exact Terminal-member pending
release/replay, retained release uncertainty and selective Cleaned retirement from
mixed cuts. Two new pending controls detect wrong-position release and false
confirmation; a new core ordering control detects Terminal-before-Launched
application. Four core and three retirement controls now run with these two.
The resource fixture serializes one synthetic pending source; this does not claim
two simultaneous native terminal captures. Cleaned application remains a model
transition without real journal/resource authority: BG-057 must integrate those
provenance and admission checks. No native source or released pin changes.


## Current retirement model — decision 0158

The suite has 246 tests, including eight new resource-disposition/retirement tests
with three embedded omission controls. A single Retirement owner validates an
exact Applied Cleaned receipt, prior phases, source-bound empty resource inventory,
applied reclaim and no unresolved obligation before marking either cut member.
A failed mark closes the core and retains started/retired progress, observed
inventory and any returned diagnostic. Exact replay marks nothing again and leaves
source history/cut receipts intact. This is synthetic adapter behavior, not native
cleanup, pending release, sustained reuse or recovery. Mixed-phase cut retirement
remains outside this initial entry point.


## Current cut coordinator slice — decision 0157

The suite now includes ten pure cut-coordinator tests (238 model tests total),
with three embedded source omission controls. Exact retained source/cut identity,
two-service ordering, six-record reservation/cancellation bounds, revalidation,
uncertain capture and replay receipts are modeled using a counted synthetic
adapter. The model runner hashes cut_coordinator.py with its other inputs.
No native provenance, actual journal integration, cleanup, retirement or reset
is implemented by this slice. BG-059 keeps those scoped follow-ons active.


Latest update: [decision 0050](decisions/0050-channel-acquisition.md) reserves
attempt/native-slot capacity before channel creation. Seven new cases bring the
suite to 228 tests and twenty-three mutation controls. Successful replies retain
both endpoints before launch binding; confirmed creation errors use local empty-
inventory cleanup. Missing/malformed replies retain unknown ownership. Channel,
native target and service generations remain independent. All calls remain trusted
synthetic replies. BG-058 next specifies and runs a fresh consuming native
acquisition/rejection/cleanup witness. Larger-graph and stop/force automation remain open.

Current update, 2026-09-06: [decision 0026](decisions/0026-control-operation-identity.md)
separates ordinary stop and shutdown when joining pending operations. The suite
now has 37 tests and three mutation controls; three new control cases cover
same-kind stop joins, conflicting shutdown intent and unchanged state after
partial-stop rejection. Earlier results below retain their historical counts.

BG-053 completed 2026-09-05 against [decision 0002](decisions/0002-runtime-model-profile.md). The model exercises service/graph policy through synthetic time and injected observations. It does not launch processes, bind sockets, call native APIs or change files. Its external test harness writes reports and runs a watchdog-protected Python test process.

[Model source](../prototypes/runtime_model/model.py) · [independent test expectations](../tests/test_runtime_model.py) · [recorded results and source hashes](evidence/runtime-model-2026-09-05/results.json).

## Run

From the repository with Python 3.11 or newer:

```sh
python3 scripts/check-runtime-model.py
```

The harness runs the suite, three negative controls and a fixed benchmark under a 30-second subprocess watchdog. Failure or timeout returns nonzero and writes a failure report. Normal results go to `out/runtime-model/results.json`; use `--output PATH` to choose another report. Zero discovered cases and mutation controls that produce an infrastructure error rather than the expected assertion failure are rejected.

For focused debugging, without the outer watchdog or benchmark:

```sh
python3 -m unittest discover -s tests -p test_runtime_model.py -v
```

## What passed

34 test methods, including all model-designated families T01–T09, T11–T16 and T18–T21, plus a limited T17 operation-observation case. T07 includes all 24 permutations of a four-observation cut. A fixed 100-seed corpus injects 20 observations per trace; failures print seed, synthetic timestamps, input events and final status. These are bounded checks, not exhaustive proof of all state spaces.

Three isolated in-memory mutations were detected by existing test expectations: accepting stale readiness, resetting retry counts on readiness, and allowing replacement before reclaim. No mutant behavior is an option in the model API.

The first deadline-jump test exposed fresh stop budgets being assigned after an already-expired startup deadline. Cancellation now respects the earlier deadline, and a jump past escalation leaves ownership unresolved rather than inventing successful cleanup. Other checks cover deadline-versus-one-shot exit, stop rejection without side effects, retry admission after dependency loss, late launch completion and invalid-batch atomicity.

A fixed eight-service dependency chain ran 1,000 start/stop traces (26 supplied requests/observations each) in **1.438 seconds**, with **693,894 bytes peak traced Python allocation** on the recorded Python 3.14.7/macOS arm64 environment. Tracemalloc was enabled during timing. This is a single host-only model baseline, not RSS, a native-init footprint, or a production speed claim. Python 3.11 compatibility is intended but was not executed on that interpreter here.

## Model contract and bounds

`Service` declares the finite graph. `Model.start`/`stop` return an operation ID and requested effects. `Model.batch` takes at most four observations and optional nondecreasing synthetic time. `status` returns a detached snapshot. Events identify kind, service, launch generation, manager epoch and bounded payload. Completion events are synthetic trusted-adapter observations, not an authenticated wire protocol.

Effects are `(action, service, generation)` for launch, stop, force and reclaim. They never imply completion. Observation publication is represented by bounded manager records and status snapshots, not a network sink. An early reclaim acknowledgment without an outstanding reclaim request does not release ownership. Force is also only a request: missing confirmation leaves incomplete/unknown cleanup. Recovery from that uncertainty needs a future explicit reconciliation contract.

Bounds: 8 services, 16 edges, 2 automatic replacement launches per activation, 64 diagnostic records, 64 retained operation records, 256 supplied requests/observations per model instance. Diagnostic overwrite increments a loss counter. Graph and batch input validation precedes mutations. There is no unlimited arbitrary payload ingestion or wall-clock sleep in the model. A graph revision and epoch remain fixed for its lifetime.

Start requests join an identical active activation without extending its deadline. Stop validates required consumer scope before changing intent. Stop may supersede a start when its scope includes that active operation; broader concurrency/replay semantics are intentionally deferred. Restart is requested through the stop transaction and emits a new launch only after cleanup. Shutdown closes this model's admission and stops only its declared scope.

## Coverage limits and next work

- T09 models one abstract setup transaction with denied/failed completion and reclaim. It does not implement individual OS restriction steps or prove their rollback.
- T10 readiness framing, inherited descriptors and sender authority are untested here; BG-040/BG-054 own real fixtures.
- T17 models stable operation observation and joining. Client disconnect, authenticated requests and replay deduplication need BG-050.
- T20 models bounded records and untrusted text separation. Real slow/broken pipes, subscribers and filesystems remain BG-044/BG-054.
- Model events can request authority-denied outcomes; they do not enforce real privileges, process containment, cleanup or memory zeroing.
- Aether's existing lifecycle proof is unchanged. No native boot tests were rerun because native code and ABI inputs did not change.

Next is BG-054's real-child harness decision and fixtures, coordinated with BG-040 readiness transport and BG-028 ownership. Accept those contracts before building a real host supervisor. The production language, process layout and distribution integration remain open.

The canonical [source-checkout manual](man/sys-init-check-model.1) documents the
current invocation, streams, failure paths and artifact lifetime. See
[documentation coverage](DOCUMENTATION-INVENTORY.md) for review status.

Decision 0109 bounds inner host/model worker capture to 4 MiB of combined raw
stdout/stderr and 30 seconds through pipe drain/exit. Host capture failures
replay diagnostic stderr only; model failures keep passed/error fields and
include bounded prefixes in error detail. Capture exceptions clean the owned
group and reap the direct child; abrupt outer termination and detached groups
remain separate gaps. The helper is included in successful source hash maps.
See decision 0109 and the updated host/model command manuals.
