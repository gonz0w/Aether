# Control operations v0 — logical experiment contract

Status: implemented for the trusted in-process model facade under decisions 0026
and 0027, 2026-09-06. No public command, wire format, socket, native grant,
daemon or production authorization mechanism is selected. The existing model is
the lifecycle engine; its internal methods are not a remotely callable API.

Sources: [runtime R-11–R-16](RUNTIME-V0.md),
[operator research](../research/OPERATOR-INTERFACE.md),
[model implementation](../../prototypes/runtime_model/model.py) and
[native policy review](../NATIVE-POLICY-REVIEW.md). Shared
[Foundations I-01–06](../vendor/aether-foundations/v0.1.0/INTERFACES.md) and
[Experience commands](../vendor/aether-experience/v0.1.0/COMMANDS.md) constrain
future delivery; this document owns sys-init semantics only.

## C-01 Identity and admission

Keep manager epoch, configuration revision, authenticated session, request sequence,
operation ID and worker generation separate. None is authority by itself. The
initial facade prototype may use one trusted in-process caller; that is not native
authentication. Real delivery must bind caller rights to target scope at the
enforcing boundary, with separate observation and mutation rights. Unknown epoch,
wrong revision, denied authority and invalid requests reject before state changes.

A logical mutation contains version 0, expected epoch/revision, positive request
sequence, verb, explicit service-name list and operation budget. The existing
service grammar is authoritative for the experiment; no glob or implicit all
selection. Accept only start, stop and shutdown initially. Shutdown must explicitly
cover the whole managed experiment; it never means host shutdown. Reject unknown
fields/versions/verbs, duplicate names, boolean-as-integer values and out-of-bound
input. Normalize selection order before semantic comparison. Restart, enable,
disable and persistent configuration remain outside this initial facade.

Use at most eight selected services and the model's 1..1,000,000 logical-tick
budget. Epoch/revision use the model's 1..64-character bounds. Sequences and
operation IDs are positive unsigned 64-bit values without wrap; exhaustion rejects
new identity allocation. Logical ticks are not milliseconds. Serialization byte
limits, encoding, parser depth, endpoint rights and clock mapping must be specified
before wire parsing or native delivery.

## C-02 Receipt versus operation outcome

Admission reports accepted(new operation), joined(existing operation), or rejected
with a stable reason and any conflicting operation identity authorized for the
caller. Operation identity is (epoch, ID); preserve kind, normalized effective
scope, configuration revision and the original absolute deadline. A receipt does
not mean readiness or cleanup success. Operation observation reports pending,
success, failed, cancelled, incomplete or unknown. These use existing model
outcomes where available; do not rename old reports or native markers.

Observation and client wait expiration have no lifecycle effects. A finite client
wait returning still-pending does not cancel the manager operation. Disconnect
also leaves it owned. State-changing cancellation is an authorized stop that
supersedes a pending start/retry under C-04; no generic cancellation of unknown
side effects is assumed. After manager restart, old-epoch results are unknown;
never automatically resubmit them as new work.

## C-03 Join, conflict and budget preservation

Serialize conflicting operations in the initial profile. Repeating an active start
with the same effective closure joins without extending deadline or resetting
retry count. Same-kind stop with the same scope joins similarly. Shutdown and
ordinary stop are distinct semantic intents even when scopes match: while either
is pending, the other conflicts without changing admission state. This makes
shutdown explicit rather than silently upgrading an operation that other callers
already observe. Once the stop completes, a new shutdown can close admission.

Changing a budget on a different request that joins existing work does not extend
that work. A transport replay under the same request identity must have identical
payload, including its budget; otherwise it is an identity conflict. Joining a
pending operation and replaying a request are different mechanisms.

## C-04 Supersession and resource ownership

Validate stop scope and authority first. A stop may supersede a pending start only
when its scope includes the start scope and all required-consumer constraints
pass. Reject partial/conflicting scope without changing desired state or timers.
Accepted stop closes readiness/retry admission immediately, marks the prior start
cancelled, and creates its own operation. Cancellation does not release ownership.

