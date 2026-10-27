# AF09 admission and drain diagnostic

[Issue75](https://github.com/gonz0w/Aether/issues/75) records the initial
implementation; [issue77](https://github.com/gonz0w/Aether/issues/77) records
the native-yield correction. [Issue64](https://github.com/gonz0w/Aether/issues/64)
owns native acceptance. This reference describes the implemented experimental compiled
diagnostic family and its host checks. Complete current qualification, target
fit/preparation and native witness gates remain separate; no guest is selected.
Initial design base: public main `33ace875cbd9dafc94aebd93f20c29dbd6546698`.

## Review decision

Owner review recorded2026-10-26 in issue75 approves one closed Zig option, `-Dnative-af09-drain=CASE`, default `none`.
`none`, whether explicit or omitted, preserves existing behavior. The eight
selected values and their prospective observations are:

| Case | Actual activity selected | Required distinction |
| --- | --- | --- |
| `file_prefix` | Child queues the first32 bytes of a FILE-write request. | No late request bytes consumed or filesystem write. |
| `exec_prefix` | Child queues the first32 bytes of an exec608 request. | No late request bytes consumed or executable replacement. |
| `fork_prefix` | Child queues the canonical first32 bytes of fork304. | No late request bytes consumed or second copy. This is not an admissible nested child fork. |
| `stream` | Child queues one complete32-byte stream request. | No late request consumed or stream effect. |
| `no_ack` | Hold the engine primary after its completed counter output, before ACK send. | Real empty read, park and deadline; no ACK bytes transferred. |
| `partial_ack` | Hold completed ACK16-byte writes at fixed release ticks. |48 actual ACK bytes do not complete ACK64 or renew the deadline. |
| `exit_deadline` | Let ACK and cleanup/export finish, then hold actual normal exit before terminal publication. | ACK/export do not establish native engine terminal or reclaim. |
| `pending_fragment` | Publish one actual ACK16 fragment while owner park is deferred until its real deadline. | Deadline precedence over an already pending fragment event; no full-ACK or event-arrives-on-deadline claim. |

[DEVELOPMENT](DEVELOPMENT.md#rc1-review-follow-up-rendering-and-negative-controls)
requires explicit human review of new non-boolean controls. The human approved this exact eight-case proposal after draft PR76; the control
review is complete. Implementation, host checks and matched offline preparation
may proceed. Separate implementation/evidence review remains required.
This decision grants no guest authority and changes no resource limit.

Case IDs1..8 follow table order; `none` emits no case. Use only the separate
Rust cfg `fs_af09_drain`, mutually exclusive with `fs_home_probe_three` and
requiring the current HOME feature closure.

The build must reject unknown values, release-artifact selection, SMP, the Zsh
application profile, missing native image/ABI31 guarded-owner composition and
conflicting storage-lifetime diagnostics. Omission controls belong in compiling
host source mutations, not additional public build switches. The exact selected
case must agree across kernel, C fixture, engine configuration and prepared
receipt; missing, mixed, substituted or stale associations fail closed.

## Workload and service ledger

Keep `fs_home_probe_three`, its seals and all existing default paths exact.
The new profile uses the real home adapter to open name `probe`, length5,
write-only, without create or cloexec. It does not read, stat, seek, change CWD,
write or explicitly close that FILE. The parent creates one ordinary owner pipe
and forks one child through the existing copy, rebind and publication path.

The parent exits through existing scalar trap `0x100e7` with status0, without
returning through C descriptor cleanup or waiting for the child. Unexpected trap
return is a fixture failure. The child completes genuine startup304/READY32 and
parent-disposition32, explicitly calls existing native READY after fork return,
then sends two real16-byte chunks on its authenticated owner request endpoint.
It subsequently yields through its existing native callback with operation
`0x1fffe` and four zero arguments, without reading a reply or performing
descriptor cleanup. A zero result continues waiting; a nonzero result preserves
fixture failure119. This path must not call libc `sched_yield`, whose Linux-style
operation is unsupported by the selected native kernel.

The first three success cases retain their continuation in initialized process
memory; only32 bytes are queued. Existing encoders and actual identity/descriptor
records supply fields. Fork's slot field starts after this prefix; current
`aefd_fork_arm` and codec require parent slot1, so the child fork continuation is
not authorized. Do not weaken this restriction to improve a diagnostic claim.
The stream case uses a complete request for the genuinely created pipe.
Deadline cases use the same admission/settlement workload with the FILE prefix.

Expected actual service counts are two bootstrap mutation-provider attempts
(mkdir/create) and three requests (lookup, final shared FILE close, disconnect).
Name continuation is a frame, not a fourth request. Counts do not include every
provider I/O operation. The probe remains empty in the later normal cold reader.
The final shared FILE alias closes once; unchanged CWD needs no extra Dir close.

Owner-to-engine bytes total256: lookup128, FILE close64 and disconnect64.
Engine-to-owner bytes total256 before ACK: greetings128, lookup64 and close64;
complete disconnect ACK64 brings this total to320. Success requires one copy,
zero execs, late consumed0/discarded32 and three normal reclaims: child, parent,
engine. Every count is an observation, not a value assigned by the fixture.

## Generation-checked admission checkpoint

Bind only the actual parent1, copied child2, engine0 and owner6 generations and
actual request/reply channel identities. Track the successful native copy and
actual startup304/READY32/parent-disposition32 ledger. No fixed token grants
additional authority and no user pointer is retained.

After ordinary native READY validation, result0 and first readiness publication,
hold the child's completed primary return. After normal owner/handle validation,
defer the next parent-status query body following copy publication. Synchronous
publication has no such query inside it, so this does not hold the parent before
its disposition can arrive. Support either checkpoint arrival order.

Once the query is pending, release the child to make its two checked writes.
Publish the ordinary query result only after actual parent normal terminal,
child native READY and exactly32 queued child bytes with zero consumption.
Revalidate generations and channels before completing the ordinary query body.
Do not cache a nonterminal result and replace it with a diagnostic success.

Persist only scalar identities, phases, counters, deadlines and pending flags.
Completed registers live in the domain-owned primary Execution frame, preserving
FS/FP and wait state. Do not retain an exception-stack frame, slice, capability
reference or transfer buffer. Do not use State.frozen, recursive exceptions,
rewound instruction pointers or generic syscall replay.

Each hold must rotate. Add primary-only exclusion in normal context selection
and its idle fallback; engine helper contexts remain eligible. Never use the
existing session-lifecycle whole-domain channel-wait exclusion as a hold. Cancel
or invalidate matching holds on terminal, reset or reclaim; never release a
replacement generation or overwrite a frame occupied by another wait.

## Fixed deadline and actual progress

T0 is the first successful owner observation `0x2a000` after the positive parent
status query. Require T0<=5400 and checked D=T0+500<=5900. The observed nonzero
RDX of every actual owner park in the drain phase after T0 must equal D.
Healthy startup parks retain their existing zero/no-deadline value. Diagnostic timing derives from real
delivered PIT ticks, including idle IRQ progress, not wall-clock estimates.
A missed setup window fails the case; it never moves or renews D.

For `no_ack`, hold only after checked output8 has actually copied its record and
returned8; no ACK write is attempted. For `partial_ack`, copy the first16 ACK
bytes and hold their completed return until R1=T0+100. Copy the second16 and
hold until R2=T0+200. Copy the third16 before D and hold through D. Each hold
must be reached strictly before its release tick. Withhold the final16.
For `exit_deadline`, hold the real normal-exit trap before finish publishes
terminal, after actual ACK and cleanup/export observations.

For `pending_fragment`, first hold the engine at the same completed checked
output8 return as `no_ack`, before any ACK send. Only after validated counter
output and a successful hold, publish one existing sustained event. If the owner
parked before counters, it completes its ordinary event wait, reobserves and gets
ACK-channel EAGAIN again before reparking into the deferred path. Counter-first
arrival uses the same deferred path. Keep the engine held until actual postcounter
owner ACK-channel EAGAIN and deferred park capture. Defer the
owner's validated park before Events.park and keep Events unoccupied. Save only
its actual expected sequence and D. Release the completed counter return, allow
the first real ACK16 copy/publication, and hold that completed engine return.
Require the resulting event sequence to exceed the saved sequence and exactly16
ACK bytes retained strictly before D, with zero ACK reads while held.
Do not fill the32-byte channel.

At real IRQ tick D (later registration invalidates setup), under the existing
IF=0 boundary before normal refresh,
revalidate identity and call ordinary Events.park(saved_sequence, actual_tick,
saved_D, actual_serial_ready), then normal refresh/take/result mapping. Do not
call a fictitious poll overload or write a synthetic -110. Existing deadline
precedence determines the result. Occupied, exhausted, stale, late or incomplete
setup invalidates the case. This witnesses an already pending fragment event;
it does not witness an event physically arriving on tick D.

All deadline cases require actual EAGAIN, actual park/-110, both source-close
attempts with their real results, and admitted/unreclaimed engine obligations.
No successful Halt or engine reclaim is permitted. UD2 or watchdog expiration
alone is never an oracle. Timeout media is not evidence of clean export,
recovery or durable success. A negative may observe earlier export only when
that event actually occurred, as in `exit_deadline`.

## Actual pre-ACK counters

After successful disconnect dispatch in actual names-service::run_bound and
before ACK send, emit exactly one private eight-byte record:

| Offset | Encoding | Meaning |
| --- | --- | --- |
|0 |u8=1 | Version |
|1 |u8=1 | Successful disconnect dispatch phase, not completed ACK/export |
|2..3 |little-endian u16 | Actual owner mutation attempts, checked conversion |
|4..5 |little-endian u16 | Actual incremented service request count, checked conversion |
|6..7 |zero | Reserved |

Under `fs_af09_drain` only, add safe method
`fn af09_counts(&mut self, mutations: u64, requests: u64) -> Result<(), i64>`
to Channel and Io; Framed forwards it directly. Host implementations must record
or reject it; no successful default no-op. Nonselected traits retain their shape.
Use this cfg-only safe Channel::af09_counts to Io::af09_counts forwarding method;
Endpoints alone crosses its existing documented unsafe native trap boundary.
Keep the service crate's `-Funsafe-code`. The record uses existing checked output
operation0x10001, stream1, live initialized buffer and extent8; remaining scalar
arguments are zero. Do not add owner storage, a callback framework, syscall,
grant or output buffer. Fail on conversion overflow or a return other than8. Preserve negative errors;
other nonnegative results fail. Do not retry or send ACK after reporting fails.

The selected successful HOME engine emits0 prior bytes into its256-byte output;
require actual offset0 and final count8. Prior output, missing/duplicate records,
wrong length/version/reserved fields or mismatched counts invalidate the witness.
Preserve existing failure markers and the default exact-three predicate; the
new selected normal-completion predicate is exact-two/three-request. Dispatch,
ACK send, Stop::Disconnected, report assignment and export stay separate facts.
The packet proves counts at dispatch. Final negative evidence must also rule out
later source requests/admissions; the packet alone cannot prove that. Preserve
the final256-byte request ledger and actual engine holds. Cold-reader acceptance
needs its separately authorized native execution.

## Typed trace and strict consumption

Only this compiled profile may emit complete ASCII rows:

```text
AF09-DRAIN v=1 case=C row=N phase=P slot=S gen=G seq=E tick=T deadline=D status=R count=K aux=A
```

Unsigned numbers use canonical decimal; status is signed canonical decimal.
No leading zeros except0, plus sign, ANSI, CR or embedded controls are allowed.
Fields occur once in this order, followed by one LF and no trailing fields.
Case is1..8, slot0..6, phase is in the closed table; other unsigned fields are
u64 and status is i64. row starts0 and increments without gaps. seq is the actual
sustained event sequence, not row ordinal, except phases10 and26 carry the
actual saved expected park sequence; phase11 carries the actual completion
sequence, which may also precede a later publication. Compare the saved expected
value with the actual ACK publication sequence in phase17 and the recorded
completion sequence in phase11; phase11 need not be current at emission. tick is actual total_ticks. Slot/gen
identify the affected live or retained domain. Do not log pointers or usable
capability tokens. Deadline0 means no observed park deadline. Inapplicable fields
are zero. Repeated progress phases carry actual cumulative totals.

| Phase | Actual boundary and field meanings |
| --- | --- |
|1 | Selected case begins. |
|2 | Successful copy: child slot/gen; count cumulative copies. |
|3 | Startup delivered: child slot/gen, count304. |
|4 | Child native READY completed and held: child slot/gen, status0. |
|5 | Authenticated parent query deferred: parent slot/gen. |
|6 | Late child request write: child slot/gen, cumulative count16 then32. |
|7 | Parent normal terminal: parent slot/gen, status0. |
|8 | Ordinary positive query: parent slot/gen, native RAX in status, terminal kind in aux. |
|9 | First drain observation: owner slot/gen, actual seq/tick, fixed deadline. |
|10 | Actual park request: owner slot/gen, expected seq and deadline. |
|11 | Actual park completion: owner slot/gen, status/seq/completion tick and same deadline. |
|12 | Late child request read: child slot/gen, cumulative consumed count. |
|13 | Queue disposal: child slot/gen, count discarded, aux cumulative late reads. |
|14 | Stop result: target slot/gen and actual status. |
|15 | Reclaim result: retained target slot/gen and actual status. |
|16 | Checked output8 at offset0: engine slot/gen, status8, count mutations, aux requests. |
|17 | Disconnect ACK write: engine slot/gen, cumulative count. |
|18 | Disconnect ACK read: owner slot/gen, cumulative count. |
|19 | Source-close result: owner slot/gen, actual status, aux0 request side or1 reply side. |
|20 | Engine normal-exit trap before finish: engine slot/gen, requested status. |
|21 | Engine normal terminal publication: engine slot/gen, actual status. |
|22 | Retained obligations: engine slot/gen, count admitted flag, aux retained backing flag. |
|23 | Successful clean Halt boundary: owner slot/gen. |
|24 | Transfer EAGAIN: caller slot/gen, status-11, aux direction ID. |
|25 | Completed-return hold/release: affected slot/gen, count hold ID, aux0 hold or1 release. |
|26 | Deferred park capture/registration: owner slot/gen, saved seq/deadline, aux0 capture or1 registration. |
|27 | Fork wire READY consumed: child slot/gen, count32. |
|28 | Parent disposition delivered: parent slot/gen, count32. |
|29 | Diagnostic failure: affected slot/gen if known, status setup-failure ID. |
|255 | Diagnostic overflow; verdict invalid. |

Direction IDs:1 child request write,2 child request read,3 engine request write,
4 engine request read,5 engine reply write,6 engine reply read. Hold IDs:1 child
READY,2 counter return,3 ACK return,4 engine exit. Setup-failure IDs: -1 identity,
-2 publication/queue, -3 conflicting wait, -4 timing, -5 output/counters,
-6 unexpected operation, -7 trace encoding. These diagnostic IDs are not native
syscall errors or substituted results. Rows follow actual checks/effects.

The owner closes its reply reader before its request writer. Phase19 therefore
records exactly reply-side aux1 followed by request-side aux0, both with their
actual successful status. The oracle preserves that order, the two distinct
endpoint identities and the existing counter/close/retained-obligation ordering;
it does not sort records or accept either order.

A fixed256-byte buffer accommodates the worst250-byte permitted row. Limit
AF09 output to32768 bytes, reserving256 bytes for one overflow row. Before an
ordinary row would exceed the nonreserved budget, emit phase255 once and
suppress further AF09 rows. Preserve emergency output and invalidate the witness.
The total capture remains64KiB; neither bound may silently truncate accepted
trace. State is fixed-size and compile-time absent for `none`; measure its actual
size before acceptance. Do not enable storageLifetime or repurpose the176-byte
all-workers-gone observation. Existing machine markers remain exact.

The eventual versioned parser must reject unknown phases, duplicate singleton phases, impossible ordering,
malformed numbers, missing identities, stale generations, incomplete capture,
overflow and wrong selected case. Match actual prepared image/input identities
before parsing; unknown evidence never means success. Parent/child traffic,
source cleanup, engine terminal/export and final Halt require their own typed
facts. Host-created examples test parser behavior only.

Writer validation retains the complete raw UART capture and its hash. Require
one complete kernel-entry line, `AETHER M1: entered x86_64 kernel`, at its actual
LF boundary. Firmware and bootloader bytes before that line may contain terminal
escapes and CR; they are an uninterpreted preamble, not diagnostic evidence.
Reject missing, repeated or embedded entry boundaries and protocol or failure
markers hidden in the preamble. Keep kernel output strict ASCII/LF, including
rejection of ESC, CR and NUL, and preserve every typed and ordinary witness
check. Do not strip ANSI sequences, normalize line endings or alter the raw
capture. Standalone trace decoding still preserves unparsed bytes verbatim.
Historical transcript replay establishes parser behavior only; it cannot change
the failed campaign's disposition or supply a skipped cold reader.

## Verification and ownership

The concrete contract has separate peer review and recorded human control
review. Obtain separate review of the implemented candidate before integration.
Kernel work owns the closed build guard, scalar checkpoints, actual trace hooks,
primary-only exclusion and actual-body Zig harnesses. Userland work owns matched
C requests, service-counter forwarding, selected predicates and their direct
host tests. Lead owns script/qualifier/parser association, documentation, evidence
and integration. Keep disjoint edits; no component authority changes.

Selected tests must execute actual query/READY/transfer/Events/scheduler bodies,
cover both checkpoint arrival orders, generation cancellation, idle tick
progress, helpers versus primary exclusion, saved frame/FS/FP state and unchanged
authority/reserved/pointer/direction/capacity/error precedence. Reject wrong
endpoint/generation/prefix, only16/31 queued bytes and incomplete publication.
Compiling semantic omissions must fail for early query/release, removed exclusion
or generation checks, late consumption, fabricated transfer, renewed deadlines,
engine-wide blocking, omitted source closes and false clean completion.
Host scaffolding cannot qualify IRQ/CR3 or native behavior.

After source review and explicit control review, freeze final inputs, refresh
only affected qualifications and measure complete owner/process/engine fit.
Do not weaken a1097-input historical shape or pad/drop a new closure to preserve
its old count. Use an explicitly reviewed current shape if real inputs change.
At the major handoff run the justified complete host gate and finite target
preparation, retain every failed attempt and compact identities/results, and
remove owned generated outputs. Keep only maintained dependencies and one
current pending artifact set. No full source, SDK or build archives.

Keep seven domains, twelve channels,35MiB,9 mutations/96 requests, owner49152-byte
code/8192-byte resident/8184-byte conservative stack and existing process/engine
admission. Writer60s/6000 ticks and reader30s/3000 ticks remain ceilings. Focused
host300s, children180s, independent4MiB diagnostic streams,16MiB compiler files,
complete host900s remain. The complete eight-case AF09 offline family uses the
[owner-adopted5400-second default](../PROJECT.md#af09-offline-family-budget-2026-10-26);
other target suites retain1800 seconds.
Existing exact media allowances are separate. Any measured fit failure or actual
authority/resource change needs its real disposition. This diagnostic grants no
guest, automatic retry, runtime sufficiency, Zsh/TTY, persistent ISO or release
acceptance.

## Simplicity rationale

The simpler existing helper waits for its child before parent exit and cannot
establish the admission cutpoint. Sleeps alone cannot establish which request
was queued before that observation. Reusing actual completed scalar returns and
ordinary Events avoids transfer replay, a new syscall or scheduling framework.
The cost is one closed diagnostic family and bounded observations across current
components. No production complexity is removed now; broader scheduler repair,
nested-fork authority, installed service policy and general tracing are deferred.

## Host parser and selected offline preparation

From the system root, run the standard-library checks separately:

```sh
python3 -B -m unittest discover -s tests -p test_af09_drain_trace.py -v
python3 -B -m unittest discover -s tests -p test_af09_drain_witness.py -v
python3 -B -m unittest discover -s tests -p test_af09_drain_inputs.py -v
```

`scripts/af09_drain_trace.py` decodes bounded canonical rows and retains other
UART bytes verbatim. `validate_witness(capture, case, admission)` checks complete
prospective writer observations, including ordinary admission, counter output,
terminal, cleanup, panic and Halt markers. The measured admission map has exactly
`engine_pages`, `shell_pages`, `helper_pages` and `owner_bytes`; helper geometry
belongs to the prepared envelope, while this workload copies the parent without
loading that helper. Native READY and wire READY have a causal partial order.
Saved park/completion sequences may precede the current event sequence.

Associate capture bytes with the exact selected prepared image and input hashes
before calling the oracle. A successful parser result explicitly records
`native_executed=false`; it neither establishes execution nor qualifies cold
recovery. The four successful cases require an independent read-only reader
with empty `probe`; the four deadline cases preserve failure obligations and
must not be recovered as cleanly exported media. Synthetic controls exercise
these checks without running a guest.

The existing offline tools accept one explicit `--native-af09-drain CASE` with
paired `--diagnostic-host-inputs PATH` and
`--diagnostic-host-inputs-sha256 SHA`. Omission keeps `none`; paired inputs are
forbidden for `none`. Selected engine, guarded-input and preparation receipts
use distinct drain schemas and bind one exact case throughout. They preserve
the existing limits, ABI31 and envelopes. The autonomous selected writer has an
empty UART script. Preparation includes pristine/writer/recovery for four clean
cases, and pristine/writer only for deadline cases. Reader kernels retain their
ordinary read-only profile; only the writer selects the diagnostic kernel flag.

The host manifest schema is `aether-af09-drain-host-inputs-v1`, with exactly
`schema`, ordered `cases`, current absolute-path `inputs` hashes and `records`.
Its fixed record roles are `c_fixture`, `c_fixture_impact`, `c_entry`, `counters`,
`builders`, `kernel`, `build_guards`, `regressions`, `complete_host` and `review`;
each identifies retained raw provenance by path/SHA-256. All bytes are rechecked.
The manifest binds reviewed provenance; opaque labels are not automatic test
qualification, execution proof or approval. Keep these private receipts private.

The fresh owner receipt uses explicitly selected component-wrapper v2, fixed
1106 inputs/911 commands, the `af09-drain-owner-2026-10-26` qualification profile
and its reviewed af75 harness identity. The original v1 reader keeps its exact
1097-input shape; no padding, dropped input or automatic count adaptation is
permitted. Old producer/helper receipts remain baseline recipe evidence, while
the selected C/counter/kernel/reader tests establish their own host coverage.

## Independent userland host prerequisites

From a provisioned `userland/` checkout, with pinned Clang/clang-format21.1.8,
the installed macOS SDK and the retained private formatting configuration
`docs/quality/clang-format.yaml`, run the C checker with an unused evidence directory whose parent already
exists and has no symlink ancestors:

```sh
python3 -B experiments/filesystem-service/fd_home_drain_checks.py --evidence /private/tmp/af09-drain-check-UNIQUE
```

The checker compiles only host doubles and actual C adapters/codecs. A public-only clone lacks that private configuration and reports a prerequisite
block; do not reconstruct it or treat the block as a pass. It never
constructs a native image or invokes the proposed kernel selector. It retains
compact JSON receipts, removes its temporary objects/executables, pre-freezes
SDK headers, verifies actual dependency files and records the selected direct
compiler/linker identities. This is not a complete transitive toolchain or
host-loader provenance claim. Its stricter4MiB file cap covers host artifacts
as well as each stream; native builders retain their separate16MiB allowance.

Help/version use ASCII stdout. Result/receipt-path summaries use escaped plain
text on stdout; the receipt file contains JSON. Progress/errors use escaped
stderr. Exits are0 pass,1 operational/check failure,2 blocked prerequisite
and64 usage. Output conflicts fail before compilation. This internal checker
adds no installed command, native output or renderer-conformance claim.

The C fixture retains initialized full request references and submits only the
selected32 bytes. Parent native-exit return and any returned native-entry failure
trap before C descriptor cleanup. Host evidence covers34 scenarios, seven named
compiling omissions and the same scenarios under UBSan; ASan remains unavailable
under the recorded host incompatibility. The actual three-argument shell wrapper and native-main guard have separate
host entry controls. Peak target fit and native execution remain separate.

The selected Rust source implements safe pre-ACK counter forwarding through
HomeActivated, Framed and Endpoints, plus exact2/3 normal-completion predicates.
A private bounded host recipe exercises the actual service loop/adapter and
activation wrapper, required cfg/trait denials, strict Clippy/format and default/
old-three launch regressions:66 methods across41 commands. It preserves the
service crate's unsafe-code prohibition. Its exact commands, tools, source and
input receipts remain local; there is no separate public counter-only runner.
Do not treat the existing full HOME checker as a host-only command.

These checks establish host source behavior. The kernel checkpoint and prospective
oracle implementations have separate source review and actual-body controls.
Current complete qualifications, matched target artifacts, full fit and the major
handoff host gate remain issue75 acceptance gates. Existing receipts cannot qualify
changed inputs, and no historical seal is rewritten. Human review of the new
kernel control is recorded in issue75; guest execution remains separate. The synthetic parser checks above prove only prospective oracle behavior.

The maintained C controller also has direct mock checks, from `userland/`:

```sh
python3 -B experiments/filesystem-service/fd_home_drain_checks_tests.py
```

Its eleven methods exercise unknown/unresolved child cleanup and helper
exceptions without starting real children. They require retained work/evidence
until cleanup is known, and use controlled clocks to deny initial/final hashing,
cleanup or receipt-write expiry. These are host controller checks, not native
process or deadline evidence.
