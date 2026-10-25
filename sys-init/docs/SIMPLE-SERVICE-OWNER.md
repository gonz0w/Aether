# Simple service owner

Current extension: [BG-065 pair composition](SIMPLE-SERVICE-PAIR.md) adds an
explicit slot argument, exact-generation stop and Stopping state. Its validation
supersedes the historical group/image counts below for the current source.

BG-064 introduces [service_owner.rs](../prototypes/native-supervisor/service_owner.rs):
one current attempt with fixed storage, typed resource handles and explicit errors.
It is the first reusable v1 component, not yet the boot/service coordinator.

`Service::new` borrows a unique Identity and accepts a total attempt budget.
`start` admits only an Idle owner with budget and a fresh checked generation.
Channel acquisition precedes launch; a successful launch transfers the writer.
A known launch failure retains both endpoints for explicit cleanup. Channel failure
before any resource grant leaves no known handles. Every admitted attempt consumes
budget, including a failed acquisition; rejected admission performs no operation.
This is an activation-wide budget, not yet a rolling crash-loop/backoff policy.

`cleanup` requires the original owner and exact generation key. A worker must be
observed terminal before closure/reclaim. Successful operations clear only their
own handles, in writer → reader → worker order. Known failure retains the remaining
handles and allows explicit cleanup retry. First and latest failure remain available
after cleanup until another admitted attempt. Old keys cannot mutate a replacement;
no completed event history is kept. The caller must retain this owner while it has
resources or uncertainty: dropping it performs no automatic kernel cleanup.

The Backend contract is synchronous and single-owner. Known errors certify no
resource consumption/transfer by that operation. Unknown outcomes may have executed:
the owner retains available references and freezes, refusing both start and cleanup.
This includes an unknown acquisition where no handle was returned. There is no
reconciliation, automatic replay or reset API. Kernel/resource authority stays in
the adapter; numeric metadata and copied keys confer no new grants.

## Native binding and acceptance

[owner_fixture.rs](../prototypes/native-supervisor/owner_fixture.rs) drives the same
implementation through the existing adapter and pinned service worker. It is a
fixture, separate from the reusable owner. It conservatively classifies native
errors as Unknown. Only the adapter's pre-trap invalid-slot launch rejection is
classified Known. Changing that classification needs evidence for the affected
operation; it is not a blanket assertion that all errno returns had no effects.

Three fresh AENIN003/ABI16 cases pass:

| Case | Exact result |
| --- | --- |
| simple-owner | Three exit-kind/result-18 terminal observations, complete cleanup and fresh generations; exhausted fourth admission; 100/reclaimed3 |
| owner-launch-denial | Local slot-2 launch denial after channel acquisition; writer/reader cleanup; three subsequent complete cycles; 100/reclaimed3 |
| owner-close-error | Fixture closes the reader before the owner's close; actual stale close returns operation0x24003/errno13; owner retains references, freezes and denies replay; 1122/reclaimed0, expected profile rejection |

The last case deliberately creates an external-close mismatch and is a denial
witness, not successful cleanup or recovery. It terminates through the existing
internal assertion contract. The success images are 2,288 and 2,448 bytes; the error
case is 2,528 bytes under unchanged 16 KiB code/4 KiB stack limits. These workloads
pass without a guest fault; neither stack high-water nor boot performance is measured.
The first attempt mistakenly selected the default worker, so the first case failed
1120/reclaimed0. The corrected run selects the pinned service worker explicitly;
both attempts are retained. No producer/worker/release pin changed.

Six host Rust tests exercise the implementation: 100 completed cycles in fixed
storage; attempt exhaustion; channel/launch failure; remaining resources across
terminal/close/reclaim errors; writer cleanup and first-error retention; every
operation's Unknown result; stale generation, foreign owner and live-worker denial.
The first aggregate run executed all eleven host groups successfully but rejected
the old hard-coded ten-group total; the aggregate now requires eleven. A separate
compatibility driver first used the wrong retained ABI6 directory layout; its
corrected comparison verifies all 587 previous images byte-for-byte unchanged.
Both unsuccessful driver attempts remain retained. Final sealing also exposed
an inherited receipt-count mismatch: the eleven test methods produce twelve named
check records. Teardown now verifies the exact record set and raises on a failed
receipt instead of silently writing a result that disagrees with unittest. The
pre-fix aggregate passed its tests but its failed receipt is not acceptance.

Three private source mutations remove identity, uncertainty and writer retention
checks and fail their designated tests. These are required by the existing
sample-receipts gate, now eleven test groups. Host fake handles do not qualify
native cleanup. Counter wrap is guarded in code; direct near-u64-limit execution
is not covered by the six tests.

## Review and next work

The core introduces no allocation, unsafe code, new dependency or native syscall.
Existing unsafe sites are unchanged. Exclusive mutable access serializes each
operation; exact owner/generation checks precede cleanup calls. A live worker
prevents cleanup; partial failures cannot authorize a replacement. Successful
completion frees current resource state without resetting generation or budget.
No independent review is claimed.

Foundations O-01/03/04, I-01/03–06 and E-01/04–08 apply to this scoped owner and
its evidence. Existing Experience internal-marker exception remains; no operator
renderer or shared service format is added. Distribution durable/replacement
recovery remains unqualified and deferred; other-OS product support is retired. Original
work is BSD-2-Clause; retained/vendored bytes remain unchanged.

Next BG-065 composes these owners into a small two-service start/stop path with
explicit dependency order and stop-request errors. Configuration transport, useful
userland images and the long-running boot profile remain the concrete integration
gaps in [the v1 audit](V1-IMPLEMENTATION.md). No checkpoint model is needed.

[Retained validation](evidence/simple-service-owner-2026-09-07/README.md) records
fresh host/native results, compatibility comparisons, source pins and failures.
