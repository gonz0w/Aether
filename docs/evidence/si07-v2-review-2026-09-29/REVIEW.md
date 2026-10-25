# Aether enforcing-owner review of the sustained proposal

Aether-side disposition: the proposed AERIO002/NIO2/0x7b private wire domain is
compatible with the selected AENSI001/ABI22 kernel mechanisms under the conditions
below. It needs no new kernel syscall, grant or capacity increase. This clears
Aether's protocol-design objection; it is not runtime adoption, sys-init approval,
source-owner sign-off, payload qualification or a published shared standard.

## Required invariants

Native instance/channel/memory/thread identities remain64-bit typed values with
28-bit nonwrapping generations and holder checks. Private epochs are a separate
16-bit wire namespace. For this first sequential cohort, backend slot1, runner slot0
and child slot2 must each have native generation equal to the selected epoch. The
existing launch sequence can support this starting from a fresh factory cohort;
its counters alone do not prove it after interrupted or failed admissions.

Check full-width native generation returned by0x20005 before any cast. The current
four-role-io.c and native-io.c cast directly to unsigned; that must be changed in
userland's opt-in profile. The owner must verify successful typed launch identities
and expected slot/generation before publishing carrier/bootstrap/admission data.
Diverged cohorts reject and clean up admitted resources; do not reset a kernel
lifetime, mask off high bits or invent a mapping. Existing channel ownership and
native endpoint authentication still enforce every operation.

Epoch1..65535 preserves the six role-selector prefixes and disjoint0x7b receipts.
The seven private namespaces are disjoint at every allowed epoch;65536 would enter
role fields and is forbidden. Complete last-epoch cleanup, then retire that cohort
before further admission or channel allocation. A fresh namespace requires separately
authorized fresh native domain/connection, not an in-place counter reset. Exhaustion
and service restart policy remain sys-init's responsibility; this review assigns
no new user-visible error or implicit restart authority.

AERIO002 retains the160-byte four-role carrier and exact row ordering/rights/bounds.
NIO2 is required at offset28 of the32-byte child bootstrap; v1 requires zero there.
0x7b000000|epoch applies consistently to admission, collection and terminal-exit
policy. Wrong/mixed tags, padding, sizes or identity fail before binding publication.
A successful collection consumes the receipt; recollection is ECHILD. A numeric
receipt is never a kernel capability. Preserve exact negative reply padding,
representable exit0..255, poisoned transport and terminal-before-reclaim cleanup.

## Exact local integration changes after payload delivery

| Current owner path | Required opt-in v2 change |
| --- | --- |
| success.rs carrier | Select AERIO002 only with a matched v2 input manifest; validate full native cohort first. Existing AERIO001 defaults remain. |
| owner.rs bootstrap | Set offset28 NIO2 only for the matched child transport; retain zero for legacy consumers. |
| success.rs admission/collection | Use0x7b epoch receipt consistently; retain native endpoint/instance checks, single collection and ECHILD. |
| success.rs launch/reclaim loop | Prove fresh slot cohort across backend/runner/child; reject divergence and pre-effect exhaustion; retain exact statuses, close/terminal/reclaim order and stale denial. |
| sustained.rs input/finalization | Preserve owner-only UART/event/halt and settle bounded work before halt; no supervision policy expansion. |
| Userland input closure | Full four-role/native-I/O/bootstrap/result/runner selection plus rebuilt runner and bytecount, source/SDK/tool/flag pins and profile manifest. Pure decoder patches alone are insufficient. |

Keep current exploratory owner and all bounded controls unchanged until matching
payloads can execute this whole closure. Merely swapping carrier magic now would
make generation1 fail against v1 consumers and would supply no useful qualification.
No old compiled profile or evidence is rewritten by this design review.

## Qualification when inputs arrive

Freeze the exact versioned payloads first. Build the opt-in owner against them,
inspect linked code/stack and retain each attempt. Exercise real idle beyond3000
scheduler ticks, five runner/bytecount/backend cycles including generation3, exact
6-newline output, runner/child0 and backend17, complete endpoint/worker reclaim and
real authorized input halt. Qualify stale/foreign endpoints, consumed receipt,
cohort divergence, old/new profile mismatch, malformed bootstrap/reply, pre-effect
exhaustion and the supported interrupted/poisoned transport exclusions. Combine
these with the existing wait-registration/worker/foreign/final-action controls and
matched legacy command regressions. Then sys-init supplies its actual owner and
independently consumes the frozen producer handoff.

Existing wake/authority probes remain component evidence. Host namespace arithmetic
and Debug/ReleaseSafe state-core tests cannot establish v2 native transport or65,535
native launch cycles. General storage, shell, packages, all-race recovery and R1
assembly remain separate. No new unsafe, resource, authority or dependency change
is introduced in this review.
