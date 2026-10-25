# Small Aether v1: implementation audit

**2026-10-03 update:** the audit below is historical. The [current SI-07/v1
map](SI07-DISPOSITION.md) incorporates the paired owners, script startup and
sustained command loop. Next is a maintained ABI22 build/run recipe, then explicit
configuration and bounded supervision on one matched useful path.


2026-09-07; BG-063 complete as a source audit. Implements the planning step in
[V1-SCOPE](V1-SCOPE.md), not new runtime behavior. Existing prototypes remain intact.

## Keep, simplify, defer

| Code | V1 disposition |
| --- | --- |
| `prototypes/native-supervisor/adapter.rs` | Keep the native syscall/typed-handle boundary as the starting point. Review fixed grants/image selection, wait limits and partial cleanup before product use. |
| `prototypes/native-supervisor/service.rs` | Reuse the direct service record, readiness identity, cleanup-before-retry, finite attempt budget and dependency rules. Replace scripted `run_*` scenarios with a small reusable supervisor. |
| `prototypes/native-supervisor/init.rs` | Keep as the fixture entry point. Its cfg dispatch and assertion-result exit are not the product boot loop. Add a separate product entry point once the reusable service owner is qualified. |
| `prototypes/native-supervisor/service_worker.c` | Retain as a failure/readiness fixture. It is not an essential system service. |
| `prototypes/native-supervisor/sample_receipts.rs`, `terminal.rs` | Reuse precise terminal kind and generation checks where needed. Do not equate exit result values with terminal kind or reuse historical readiness. |
| `binding.rs`, `cut_reservation.rs`, `pending_history.rs` and runtime-model journal/retirement modules | Keep as experiments and evidence. Do not make the six-cut journal or completion archive a dependency of v1. |
| `prototypes/host_runtime/descriptors.py` | Reuse inert validation principles and graph tests, not this host-specific target or Python runtime on Aether. Choose the minimal native boot configuration after image identity/launch mapping is known. |
| `prototypes/host_runtime/runtime.py`, `prototypes/runtime_model/model.py` | Keep host/model regression oracles. Their finite observations/effect history and POSIX process APIs are not a perpetual native daemon implementation. |
| `tests/native-init.py` and pinned evidence | Keep enforcement and failure witnesses. Add focused product-path cases; preserve fixture markers and distinguish test completion from shutdown. |

The direct native path already demonstrates generation-bound readiness, cleanup
before replacement, three-attempt exhaustion and dependency admission rules
([service reference](NATIVE-SERVICE.md), service.rs `run_readiness_retry`,
`run_retry_budget`, `run_dependency_loss`). We do not need a journal framework to
express these policies. This does not mean those scripted cases are already a
reusable supervisor.

## Smallest implementation path

Continue with Rust/no_std for the initial native implementation because the
existing adapter, compiler recipe and consuming witnesses use it. This is reuse
of the established implementation, not a claim that other languages cannot fit.
Keep OS calls behind the native adapter and policy state independent of it.

Use a fixed inventory initially matching the demonstrated two-worker profile,
with one current record per service: desired state, instance generation, phase,
owned handles, retry budget/deadline and last outcome. Retain operation failure
and outstanding ownership until resolved. Discard completed per-attempt detail
only after verified cleanup; increment identity before replacement and reject
stale instance inputs. No lifetime event log or checkpoint archive is required.
A two-service implementation is an initial bound, not proof that the eventual
useful environment requires only two tasks.

The immediate change is BG-064: extract a reusable service owner with explicit
partial-launch/cleanup behavior. In `service.rs::start_mode`, channel creation
and launch currently call `accepted`, which terminates the fixture on failure.
That is useful for a test oracle but does not supply a recoverable product path
when a writer/reader has been acquired and launch fails. `dispose` similarly
assumes all operations succeed. Keep the old fixture unchanged and implement the
product owner separately with retained errors and exactly tracked resources.

