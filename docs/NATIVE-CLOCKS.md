# Native elapsed clock and absolute wait

## Ordinary-app read-only monotonic grant

The [ordinary one-app launch](NATIVE-LAUNCH.md#ordinary-one-app-namespace-launch)
adds operation0x28012 with a distinct kind0x36 capability. Its identity uses the
existing codec but does not select sustained mode. One32-byte binding in the
authoritative local app State holds clock, namespace reader/writer and full
engine request-reader epoch. No global capability table or ambient query is added.

RDI is the exact held token; RSI/RDX/R10/R8/R9 must all be zero. The ordinary
combined ABI31 init/guarded-owner-stack profile is required. Query rejects an
unadmitted/terminal app, zero/wrong-kind/foreign/stale token or mismatched app slot
and nonreused generation with EACCES(-13), before sampling. Nonzero other operands
give EINVAL(-22). Disabled profile, disabled source or interrupt-tick diagnostic
substitution gives ENOSYS(-38). An authorized query returns checked nonnegative
signed nanoseconds, or the real source error: unavailable(-38), regression(-5),
overflow(-75). Values above INT64_MAX reject. The binding and user storage are
unchanged; the monotonic provider retains its existing source observations.

Terminal exit/fault, forced stop, reclaim, reset and init close clear the complete
binding; replacement cannot reuse the old lifetime token. This grant gives no
thread creation, RTC, wait or clock-adjustment right. Engine thread grants and
operations0x28000..0x28011 retain their contracts. The issue99 shared-core and
actual-body host tests cover authority before sampling, errors, signed overflow
and all binding-revocation sites. Device sampling is an explicit host substitute;
native qualification and issue100 consumer adoption remain separate.

## Idempotent supervisor clock mapping —2026-10-23

clock.attach accepts either an empty entry or its exact expected physical frame
and flags with only hardware Accessed bit5 permitted to differ. Source readiness
remains required. It preserves the observed Accessed state when installing the
same supervisor alias; every other flag/frame mismatch still asserts before a
mapping write. The MMIO leaf remains supervisor RW/NX/PWT/PCD, without user access
or adjustment authority. No clock/UTC policy, TLB protocol, mutable owner or budget
changes. Native exec retains kpdp while rebuilding low tables, so repeated attach
must accept this legitimate CPU-maintained state.

Actual attempt7 records ready1/have917a023/want917a003 immediately before the old
assertion; exact source/ELF verification attributes this occurrence to clock.attach.
Earlier generic-only failures retain their individual uncertainty. See
[decision0219](../sys-init/docs/decisions/0219-clock-attach-assertion.md) and
[review/evidence](reviews/2026-10-23-af07-kernel-panic.md). The final
matching three-guest sequence passes:7/0/0,21 cleanup,220 paired waits/halt1894,
full780248-byte recovery and unchanged recovery media, all VMs stopped. The final
931-method Python/all Zig checkpoint and11 owner-harness methods pass. This scoped
correction does not qualify the persistent shell/ISO.

The temporary selected ABI31 state logger is removed after preserving its source
in commit2348402be. No consumer treats its row as acceptance; normal output/panic
markers and old selections stay. Run `PYTHONPATH=tests python3 -B -m unittest
test_clock_attach -v`: actual Debug/ReleaseSafe attach, simulated hardware Accessed
between attaches, all64 bit alterations with Accessed clear/set, absent source,
wrong frames, no failed writes and four compiling semantic controls. Host bit
simulation is distinct from the actual native diagnostic above. No generic page-table
repair, widened mask or assertion bypass. The existing BSP/IF=0 owner serialization
and inactive exec target root remain; no general concurrent updater is claimed.

Private opt-in BSP q35 experiment,SI-01/R1-03,2026-10-05. Requires
-Dsmp=false,-Dnative-memory=true,-Dnative-threads=true,-Dnative-thread-pair=true,
-Dnative-clock=true with AENATC01/AENSUP01. Kernel clock mechanisms do not imply
musl/SDK adoption, UTC, cross-core time or OpenZFS startup. Current evidence and
next action belong in [STATE](../.planning/STATE.md).

## Current libc experiment scope — 2026-10-05

Requirement: exercise actual pinned musl 1.2.6 monotonic timed conditions and
elapsed sleep against the existing BSP clock/absolute park, in the private
two-child profile. Preserve the original absolute deadline across spurious
wakes, mutex release/reacquisition, and sleep retries. Reject invalid times,
overflow, unsupported clocks/shared waits and deadlines beyond the native
one-second admission bound. Native failures must reach the caller, never become
successful sleep or an endless condition retry. Realtime relative nanosleep
means elapsed duration; realtime absolute sleep/conditions still require UTC
and remain unavailable. Signal delivery/cancellation/interruption is not added.

Aether owns the fixture and native enforcement; userland owns maintained SDK
adoption. No kernel operations, pins, default SDK, sibling files or expanded
worker quotas change. Borrow musl's existing waiter-list and mutex cleanup;
replace only its timed backend conversion, which otherwise loses the absolute
deadline and suppresses unsupported native errors. Sleep uses a thread-local
stack word, not a shared service or new kernel object. The caller must supply
valid timespec/storage pointers as for the existing in-process libc boundary;
the kernel checks and pins each owned RW wait word while parked. No user pointer
borrow survives completion. Source failure and malformed values fail closed.

Simpler alternative: keep relative futex timeouts. It cannot preserve deadlines
between userspace conversion and park and hides provider failures. Reusing the
existing absolute primitive avoids another timer API; no old fixture is removed
until its existing consumers migrate. Test actual timeout/signal/relock,
spurious wake, absolute/relative sleep, expired/malformed/overflow/too-far/UTC
denials and deliberately early completion. Run affected legacy virtual timed
conditions plus host/pin checks. Retain compact hashes/results/logs only.

## Service-worker qualification scope — 2026-10-05

Requirement: enable the existing private elapsed clock/absolute wait with the
82-worker filesystem trial only after full-owner timeout, counted wake, requeue,
mapping-pin, stop/replacement and legacy qualification. All workers first park
on an untimed gate; publish one owner-local deadline only after capacity is full.
The service retains82 live slots/8192 pages and each peer two slots/128 pages.
No new time operation, grant, shared mutable owner, quota or production SDK.

Forbidden outcomes: early completion accepted as timeout, changed deadlines on
requeue, missing/excess wake counts, unmapping/protecting a live wait word, lost
registration after replacement or unresolved cleanup. Existing thread-capability
and RW mapping checks remain at the kernel boundary. Client stack/TLS words remain
mapped until confirmed native exit, then exact-ID retirement precedes unmapping.
Stop must quiesce all parked children before service memory is reused.

Tests borrow the already qualified bare storage descriptor/cookie witness, not a
production musl TCB. Measure observed deadline lateness including interrupt scan,
serial diagnostics and scheduling; reject a one-second settlement overrun in this
q35 trial. The scan is statically bounded by92 context pointers across four owners,
83 for the service and three per peer. Temporary largest list remains672 bytes;
no measured stack high-water or physical WCET claim follows. Keep one shared
deadline source sample per IRQ and owner-local bounded scans. The combined private
profile adds one post-scan read for measurement and three numeric counters plus a
validity bit; no context pointer or authority is retained. Broader platforms,
signals, expanded actual musl timed conditions and real engine sizing remain open.

Simpler alternative: leave the combination disabled. That prevents filesystem
workers using the required real deadlines. Reuse the existing wait records and
bounded scans instead of adding a timer queue/API. This removes the provisional
build incompatibility only after native proof; no unrelated runtime refactor.
Run focused native controls, existing two-child clocks and host/pin checks; retain
compact commands, hashes, outcomes and short logs, never generated archives.

## Source and ownership

BSP owns the stopped q35 HPET counter at fixed0xfed00000. Validate q35 bridge,
64-bit capability and reported10ns period; reject absent/unsupported/previously
owned hardware. Boot validates the physical pages of initial page tables through
usable/bootloader memory-map regions and checked HHDM addresses. Two reserved
4KiB kernel tables map one supervisor RW/NX uncached MMIO page at kernel PDP509;
all native roots retain that supervisor-only alias. Tables stay fixed after boot,
mutable clock/device state stays BSP-owned. No device pointer or adjustment rights
are returned to users. General ACPI discovery/physical platforms remain deferred.

Ordered bounded high-low-high reads avoid a torn low-word rollover. Epoch is source
initialization within this boot; checked128-bit counter*period conversion floors
to signed64 nanoseconds. Counter reset/full wrap, unavailable/stopped source and
range exhaustion reject. The reported counter tick is10ns; repeated reads are
allowed, and effective syscall/emulator observation granularity is not certified.
Observed target samples are multiples of1000ns. Scheduler latency and counter
accuracy are separate. Reported-period scaling is a q35 reference
qualification, not empirical physical/TSC calibration or calendar time. The
counter advances without delivered PIT interrupts; periodic PIT IRQs only schedule
expiration checks. No HPET comparators/legacy replacement or timer API is enabled.

Register facts: [Intel HPET1.0a](https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/software-developers-hpet-spec-1-0a.pdf),
[QEMU HPET](https://github.com/qemu/qemu/blob/master/hw/timer/hpet.c) and
[register header](https://github.com/qemu/qemu/blob/master/include/hw/timer/hpet.h).
These are research references; executable evidence pins actual emulator/tool bytes.
No upstream driver is copied. The accepted [clock direction](CLOCKS-TIMERS.md)
retains TSC evaluation, truthful UTC and coherent per-core timelines as later work.

## Native operations

RAX selects operation,RDI carries the existing caller's thread capability from
AT_AETHER_THREAD0xa001. A foreign/missing grant denies -13 first. Disabled
experimental clock returns -38. Native operation allocation is local, not a new
shared standards ABI or production musl clock ID. Existing0x2800e virtual time and
all older tick waits remain unchanged.

| Operation | Inputs | Success/result |
| --- | --- | --- |
|0x2800f observe|RSI selector0(monotonic);RDX/R10/R8/R9 zero|RAX signed64 nonnegative elapsed nanoseconds|
|0x28010 compare/park|RSI aligned RW32-bit owner-local word,RDX expected32-bit value,R10 absolute monotonic ns deadline,R8/R9 zero|Atomic comparison/register/park; later RAX0 on matching wake,-110 on timeout;RDX elapsed ns|

No user timespec pointer, mutable timer handle or new allocation. At most1s future
remaining time is admitted. Invalid reserved/selector/value/alignment/deadline fields
return -22; invalid RW word -14; mismatch -11 before expiry; already expired -110
without registration. Clock failure returns -38(unavailable),-5(regression),-75
(range exhaustion). Immediate error RDX is not an elapsed observation. Actual
registered source failure completes -5/elapsed0, never successful timeout.

Only current core/caller-owned word registrations are supported. Compare and park
run with IF=0; existing word pinning forbids unmap/protect until completion or stopped
teardown. Wait records explicitly retain tick or monotonic domain; requeue retains
original start/deadline/domain. Timeout precedes simultaneous wake, and expired
waiters do not consume wake count. Context reset clears registration. Source errors
settle registration as error. No signal/cancellation/retry/POSIX-condition semantics
are inferred; mutex atomic release/reacquisition and SDK adapters remain userland
integration work. Realtime/UTC stays unavailable rather than uptime relabelled.

## Qualification

The historical [qualification packet](evidence/native-clock-2026-10-05/README.md)
records actual musl/native-memory clients and source/deadline models. Its archive
setup/check recipes are retired under the maintainer's POC retention decision.
Use current pinned inputs and compact results for new qualification. Current
maintained scripts/thread_smoke.py --pair,--waits,--indefinite,--pthread-lifecycle
provide older semantic regressions with the matching current SDK/tools lock.
The private probe uses a word wait to demonstrate an actual scheduler park;
user-space yield/poll loops are used only to test read ordering, never as sleep.
Default image, normal output, released pins, quotas and siblings remain fixed.
Missing independent SDK/readers/physical targets and full engine remain explicit.

POC retention changed on2026-10-05: historical archive setup/check recipes are now
retired. For subsequent private clock work, use the checked current SDK/tool lock
in `.deps/native-current/sdk`, the retained `clock-probe.c`, and a fresh owned root;
keep compact results/logs rather than rebuilding historical archives. Maintained
legacy wait regressions accept that SDK through their existing explicit arguments.
See [DEVELOPMENT](DEVELOPMENT.md#evidence-and-failures) for retention and
[the disposal notice](evidence/README.md) for historical replay limits.

Private observation schema: `NATIVE CLOCK park task=N start=NS deadline=NS` on
successful registration and `NATIVE CLOCK timeout task=N now=NS elapsed=NS` on
clock-domain timeout completion. Values are decimal owner slot and source ns;
no authority token. Existing success/terminal/idle schemas remain. These scoped
machine observations accompany retained run start/end timestamps, not per-line host
timing measurements, latency/WCET
or physical frequency certification. The combined private service-worker clock
profile now has the scoped native qualification below.

## Libc test command

```sh
python3 scripts/libc_clock_smoke.py --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

The private `LIFE_REAL_TIME` fixture compiles unchanged upstream musl condition,
mutex, join, sleep and cancellation-state source from the SHA-verified 1.2.6 input.
Its checked `__timedwait_cp` patch sends only non-null deadlines to the absolute
backend; untimed waits retain the older route. The backend maps compare mismatch
to spurious wake, checks timeout observations against the original deadline and
propagates other native errors. No new dependency or syscall is introduced.
The exact upstream/local inputs, patch, compiler/linker commands and final ELF
hashes are kept in compact suite receipts; generated sources/objects/ELFs/images
are removed after each complete or failed run. No archive replay is required.

Timespec values are checked before multiplication/subtraction/addition. Future
waits above one second return EINVAL rather than repeatedly restarting a duration.
Default realtime timed conditions and absolute realtime sleep return ENOTSUP;
monotonic clock absence returns ENOSYS and source errors remain errors. Untimed
condition waits, shared conditions, signal delivery and cancellation remain under
the earlier fixture's limits. A condition timeout/error still goes through musl's
waiter unlink and mutex reacquisition. Nanosleep returns -1/errno; clock_nanosleep
returns its error number and leaves errno unchanged. Successful calls leave rem
untouched; no interruption/remaining-time claim is made. A sleep's local RW stack
word stays pinned only while parked, with no retained registration after completion.

Tests require native park/timeout lines and repeated identical deadlines, not just
wall-clock delay or a success marker. The deliberately early-timeout kernel must
fail sleep as EIO (fixture terminal331); a disabled clock rejects terminal330.
The legacy virtual timed-condition case still runs without enabling native-clock.

## Service-worker test command and scan observation

```sh
python3 scripts/service_clock_smoke.py --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

The `native-clock`/`native-service-workers` combination reuses the existing source,
wait records and worker bounds. It keeps absolute deadlines and wait-word pins
through counted wake/requeue and confirmed stop, with an expired or compare-mismatch
spare admission after full-slot denial. All backing is released only after native
clear-TID/terminal observation and exact-ID retirement. The largest service stack
requests remain256KiB per worker, with4KiB cookie pages; this is a bare native client,
not expanded production pthread storage or actual OpenZFS execution.

The private combined profile emits one numeric ASCII summary before the existing
supervisor result: `NATIVE CLOCK workers scans=N max_contexts=N max_ns=N valid=B`.
`scans` counts periodic wait scans; `max_contexts` counts all owner context pointers
examined (including unused records); `max_ns` is the largest source-observed scan
interval, including per-timeout serial formatting/output, but excluding refresh and
later scheduling work. `valid=0` means a measurement source was unavailable or
regressed; it cannot satisfy qualification. Three BSP counters and one validity bit
remain boot-local diagnostics with no authority or pointer cache. No normal profile
output changes. The existing q35 source granularity/accuracy limits still apply;
observed cost and static pointer bounds do not establish physical WCET, exception
stack high-water, full IRQ latency or a release performance guarantee.

The checker requires166 actual deadline registrations (two82-worker generations
and one two-worker peer), exact owner-specific timeouts, unchanged cohort deadlines
and distinct replacement deadlines. Wake has no timeouts; confirmed stop leaves84
live-generation timeouts. Deliberate early/wake/requeue/pin failures must produce
exact primary388/394/392/392 and supervisor401 outcomes before the existing panic.
The same pinned historical supervisor source validates normal yields/exit status,
stop144/kind3, three reclaims, stale grants and fresh replacement; historical setup
and archive recipes are never executed. The retained old bare park client supplies
one clock-disabled capacity regression. Maintained two-child musl clocks and normal
M4 regressions remain separate selections.

## Expanded actual musl timing scope — 2026-10-05

Requirement before implementation: exercise actual musl timed-condition cleanup
and relative/absolute elapsed sleep with82 real service pthreads/two peers, using
the qualified source/absolute-wait primitives and existing256/128KiB stacks,
4KiB guards, TSD destructors and join/retirement. Repeated expiration, explicit
spurious wakes retaining deadlines, broadcast/relock and confirmed stop/replacement
are selected. Malformed, overflow, over-bound and unsupported UTC requests must
return errors with mutex reacquired and no stale waiter. Deliberately early
completion must fail for its named result, rather than count as a successful sleep.

Authority remains the held thread/memory grants; caller-local libc timespecs and
private condition/sleep words are borrowed only during calls. Atomic diagnostic
publication is cleared before a waiter returns; confirmed native waiting is required
before injecting a wake. Actual upstream mutex/list cleanup owns synchronization;
no cancellation, signal/interruption, shared-process condition or UTC claim is
added. No kernel ABI, quotas, ambient authority, default SDK, released pins or
sibling files change. Aether owns this private conformance experiment; userland
owns maintained libc adoption; Rust filesystem/OpenZFS startup remains subsequent.

Reuse the pinned existing actual-pthread fixture with checked local insertion
points, preserving its original bytes/notices; keep the timing extension in one
owned source. Simpler alternative: repeat the bare capacity trial. It cannot prove
musl waiter-list, TCB, destructor and mutex semantics, so reuse actual musl instead.
This removes no runtime mechanism now, but avoids duplicating the pthread lifecycle
adapter or adding a timer queue/service. The only new build selection includes
upstream key functions for the real-time/TSD composition. Generated derivatives
are disposed after each attempt, with exact transforms/hashes and compact results.

Select full positive/repeated/spurious/broadcast/stopped native trials, exact early
and disabled controls, unchanged joinable/reaper regressions and host trace
corruptions. Run full host/pin checks and scoped C formatting. No unrelated M4 run
is needed unless kernel code changes. Update this reference, workflow inventory,
companion boundary and STATE with actual outcomes and explicit provider/engine gaps.

Expanded actual-musl command:

```sh
python3 scripts/service_libc_clock_smoke.py --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

The maintained runner SHA-checks the small historical actual-pthread/supervisor
source inputs, then records exact local insertion transforms. It never runs their
retired setup/archive recipes or edits historical inputs. The owned timing extension
uses a shared private monotonic condition/mutex, explicit per-worker publication
and one common900ms deadline per generation. Spurious injection wakes each confirmed
native waiter once; every callback retry retains that deadline. Broadcast wakes
through musl's existing waiter chain, with actual blocked mutex relock observed
before the parent unlocks. Each worker then executes a200ms relative nanosleep or
absolute monotonic clock_nanosleep. Each checks actual elapsed time, preserved errno
and untouched rem. Invalid condition deadlines and unsupported UTC return with
mutex reacquired. Final waiter lists/publications must be empty before destruction.

Trace qualification requires complete condition cohorts/original-deadline retries,
substantial real sleep parks, owner-specific periodic expiration observations,
actual66/34-page pthread mappings, bounded allocator retention,8192/128 quotas,
confirmed stop, stale-grant rejection and three reclaims. An absolute sleep can
already be due before its backend runs; expiration during an unrelated wake scan
has no periodic timeout line. These legitimate cases cannot be rejected by demanding
one periodic log per libc completion. Every libc result/elapsed-time assertion still
runs inside the actual witness. Interleaved lines alone cannot attribute each timeout
to a particular child; they supplement, not replace, those checks. Exact early381
and disabled380 controls require the primary terminal and supervisor401 before panic.
The same pinned original fixture supplies unchanged clock-disabled joinable/reaper
regressions. No new machine output, runtime operation or service boundary is added.

Expanded actual-musl qualification is recorded in the
[compact result](evidence/service-libc-clock-2026-10-05.json): all nine final native
cases and five smaller regressions pass, with168 Python host tests and eight new
trace corruptions. Seven initial compile/configuration/observer failures are retained
and classified. Final ordinary332/spurious498/stopped250 parks satisfy complete
condition cohorts; periodic settlement logs remain partial as described above.
Largest measured wait scan is15.562ms including UART diagnostics, exceeding the
nominal10ms tick interval; this is no full IRQ/physical WCET or production latency
certification. The source is independent of delivered ticks. Generated files are
removed; final expanded/small suites dispose448/1685 artifacts, about94/71MB logical,
without archives. Current input hashes and released pins remain unchanged.

The legacy backend is restored byte-for-byte from the checked timedwait transform
and compiled with its original upstream-specific recipe, including existing warning
migration exceptions. No broad suppression or default SDK fallback is introduced.
The new optional internal `pthread_keys` build selection only includes actual musl
key functions for the real-time/TSD composition. Next bind selected OpenZFS elapsed
callers to this backend with their actual domains/errors, then required scoped
providers/resources and measured engine startup/fini/restart. Production SDK,
UTC, cancellation/interruption and shared-process waits remain unqualified.

## OpenZFS elapsed caller scope — 2026-10-05

Requirement before code: adapt the selected pinned libzpool CV/delay and libtpool
elapsed paths to monotonic conditions and deadlines, then execute actual libzpool
functions with the qualified musl/native backend. Keep absolute hires deadlines
unchanged; tick deadlines/delays must follow the existing gethrtime() >>23 lbolt
quantum rather than truncating through integer119Hz/milliseconds. Preserve checked
sign/range/arithmetic, mutex owner clearing/reacquisition and explicit source/wait
errors. UTC helpers remain unavailable; uptime must never become a persistent date.

Aether owns this private port/conformance composition; userland owns maintained
SDK and the filesystem owner owns eventual engine/provider integration. Held native
thread/memory grants still authorize clock/waits and all words/mutexes/timespecs
are live owner-local borrows. Do not widen82/two live slots,8192/128 pages, one-second
future native waits, ABI, default SDK, released pins or sibling files. Long requests
must reject honestly under this private backend; long-wait production integration,
tpool worker lifecycle, UTC and full engine startup remain subsequent qualification.

Simpler alternative: relabel the default clock or return successful delays. That
would conflate UTC/elapsed domains or skip blocking, so choose small checked changes
to the actual upstream-derived source and reuse existing pthread qualification.
No new timer service/queue/framework is needed. Record exact function transforms,
reconstruct the selected baseline byte-identically, replace only reviewed objects
and retain upstream CDDL notices. Generated functions keep their upstream style;
new original bridge code uses the reviewed Clang21 formatting profile. Dispose
all derivative build artifacts, preserving compact hashes/commands/logs.

Complexity removed: these selected caller paths no longer convert elapsed deadlines
through UTC or truncate tick delays through milliseconds. The private test bridge
adds no production service boundary; it reuses the qualified pthread composition.

Selected tests: actual82/two-worker absolute CV timeout/spurious/broadcast/stop,
relative hires/tick CV waits, no-early exact tick delay and expired inputs; named
old-domain/early/disabled errors; deterministic actual-function arithmetic/owner
and tpool domain/error controls; unchanged actual-musl regressions; full host/pins.
Bind claims to the layer tested: full-object/ELF builds do not execute the engine,
and caller tests do not certify complete tpool/ARC/filesystem startup. Update
STATE, this reference and the existing workflow/companion boundary with results.

The private composition uses:

```sh
python3 scripts/service_libc_clock_smoke.py --openzfs --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

The optional mode copies exact selected header definitions into a generated probe
header and calls the actual complete libzpool object, compiled with section removal
for unused functions. It does not replace CV/mutex/delay with a model. A private
assert/exit bridge routes fatal125 to the owner's existing native exit operation;
the original success-only thread witness cannot otherwise report fatal `_Exit`.
It is absent from the selected full-engine relink. Raw POSIX error tests also clear
and restore the OpenZFS owner field across their unlock/relock, while holding the
actual lock when observing owner state. Lib tpool probes copy only its actual
initializer/deadline blocks; they do not start a pool or prove worker lifecycle.

New native waits remain bounded to one second. Tick requests use8388608ns per
tick, consistent with the current `gethrtime() >>23` contract; no global conversion
macro, ABI or approximate119Hz constant changes. Overflow/invalid native requests
and unsupported UTC fail explicitly, without reporting successful elapsed waits.

[Compact qualification](evidence/openzfs-elapsed-2026-10-05.json) records ten final
OpenZFS/native cases, nine unchanged actual-musl regressions and172 host tests.
Controlled actual-function C tests cover22 arithmetic/error/owner/block scenarios;
native traces retain complete common-deadline cohorts while allowing bounded extra
caller waits. Full-engine baseline and original objects rebuild byte-identically;
only two objects change, with no test observer in the selected ELF. Actual CV
timeout/spurious/broadcast/stop, relative hires/tick waits and8-tick delay pass.
Lib tpool block probes do not establish worker lifecycle. The private assert/exit
bridge reports exact125 controls; it does not qualify production diagnostics.

Two initial failed target attempts and two host-test setup mistakes remain in the
result, alongside an intermediate ten-case pass. The initial positive timeout's
exact cause was not established; missing fatal exit routing and raw-error mutex
owner bookkeeping were corrected before final qualification. All6458 input hashes,
103 frozen sources, released pins, workflow and simplicity hashes pass. Final scan
peak8.892ms includes UART and is no physical/WCET certification. Final port and
unchanged regression runs dispose479/448 generated files (about139/94MB logical)
without archives. Next qualify required scoped providers/resources and actual
heap/ARC/helper closure, production long waits and UTC before engine entry.

## Segmented long-wait scope — 2026-10-06

Requirement: qualify elapsed sleeps and actual musl monotonic conditions beyond
one second in an opt-in private conformance profile. OpenZFS's idle linger needs
longer waits; reject neither valid durations solely at the libc boundary nor
report an intermediate park timeout as the original operation's completion.
Keep the original absolute deadline and the native one-second park admission.
Each chunk uses the same capability/word and checks its own timeout against a
fresh source read. Wakes/mismatches return to musl; native errors remain errors.

Forbidden outcomes: restarted original deadlines, successful early completion,
spinning instead of native parking, swallowed denial/source errors, stale wait-word
borrows or changed default SDK/kernel/ABI/quotas. Userland owns production adoption;
Aether owns this private producer witness. No sibling or released pin changes.
UTC, signals/cancellation, physical accuracy and actual engine entry stay excluded.

Simpler alternative: enlarge the kernel admission bound. Repeated bounded parks
compose the existing primitive without adding kernel policy or native operations.
One reviewed loop in the opt-in backend is sufficient; no timer service, mutable
registry, allocation or retained pointer is introduced. Caller-local timespec/word
borrows and native mapping pins remain in force for each park and through its
completion. Stop/reclaim retains the existing kernel contract. Default short-only
builds remain unchanged; the opt-in is an experiment, not a second public SDK.

Select actual-C controlled clock/park tests for chunk limits, final deadline,
wake/mismatch, early intermediate timeout, authority/source failures and signed
range boundaries; actual two-second relative/absolute sleeps and monotonic
conditions with original-deadline retries, reacquired mutex and waiter cleanup;
and deliberately early native completion/old-bound rejection. The two-second
condition runs on each primary; unchanged child conditions supply the spurious
wake/signal/contended-relock regression, not a long-wait cohort. Use the existing private libc clock
runner with a documented long-wait mode. Reuse unchanged kernel/default-profile
results only after checking default object identity. No full host/native suite is
selected for this bounded private adapter change; maintained SDK intake remains
the next broad checkpoint. Longer production linger and full engine budgets are
not qualified by a two-second witness. Keep compact results and remove outputs.

Run the focused opt-in profile from the repository root:

```sh
python3 -m unittest discover -s tests -p test_long_waits.py -v
python3 scripts/libc_clock_smoke.py --long-waits --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

The long mode runs real/repeated/early/old-bound cases; the default five-case profile
is unchanged. Old-bound keeps the long-aware condition fixture but recompiles the
actual helper without the opt-in, requiring exact341 rather than generic failure.
The existing30-second VM watchdog and native one-second admission remain intact.

For a correction affecting only one control, the same runner accepts `--case`:

```sh
python3 scripts/libc_clock_smoke.py --long-waits --case old-bound --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

Selection rejects unavailable/unknown cases before any build; a one-case result
reports only that case. All modes verify the boot envelope contains the recorded
ELF. Default five-case and opt-in four-case plans remain explicit; subset success
cannot stand in for a complete profile at the next broad checkpoint.

## Service long-sleep and stop scope — 2026-10-06

Requirement: compose opt-in segmented elapsed sleep with the actual82/two-worker
fixture and confirmed stop/replacement. Keep the existing900ms shared condition
cohorts, original-deadline spurious retries and real musl mutex/TLS/TSD/retirement;
then every completed worker takes a two-second relative or absolute sleep.
The stop trial waits until all82 service workers have entered those sleeps, parks
the primary until more than one second after the latest start, verifies every
worker is still parked and none has completed sleep, then exposes stop readiness.
Thus stop occurs after first-chunk expiry rather than before long sleep admission.

Forbidden outcomes: early sleep, source errors hidden as timeout, pointer/backing
reuse before quiescence, stale registrations in replacement, changed quotas or
public SDK/kernel contracts. Wait words are caller-local/native-pinned for each
park; fixture atomics publish scalar start times/counts only. No new service,
mutable authority table, allocator, timer object or production POSIX interface.
Aether owns the producer witness; userland still owns maintained SDK integration.

Simpler alternative: reuse the two-child result alone. It does not exercise live
segmented waits during82-worker teardown. Reuse the existing supervisor/adapter
and segmented helper, add only opt-in fixture observations and a native park for
the primary's stop staging. Keep default short-mode bytes unchanged. Existing
machine output/markers remain unchanged; no new renderer behavior. Reuse earlier
helper arithmetic/error proof after source identity review.

Select timeout/spurious/stop and old short-backend384 controls in the long profile,
one default timeout regression and focused trace/selection tests. The shared
conditions remain short; this does not qualify82-worker long conditions or actual
30-second tpool linger. A narrow supported case selector reports only executed
cases, never full-suite acceptance. Freeze sources, preserve compact failures and
remove generated outputs; maintained SDK intake remains the next broad checkpoint.

Focused service commands (the first selects four cases):

```sh
python3 -m unittest discover -s tests -p test_service_libc_clock.py -v
python3 scripts/service_libc_clock_smoke.py --long-waits --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
python3 scripts/service_libc_clock_smoke.py --case timeout --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
```

Use `--long-waits --case stop` to rerun only that available control after a
relevant correction. Long mode rejects OpenZFS modes/unavailable cases before a
build; other case selection rejects unknown cases rather than passing zero cases.
The default full profile remains available. No new kernel/renderer diagnostics.

[Compact result](evidence/service-long-sleep-2026-10-06.json): timeout498 parks/
429 timeouts, spurious664/430, stop501/402 and actual old-bound384 rejection pass
across three attempts. Every native park remains at most one second; successful
supervision requires exact three reclaims. Default timeout passes332/243 and its
ELF matches the prior qualified image. Final-source build-only checks reproduce
the executed timeout/spurious/stop ELFs exactly, permitting focused reuse after
the STOP_LIVE-only correction and whitespace change. Kernel/build, supervisor,
other adapter inputs and all242 selected SDK members remain unchanged. This is
combined selected-case evidence, not a full final-profile or production SDK run.

Initial stop failed387 before workers left the900ms condition: bounded yields
finished before elapsed time. Primary now parks through that deadline before
checking sleep entrants. Both formatting failures and the native failure remain
in the compact receipt.14 service and11 workflow host tests, inventory41/25/84,
syntax, scoped C formatting and exact default OpenZFS adaptation pass. All generated
run outputs are removed; only compact JSON/logs remain. No large engine/full suite
is selected for this opt-in fixture change.

Actual engine-runtime integration still needs the matching maintained SDK/backend
and tool lock through the [handoff](COMPANION-PROJECTS.md#native-storage-runtime-integration-gate--2026-10-06).
Long conditions at82 workers, real30-second tpool linger, truthful UTC and required
provider/engine/helper/ARC/entropy budgets remain separately unqualified.

## Maintained runtime intake scope — 2026-10-06

Requirement before implementation: independently consume userland's corrected
private service-runtime-v0 supplement, seal
`101001e0edefb8471546ebc85d9aea6ffa759529243c8507abe288ddb84d0ba1`,
without promoting default SDK pins or copying a second base SDK. Verify all282
delivery members and matching240 base-seal members before consuming code. Retain
one dependency copy of the supplement, its sources/notices and link metadata;
use the existing guarded base. Rebuild privately and compare the delivered archive.

An independent application uses public delivered headers/archive, actual pthread
TLS/TSD, long monotonic condition/sleep, detached retirement and charged reaper
accounting. Fill81/one application slots, reject extra admission unchanged, close
admission with busy finish, join remaining workers, then confirm zero live after
finish. Existing supervisor operations require exact successful owner generations,
stop/reclaim and fresh replacement; do not reuse the private conformance backend.
Actual clock-disabled and dishonest early-expiry controls must reject for named
application reasons. Strict link must omit the old generic adapter; inspect actual
engine composition rather than calling a successful fixture engine startup.

Forbidden outcomes: unsealed/mutable sibling inputs during build, overlapping
strong runtime adapters, stale handles or backing reuse before confirmed cleanup,
lost lifetime charging, fabricated UTC/provider success, relaxed kernel quotas,
or unsupported synchronization silently accepted. Caller-local pointers remain
valid libc borrows; native kernel checks bound/pin wait words. Runtime state is
owner-local. Admission/retirement is userland-owned; kernel ABI and service policy
stay with their owners. Cancellation/signals/UTC remain explicit exclusions.

The smaller alternative of replaying producer images would not independently
exercise the supplied archive. Use one native client and existing supervision;
no new service framework, production libc fork or general SDK selector. Select
intake/seal/oracle host controls, complete affected intake native cases and the
full host suite once at this integration checkpoint. Keep commands/hashes/short
failures and remove all generated outputs. Matching engine providers/lifecycle
remain the next gate even if intake passes.

Commands from the repository root:

```sh
python3 -m unittest discover -s tests -p test_service_runtime.py -v
python3 scripts/service_runtime_smoke.py --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The CLI accepts `--case normal|stop|disabled|early`; it validates coverage before
intake and reports only selected cases. Help/version use stdout and exit0,
usage errors use stderr/64, failures stderr/1. Output is plain ASCII with escaped
untrusted control characters; existing kernel/protocol markers are unchanged.
The existing native smoke helper has its scoped historical presentation exception.

[Compact result](evidence/service-runtime-intake-2026-10-06.json) records independent
normal/stop native lifecycles and exact804/802 controls across three native attempts.
All282 sealed delivery members and240 unchanged SDK members verify; runtime archive
`0d9b906f2fcf505ee69bc7c74a7e0e2ad4fb805f53963a343fdd709fbfcb6178`
rebuilds identically. One reaper leaves81/one application slots. Full capacity,
TLS/TSD, long conditions, detached cleanup, EAGAIN output preservation and busy/final
shutdown retain84/four admissions and end at zero live. Stop uses API143/kind3,
then exact three reclaims and fresh replacement. Explicit stop is not an ordinary
terminal log line; the original checker failure and its source-bound correction
remain distinct from actual native failure. Two prior compiler setup failures
remain compact. Final client/supervisor/kernel identities justify rechecking the
existing successful traces, without repeating their VM runs or claiming a full
final-profile run. Full host checkpoint passes196 Python checks; final CLI-only
and input-copy checks pass five focused tests. Inventory41/26/85, format/syntax/input checks pass.

The retained whole engine strictly links with the supplement after removing the
old adapter; keeping both yields named duplicate `__aether_io`. Map input identities
bind actual runtime objects, not default libc substitutes. The retained startup
object has no new runtime init/finish; this composition is build-only and must not
be booted as an initialized engine. Generated outputs are disposed, leaving compact
results/logs and one dependency supplement/source/notice copy. No second SDK copy.

The old SDK-delivery blocker is cleared. Before actual engine execution, compose
the selected native ports/providers and explicit serialized init/finish lifecycle,
qualify queues/helper/ARC resource admission and required identity/configuration/
volume/UTC/cancellation/linger semantics.82 observed host application workers plus
one reaper exceed the82 native worker limit; neither a quota increase nor a revised
engine policy is selected by this intake. Remaining work is local, not a claim
that every Aether backlog item is externally blocked. No engine or R1 acceptance.

## Maintained runtime OpenZFS waits scope — 2026-10-06

Requirement before code: compose the pinned, already selected OpenZFS mutex and
monotonic CV functions with the maintained runtime archive, independently of the
old private backend. Reuse the existing runtime client and supervisor: actual
OpenZFS callers must preserve mutex ownership across two/three-second waits at
81/one application workers plus the charged reaper, normal finish and confirmed
stop/reclaim/replacement. Missing clocks must reject804; dishonest early expiry
must reach actual OpenZFS fail-closed125 rather than become a successful timeout.

Forbidden outcomes include mixed adapters, ambient authority, weakened quotas,
unchecked input drift, fabricated timeout/UTC, and reuse before confirmed reclaim.
Objects and words remain owner-local; the kernel retains existing pin/park checks.
An assertion-to125 bridge is private caller-test code, never an engine provider.
No engine entry, pool lifecycle, persistence, resource-policy or SDK-pin changes.

The simpler alternative is the existing POSIX-only client, but it cannot show the
actual OpenZFS caller's error and owner bookkeeping. Reuse its lifecycle and the
existing pinned port builder with one opt-in adaptation; no new runtime or test
framework. Nothing obsolete can be removed yet: the old private fixtures still
qualify distinct ports. Select focused adaptation/oracle tests, actual normal/stop
and disabled/early native cases, workflow inventory and scoped formatting. Keep
compact results and dispose generated outputs. Full host coverage was completed
at intake; this caller-only extension does not change kernel/shared interfaces.

```sh
python3 -m unittest discover -s tests -p test_service_runtime.py -v
python3 -m unittest discover -s tests -p test_openzfs_elapsed.py -v
python3 scripts/service_runtime_smoke.py --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2 --openzfs-waits
```

The same `--case` selects one affected case for diagnosis. Without
`--openzfs-waits`, the original client and802 early-expiry oracle are unchanged.
The opt-in derives a checked private client, copies pinned CDDL declarations,
reproduces the pinned port baseline, and links function-section caller objects
with the maintained archive. Map checks require actual OpenZFS object origins.

[Compact result](evidence/service-runtime-openzfs-waits-2026-10-06.json) records
all four cases passing on one frozen source set. Normal/stop retain exact three
reclaims and fresh replacement, full81/one application capacity plus reaper,
busy/final finish, TLS/TSD and detached cleanup. Actual OpenZFS CV/mutex functions
preserve owner reacquisition and two/three-second deadlines. Missing clocks reject804;
early expiry reaches actual caller assertion125. Maps bind all four actual callers;
the selected baseline rebuilds identically.21 focused host checks and inventory
41/26/86 pass; scoped formatting/syntax and offline pins pass. All6458 engine inputs
verify after the run. A wrong checker path failed before the corrected command;
that diagnostic remains distinct from successful checks.515 generated files
(76,343,418 bytes) are removed; retained run files are JSON/logs only.

This does not execute `kernel_init`/`kernel_fini`, the tpool lifecycle or a pool.
The next composition must bind all selected provider ports and explicit serialized
runtime init/finish around actual engine startup/fini. Native queue/helper/ARC/heap
admission and identity/configuration/volume/UTC semantics remain gates before
execution. The82-record limit and32MiB ARC floor are unchanged; passing this
private caller cohort does not admit the engine profile or establish persistence.

The next [whole-engine build-only selection](OPENZFS-FEASIBILITY.md#maintained-engine-composition-scope--2026-10-06)
uses `--engine-link` in the same runner. It composes all implemented provider ports
and explicit lifecycle calls; native case selection is incompatible. Its host/build
checks and remaining entry gates are recorded in the filesystem feasibility reference.

## Raw RTC intake scope — 2026-10-06

Requirement before code: supply a bounded coherent raw calendar-source observation
for Aether-userland's assigned shared UTC policy. This private BSP q35/TCG profile
reuses the held thread grant for read-only observation; no clock-adjustment right,
UTC epoch, libc clock ID, new service or calendar conversion enters the kernel.
Only `native-rtc` plus the existing native-clock/thread pair enables it. Defaults,
older operations, worker/backing quotas, SDK bytes and released pins remain fixed.
Aether owns native enforcement/source qualification; userland owns source trust,
calendar conversion, runtime UTC publication and checked timestamp consumers.

Private operation0x28011: RDI is the exact live owner's thread capability, RSI an
8-byte-aligned owner-local writable64-byte record, RDX64, R10/R8/R9 zero. Check
capability first(-13), enabled profile(-38), fields(-22) and **every** output byte
(-14) before device access. Overflowing/cross-page ranges must fail without any
output mutation. Borrow storage only during the synchronous IF=0 call; copy the
entire zero-initialized result only after success. No pointer survives return.

Little-endian record: u32 version1/size64/source-kind1(q35 emulated RTC)/flags0;
u64 monotonic-before/after nanoseconds at offsets16/24; ten raw bytes at32:
seconds, minutes, hours, day-of-month, month, year, century(register0x32), A, B, D;
22 reserved zero bytes. Two identical observations bracketed by UIP checks,
SET clear, normal32kHz divider and battery-valid flag are required. At most eight
attempts and2ms observed elapsed are admitted; instability/budget exhaustion
returns -11, invalid/unavailable source -38, monotonic regression -5/overflow -75.
Hardware flags/labels are observations, **not authenticated UTC or trust**. Raw
BCD/binary/12h/24h calendar validation stays in userland. Resolution is one second;
read bounds do not eliminate that quantization or establish accuracy/UTC offset.

The source is deliberately QEMU TCG only: require the TCG hypervisor signature
and existing validated q35/HPET profile. BSP serializes selector/data access;
no IRQ/NMI handler accesses CMOS. QEMU masks selector bit7 and its index read
returns0xff, so reading port0x70 cannot preserve an NMI mask. This provider never
reads that index, writes CMOS data, clears register C, or programs RTC interrupts.
It writes only index0x70 with bit7 clear, which has no NMI side effect on this
emulated device. Physical/other hypervisors remain unavailable; their selector/NMI
ownership, ACPI century discovery and source validity need separate qualification.
[QEMU RTC source](https://github.com/qemu/qemu/blob/master/hw/rtc/mc146818rtc.c)
and [register definitions](https://github.com/qemu/qemu/blob/master/include/hw/rtc/mc146818rtc_regs.h)
are research references, not a claim to have inspected a matching11.1.1 source tag;
executable tests pin the installed emulator bytes. No upstream driver is copied.

Forbidden outcomes: a torn calendar sample, guessed century/epoch, uptime passed
as UTC, unbounded polling, physical NMI state changes, foreign/stale grant success,
partial output or adjusting calendar time through a read operation. Focused pure
source tests cover update/mode changes, invalid/frozen sources, retry/budget and
source failures. Native tests use explicit QEMU dates (including a leap day),
wrong grants/reserved fields/read-only/cross-page outputs, repeated owner replacement
and disabled-source denial. Maintained runtime's UTC remains unavailable.

Simpler alternative: explicit userland UTC configuration alone remains allowed,
but it cannot qualify the required raw source intake for unattended startup.
Reuse the existing clock grant/syscall rather than add another service/table/RTC
object. One cohesive bounded reader and architecture adapter are the added cost;
no old path is removed. Physical discovery, synchronization, adjustment, realtime
waits and persisted timestamps remain subsequent affected-owner work.

Command (current sealed maintained runtime, with ordinary profiles unchanged):

```sh
zig test kernel/native_rtc.zig
python3 -m unittest discover -s tests -p test_rtc_source.py
python3 scripts/service_runtime_smoke.py --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2 --rtc-source
```

Use `--case rtc`, `--case rtc-leap` or `--case rtc-disabled` for focused iteration.
The QEMU dates are explicit test inputs, not a production configuration or a UTC
trust decision. Source samples validate in the target; numeric values are not
exported as measured accuracy. Owned images/builds are disposed after each run.

### Aether-userland UTC intake requirements

The maintainer assigned shared UTC policy to Aether-userland on2026-10-06.
[Compact source result](evidence/rtc-source-2026-10-06.json) supplies the native
boundary above; the elapsed-v2 supplement supports monotonic only. The
UTC owner delivery must preserve the guarded base, explicitly declare source
interpretation/trust and establishment lifetime, validate calendar/mode/century and
checked epoch arithmetic, publish a consistent shared runtime estimate, and keep
unestablished/malformed/unavailable sources as errors without output mutation.
Source-kind1 and VRT do not certify UTC; interpret an RTC as UTC only under explicit
profile/configuration policy. Declare one-second quantization/read uncertainty;
nanosecond timespec fields do not establish nanosecond accuracy. No adjustment,
synchronization, realtime absolute wait or daemon requirement is implied.

Provide an opt-in reproducible sealed runtime/recipe and actual positive/failure
consumers for independent intake here. Rebuild checked OpenZFS timestamp consumers
before persistent pool claims; engine bodies ignoring libc failure remain unsafe.
The later [opt-in UTC intake](OPENZFS-FEASIBILITY.md#shared-utc-engine-intake-scope--2026-10-06)
supersedes the missing-delivery gate and passes actual engine consumers. The
[reaper handoff below](#result-and-maintained-owner-handoff) records the current
maintained-runtime blocker; independent reader acceptance remains open.


## Maintained runtime detached-reaper cycle scope — 2026-10-06

Before implementation: review of the exact sealed elapsed-v2 backend identifies
an executable wait-cycle hypothesis, inherited unchanged by opt-in UTC-v2.
After allowing detached A to exit, `reap()` observes native stop and then takes
musl's thread-list lock. Detached B can acquire that lock while exiting, publish
pending retirement in actual `__unmapself`, and wait for reaper permission. The
reaper cannot reach B while blocked on B's lock. This is not yet a native witness
or attribution of the earlier OpenZFS stall; distinguish those claims.

A private C probe will link the exact maintained archive, transparently wrap
external `__unmapself` and reaper `__tl_lock` entry to order the two exits, and
call both original bodies.
It never writes private pending/allow-exit records, changes reaping or supplies
synthetic native state. A emits a readiness event from its exit wrapper and waits until B has parked
on its held musl lock, then calls the original exit body. After A stops, the reaper lock-entry wrapper yields until B owns the real lock,
then invokes the original acquisition. B then
owns the real thread-list lock and delays entry only until A has natively stopped
but remains unretired and the reaper is parked. B then enters the original body;
two subsequent observations, separated by a real monotonic park, must show both
B and reaper parked, A stopped/unretired, and the real lock still owned by B.
Only that complete cycle yields diagnostic terminal870. Generic assertion (`1000 + source line`),
unformed ordering or elapsed watchdog failures cannot satisfy it. The owner then
terminates as a diagnostic failure: no clean finish, UTC close or reclaim claim.

A serial-exit control holds B in its callback until A's native record is retired,
then allows B's original exit. It must finish with runtime live0 and normal
owner/replacement/reclaim. The existing small peer runs only its charged reaper
and clean finish; the two-application-worker ordering applies to the8192-page
owner. Native IDs come from capability-authorized queries; the sealed private
profile's eight-ID admission stride identifies its first reaper. Numbers confer
no authority. Only status is observed; the runtime still owns unmap/retirement.
All pointers are same-owner static/stack borrows, callback arguments live for
the whole run, and atomic flags publish ordering. No native ABI, kernel, SDK,
calendar, quota, or sibling change; preserve82/512/8192 and current watchdogs.

Simplicity: use the existing maintained-runtime runner, original archive, existing
query/wait/wake primitives and a narrow linker wrapper. A new scheduler or tracing
interface would add authority and duplicate mechanisms. No runtime complexity is
removed here; attribution must precede an owner fix. Test actual link origins and
wrapper omission, profile rejection, cycle and serial control with compact frozen
receipts. If confirmed, the maintained-runtime fix belongs to Aether-userland;
current pins cannot be silently patched locally or promoted.

### Result and maintained-owner handoff

[Compact witness](evidence/service-runtime-reaper-cycle-2026-10-06.json) confirms
the cycle in the exact elapsed-v2 archive: terminal870, supervisor401 and zero
reclaims. Five actual ELF/map origins bind both wrappers plus original
`__unmapself`, `reap` and `__tl_lock`; the exit-wrapper omission cannot link.
After entry ordering has ended, two native observations separated by an actual
one-millisecond monotonic sleep see A stopped/unretired, B and reaper parked,
B owning the real musl lock, and runtime live/admissions3. The serial-exit control
passes live0 shutdown, normal terminals, replacement and three reclaims with the
same maintained archive. This is an executable adverse schedule, not a claim of
exhaustive scheduling coverage or a spontaneous reproduction of the original
UTC/OpenZFS stall. Initial build/ordering/assertion failures remain in the receipt.

Aether-userland owns the fix. Its reaper must never block on a lock held by a
worker that requires reaper permission to exit. Protect mutable admission/reaping
records and lifetime independently of that circular dependency; draining a
snapshot of pending workers before acquiring the list lock alone still races with
a new detached exit. Keep the charged reaper, confirmed native stop before
unmap/retire, owner-local authority, failed/busy finish semantics and82/512/8192
limits. A reviewed fix must include adversarial overlapping detached exits,
serial retirement, joinable workers, busy/final shutdown, exhaustion and
stop/replacement. No unsafe unmap or early live0 may replace the deadlock.

Deliver a reproducible new sealed elapsed supplement and rebuild the opt-in UTC
supplement against that exact fixed base. The current UTC archive inherits the
same backend source byte-for-byte. Independent intake here must verify seals,
actual bindings and cleanup, replace this expected-defect oracle with an owner
fix's successful retirement oracle, and rerun the affected maintained-runtime /
actual OpenZFS helper-reuse cases before SPA/ZIO/persistence qualification.
The guarded SDK/native ABI can stay unchanged. Neither current candidate is
silently patched, promoted or accepted by this diagnostic; human reader review
and the earlier missing-terminal attribution remain open. No sibling is edited.

Reproduce the current defect and serial control from the repository root:

```sh
python3 scripts/service_runtime_smoke.py --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2 --case reaper-cycle
python3 scripts/service_runtime_smoke.py --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v2 --case reaper-serial
python3 -m unittest discover -s tests -p test_service_runtime.py
```

## Corrected reaper v3 independent intake scope — 2026-10-06

Before code: userland now supplies immutable elapsed v3 (294 members, seal
`5adc4f6e9c255df3ead08404fca177d22db00a089429f1c0666fd90dd1812c6d`, archive
`8262b1977be3b8fff449a6e9ac6d86b20acbc7ab0a1e38102287aecff20b9b23`) and
UTC v3 (343 members, seal
`ce420b8ac745287ea057b6c0b8949eb436a63b519e270b7ed7bf164ef342bad3`, archive
`693518d97acafe99f427cae5b42b5cc7aea7f0e8656c17f185fc8c24a0e06150`).
The guarded240-member SDK is unchanged. Preserve v2 diagnostic/default selections
and all released pins; choose these new candidates only through an explicit
`--fixed-reaper` intake. Copy/verify into separate retained dependency roots,
verify exact nested base and tool hashes before executing sealed recipes, and
require archive-identical offline rebuilds. No mutable sibling recipe is executed.

Requirement: independently qualify corrected record ownership and overlapping
retirement before actual SPA/ZIO. Creators/joiners retain musl serialization;
sole reaper owns pending detached records through stop/unmap/retire, resets state
and live before publishing atomic thread=NULL last. Creator acquire of NULL must
order that cleanup before reuse; finish may see live1 before NULL but joins the
reaper before successful live0. No reaper list-lock acquisition may depend on an
exiting worker awaiting its permission. Preserve fail-closed stop, authority,
82/two live workers,512 admissions,8192/128 pages and existing watchdogs.

Use the existing two-exit witness for a successful corrected schedule: B holds
its actual musl list lock until A's native record has been retired, then enters
original __unmapself; repeat eight times before normal live0 finish. Old v2 still
requires exact870, never a successful retirement claim. Serial control and the
existing full-capacity join/TSD/busy-final-shutdown/stop/clock controls exercise
direct consumers. Add a small independent lifetime-exhaustion probe requiring
all512 charged admissions, unchanged denied pthread handle and live0; do not
reuse userland's passing receipt as native acceptance. Then rerun actual UTC
SPA/taskq helper reuse and source/policy/phase controls with the new nested base.
No fabricated UTC, record writes, early unmap, quota widening or pool acceptance.

Simplicity/security: use existing owner-local observations and runner, no second
scheduler/record lock or interface. The simpler fix is userland's atomic free-last
publication and removal of the circular lock dependency, whose source contract
is reviewed above; another lock hierarchy is unnecessary for sole-reaper records.
A small explicit candidate switch preserves the still-used v2 defect control;
no general version manager is needed. This intake adds no trusted kernel surface,
service/policy boundary or dependency license. Static atomic ordering words and
callback arguments live through confirmed retirement; original runtime still owns
cleanup. Runtime native checks, actual helper composition, malformed/mismatched
seal/profile controls and scoped formatting/syntax are selected; broad host/Zig
checkpoint once at completed integration. No production pool, independent human
reader sign-off, spontaneous stall attribution or sibling edits follow.

Initial intake correction: v3 keeps the exact tools lock under its sealed SDK,
not at the packet root. The first attempt stopped before building; use the already
verified identical guarded SDK lock. The initial independent512-admission probe
used the two-worker witness's two-second budget for the whole512-operation
workload, and rejected at its own deadline (1042), not the supervisor watchdog.
That is not exhaustion acceptance or evidence of a second deadlock. Before its
rerun, set this new workload's explicit overall budget to15 seconds with a
one-second progress bound per retirement. Keep existing guest/supervisor/other
probe bounds and512/82/8192 unchanged. Preserve the failed native attempt.

### Corrected candidate intake result

[Independent v3 result](evidence/service-runtime-fixed-reaper-2026-10-06.json)
verifies294/343/240 seals and identical isolated elapsed/UTC rebuilds. Four
wrong-revision selections reject the exact seal before build/copy; unsupported
candidate/profile combinations reject as usage before intake. The new selector
leaves default v2, guarded SDK and all released standards pins unchanged.

Seven corrected elapsed native cases pass: ordered overlap, serial exits,512
admissions, normal capacity/join/TSD/busy-final shutdown, stop/replacement, disabled
clock804 and early expiry802. Each successful case requires all three owners to
finish/reclaim normally; stop retains its confirmed-stop oracle. Eight overlapping
pairs per large owner explicitly retire A while B holds the actual musl lock,
then enter original B exit and retire it, ending live0. Exhaustion requires512
charged admissions in each owner (511 application workers plus reaper), rejects
one more without changing its handle, and finishes live0. The old v2 archive still
produces exact870/401/zero reclaims with the same final witness source.

Six corrected UTC/actual-engine cases pass: normal/leap timestamps, disabled RTC856,
missing policy855, eight actual SPA/taskq reuse cycles per owner (24 total,29 phase
rows) and the exact short847/zero-reclaim control.49 actual origins bind checked
time, actual upstream SPA/taskq and maintained providers. Whole readonly media
stays unchanged; helper drain/destroy and UTC close precede live0 runtime finish.
No initialized SPA, physical ZIO, pool/create/import/transactions/reboot or
production filesystem service is qualified. Initial leap-stall attribution and
independent human reader sign-off remain open; the confirmed reaper delivery
blocker is cleared within this private candidate intake. Continue actual SPA/ZIO
qualification on explicitly selected v3, without silently promoting defaults.

The later [UTC evidence assessment](OPENZFS-FEASIBILITY.md#utc-timeout-evidence-assessment--2026-10-07)
verifies the original failed report/remaining full serial log and exact v2/v3
backends. No terminal/phase/lock snapshot can attribute the original event. The
separately proven defect class is corrected, but its causal connection remains
unknown. An independent human must decide whether that superseded-v2 observation
is adequately bounded for the disposable opt-in-v3 pool experiment; reviewer
assignment or source/fixture checks cannot supply acceptance. This assessment
does not alter any native/runtime/UTC contract or released/default pin.

```sh
python3 scripts/service_runtime_smoke.py --fixed-reaper --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v3
python3 scripts/service_runtime_smoke.py --fixed-reaper --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v3 --case reaper-cycle
python3 scripts/service_runtime_smoke.py --fixed-reaper --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v3 --case reaper-serial
python3 scripts/service_runtime_smoke.py --fixed-reaper --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v3 --case reaper-exhaustion
python3 scripts/service_runtime_smoke.py --fixed-reaper --delivery ../Aether-userland/build/sdk-deliveries/native-service-runtime-2026-10-06-v3 --engine-utc --utc-delivery ../Aether-userland/build/sdk-deliveries/native-utc-2026-10-06-v3
```
