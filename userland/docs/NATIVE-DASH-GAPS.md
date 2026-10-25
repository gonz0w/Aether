# Native dash integration refresh (UL-045)

Latest checkpoint,2026-09-29: [serial acceptance](../experiments/dash-native/SERIAL-ACCEPTANCE.md)
closes SERIAL-SESSION-01–06 for private008/ABI23.169 native cases and132 Python plus
configured host checks pass. Next shared SDK and independent reviews; SI-07 and
full M3/R1 remain open. Earlier handoffs/checkpoints below are historical.


Serial continuation,2026-09-29: [SERIAL-SESSION handoff](../experiments/dash-native/SESSION-SERIAL.md)
is pinned with eight passing host semantic controls. Real interactive native
execution remains NOT RUN, pending Aether owner delivery and consumer replay.


Latest checkpoint,2026-09-29: [scratch acceptance](../experiments/dash-native/SCRATCH-ACCEPTANCE.md)
closes SCRATCH-SESSION-01–06 for private scripted execution.154 native cases and127
Python plus configured host checks pass. Real serial composition, SI-07, shared
SDK/reviews and full M3/R1 remain open. Earlier checkpoints below are historical.


Latest checkpoint,2026-09-29: [failed-exec acceptance](../experiments/dash-native/FAILED-EXEC-ACCEPTANCE.md)
closes EXEC-SESSION-01–06 for private scripted execution.142 native cases and123
Python/configured host checks pass. Next scratch/serial composition; SI-07,
shared SDK/reviews and full M3/R1 remain open. Older checkpoints are historical.


Latest checkpoint,2026-09-29: [recovery acceptance](../experiments/dash-native/RECOVERY-ACCEPTANCE.md)
now closes RECOVERY-01–06 for private scripted execution.133 native cases and119
Python/configured host checks pass. Failed-exec, scratch and serial composition,
shared SDK/reviews and SI-07 remain open. Older checkpoints below are historical.


Current checkpoint,2026-09-25: [composed SESSION acceptance](../experiments/dash-native/SESSION-ACCEPTANCE.md)
now has910 passing native cases and exact separate-stream/cleanup evidence. The
2026-09-05 review below is historical. Remaining integration: early-reader/failed-
exec/scratch/serial composition, shared SDK and independent reviews, followed by
the separately owned TTY/persistence/package/sys-init gates. Full M3 remains open.


2026-09-05. The next useful native integration is an independent requester for
Aether's new connection-bound launch broker. The prepared C requester compiles;
its runtime acceptance is UL-046. Dash itself is still a Linux-reference artifact.
Buffered FILE support does not close its process or shell-startup requirements.

## Current companion inputs

| Input inspected | What it provides | Limit relevant to userland |
| --- | --- | --- |
| Aether NATIVE-LOOKUP | Immutable executable names resolve within an explicit owner mapping before launch | A trusted mapping is not kernel authority; no file-backed executable loading or PATH |
| Aether NATIVE-PROCESS and Rust broker/owner helper/runner | One connection-bound requester can request a named worker and collect its ticket; namespace is restricted to worker | Source contract and runner cases are present. No retained native-process bundle was found in docs/evidence during this review; no producer runtime or userland acceptance is inferred |
| Aether NATIVE-INIT and sys-init NATIVE-INIT/NATIVE-COVERAGE | Separate ABI-6 consumer reports seven cases for bounded waits/deadlines, readiness and whole-domain fail-closed shutdown | Frozen producer/consumer scope; no general waitpid, SIGCHLD, process inheritance or restart |
| pkg-mgr STATE and supervised handoff | Existing private-root artifact transport and native-memory package witness | Not runtime filesystem lookup, ELF replacement, authenticated base distribution or service activation for this broker |
| Canonical PROCESS-FD review | PD-01–12 remains an unreleased four-owner proposal | Status pending, zero reviews in the inspected record; no owner acceptance supplied by this refresh |

The broker occupies the supervisor domain, retaining factory/image grants and
authenticating the requester through its delegated endpoint ownership. It launches
one worker at a time in the other native slot. It rejects all nonzero inheritance
masks before admission; collection consumes a connection-local ticket. It has no
argv/env request fields: the broker supplies the fixed worker startup record.
Requester death closes admission and triggers owned cleanup. Supervisor death
retains ABI 5's fatal limitation; ABI 6 is a separate profile, not silently combined.
The file-service fixture also uses AENFS001, but it has different bootstrap roles
and a different protocol. Sharing an envelope magic does not compose the services.

## Dash gaps after UL-044

This compares actual pinned dash source with the bounded adapters. It does not
claim an exhaustive syscall inventory or exact first runtime failure.