Test that owner on the host with a deterministic fake of the adapter boundary,
then wire the same implementation into a fresh pinned Aether case. Cover launch
failure after channel creation, close/reclaim failure, cleanup before replacement,
stale-generation rejection and repeated successful cycles using constant storage.
The fake tests are implementation tests, not a new general policy model. No
product/native completion claim follows until the consuming target run passes.

After that: add a small boot loop and immutable service table, bind actual image
roles to it, then configuration input, restart/dependency/stop behavior and plain
status output. Use a build-time validated inert table first if the boot contract
lacks configuration transport; do not invent a target filesystem or shared schema.
Select final descriptor fields/transport with the actual service-image boundary.
Avoid a second generic graph/control framework. Finish with the real boot/failure/
shutdown scenario and the short operator guide in V1-SCOPE.

## Actual service and boot boundary

Read-only sibling review found a useful command milestone, not a directly
launchable sys-init service set:

- Aether-userland's `docs/evidence/four-role-native-2026-09-07/README.md` records
  a real `bytecount --decimal` command under its source-built owner/backend and
  independent parent, producing exact `6\n` with six task reclaims. The source
  parent and producer-success backend are retained in that bundle/preparation.
  It is a candidate first real command integration witness, not an interactive
  environment or a long-running daemon.
- `docs/evidence/dash-workload-handoff-2026-09-07/README.md` in Aether-userland
  retains twelve actual-shell candidate workloads, explicitly native NOT RUN.
  The latest STATE records native startup acceptance but still awaits the full
  dash delivery. Do not claim a functioning shell from its startup probe.
- Aether `docs/NATIVE-INIT.md` defines sys-init's two-worker AENIN003/ABI16
  composition. `Adapter::launch` selects the fixed image grant 0xc001 and a slot,
  passes a short fixture mode, and transfers one readiness writer. That is not
  the userland four-role startup/collection contract. Swapping in a userland ELF
  cannot establish correct grants, I/O, arguments or lifetime ownership.

Concrete integration questions before a useful boot claim: which image roles and
startup/I/O grants can sys-init own; how it receives the selected service table;
and which actual command or shell entry point the producer/userland pair supports.
The exact producer/consumer packet needs independent intake. These are unresolved
interfaces, not a request to rewrite the kernel or assume all kernel work is absent.
No sibling files were changed and no handoff message was sent.

## Limits to resolve on the chosen product path

The inspected native init profile has one active wait slot, at most 64 lifetime
wait registrations and a 3000-interrupt experiment watchdog. The adapter also
tracks that wait count. AENIN003 expands code size while retaining earlier
lifecycle semantics. Removing the local check cannot remove producer exhaustion.
A long-running init needs a qualified product execution/wait strategy; initially
polling observations avoids wait-token consumption but does not remove the guest
watchdog or prove acceptable idle cost. The kernel's concrete profile must be
reviewed with the boot path before requesting any new mechanism.

`Adapter::stop` requests native worker stop; it is not a graceful POSIX signal.
The kernel documents fail-closed owner-death cleanup and halt, which is distinct
from an operator-requested orderly service shutdown, filesystem flush or poweroff.
The inspected adapter exposes no operator shutdown input or poweroff operation.
Define that input/terminal action with the selected environment; do not use
`finish(100)` or a VM test exit as the product shutdown implementation.

The current composed fixture's 16,360-byte image does not measure the proposed
smaller product path. Measure that path before deciding it needs a larger limit.
Raw authority/error/cleanup checks remain required; completed history retention,
replacement-owner recovery and broad platform qualification remain deferred.

## Review and validation scope

Foundations O-01/03/04, I-01/03–06 and E-01/04–08 apply: preserve authority,
identity, actual errors, explicit bounds and evidence layers. Distribution boot,
service, persistence and observability claims remain limited to inspected inputs.
No new standard, release pin, dependency or ABI is adopted. Technical review
separates script assertions from product error handling and command startup from
service supervision. Independent review is not claimed. Documentation impact:
this implementation map, BG-063/064 and the current roadmap/state. Full local
check results and inspected-source pins are retained in
[evidence](evidence/v1-implementation-audit-2026-09-07/README.md).
