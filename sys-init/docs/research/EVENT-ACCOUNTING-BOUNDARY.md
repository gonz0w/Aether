# Lifecycle event accounting review — 2026-09-06

Local source research for BG-050/BG-033. Sources are
[Model.batch and _pump](../../prototypes/runtime_model/model.py),
[EffectLedger](../../prototypes/runtime_model/effect_ledger.py),
[AccountedDelivery](../../prototypes/runtime_model/accounted_delivery.py), and
[the control facade](../../prototypes/runtime_model/control.py). The retained
evidence bundle snapshots these exact inputs. No external API is inferred.

## Findings

1. Eight services can all reach their stop deadlines in one cut. Four matching
   exit observations in that cut then cause four reclaims: eight forces followed
   by four reclaims. The submission ledger's eight-slot bound is insufficient.
2. A pending launch that reaches its stop deadline emits force. A matching late
   launched observation, in the same or a later cut, emits force again for the
   same generation. The existing ledger excludes force and uses a seen-kind bit
   per generation; merely adding force to that set would reject the second
   occurrence. Silently dropping it would assume the first force covered a launch
   that had not yet been observed. Native invocation semantics are not established.
3. Successful start clears active while services remain supervised. A later fault
   still emits reclaim. It can occur while an unrelated service's start is active.
   active.id is therefore neither always available nor necessarily the cause.
   Operation history is bounded and must not be the sole ownership record.
4. A reclaim acknowledgment alone does not call batch and cannot release model
   ownership. Producer execution, terminal observation and cleanup remain separate.
   Similarly, a rejected-before-effects launch does not automatically justify the
   model's denied event: that event retains owned state and requests reclamation.
   Whether any producer resources exist requires the exact producer contract.

## Conservative bound, not a tight maximum

The deadline pass emits at most eight force effects. The at-most-four input
observations can directly emit at most four additional late-launch forces. The
pump emits at most one effect per service per invocation: terminal reclaim,
stopping stop, retry launch or queued launch are mutually exclusive phases, and
flags/phase changes prevent repeat emission on its nine passes. Its only recursive
entry is successful single-service restart. The selected service is then unowned
and emitted no reclaim/stop in that invocation; the recursive launch uses its
remaining per-service allowance. Other nodes cannot gain fresh evidence in that
recursion. Thus twenty effects is a conservative cut bound for this source.
The twelve-effect witness is a reachable lower bound, not proof of tightness.
Any new effect site, phase transition, batch size or recursive pump path requires
revisiting this derivation. Tests are examples, not exhaustive proof of the bound.

## Required next experiment

BG-057 must specify a separate event journal before integration:

- Identify each occurrence by fixed manager epoch/revision, monotonic cut serial
  and index, plus service/generation/kind. Keep the owning activation or stop cause
  explicitly; distinguish it from the currently active client operation. Specify
  bounded retention and retirement without relying on the 64-operation history.
- Reserve the whole declared cut budget before changing clock, event count,
  desired state or ownership. Denial leaves all of them unchanged. Input validation
  also precedes mutation. Do not split a supplied cut or its deadline priority.
- Keep caller ownership of unaccepted observations. A native queue that cannot
  retain them must report observation loss; backpressure cannot imply that the
  real world or native deadlines paused. Unknown obligations must not indefinitely
  suppress the only terminal evidence capable of supporting recovery. Define a
  bounded failure/reconciliation route before claiming production liveness.
- Treat two force occurrences explicitly. Choose either distinct invocation
  obligations with matching producer evidence or a reviewed lifecycle change;
  do not deduplicate by kind/generation in the transport layer.
- Preserve captured raw obligations on post-mutation failure and close further
  mutation. No rollback, replacement driver or durable recovery is implied.

## Producer mapping gate

| Result | Permitted accounting interpretation | Additional evidence needed |
| --- | --- | --- |
| Confirmed rejection before effects | Record rejection of the exact obligation | Whether resources were ever reserved; explicit rollback/no-instance result before changing ownership |
| Confirmed launch execution | Record executed | Matching instance identity and launch observation; readiness is separate |
| Confirmed stop or force execution | Record executed | Terminal evidence; no inferred exit or cleanup |
| Confirmed reclaim execution | Record executed | Exact completed mapping/reference cleanup and reuse/zeroing witness required by the selected producer |
| Lost/ambiguous result | Retain unknown obligation | Authoritative reconciliation; no automatic retry |

This table is a consumer acceptance checklist, not an implemented native result
decoder. Select one producer profile under BG-032, retain its exact result codes
and matching artifacts, and prove each applicable row with consuming witnesses.
ABI-9 channels do not inherit ABI-6 timing or recovery contracts. Existing native
fixtures remain unchanged. No new shared rule is needed: these are sys-init
lifecycle algorithms under the existing Foundations requirements.