| Requirement | Current evidence | Still missing for the shell |
| --- | --- | --- |
| Startup and identity | Native C/TLS/allocator; dash main.c calls getpid and generated init before procargs | Native process identity and verified initialization; developer UID/GID values are not authority |
| Minimal `dash -c ':'` | Pinned source reaches opts changed/signal setup before evaluation | Even a builtin-only command is not a readiness shortcut: trap.c returns after failed sigaction query and ignores the setter result. ENOSYS alone can be hidden by upstream control flow |
| Descriptor table and flags | Four-entry file facade, separate older eight-entry stream facade; shared offsets and cleanup tested | Dash redir.c requests F_DUPFD_CLOEXEC at descriptor 10. Neither table can serve this; no selectable flags or inherited standard descriptors |
| Regular-file I/O | Read-only single-component open; fixture-created 64-byte scratch; bounded lseek and FILE callbacks | Public create/truncate/append/modes, metadata, cwd/directories, shared namespace and larger workload bounds |
| Output and input | Separate byte-stream and file-service profiles | No integrated stdin/stdout/stderr routing, console input, controlling TTY or terminal modes |
| External commands | New broker source can launch fixed worker with empty inheritance | Shell fork/vfork state semantics, executable replacement, argv/env, inherited descriptors and compatible parent/child identity |
| Child completion | Broker collection and ABI-6 supervisor waits are distinct bounded seams | Dash uses wait3, WNOHANG and signal-aware job bookkeeping; neither seam establishes these |
| Pipelines, substitution, here-docs | Native channels plus Linux dash reference cases | Inherited/duplicated pipe ends, blocking/wakeup, EOF/EPIPE/SIGPIPE and copied shell state |
| Package admission | Pinned dash source and exact reference ELF, private package transport | Authenticated source/artifact closure, licenses and release policy; UL-016 remains open |

Dash input/redirection calls use scalar libc interfaces and fcntl; internal
buffered FILE improvements are useful C-library progress, not a replacement for
those shell requirements. The Linux-reference ELF still uses Linux transport and
must not be inserted into a native envelope and called an Aether port.

## Next executable workload and owner handoff

UL-046 consumes a captured broker, namespace and worker source set, builds the
[prepared requester](../experiments/native-process/README.md), and boots a matched
AENFS001 envelope. Start with two named launches and exactly-once collection;
exercise refusal of nonzero inheritance, denied direct native launch, restricted
namespace, malformed fields, stale/forged tickets and cleanup. Then consume the
owner's allow_inherit/wide_scope/repeat_collect controls and requester partial/exit
variants with exact independent rejection contexts. Retain positive worker
17/33, requester 29 and three reclaims. Freeze any source drift before execution.

This bounded consumption can proceed locally without inventing a new kernel ABI
or claiming the pending PD proposal is accepted. It is the next integration seam,
not an implementation of dash's POSIX process calls.

After that witness, the owner discussion needs concrete decisions on:

- Combining process requests and file/standard-descriptor ownership within current
  slot/channel limits; reverse transfer and inherited authority are absent today.
- Fork/vfork strategy versus a spawn-only intermediate tier, executable replacement,
  copied shell state, argv/env bounds and parent/child status ownership.
- Sufficient descriptor bounds (including index 10), atomic flags and checked libc
  fallbacks, signal/mask behavior and interrupted-close/collect semantics.
- Whether and how broker lifecycle consumes ABI-6 waits/shutdown while sys-init
  retains policy. A global fail-closed shutdown is not recovery or parent death.

These are local consumer questions routed to the canonical
[PD proposal](../../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md),
not new shared requirements or authorization to edit sibling implementations.
No messages were sent, review approvals fabricated or release pins changed.

[Review/build evidence](evidence/native-dash-gaps-2026-09-05/summary.json)
retains inspected source bytes/hashes, the current pending review record, selected
dash-source/archive consistency checks and the prepared requester build. No native
runtime suite was run for UL-045; previous target results retain their own scope.

## Later integration review (UL-052)

The earlier broker snapshot above is historical. UL-051 now has independent
one-entry inherited admission, rollback and one-shot result collection evidence.
The [libc integration plan](INHERITED-LIBC-PLAN.md) identifies the remaining bridge:
the tested inherited protocol owns positions in the broker, while the older local
file facade owns offsets itself. Fixed index 10 and normal-exit collection do not
establish general descriptor flags, F_DUPFD_CLOEXEC or waitpid. UL-053 can test
bounded musl read/close without promoting native dash or M3.

## Native SDK preflight and next integration (UL-007)

2026-09-07: [local link evidence](evidence/dash-native-link-2026-09-07/README.md)
now separates link availability from runtime semantics. All pinned reference
objects link against the captured native SDK/CRT and existing adapter: static
x86-64 ELF, 241272 bytes, 54 LOAD pages, no unresolved symbols. No native execution
was attempted. Linux-configured objects remain reference inputs; neither the
configuration nor the page budget is runtime-qualified.

