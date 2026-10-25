# SI-07 native request-denial controls — 2026-10-03

Before-code requirement: qualify four negative requests at the authenticated
child-request dispatch boundary: oversized count17, nonzero reserved padding,
runner-context selector on a child connection, and an epoch1 selector during a
real generation2 cycle after generation1 completed/reclaimed. The tests corrupt
one complete real child frame immediately after IPC receipt; this is explicit
fault injection into the existing owner dispatcher, not a replacement C caller or
proof of arbitrary native endpoint spoofing. Original child/parent/kernel/sys-init
sources, ABI, grants, quotas, release pins and earlier evidence remain unchanged.

The real dispatch must return EACCES13 for count/padding or EBADF9 for foreign/stale
selectors, with exact32-byte negative reply padding, zero child I/O progress and
no backend output effect. Deliver the response on the real owned child connection;
a private observer then stops/observes clients, closes/reclaims their endpoints/
tasks, closes backend references, observes backend17/reclaim and stale denial,
then halts with three reclaims (six after the stale case's first successful cycle).
The healthy first stale cycle must produce exact6-newline/0/0/17 before rejection.
Generic panic, timeout or missing input never counts as a passing negative.

Security/ownership: private selectors are authenticated-connection-local data, not
native grants. Validate before dispatching any backend operation. Buffers remain
live through synchronous trap calls. Stop acceptance is followed by terminal,
closure and reclaim; observation is not policy ownership transfer. Test observer
cleanup does not implement sys-init recovery or arbitrary mid-effect cancellation.
No new unsafe boundary, dependency, authority or resource growth is introduced.

Simplicity: mutate a copied fixture at the actual decoding boundary and retain its
normal dispatch. A separate adversarial service/runtime is unnecessary for this
narrow experiment. Host-only validators cannot demonstrate live native dispatch/
reply/cleanup. No maintained runtime mechanism is added or retired. Freeze sources
for native runs, inspect linked/raw/stack/builtin targets, retain every attempt,
run exact trace corruption controls plus host/pin/workflow/Experience/link checks.
Documentation impact is the existing reference, STATE, ROADMAP and workflow gaps.
Remaining framing/foreign-endpoint/race/consumer and useful-shell coverage stays open.

## Results

All four real QEMU executions pass. Count17/nonzero padding return -13; a still-live
runner-context fd4 selector on the child connection and a retired epoch1 selector
in actual generation2 return -9. The original dispatcher produces the exact
zero-padded32-byte reply, delivered through the real child writer. The observer
then confirms stopped143/kind3 child/runner, endpoint/task retirement, untouched
backend output, backend17, stale denials and authorized halt. Halt records three
reclaims, or six in the stale case after the first healthy exact6-newline/0/0/17
cycle. Every run retains more than3000 actual idle ticks. Stopped clients are
asserted in the owner; ordinary serial prints backend17, denial proof and counts.
This is not an independent backend-byte oracle or production recovery policy.

Four final trace comparisons pass;53 deliberate semantic corruptions reject.
Maximum raw/linked code is10472/16384 and estimated stack3832/4088. Raw images equal
ELF binary extraction; inspection.json and manual-inspection.md bind the scoped
GOT/register/stack review. Sources are frozen per case and original production
source hashes remain unchanged. Pinned inputs and the prior producer seal are
copied under inputs/. No sibling, public ABI, grants, limits, policy or release pin
changes. Host/pin/workflow/Experience checks are recorded in checks.json.

Failures retained: the initial count build fails E0308 because a32-byte put helper
was used on a384-byte frame. The corrected count-2 uses bounded byte copying;
no guest ran in the failed attempt. Three resource-inspection attempts rejected
previously unlisted compiler-selected memcpy registers; inspected targets now
qualify and all earlier outputs remain. No native run failed or was retried.

This closes the focused local private-dispatch count/padding/foreign/stale witness
gap. It does not exercise an actually forged native endpoint or truncated frame,
exhaustive interruption races, independent consumption of these controls, complete
SUSTAIN-01–06/SI-07, SDK/reader approval, useful shell, persistence/packages or R1.
Next: broader retained-frame/wait transitions with the actual owner contract and
useful-shell-session integration, keeping sys-init ownership explicit.

## Reproduction and retention

From repository root with pinned tools:

```sh
python3 docs/evidence/si07-request-denial-2026-10-03/build.py count-2
python3 docs/evidence/si07-request-denial-2026-10-03/run.py count-2
python3 docs/evidence/si07-request-denial-2026-10-03/audit.py
python3 docs/evidence/si07-request-denial-2026-10-03/check-native.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Repeat build/run for padding, foreign and stale. Build/run/audit reject reuse;
audit requires all four built roots. After cleanup restore indexed generated
artifacts and per-case source exports first, or choose a fresh dated attempt.
The initial failure additionally used build-initial.py count. retain.py verifies
all generated and source archive members before removing only these five owned
duplicate roots, including the failed build. SHA256SUMS binds the final packet.
