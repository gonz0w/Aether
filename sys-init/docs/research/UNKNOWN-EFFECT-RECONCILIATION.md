# Unknown effect reconciliation review — 2026-09-06

Selected source review for BG-033/BG-032/BG-057. The
[fifteen frozen inputs](../evidence/reconciliation-review-2026-09-06/reviewed-files.json)
are copied and hash-checked; they are not a producer build pin. Existing sys-init
native evidence remains scoped to its own retained inputs. No new target run,
recovery mechanism or cross-project owner acceptance is claimed.

## Finding

The reviewed profiles support confirmed-return accounting and separately bound
observations. They do not supply a general protocol that can resolve an unknown
effect after loss of its reply or owner. Keep unknown slots unresolved. Build the
confirmed-result mapping next, with explicit rejected-evidence cases; do not use
terminal state, stale-handle errors or a new owner's guess to clear the journal.

## ABI 6: exact evidence boundaries

The [init contract](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/docs/NATIVE-INIT.md)
limits the profile to one BSP supervisor, two worker slots, one registered wait
and 64 wait registrations. It explicitly excludes replacement, authorized
inventory and lost-observation reconciliation. Supervisor death closes and zeroes
the whole local domain, invalidates retained state and halts. Nothing survives to
export a receipt to a replacement owner. This is a profile limit, not proof that
all Aether recovery mechanisms are absent.

The captured [native trap implementation](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/kernel/arch/x86_64/native_c.zig)
provides the following source-level distinctions:

| Evidence tied to the original live owner and exact target | Supported interpretation | Does not establish |
| --- | --- | --- |
| Successful 0x23001 launch return | Launch completed; returned worker handle identifies admitted slot/generation; writer transferred | Service readiness, terminal state or recovery if this handle/result was lost |
| Negative launch return from validated pre-admission paths | This call did not admit the child or transfer its endpoint | Cleanup of separately allocated channels; arbitrary transport failure before effects |
| Successful 0x20007 stop return | Handler completed; target is terminal (or was already terminal) | That this occurrence caused termination, graceful POSIX signaling, reclaim, or a separate force API |
| 0x25001 observe on retained worker | Revision, terminal detail+1 or zero, historical-ready bit for that valid target | Which effect caused the state; full terminal kind (not returned by this operation); current readiness after terminal |
| 0x20001 status on retained worker | Terminal detail+1 and separate terminal kind (R8), plus profile fields | A reply for a particular journal occurrence or POSIX wait-status translation |
| Successful 0x20002 reclaim return | Target was terminal; its local root was detached, backing zeroed and checked, then admission/image metadata retired | Cross-core/device quiescence, release of all supervisor endpoints/waits, or receipt replay after return loss |
| EBADF from a later lookup | Supplied handle does not name a currently admitted matching target | Whether a launch ever succeeded, who reclaimed it, or completion of the unknown journal occurrence |

Lookup compares admitted state and the full generation-encoded handle. A service
name or copied numeric handle alone is not authority. The sys-init
[adapter](../evidence/reconciliation-review-2026-09-06/reviewed/sys-init/prototypes/native-supervisor/adapter.rs)
checks terminal observation before reclaim and decrements its worker counter only
on a decoded successful reclaim return. Its counters are local bookkeeping; they
are not an authoritative inventory for another owner. The observation projection
omits terminal kind, so detail 143 alone must not be translated to a signal/stop
kind. Keep exact native kind/detail separate when selecting a richer projection.

The reclaim handler's local zeroing guarantees are meaningful positive evidence
for a received return under this exact profile. Do not flatten them into merely
"request accepted"; equally, do not generalize them into a lost-reply recovery API.
The model's force request has no independently selected native mapping yet.

## Retained waits are not an effect receipt ledger

The [wait implementation](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/kernel/native_wait.zig)
retains a terminal completion status once selected. At refresh, deadline expiry
wins before missing target, which wins before revision change. A previously
completed changed/timeout/canceled status is not overwritten by later reclaim.
Thus absence of a reclaimed status cannot prove the target remains allocated.