The linked getpid/getuid/vfork/execve wrappers use native interrupt transport,
with operation values 0x10027/0x10066/0x1003a/0x1003b. The captured kernel dispatcher
returns ENOSYS for those operations. Thus symbol availability does not establish
POSIX semantics. The older broker/table descriptions above are historical, not
an inventory of every current native service. Four-role command and actual-cat
progress supplies useful bounded I/O evidence, but does not implement these calls.

The next owner-reviewed producer/consumer work is:

1. **Startup admission.** Pin a producer SDK/runtime pair implementing truthful
   process identity and the signal query/set/mask behavior used by this dash
   configuration, plus inherited standard descriptor bindings. Exercise identities
   and signal state round trips explicitly before accepting builtin execution;
   denied/malformed startup must not publish partial authority. Identity values
   are bookkeeping and never substitute for native grants.
2. **One external command.** Decide and implement the fork/vfork/exec strategy for
   actual dash control flow, argv/environment and child state, with wait/status
   collection and exactly-once cleanup. Run a deterministic helper and failed exec;
   require exact status/output, denial and child reclamation. A spawn-only runner
   remains a different tier unless dash source is deliberately adapted and tested.
3. **Redirection and pipes.** Provide descriptor allocation including >=10,
   F_DUPFD_CLOEXEC, duplication/restore and inherited endpoints. Then run file
   redirection, pipeline EOF/early-reader failure, substitution and wait workloads
   against explicit native resource bounds. Retain actual shell and helper receipts.

Aether owns kernel/runtime semantics; libc adaptation belongs to the selected SDK
owner; userland owns dash configuration, adapters and independent workload/oracles.
Route shared process/FD decisions through the canonical pending PD proposal and
owner review. This local sequence is not a new accepted ABI, an owner approval or
permission to edit sibling implementation. Current acceptance remains NOT RUN for
native dash. UL-016 source/license trust and UL-008 TTY work remain separate gates.

### Prepared startup consumer

[UL-007 startup probe](evidence/dash-startup-probe-2026-09-07/README.md) now builds
against the captured native SDK. Its six host cases reject invalid PID, failed
signal query, false-success disposition/mask setters and missing CLOEXEC, while
checking state restoration and duplicate closure. Native execution is NOT RUN.
This is a narrow prerequisite witness, not full dash startup acceptance. On a new
producer delivery, capture/pin the matching source/SDK/envelope; run the unchanged
probe with independent terminal and cleanup checks, then denied/malformed startup
and actual dash initialization. Preserve its stage exits and existing native
markers. The current dispatcher still lacks the necessary POSIX operations.


### Independent native startup qualified — 2026-09-07

[Local reproduction](evidence/dash-startup-native-2026-09-07/README.md) now passes
all222 command cases including nine startup cases. Our unchanged probe passes
natively in two generations; exact stage mutants and malformed-admission controls
pass their independent oracles. Alias I/O, flags/exhaustion, state reset and four
reclaims are exercised by the matched wrapper/owner. Earlier NOT RUN and waiting
notes are historical for this bounded prerequisite only.

No full dash acceptance follows: custom signal handlers/delivery, internal musl
masking and fork/exec/wait remain unsupported here. Aether is progressing full
dash separately. Next capture its matching delivery and test actual initialization,
external command/failure/wait, then redirection/pipeline/EOF and cleanup. Preserve
this startup evidence and independent review gate; no success stub is authorized.

### Shared mask and descriptor replacement qualified — 2026-09-07

[Local mask/dup2 reproduction](evidence/shell-mask-consumer-2026-09-07/README.md)
passes227 command cases including14 startup-family cases. Public sigprocmask and
actual musl block/restore helpers now share caller Execution state; the duplicate
C mask is removed. Bounded dup2 replacement and exact self/flag/close controls
also pass. Earlier missing internal-mask/dup2 notes are historical for this scope.
Custom-handler delivery, full dash initialization and fork/exec/wait remain open.
The producer's newer synchronous self-upcall is not a complete handler delivery;
retain separate evidence and consume a completed matched handoff before shell tests.


### Actual dash signal/init consumer checkpoint — 2026-09-08

[Local reproduction](evidence/dash-init-consumer-2026-09-08/README.md) passes all291
native command cases from the completed generated-init packet. Actual dash signal
routines and init execute using32 unchanged reference objects. Exact local serial
checks cover normal two-generation/four-reclaim behavior and skipped-signal/init
client102/103 with owner1501. Source/SDK identity and outer cleanup pass. Earlier
blanket missing-custom-handler notes are historical for this bounded private
signal route; general public signal production and process notification remain open.

