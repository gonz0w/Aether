# Native init experiment v1

AENIN001 is a separate BSP-only profile, ABI 6. It uses the 56-byte two-ELF
launch envelope and channel/paired-channel operations from NATIVE-FILES.
Existing profiles and completion markers keep their behavior. Supervisor entry
R9 is an owner-bound observation grant 0xe001; workers cannot use it. No shared
standard or immutable consumer pin changes. This supplied SI-01–03 producer
inputs, independently consumed within this bounded scope under
[sys-init decision 0017](../../sys-init/docs/decisions/0017-native-init-consumer.md).
The [subsequent reuse refresh](../../sys-init/docs/evidence/native-slot-reuse-consumer-2026-09-05/README.md)
also accepts both sequential orders on the corrected producer. This is historical
matching-artifact acceptance, not fresh execution of the current checkout; broader
clock, delegation and recovery requirements remain unsupported below.

## Clock and registered observation

This is an asynchronous registered wait, not a blocking scheduler or POSIX clock.
The supervisor polls retained completion and may yield between polls. Interrupt
gates serialize registration with local worker events: no user execution or timer
handler can interleave the comparison and registration. A worker readiness-bit
transition or terminal transition increments its observation revision once.
Repeated ready calls do not generate events. Events before registration are
found by comparing a previously observed revision; events after registration
are retained until release. There is one wait slot and at most 64 registrations
per boot; tokens retire without wrapping. No allocation, event queue or spurious
completion. Historical ready does not authorize admitting a terminal service.

Clock units are delivered BSP PIT interrupts since native entry, divisor 11932,
nominal input 1193182 Hz. This is monotonic interrupt time, **not elapsed wall
or suspend-inclusive time**: delayed/coalesced interrupts are not reconstructed.
No suspend/resume, wall-clock conversion, time-setting, SMP clock synchronization
or hard real-time guarantee. u64 counter never wraps (overflow is fatal). The
separate 3000-interrupt fixture watchdog still bounds this experiment; consumers
must use shorter deadlines. Production service timing needs a calibrated clock
and idle/suspend accounting before adopting millisecond policies.

All operations use int 0x81, RDI=observation grant. Unused RSI/RDX/R10/R8/R9 must
be zero. Errors are negative errno. Wrong caller/grant EACCES(13), invalid fields
EINVAL(22), stale target/token EBADF(9), occupied slot EBUSY(16), retired wait
pool ENOSPC(28). No authority is conferred by copying numeric handles.

| RAX operation | Additional inputs | Success outputs |
| --- | --- | --- |
| 0x25000 clock | none | RAX=ticks |
| 0x25001 observe | RSI=worker handle | RAX=revision, RDX=terminal detail+1 or 0, R8=historical ready |
| 0x25002 register | RSI=worker handle, RDX=observed revision, R10=absolute deadline | RAX=wait token |
| 0x25003 status | RSI=wait token | RAX=pending 0 / changed 1 / timeout 2 / canceled 3 / target reclaimed 4; RDX=revision, R8=completion tick |
| 0x25004 cancel | RSI=wait token | Same retained status outputs; cancel only changes pending |
| 0x25005 release | RSI=wait token | RAX=0; invalidates token, frees slot |

Revision input may not exceed the current revision. At registration and every
subsequent trap completion, refresh pending waits: deadline <= current clock
wins over a simultaneous revision change; otherwise missing target completes
as reclaimed, otherwise revision mismatch completes as changed. Status remains
stable after completion even if the target is reclaimed. Cancellation refreshes
first, so it cannot erase an already observed event/timeout. Reclaim does not
implicitly consume a wait. Exact-deadline registration is immediately timed out.

## Delegated readiness mapping

Use one fresh channel per service generation. Supervisor retains its reader and
moves the sole writer at validated launch to either the first-party service or
a designated helper. Failed launch preserves the writer; successful transfer
removes old-holder authority. A service cannot further delegate through the
supervisor-only launch factory. General dup, arbitrary helper spawning, inheritance,
revocation trees and multiple writers are unsupported. No new grant API is needed
for a supervisor-launched helper. Payload generation fields are untrusted data;
receiver binds the endpoint to its own service-generation record.

Writer termination seals the queue; buffered bytes remain readable before EOF.
Reader closure forbids further writes (EPIPE); both closures discard and zero
bytes. Therefore sys-init must observe service liveness and its current generation
before admitting readiness, reject buffered notifications after owner death,
stop an independently running helper explicitly, close the old reader and allocate
a fresh channel for replacement. Closing a reader is not arbitrary revocation.
This profile does not provide atomic channel-read-plus-liveness admission; policy
must handle a service dying immediately after any observation. Channel polling
uses the SI-01 clock for its deadline; lifecycle registered waits do not wake on
byte arrival. See NATIVE-CHANNEL for bounded stream semantics.