A retained wait reporting target-reclaimed is evidence about the exact target
bound at registration. It is not an occurrence ID for a reclaim call, a full
resource inventory, or proof that unrelated endpoints/waits were released. A
consumer would need retained valid registration, owner/target mapping, producer
identity and an explicitly defined reconciliation result before using this fact
to discharge any obligation. The current adapter/journal has no such mapping or
separate "postcondition established, execution attribution unknown" outcome.
Never relabel such a fact as executed simply to free capacity.

## Newer broker profiles do not close this gap

The [process broker](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/docs/NATIVE-PROCESS.md)
has connection-owned tickets and one outstanding request, without replay IDs.
Its collection consumes the ticket, and client-death cleanup differs from sys-init
connection-loss-preserves-work policy. The
[connections profile](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/docs/NATIVE-CONNECTIONS.md)
demonstrates private channels and bounded replacement generations, not takeover of
an old supervisor's ownership or ABI-6 timing/recovery.

The current [command contract](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/docs/NATIVE-COMMAND-IO.md)
now includes reply-failure tests. The captured
[transport adapter](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/user/native-command/transport.h)
and [probe](../evidence/reconciliation-review-2026-09-06/reviewed/Aether/user/native-command/reply-probe.h)
discard a successful read/close reply or corrupt metadata after the real broker
operation. They poison the connection, with no further channel calls. These are
useful witnesses of uncertainty containment, explicitly not recovery. A broker's
private retained terminal record or CLI exit mapping is not automatically available
to an authorized replacement sys-init owner.

## Evidence and standards disposition

The retained [SI-04 consumer record](../evidence/reconciliation-review-2026-09-06/reviewed/sys-init/docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
binds producer summary 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155
and independently demonstrates normal sequential reuse and cleanup controls.
The [native catalog snapshot](../evidence/reconciliation-review-2026-09-06/reviewed/sys-init/docs/native-coverage.json)
is historical evidence, not a new execution of the current source reviewed here.
Do not combine mutable source findings and old passing binaries into a new target
claim. Existing normal-path observations do not witness lost-reply reconciliation.

The captured [central registry](../evidence/reconciliation-review-2026-09-06/reviewed/Aether-standards/tools/releases.json)
still lists the three existing v0.1.0 releases. O-01/04, I-03–06, E-04–08 and
Distribution ID-04 apply: keep authority, state, execution and ownership distinct.
No shared pin or ABI upgrade is selected. Future shared recovery authority rules
belong in Aether-standards; exact sys-init lifecycle mapping remains local.

## Follow-ons before completion

BG-058 captures the next local contract and model experiment for confirmed ABI-6
results: bind producer profile, live owner, original issued token and retained
worker/wait identity; classify execution separately from terminal/cleanup; reject
profile mixing, wrong generation, timeout, EOF, EBADF and queued terminal data as
unknown-resolution proofs. Begin with positive received results, not an invented
reconciliation certificate. Source review does not establish native acceptance; matching consumer witnesses
are required when implementing the adapter.

BG-033/BG-032 and OQ-022 retain the actual recovery question: which enforcing
producer/owner can publish authoritative retained outcomes or establish a scoped
postcondition after ambiguity, and with which retirement/authority rules? No
concrete new kernel syscall is justified until that consumer contract distinguishes
missing mechanisms from deliberately unsupported profile behavior. Unknown recovery
is blocked in the currently selected profiles; confirmed-result mapping and its
negative model tests can proceed locally. BG-057 retains inbox/control composition.

## Concurrent producer documentation update

Two mutable documents changed during review. The separately retained
[late source manifest](../evidence/reconciliation-review-2026-09-06/late-reviewed-files.json)
and diffs preserve both versions. The newer command checkpoint reports 51 cases
for completed child-result mapping, separating raw kind/detail from parent exit.
It explicitly leaves general cleanup failure, stop and unknown-result recovery
open. This does not alter the reconciliation conclusion or qualify any sys-init
consumer. No implementation source among the selected inputs changed at recheck.