The generated-init witness requires PPID -38, raw unsupported geteuid, empty PWD
and the exact getcwd warning. It qualifies observation of the missing contracts,
not truthful identity or a successful shell. Next owner delivery must implement
truthful parent identity, then explicit launcher/session user metadata and scoped
directory/CWD semantics. IDs cannot confer authority. Actual main, exec/wait,
redirection, pipes and prepared script workloads remain unqualified. No full native
configuration, host kernel/M4 rerun or independent review is inferred.


### Direct-parent consumer checkpoint — 2026-09-08

[Local qualification](evidence/dash-parent-consumer-2026-09-08/README.md) passes
all295 native command cases, including four parent cases. Actual getppid and
generated PPID=4 agree with the root supervisor's PID4/parent0; both worker
placements pass two generations/four reclaims. Disabled routing and self-PID
substitution reject client104/owner1501. Earlier missing-parent notes are historical
for this fixed direct-launcher profile; native authority and parent lifecycle are
not inferred from a numeric identity.

Next: explicit validated launcher user/group metadata, then scoped directory/CWD
support. Existing generated init still diagnoses unsupported geteuid and getcwd;
full main and process/pipe workloads remain open. No sibling/default/pin change,
new public signal producer or broader review acceptance follows from this run.


### Metadata intake and full-main configuration — 2026-09-08

The [consumer metadata checklist](../experiments/dash-native/METADATA.md) reviews
the completed AECAT002 proposal; metadata runtime acceptance remains NOT RUN.
Its twelve case families preserve version isolation, staged metadata/descriptors,
real/effective identity separation and zero-UID authority denial. Actual initvar
must be tested with a controlled environment; inherited PS1 can override its default.

[Static evidence](evidence/dash-metadata-review-2026-09-08/README.md) confirms the
Linux-reference main.o omits the upstream !linux UID/GID equality guard before
interactive ENV. Current native fixtures wrap main, so no full-main result covers
this behavior. Before actual-main/interactive acceptance, select native configuration
and startup environment policy, including any secure-execution/filtering reliance,
and exercise equal/unequal UID/GID tuples. Metadata values still confer no native
authority. This finding is a configuration gate, not a shipped exploit claim or a
reason to block the separate initializer witness. UL-081 tracks it under UL-007.


### Bounded metadata consumer checkpoint — 2026-09-08

[AECAT002 local evidence](evidence/dash-metadata-consumer-2026-09-08/README.md)
passes309 command cases, including14 metadata cases. Informational real/effective
UID/GID and actual PS1 selection now execute with positive/invalid-input cleanup
and zero-UID denial checks. Earlier metadata NOT RUN notes are historical for this
bounded delivery. Five [checklist rows](../experiments/dash-native/METADATA.md)
remain partial; preserve their narrower observed scope. Raw credential support,
full metadata-contract acceptance and authenticated identity are not implied.

Scoped directory/getcwd remains an owner dependency. Full-main configuration,
actual main/exec/wait/pipes and M3 remain unqualified. The early incomplete serial
inspection and subsequent passing completed-receipt checks are both retained.


### Initial scoped directory consumer checkpoint — 2026-09-09

[Local AECAT003 evidence](evidence/dash-cwd-consumer-2026-09-09/README.md) passes
319 native command cases. Actual init obtains PWD=/work for absent, matching,
relative and out-of-scope inherited PWD without the old getcwd warning. Five bad
grants remain unpublished and clean up; skipped publication rejects106/1501.
Earlier wholly unsupported-CWD notes are historical for this single private fixture.
Only st_dev/st_ino/st_mode are supplied; general paths/stat/chdir remain unsupported.

The initial matrix still needs reply-failure/poison teardown, version/truncated
bootstrap, alias/mismatched identity/PWD controls and forced getcwd ENOMEM. Retain
the five metadata partial rows and native-main ENV configuration gate. Actual main,
exec/wait/pipes and M3 remain open; no source/default/pin or review acceptance is
inferred beyond the captured bounded reproduction.


### Directory bootstrap rejection checkpoint — 2026-09-09

[Local evidence](evidence/dash-cwd-bootstrap-consumer-2026-09-09/README.md) passes
323 native cases. Stdin alias, EOF halfway through the final directory record and
header-only V2/V3 mismatches reject and reclaim four tasks over two generations.
These narrow witnesses supersede the preceding wholly untested alias/version notes.
Stdout/stderr aliases, V1/V3 and queued-body mismatches, other truncation boundaries,
reply corruption/truncation and poison/no-further-traffic/teardown, identity/PWD
mismatch and forced getcwd ENOMEM remain unqualified. Preserve the five metadata
partial rows, native-main ENV configuration and actual main/exec/wait/pipes gates.