A launch issued before that cut remains manager-owned even if completion arrives
afterward. Observe the actual generation, request stop, observe terminal state and
reclaim before successful stop completion or replacement. Late readiness cannot
restore desired-running state. Cleanup failure or lost observation produces
incomplete/unknown with retained ownership, never a successful stop. Native
asynchronous launch/cancellation still requires its own consuming witness.

## C-05 Bounded replay — trusted model implementation

The facade uses one trusted session per manager instance,
strictly increasing request sequence and a 64-receipt cache. Reserve a cache slot
before lifecycle mutation. Reject sequence gaps and changed payload under retained
identity without effects. Retained identical replay returns its original receipt,
with current operation observation separately, and never dispatches again.
After structural/identity validation, cache the dispatch receipt and advance the
sequence even when lifecycle admission rejects (for example, a conflict). Earlier
validation failures do not consume a sequence. Commit the receipt with the effect
within the prototype's single-threaded dispatch; unexpected partial failure makes
the session unusable/unknown rather than allowing the request to run again.

Keep a high-water sequence even after evicting the oldest receipt. A sequence at
or below that watermark whose receipt was evicted returns retired/unknown; it
must not be treated as fresh work. Receipt eviction never cancels or evicts an
active lifecycle operation. Keep the active operation independently of the model's
bounded completed-operation history. Unknown historical outcome is not success.

The initial prototype need not survive crashes: any crash or lost session makes
ambiguous receipt unknown and forbids automatic replay into a fresh epoch. Native
epoch uniqueness, session establishment, multiple callers and durable deduplication
remain explicit open contracts. A counter or cache alone is not exactly-once
execution. Tests must cover eviction, changed replay, gaps, exhaustion and ambiguous
receipt before this proposal is considered implemented.

## Acceptance map and next work

| Case | Independent expectation | Current witness |
| --- | --- | --- |
| C01 | Joined start keeps ID/deadline | model T17 join |
| C02 | Joined stop keeps ID/deadline and emits no new stop | added model control test |
| C03 | Stop/shutdown with equal scope conflict in either order; intent unchanged | added model regression |
| C04 | Stop supersedes start; late launch remains owned until terminal/reclaim | model T16 late launch |
| C05 | Stop cancels pending retry and ignores readiness | model T16 retry timer and T07 |
| C06 | Scope rejection preserves state | model T14/T21 and added invalid-scope snapshot |
| C07 | Identical request replay never dispatches twice; changed payload rejects | ControlTests replay/join/conflict cases |
| C08 | Evicted/stale/gapped/overflow identities cannot replay as new | ControlTests eviction/history/invalid-input/exhaustion cases |
| C09 | Wait expiry/disconnect causes no cancellation | ControlTests nonblocking logical wait; no socket or wall-clock wait |
| C10 | Wrong caller/epoch/revision rejected before effects | Epoch/revision validation tested; real caller authority remains unimplemented |

The [facade](../../prototypes/runtime_model/control.py) and
[ControlTests](../../tests/test_runtime_model.py) implement C07–C09 with injected
logical time and no sockets/services. [Decision 0027](../decisions/0027-control-receipts.md)
defines exact payload keys, result schemas, limits and conservative ID exhaustion.
Receipt replay returns no effects; effects are first-dispatch output only.
`wait` samples state without advancing the model clock. `disconnect` detaches the
waiting view while the manager retains its session. Neither is a network API.

The [external boundary proposal](CONTROL-BOUNDARY-V0.md) now specifies byte/depth
limits, encoding, session authority and ambiguous delivery. Decision 0028 enforces
one facade per Model lifetime; reconnect must retain that facade. Decision 0029 implements
the pure request decoder and tests it with the facade. Decision 0030 implements bounded
receipt encoding; decision 0031 adds observation/wait replies. Next specify
caller binding, scope/revocation and execution acknowledgment before real transport;
decisions 0032/0033 implement memory delivery, incremental framing and logical deadlines. Publish CLI grammar/exit mapping only
after those tests and owner review. BG-050 remains active; BG-045/BG-032 retain
status/native mechanism follow-ons. No durable or exactly-once guarantee.
