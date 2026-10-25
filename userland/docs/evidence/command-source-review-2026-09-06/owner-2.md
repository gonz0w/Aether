# Deterministic runtime model

Latest update: [decision 0039](decisions/0039-event-journal.md) implements an
isolated event journal. Twelve new cases bring the suite to 146 tests and thirteen
mutation controls. Twenty-credit cut reservations, occurrence identity, retained
supplied cause and explicit unknown/capture failure are tested. The journal does
not call Model.batch or infer provenance. BG-057 remains active for lifecycle
cause retention and observation admission; native result mapping remains open.

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