### Actual dash command/script consumer checkpoint — 2026-09-09

[Local369-case evidence](evidence/dash-file-consumer-2026-09-09/README.md) executes
real dash main/parser/builtins/exit and real script open/read/parser input through
an explicit V4 root. Nine exact main/file and18 metadata serial checks pass.
All12 metadata checklist rows now have bounded evidence, superseding the earlier
five-missing-observation status. A separate guard-enabled main object is selected;
the original Linux-reference object remains unchanged.

The no-ENV command/script scope does not qualify ENV policy or external children.
V4 admission, independent opens/exhaustion/stale/alias offsets, malformed/lost reply
and service-stop cleanup, actual-main ENV/-p, and existing argv/signal/syntax/
exec/wait/redirection/pipelines remain open. Old no-open/no-main statements are
historical for the basename-only fixture. General paths/stat/persistence and M3
remain unqualified; producer host/M4 evidence is distinct from local reproduction.


### V4 admission consumer checkpoint — 2026-09-09

[Local384-case evidence](evidence/dash-file-admission-consumer-2026-09-09/README.md)
adds14 normal root-admission rejections and an early-publication failure control.
Normal malformed grants finish110/17/17 over two generations/six reclaims; the
mutant fails113/1501 with zero reclaims. The prior nine main/file cases still pass.
Earlier wholly-unqualified V4 admission notes are historical for selected fields,
aliases, EOF192/208/223 and header-only V3/V4 mismatch only. Queued V4 bodies,
independent opens/exhaustion/shared offsets/stale references, malformed/lost replies,
service-stop recovery, ENV/-p and external-command/wait/pipe workloads remain open.


### File-description consumer checkpoint — 2026-09-09

[Local387-case evidence](evidence/dash-file-descriptions-consumer-2026-09-09/README.md)
adds independent-open/shared-alias offsets, CLOEXEC, local FD and backend sequence
exhaustion, stale/wrong-binding denial, access-rights rejection and EOF/close checks.
Positive two-generation/six-reclaim and exact offset/reference mutant rejection
are independently checked alongside prior24 admission/main controls. This is a
separate bounded descriptor client; the actual dash script remains a regression.
Earlier wholly-unqualified description/offset notes are historical for this scope.
Queued V4 bodies, malformed/lost replies/service-stop recovery, ENV/-p and actual
external-command/wait/pipe workloads remain unqualified.


### Known-result client-reply recovery checkpoint — 2026-09-09

[Local397-case evidence](evidence/dash-file-recovery-consumer-2026-09-09/README.md)
adds queued V3/V4 mismatch and corrupted/cut client open/read/close reply controls.
Known backend records retire only after client termination; six-reclaim outcomes
and omitted-retirement/wrong-witness rejection are independently checked. Earlier
wholly-unqualified queued/client-reply notes are historical for this bounded scope.
Missing/malformed backend responses and confirmed service-stop recovery remain
unqualified; the owner knows the result in current tests. Preserve8192-byte owner
bound (new maximum8056). ENV/-p and actual external-command/wait/pipe workloads
still gate full M3. General restart/replay/persistence behavior is not inferred.


### Malformed-backend consumer intake prepared — 2026-09-09

[Static review](evidence/dash-backend-intake-2026-09-09/README.md) defines four exact
consumer expectations for the producer's still-in-qualification malformed-backend
packet. Service stop must be queried and verified before description clearing;
forced stop has no normal file-exit log. Captured source review is not local native
qualification. Preserve397 as the latest local case count until a completed sealed
packet passes reproduction. Missing/partial/timeout backend replies, ENV/-p and
actual external-command/wait/pipe workloads remain unqualified.


### Malformed-backend consumer checkpoint — 2026-09-10

[Local401-case evidence](evidence/dash-backend-consumer-2026-09-10/README.md) verifies
three complete malformed-backend replies with confirmed scoped stop before local
record clearing and six-reclaim reuse. Omitted stop fails1601; exact serial records
omit a normal slot2 exit line and are paired with owner stop-record checks. Earlier
pending/unqualified-malformed-backend notes are historical for this bounded scope.
EOF/timeout/ENV/syntax/helper packets now exist as verified producer-only evidence;
next local intake is the consolidated431-case command suite. The real helper witness
is not dash fork/exec/wait. Separate public-fork callback evidence does not complete
installed SDK/wait/exec or full M3; source/independent review gates remain open.


