# UP-01: Aether mechanism review and executable ownership oracle

2026-09-05. Aether's implementation-side response to the pending canonical
[PD proposal](../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md),
particularly PD-01–03 and its inherited-descriptor requirements. This is a local
mechanism assessment and host experiment, not a competing shared standard,
owner sign-off, runtime-service assignment or new native ABI. Userland retains
POSIX/libc policy, sys-init retains service lifecycle policy and pkg-mgr retains
inert artifact transport. Shared normative decisions remain in Aether-standards.

## Concrete ownership choice to take into native integration

Use one user-space owner for mutable open-file positions and reference counts
across the two clients. Each independently loaded client has a separate descriptor
table in that owner's scope. An inherited descriptor references the same open-file
record; independent open creates another record with position zero. Per-alias
rights can narrow the source rights. Closing one alias consumes only that alias;
last-reference removal creates exactly one backend-close obligation. A pending or
failed close is not a confirmed backend release.

UL-041's client-local offsets/refcounts work for one client. Copying those tables
into another ELF would produce divergent positions and premature backend closes.
For this experiment, the trusted broker can host the shared record as conformance
policy; the production owner/placement remains an affected-owner decision. No
kernel file table, pathname lookup, UID shortcut or POSIX policy is required.
The owner and backend are trusted for file authorization, contents and position
correctness; user-space placement does not remove them from that trust boundary.

A trusted connection binding determines the caller. Requests may identify only a
reference owned by that connection; supplying a parent session, backend handle or
other client's FD cannot change the caller. Public FD numbers remain reusable
POSIX indices, not authority. Internal references carry connection and descriptor
generations; stale queued references must not attach to a replacement session.
The backend's raw handles remain private to the owner. The existing ABI-7 raw
file passthrough must not remain a bypass around rights/position enforcement in
an inherited-file profile.

## Bounded workload and missing native composition

Follow-through: [AENMX001 / ABI 9](NATIVE-CONNECTIONS.md) now supplies the finite
six-channel, two-client request-framing witness described here. It does not add
shared open-file records or an inherited-descriptor bootstrap. The original host
evidence retains this review's earlier snapshot; production ownership and the
remaining shared PD review are unchanged.

Propose two file clients (requester and independently loaded child), one backend
and the existing supervisor/broker. Each client has indices 0–15, including dash's
save index 10, with two shared open-file records and a 64-byte volatile scratch.
Keep each backend transfer at 16 bytes. Use three finite generations for internal
session/reference retirement; no wraparound. This is an explicit-inheritance
spawn experiment, not fork, vfork, exec replacement, native dash or shell pipelines.

| Needed behavior | Existing mechanism or required next change |
| --- | --- |
| Three workers plus broker | ABI 8 already supplies it; no further worker increase for this workload |
| Two private client request/reply pairs plus backend pair | Six unidirectional channels; ABI 8 currently has four, so this topology needs a separately specified bounded profile extension |
| Child access to its own connection | Existing paired-endpoint launch transfers both grants atomically on successful admission; no endpoint duplication required |
| Shared offsets and alias rights | User-space owner records; no native file syscall or shared writable client mapping |
| Serve both clients | Bounded incremental per-connection framing and fair polling; the current broker's blocking full-frame receive loop cannot serve this topology |
| Child bootstrap | Owner supplies its admitted descriptor bindings on its private connection; copied FD integers alone are insufficient |
| Exit and stale isolation | Native terminal observation/endpoint closure plus owner-local alias cleanup; terminal state takes precedence over queued requests |
| Parent exit with surviving aliases | Owner retains child references until child terminal/explicit close; any sys-init stop policy is a separate operation |

The six-channel count follows from this particular topology, not a general OS
quota. Before implementation, agree the new profile's exact protocol and bootstrap
with userland; retain existing four-channel profiles and ENOTSUP for inheritance.
The broker must validate an entire inheritance list, reserve records and child
route, then invoke native launch. A rejected launch releases all reservations
without publishing a child or changing parent offsets/references. The child may
queue messages after admission, but the owner must not service them until its
route and inherited records are committed. This gating avoids assuming a native
suspended-start primitive. The host oracle models that commit boundary, not its
scheduler implementation.

If launch succeeds but its reply is lost, the owner still owns the child and
references: do not automatically replay launch or pretend it failed. Unknown
backend I/O poisons that connection's shared records; aliases cannot retry against
an assumed position. Record unresolved cleanup and require explicit lifecycle
resolution. Do not claim successful final close merely because a local reference
was removed. Current ABI-6 init policy and ABI-8 broker behavior are separate;
this proposal does not compose them or promise supervisor recovery.

## Executable host acceptance input

`tests/up01_model.py` is a host-only oracle with synthetic trusted session binding
and already-validated backend completion counts. It is deliberately not a runtime
library or native transport. `tests/test_inheritance.py` supplies twelve observable
workloads: alternating parent/child positions and independent opens; narrowed
rights; foreign/stale reference rejection; atomic malformed/native-failed
admission; rights-widening denial; both exit orders; session and descriptor reuse;
retirement/exhaustion; failed I/O position preservation; and unknown-reply poisoning.
Close records represent obligations, not completed backend RPCs. No actual file
bytes, target protection domains, scheduling races or backend replies run here.

```sh
python3 -m unittest discover -s tests -p test_inheritance.py -v
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The ordinary host test discovery includes these cases. Future native consumer
assertions should reuse the expected behaviors, not trust this model as an
implementation or authorization boundary. In particular, native tests must prove
routing identity, malformed partial frames, blocked-peer fairness, real backend
close, admission exhaustion/rollback and absence of the raw-handle bypass.

[Retained host results](evidence/inheritance-review-2026-09-05/README.md) include
three deliberately broken model controls. Existing native inheritance remains
unsupported; no QEMU or independent companion adoption is claimed by these tests.