## Supervisor death: fail-closed scope

ABI 6 deliberately has no recovery owner or replacement supervisor. Any supervisor
exit or user fault closes the whole local admission domain, invalidates all waits
and grants, terminates its two workers (including retained terminal records),
closes both channels and streams, detaches all three user roots, flushes local
translations, restores kernel-only writable aliases, zeroes all backing and
stream storage, invalidates retained state, then halts. No user task survives,
no inventory is exported and no resource is reused. The kernel remains the
bounded cleanup owner. This is fail-closed shutdown, not restart or panic recovery.

There is no old-owner execution path after shutdown, and therefore no runtime
stale-owner invocation or replacement-exhaustion experiment is claimed. Replacement,
lost-observation reconciliation and authorized inventory are ENOSYS/unsupported,
not inferred from M4. Cleanup failure panics without a success marker. Diagnostic
counts report the pre-cleanup live/terminal workers and queued channel bytes;
`AETHER NATIVE INIT CLOSED` is emitted only after cleanup invariants hold. Existing
profiles continue to panic on supervisor death. Cross-core stop acknowledgments,
TLB invalidation, transport disposal and owner-failure recovery require separate
M4-derived contracts and consuming tests; this local sweep never touches AP state.

## Reproduction and acceptance boundary

From Aether, with the existing source-rebuilt strict musl SDK and its pinned
Clang/LLD tool lock (explicit inputs, no automatic sibling discovery):