UL-007 consolidated dash checkpoint (2026-09-10): independently reproduced all
431 command cases and six shared-transfer connection regressions. All 71 selected
final serial checks pass. Backend EOF/partial/silent/late recovery, actual ENV
loading/suppression, unsupported -p, syntax-error and unchanged helper via explicit
launcher now have bounded local evidence. Source/SDK integrity and cleanup pass;
new owner maximum 8152/8192 bytes. Evidence: docs/evidence/dash-helper-consumer-2026-09-10/README.md.
Earlier pending 431-case intake notes are historical. Next review/reproduce the
verified public-wait producer candidate separately; its 147 connections/five launch
cases are not local acceptance. Dash wait4/wait3, non-normal wait/reply controls,
exec/vfork, external commands, redirection and pipelines remain gates. No full M3,
installed SDK, source-trust or independent technical/reader acceptance follows.


UL-007 serial-shell consumer checkpoint (2026-09-11): 303 native cases pass
(241 connections, five launch, two console, 32 composed-init, 23 init-large).
Six independent serial protocols pass. Actual configured dash forks/executes /next,
waits for child72, returns to a prompt, prints status72 and exits0 then7 with six
reclaims across two sessions. Original-tee/wrong-input/cleanup/wrong-exit controls
reject as specified. Evidence: docs/evidence/dash-serial-consumer-2026-09-11/README.md.
All 578 source/4311 SDK hashes remain unchanged; serial owners max9528/16384.
Retain the incorrect aggregate-count assertion, rejected relative host invocation
and missing-doc host failure. A separate host tree adds a pinned inventory document
and passes Zig/host/workflow checks including99 Python tests. Native inputs unchanged.
Earlier public wait/exec intake notes are historical for this bounded single-child
path. Repeated external children per shell, full workload scripts, pipes/redirection,
TTY, persistence/sys-init/package assembly and independent review remain open.
Next completed repeated-child lifetime delivery and matched consumer qualification;
no full M3, installed SDK, release or fresh SMP/M4 acceptance.


UL-007 repeated-command/redirection checkpoint (2026-09-11): all 254 native cases
(247 connections, five launch, two console), 12 independent serial protocols and
host checks including 99 Python tests pass in one local attempt. One dash parent
runs three external children with terminal/wait-ack disposal before slot reuse;
builtin >&2 and restored stdout, exact 72/60/19 byte accounting and six reclaims
pass. Stale token/bootstrap and raw closed fork/exec encoding controls reject as
specified. Source579/SDK4311 integrity and host cleanup pass; owner max9944/16384.
Evidence: docs/evidence/dash-redirect-consumer-2026-09-11/README.md. Kernel/build and
SDK/dash object pins unchanged; previous init-bound evidence reused, not recounted.
Earlier one-child-total limits are historical for this bounded three-command path.
Next native pipe adapter/dispatcher and terminal-driven endpoint retirement, then
unchanged DASH-substitution; pipe host core is not native support. Consumer intake
requirements are prepared in that evidence/pipe-next.md. Full scripts, concurrent
pipelines, file redirection, TTY, persistence/assembly and independent review remain.
No full M3, installed SDK or release acceptance follows.


## 2026-09-13 — UL-007 unchanged argv/signal native consumer checkpoint

DASH-argv and DASH-signal-table now pass locally through the private native
producer adapter. Seven focused cases and seven independent serial checks pass;
consumer scripts/helper/manifest match byte for byte. Positives require two
child0/parent0/backend17 lifetimes and six reclaims. Argument/environment, skipped
helper, dropped post and bypassed PID scope reject exactly as selected.
Evidence: docs/evidence/dash-argv-signal-consumer-2026-09-13/README.md.
Native run passed first attempt; a retained filename error affected retention
only and was corrected without rerun. Full local 287-case regression is NOT RUN.
Next: remaining changed pipe/exec controls and consolidated producer handoff.
Original substitution/pipeline/file/TTY/assembly gates and independent review stay
open; UL-007/M3 and public SDK/release acceptance are not complete.


## 2026-09-14 — UL-007 background wait consumer checkpoint

Unchanged DASH-wait passes locally: helper7/parent0/backend17 twice, exact owner
readback and six reclaims. All 13 focused native cases and 13 separate transcript
comparisons pass, including before/after parking, stop, ignore/block, duplicate
notification and stale-parent replacement controls. Consumer script/helper/manifest
match local bytes. Source/SDK integrity and owned cleanup pass on the first run.
Evidence: docs/evidence/dash-wait-consumer-2026-09-14/README.md.
This is bounded private-adapter acceptance; no full314, matched command-runner or
scheduler replay was performed here. Next matched phase-one replay and descriptor
closure qualification, then remaining workloads and changed-path regression.
General signals, eventual unblock, writable files/TTY/persistence/assembly and
independent reviews remain open. UL-007/M3 is not complete.


## 2026-09-14 — UL-007 descriptor closure consumer checkpoint

Unchanged DASH-fd-closure passes locally: descriptors3–63 closed after real exec,
owner readback, child0/parent0/backend17 twice and six reclaims. All three native
cases and transcript comparisons pass; injected FD3 and corrupt wait status reject
exactly. Consumer byte identity, source/SDK integrity and owned cleanup pass on the
first attempt. Evidence: docs/evidence/dash-closure-consumer-2026-09-14/README.md.
Corrected phase-one dependencies and256 source/346 support members verify read-only;
this is intake, not execution. Next matched431 command-runner/287 connections replay
with the corrected source set. Full290 closure regression, writable fd-leak-control,
other unchanged workloads, public SDK/reviews and M3/assembly remain open.


## 2026-09-14 — UL-007 matched phase-one consumer qualification

Corrected matched phase-one replay passes locally:431 command-runner plus287
connections,718 native cases on identical242 harness source hashes. All208 startup
cases indexed; ten exact syntax/argv/signal trace checks pass. Host checks including
100 Python tests pass. All602 restored source/support files and4311 SDK files stay
unchanged; all started commands have complete cleanup. Both native suites passed
first attempt. A retained collector PASS-marker mismatch was corrected separately
without native rerun. Evidence: docs/evidence/dash-phase-one-consumer-2026-09-14/README.md.
This closes the fresh matched private phase-one runtime replay gap. It does not
close independent reviews or UL-081 public SDK boundary acceptance. Next integrate
newer wait/closure sets with matching broader regression and remaining unchanged
workloads. General signal/TTY, writable files, persistence/assembly and full
UL-007/M3 remain open. No new release or installed SDK claim.


## 2026-09-14 — UL-007 matched recovery consumer qualification

Matched316 connections and431 command-runner cases pass locally, sequentially,
on identical250 harness source hashes. All208 startup and25 selected transcript
checks pass; host includes101 Python tests. All611 source/support and4311 SDK
files remain unchanged. Timings1072.68/1463.65seconds are within1800 review ceiling;
owned cleanup complete. Evidence: docs/evidence/dash-recovery-consumer-2026-09-14/README.md.
This closes newer recovery full-set replay; previous timeout remains historical.
Full artifacts are compacted with verified readback and relocation mappings to
preserve the user's cleanup preference. No sibling/SDK installation change.
Five unchanged scripts remain qualified; failed-exec is an owner contract awaiting
implementation (two fresh VMs, two sequential children/four reclaims each proposed
by Aether; actual native admissions still require measurement). Next consume that
native delivery and controls. General signals/TTY, writable filesystem, persistence,
SDK/reviews and full UL-007/M3/assembly remain open.


## 2026-09-15 UTC — UL-007 failed-exec consumer qualification

Unchanged failed-exec now passes locally. Two fresh VM positives each give real
child127/gen1, child126/gen2, parent0/backend17 and four reclaims; all five controls
reject exactly. Sequential6 focused+322 connections+431 command-runner pass (759
executions), with252 matching full-suite source hashes,208 startup and37 trace
checks. Host includes101 Python tests;613 source/support and4311 SDK files unchanged.
Full timings1019.35/1423.47seconds meet1800 review ceiling. No local retry.
Evidence: docs/evidence/dash-failed-exec-consumer-2026-09-15/README.md. New outputs
are archived/readback-verified before unpacked copies and caches are removed.
Current matrix now6/12 unchanged scripts qualified; failed-exec is no longer a
waiting item. Next scratch-backed fd-leak-control/redirection with actual dash
admissions; C/host prerequisites do not qualify scripts. General signals/TTY,
persistence, SDK/reviews and full M3/assembly stay open. No sibling changes.


## 2026-09-23 — UL-007 scratch and substitution consumer qualification

Scratch:11 focused plus355 full connections pass on266 matching harness source
hashes;22 exact lifecycle/PASS checks and104 host tests pass. Full run1163.96s
meets1800s review ceiling. Source/support631 and SDK4311 pins unchanged. Evidence:
docs/evidence/dash-scratch-consumer-2026-09-23/README.md.
Substitution:3 focused cases and3 exact transcript checks pass on later268-source
fixture;104 host tests pass,633 source/support and4311 SDK files unchanged.
Evidence: docs/evidence/dash-substitution-consumer-2026-09-23/README.md.
All local runs pass first attempt with complete owned cleanup. Archive/readback
verification precedes removal of new unpacked suites and compiler caches.
Current per-script matrix is10/12 across separately pinned private fixtures.
Next local regression is the later358 connections fixture; matching command-runner
producer/consumer coverage also remains pending. Pipeline and early-reader await
actual unchanged-script delivery; current incremental owner work is prerequisite.
Independent reviews/SDK, general signals/TTY, persistence and full M3/R1 remain
open. No sibling implementation or released pin changed.