```sh
python3 scripts/launch_smoke.py --init --libc-build SDK_DIRECTORY --tools-lock TOOLS_LOCK
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The suite builds two strict ELF producers and the Aether conformance supervisor,
then retains source/tool/receipt hashes, exact build commands, binary identities
and serial logs. Positive tests exercise event-before/after registration, retained
completion, cancellation, stale token/target and foreign-worker denial, exact-or-
already-expired boundary, actual future tick timeout, one-slot exhaustion and
64-token retirement. Host tests cover the precise equal-tick event/timeout tie
and both possible serialized orders around registration. No claim is made of
forcing an impossible user event inside an interrupt-disabled syscall.

Target controls are wrong deadline expectation (701), accepting buffered readiness
from a dead owner (702), ignored kernel deadline (701), and skipped cleanup
zeroing (dedicated panic). Separate supervisor exit and #UD cases require both
one live and one terminal worker, two queued bytes and one retained wait before
verified shutdown. The suite is kernel enforcement/conformance evidence, not an
independently authored sys-init policy client. SI-01–03 integration remains open
until that project freezes these inputs and supplies its own consuming witness.
The current helper mapping is reviewed against its INTEGRATION-GATES, not an
assertion that arbitrary production helper delegation or recovery is solved.

## Sequential reuse regression (SI-04)

The regular `scripts/launch_smoke.py --init` suite now has nine cases. In addition
to the original seven, `sequential` and `sequential-reverse` launch, observe exit
17, close the reader and reclaim each worker before launching the next, in orders
0/1/0 and 1/0/1. Each checks stale observation after reclaim and requires the exact
terminal order, three reclaims and INIT PASS. This covers retired image metadata
being reconsidered during another slot's load. No ABI, authority or quota changes.
[SI-04 companion-source verification](evidence/native-slot-reuse-2026-09-05/README.md)
also retains sys-init's exact minimal reproducer and all nine adapter cases.

## SI-05 init capacity v2 contract — 2026-09-06

Before implementation: allocate opt-in AENIN002 / ABI 15, preserving AENIN001 /
ABI 6 and all old bytes/limits. This is the same 56-byte envelope: magic[8],
u32 first ELF length, second ELF length, supervisor length, reserved zero,
32 fixture entropy bytes, followed by the two ELFs and supervisor with exact
length. ELF lengths are 1..1048576; supervisor length is 1..8192 (v1 stays
1..4096). Check bounds before sums/slicing; reject truncation, extra bytes,
reserved fields and u32 maximum lengths before admission. This x86_64-only
parser has bounded sums after validation; no untrusted arithmetic may wrap.

Workers remain slots 0/1, supervisor slot 2; no third executable. Entry RIP
0x400000, RSP 0x800ff8, RDI=15, RSI=0xa001 factory, RDX=0xc001 first image,
RCX=0xc002 second image, R8=0xd001 channels, R9=0xe001 init observation.
Clock/observe/register/status/cancel/release, channel transfer, generations,
retained observations and owner-death semantics are unchanged. Code spans one
or two immutable user RX pages; separate one-page RW/NX stack at 0x800000.
Unused code tail is zero. Every kernel alias of code remains read-only/NX.
No memory/thread grant, recovery owner or authority inferred from ABI/size.

V2 normal oracle is AETHER NATIVE INIT LARGE PASS; fail-closed oracle is
AETHER NATIVE INIT LARGE CLOSED, only after existing all-domain cleanup checks.
Normal fixture completion remains result=100/reclaimed=3; shutdown clears both
code pages, stack, workers, channels and pending observation. Normal completion
halts with the supervisor still mapped, as in v1; it is not owner reclamation.

Qualify actual second-page entry, sequential reuse, deadline and cleanup controls,
lengths 4095/4096/8191/8192, zero/8193/huge lengths, reserved/truncated/extra
payloads, old-v1 oversize rejection, second-page write fault and stack NX fault.
Check code permissions/aliases and tail zero before publishing supervisor entry.
Run old init and affected launch/profile, native memory/thread and M4 regressions
on frozen sources plus host/standards/format. Preserve every attempt and return
an immutable source/tool/artifact/raw evidence bundle for independent sys-init
pinning and its 151 existing plus proposed guard cases. Producer qualification
is not consumer acceptance. No sibling/pin/shared standard changes.

After this one unblock, resume concurrent-child work per maintainer instruction;
UP-02 remains queued and does not take precedence in this turn.

Initial target attempt passed shutdown after a real stack execution fault, but
its new oracle compared the hexadecimal diagnostic against decimal 21. Compare
against hexadecimal 15 and retain the failed attempt. Add a deliberate nonzero
code-tail control that must reject before supervisor entry, and verify the second
image entry grant in the v2 client. No old-profile oracle is changed.

Reproduce v2 with `python3 scripts/launch_smoke.py --init-large --libc-build
SDK_DIRECTORY --tools-lock TOOLS_LOCK`; retain `--init` for v1 regressions.

### SI-05 producer results and consumer handoff — 2026-09-06

[The immutable local producer packet](evidence/init-capacity-2026-09-06/README.md)
qualifies 23 ABI-15 cases and nine unchanged ABI-6 cases within 207 selected target
cases. It includes source/boot dependency and SDK archives, tool identities, exact
commands, artifacts, raw logs, failed attempts and bundle hashes in producer.json.
Host checks pass 97 Python tests, Zig tests, standards/workflow and formatting.
The second-page workload, exact bounds, malformed/old-profile oversize rejections,
dirty-tail control and actual second-page write/stack-execute faults pass. Existing
launch, command, console relay, thread, memory, image and M4 checks pass.

Producer capacity is available; sys-init must review ABI/markers, explicitly pin
and independently run its 151 existing cases and proposed guard cases before
claiming adoption. No sibling or consumer pin was changed. Independent review and
extended coverage remain outstanding. The maintainer selected this one unblock;
Aether next returns to concurrent-child work rather than advancing queued UP-02.


## SI-06 composed init profile v3

AENIN003 / ABI 16 is a separate opt-in 1..16,384-byte code profile, retaining
the 56-byte envelope, two workers and all ABI-15 grants/lifecycle semantics.
AENIN001/ABI 6 and AENIN002/ABI 15 retain their exact 4/8 KiB limits and markers.
Code maps up to four RX pages at 0x400000, with every kernel alias RO/NX and
unused last-page bytes zero before entry. The stack stays RW/NX at
0x800000..0x800fff, initial RSP 0x800ff8. Existing arena capacity suffices.
Normal success halts without reclaiming the supervisor; owner failure retains
the existing whole-domain close/unmap/alias-restore/zero sequence.

New markers are `AETHER NATIVE INIT COMPOSED PASS`,
`AETHER NATIVE INIT COMPOSED CLOSED` and the bounded mapping diagnostic
`NATIVE INIT COMPOSED bytes=N pages=N mappings=verified`. Existing output remains
unchanged. Reproduce with `python3 scripts/launch_smoke.py --init-composed
--libc-build SDK_DIRECTORY --tools-lock TOOLS_LOCK`. Its full workload executes
from page four after executable jumps through pages one, two and three.

The producer contract and evidence are retained under
[evidence](evidence/init-composed-capacity-2026-09-07/contract.md). More code does
not enlarge or qualify the composed consumer stack. Sys-init must independently
consume matching sources/tools/SDK and validate its Terminal/reclaim-capture
composition; issued reclaim/Cleaned and owner recovery are separate work.