## 2026-09-23 — UL-007 full substitution connections regression

All358 connections cases now pass locally on the exact268-source substitution
fixture. Fourteen exact scratch/substitution lifecycle/PASS comparisons pass;
all358 serials retained. Source/support633 and SDK4311 pins unchanged; owned
cleanup complete. Elapsed1148.42s meets1800s review ceiling. Prior104-test host
qualification reused after byte/tool verification, not rerun. No local retry.
Evidence: docs/evidence/dash-substitution-regression-2026-09-23/README.md.
Archive/readback verification precedes removal of the new unpacked suite/cache;
prior sealed evidence and archives remain unchanged. This closes the later358
local replay gap. Acceptance stays10/12 across bounded private fixtures.
Next dependency: matching command-runner producer/consumer qualification and
actual unchanged pipeline/early-reader delivery. Current Aether pre-exec intake
is integration groundwork, not consumer-script acceptance. SDK/independent reviews,
general signals/TTY, persistence and full M3/R1 remain open. No sibling changes.


## Parent-driven consumer checkpoint — 2026-09-24

[Local matching qualification](evidence/dash-parent-consumer-2026-09-24/README.md)
now covers the unchanged pipeline and early-reader scripts through real parent
dash jobs, completing bounded per-script evidence for12/12. All890 native cases
and21 lifecycle checks pass on287 matching runtime inputs. The parent pipeline
uses12 image admissions but15 reclaims; early-reader uses15 of each, collects only
its two copied children and proves EPIPE/pump42/pipefail with exact output.
Matching command-runner qualification is complete for this fixture.
The next gap is composition with existing serial exec/substitution/runtime in
one usable shell session. These private sh -c profiles are not an interactive
filesystem shell or R1 assembly. General signals/TTY, SDK/reviews and persistence/
package/sys-init integration remain open; no new authority or released pin changed.


## 2026-09-24 — first interactive serial pipeline locally qualified

[Consumer evidence](evidence/dash-serial-pipeline-consumer-2026-09-24/README.md)
passes898 native cases on287 matching runtime hashes. Actual pipeline input and
follow-up builtin use six prompts/events over three shell generations, with exact
output,15 terminals/reclaims and complete owned cleanup. Native grant/output/disabled
controls pass. This private006/ABI20 profile is separate from general TTY support.
Next sealed Aether shell-streams-2026-09-24 simplifies forwarding; its SESSION
lifetime proposal still requires implementation and independent whole-script tests.
No full M3/R1 or installed SDK claim follows from this checkpoint.


## 2026-09-24 — bounded serial forwarding consumer checkpoint

[Local evidence](evidence/shell-streams-consumer-2026-09-24/README.md) qualifies
long-output forwarding and exact host corruption rejection in105 native cases.
110 host tests and11 controls pass; complete guest cleanup accompanies corrupted
output. All105 kernel load images match previous consumer runtime bytes; whole
ELF hashes differ in debug sections. Earlier898 regression remains prior evidence.
The serial owner no longer captures expected script bytes; fixed job topology
remains. Aether's channel lifetime extension is not a delivered native SESSION
profile. Next qualify whole composed.sh with frozen owner lifecycle/control rules.
Shared SDK, TTY/signals, independent review and M3/R1 assembly remain open.


## 2026-09-25 — UL-007 composed SESSION independently qualified

The unchanged complete composed.sh now passes SESSION-01–06 under private
AENMX007/ABI21: three parent lifetimes,27 copies,21 helper execs,24 image admissions
and30 zero-status terminal records/reclaims; exact separate65-byte stdout and
19-byte stderr per parent. All910 matching native cases pass (121 capacity,358
connections,431 runner), plus115 Python and configured Zig/Rust host checks.
Eight independent SESSION cases,14 prior lifecycle comparisons and25 checker
rejection controls pass. Runtime293 hashes match;661 source/support and4311 SDK
regular files remain pinned. Six complete linked owners match the audited producer
ELFs; maximum inspected stack depth3688/4088, not a formal safety proof.
Native suite times407.74/1140.31/1441.82s meet1800s review ceilings; process cleanup
complete. Native and host suites passed first execution. One collector selector
error was corrected and retained without changing runtime or expected outcomes.
Evidence: docs/evidence/session-consumer-2026-09-25/README.md. Current acceptance:
experiments/dash-native/SESSION-ACCEPTANCE.md; original proposal/input pins unchanged.
Next: compose early-reader recovery, failed exec, scratch and real serial input.
UL-081 shared SDK and independent reviews, UL-008/009 TTY, persistent filesystem,
package/sys-init assembly and full UL-007/M3/R1 remain open.
