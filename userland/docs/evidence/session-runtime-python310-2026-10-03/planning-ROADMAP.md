# Roadmap

Milestones are acceptance gates, not dates or promises by companion projects.

Current execution priority (maintainer direction,2026-09-07): M3 native command
and shell integration, then M4/M5. See [execution focus](../docs/M3-EXECUTION-FOCUS.md).
Optional utility/locale refinement, reference benchmarking and provider polish
are retained in its post-release queue. Required correctness,authority,cleanup,
source/license and release checks are not deferred.

| Milestone | Acceptance | Work |
| --- | --- | --- |
| M0: research baseline | Recorded direction, source-backed gaps, owned backlog, reproducible compile-only probe | UL-001, UL-004a — complete within stated scope |
| M1: SDK and runtime decision | Pinned source/toolchain audit, compared musl approaches, agreed minimal consumer ABI, isolated ELF link with inspection evidence | UL-002/003/004b |
| M2: C runtime on Aether | Static musl test reaches main, validates args/TLS/BSS, exercises memory and I/O, exits with observed status; denial/exhaustion/malformed image checks pass | UL-006 — complete for bounded native profile; docs/M2-ACCEPTANCE.md |
| M3: useful system shell | dash candidate runs external commands, scripts, redirection, pipelines and waits; EOF, broken pipes and failed exec leave no leaked children/FDs | UL-007 |
| M4: interactive TTY | Zsh editing/completion and jobs work; Ctrl-C/Z, fg/bg, terminal restoration and session teardown are verified | UL-008/009 |
| M5: packaged supervised base | pkg-mgr-produced payload consumed by sys-init-owned boot/session flow; authenticated admin/recovery policy, metadata/trust failure checks and utility inventory verified | UL-005/010/011/012 |

M1 research, package evaluation and host packaging experiments can proceed while
native contracts are missing. Full POSIX compliance is not inferred from M5;
Distribution PX-01 supplies the proposed POSIX.1-2024 reference; UL-013 defines
the supported subset and per-interface conformance evidence separately.

M2 acceptance is scoped to the tested kernel-owned native profile. Broader M1
ABI/ownership work under UL-003 remains open; milestone evidence can overlap
without asserting all shared interfaces are finalized. M3 still requires actual
script/external-command, process/file/pipe behavior.

UL-059 public-runner acceptance is specified as AR-01–14 in
[the aether-run proposal](../docs/AETHER-RUN.md). All remain NOT RUN for a public
CLI. They supplement CR-01 and do not promote M3 or replace independent package,
service, native authority and recovery evidence. Affected-owner review and UL-063
source audit precede behavior changes.

UL-067's [CAT-01–08 proposal](../docs/TOYBOX-NATIVE-CAT.md#proposed-native-acceptance-matrix)
adds bounded cat admission, copy, rejection, initialization, I/O failure, shutdown,
lifecycle and regression gates. Local native copy, usage and I/O-error witnesses
now exist; see [current CAT evidence](../docs/TOYBOX-NATIVE-CAT.md). Finalization,
full producer/regression qualification and review remain open. These bounded
utility results do not close M3 or package/TTY acceptance.


M3 prerequisite checkpoint (2026-09-08): actual dash signal routines and generated
initialization are locally reproduced within291 native command cases. See
[consumer evidence](../docs/evidence/dash-init-consumer-2026-09-08/README.md).
Generated init deliberately exposes unsupported parent/user/CWD behavior; it is
not successful shell startup. Truthful metadata, scoped directories, actual main,
external commands, wait and pipes still gate UL-007/M3. Native regression success
does not close source trust or independent review.


M3 parent prerequisite checkpoint (2026-09-08): the direct-launcher query and
generated dash PPID now pass locally in both worker placements, within295 native
command cases. [Evidence](../docs/evidence/dash-parent-consumer-2026-09-08/README.md).
Parent identity is no longer a missing bounded prerequisite. User/group metadata,
scoped directories, actual main and exec/wait/pipes still gate M3; no general
parent lifecycle, authentication or full shell acceptance follows.

M3 configuration review (2026-09-08): [metadata intake](../experiments/dash-native/METADATA.md)
is prepared against the owner proposal; runtime cases are NOT RUN. Static evidence
shows the Linux-reference main object omits a source-conditional interactive ENV
identity check. Native configuration and startup-environment behavior need explicit
qualification before full-main acceptance. This does not close or expand M3, and
is separate from the next bounded metadata initializer witness.


M3 metadata checkpoint (2026-09-08): the [bounded AECAT002 delivery](../docs/evidence/dash-metadata-consumer-2026-09-08/README.md)
now passes locally in309 native command cases. The complete metadata checklist
still has five partial rows. Scoped CWD, full-main configuration and actual process/
pipe semantics remain M3 gates; validated advisory IDs do not establish login or
authentication. No milestone closure follows from these initializer results.


M3 directory checkpoint (2026-09-09): [initial scoped CWD](../docs/evidence/dash-cwd-consumer-2026-09-09/README.md)
now passes locally within319 native command cases. Generated init resolves /work
without its old warning. This narrows the startup gap; incomplete directory and
metadata controls, native-main configuration and process/pipe execution still gate
M3. Three supplied stat fields do not establish a general filesystem API.


M3 bootstrap rejection checkpoint (2026-09-09): [four additional bounded directory
controls](../docs/evidence/dash-cwd-bootstrap-consumer-2026-09-09/README.md) reproduce
within 323 native command cases, with rejection and four reclaims. This covers one
alias, one truncation point and header-only V2/V3 mismatches. Directory reply/poison,
identity/PWD and remaining boundary controls, metadata gaps, native-main configuration
and process/pipe execution still gate M3; no milestone closure.


M3 actual execution checkpoint (2026-09-09): [local369-case reproduction](../docs/evidence/dash-file-consumer-2026-09-09/README.md)
now proves real dash main running a builtin command and a service-backed script.
Five remaining metadata observations have bounded evidence. This advances beyond
initializers; external commands, waits, redirection/pipelines, ENV behavior and V4
failure controls remain unqualified. M3 is not closed by these two execution paths.


M3 file-root admission checkpoint (2026-09-09): [local384-case reproduction](../docs/evidence/dash-file-admission-consumer-2026-09-09/README.md)
adds selected malformed V4 fields/aliases, EOF and header-only V3/V4 rejection with
six-reclaim cleanup; prior main/script cases regress successfully. File-description/
queued-body/reply-failure controls, ENV behavior and actual external process/pipe
workloads remain gates. This does not close M3 or the full file-root contract.


M3 descriptor checkpoint (2026-09-09): [local387-case reproduction](../docs/evidence/dash-file-descriptions-consumer-2026-09-09/README.md)
adds bounded independent/shared-offset, exhaustion, stale-reference and access-denial
controls while actual dash script regressions still pass. Queued V4 bodies,
uncertain-reply recovery, ENV behavior and external process/pipe workloads still
gate M3. Conformance-client results do not establish shell child execution.


M3 client-reply recovery checkpoint (2026-09-09): [local397-case reproduction](../docs/evidence/dash-file-recovery-consumer-2026-09-09/README.md)
adds queued V3/V4 mismatch and six known-backend-result client-reply failures with
poison/no-traffic, owner retirement and six-reclaim cleanup. Unknown backend result/
service-stop recovery, actual-main ENV and external-process/pipe workloads remain
unqualified. This is bounded recovery evidence, not M3 acceptance.


M3 malformed-backend checkpoint (2026-09-10): [local401-case reproduction](../docs/evidence/dash-backend-consumer-2026-09-10/README.md)
confirms service stop before description clearing/reuse for three complete malformed
replies. Later producer EOF/timeout, ENV, syntax and helper-child work awaits local
consolidated431-case intake. Public fork is a separate candidate; wait/exec and
full external-command/pipe workloads remain gates. No milestone closure.


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


## 2026-09-11 — UL-007 pipe core consumer host qualification

The pinned unconnected pipe core passes 12 local producer host cases and 32
independent consumer chunk schedules covering backpressure/retry, byte order,
terminal-before-collection EOF, stale child denial and pending-reply retirement.
Five semantic mutants fail as expected; x86_64 no_std object generation passes.
[Evidence](../docs/evidence/pipe-core-consumer-2026-09-11/README.md) preserves the
initial formatting failure and successful fresh attempt. This is host-only;
UL-007/M3 remains open. Next action: consume the Aether native pipe dispatcher and
adapter delivery, then qualify unchanged substitution and remaining pipe/signal
boundaries. Prior native redirection evidence remains unchanged. Independent
technical/security/reader review remains pending.


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


## 2026-09-14 — UL-007 current acceptance and failed-exec intake

Current matrix: experiments/dash-native/ACCEPTANCE.md. Five of12 unchanged scripts
have bounded local native evidence (argv, signal-table, syntax-error, wait,
fd-closure); seven remain unqualified. Verified script/stdout/helper pins and three
local evidence seals. Historical workloads.json remains unchanged. Evidence:
docs/evidence/dash-acceptance-index-2026-09-14/README.md.
Next failed-exec owner proposal: experiments/dash-native/FAILED-EXEC.md. Captured
latest exec-stage treats /inputs/not-executable as absent; the unchanged script
needs actual missing127/non-executable126 distinction and cleanup. No sibling
implementation or new native acceptance. Producer suspend-recovery matching runner
is incomplete after timeout; avoid competing long runs until its matched handoff.
Full M3, SDK/reviews, remaining workloads and assembly stay open.


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


M3 acceptance checkpoint (2026-09-24): all12 unchanged dash scripts now have
bounded local native evidence. The [parent consumer replay](../docs/evidence/dash-parent-consumer-2026-09-24/README.md)
qualifies pipeline and early-reader plus matching101/358/431 suites (890 cases),
with exact output/status/collection/cleanup predicates. This closes the script
matrix and matching regression gap for this fixture, not M3 itself. Acceptance
still requires composition of parent pipelines with serial exec/substitution and
runtime in a usable shell session, plus the separately tracked SDK/review gates.
Interactive TTY, persistence and R1 package/sys-init assembly remain separate.


M3 preparation checkpoint (2026-09-24): SESSION-01–06 now defines the next composed
parent-session acceptance in experiments/dash-native/SESSION.md. Syntax/static
checks pass; no composed runtime witness yet. This adds a gate beyond the completed
twelve-script component matrix and does not mark UL-007 or M3 complete.


M3 serial checkpoint (2026-09-24): independent AENMX006/ABI20 pipeline plus builtin
passes three shell generations, six prompt-driven commands and15 reclaims within
898 native regression cases. Evidence: docs/evidence/dash-serial-pipeline-consumer-2026-09-24.
This qualifies the bounded serial interaction, not SESSION-01–06, TTY or full M3.


M3 forwarding checkpoint (2026-09-24): local105-case native replay qualifies long
combined UART output, nine commands/prompts and host rejection of corrupted output
after complete guest cleanup. See docs/evidence/shell-streams-consumer-2026-09-24.
The earlier898 regression was not rerun. SESSION-01–06 and full M3 remain open;
combined UART observation is not independent stdout/stderr or TTY acceptance.


M3 composed-session checkpoint (2026-09-25): SESSION-01–06 is independently
accepted for the unchanged private AENMX007/ABI21 scripted workload. All910 native
cases,115 Python/required Zig/Rust host checks and22 independent lifecycle checks
pass, with25 oracle rejection controls. See
[acceptance](../experiments/dash-native/SESSION-ACCEPTANCE.md). Three complete parent
lifetimes have exact separate output,27 copies,21 helper execs and30 reclaims.
This closes the combined scripted-session gap, not full M3. Early-reader/failed-exec/
scratch/serial composition, shared SDK and independent reviews remain required;
TTY, persistence and package/sys-init assembly retain their separate gates.


M3 recovery preparation (2026-09-25): RECOVERY-01–06 now specifies early-reader
recovery followed by an external command and healthy pipeline in one parent.
[Workload and handoff](../experiments/dash-native/SESSION-RECOVERY.md) are pinned;
syntax/static checks pass. Native execution is NOT RUN, pending exact owner
phase/resource agreement and sealed implementation delivery. This does not widen
SESSION acceptance or close M3.


Sustained-command preparation (2026-09-25,UL-059/081): the SI-07 generation3
consumer restriction now has a versioned private contract proposal and host field-
bound/legacy decoder evidence. [Contract](../experiments/command-runner/SUSTAINED.md)
keeps native identity separate from finite private epochs. SUSTAIN-01–06 native
checks and rebuilt inputs remain NOT RUN; this is not M3/R1 or sys-init acceptance.


## 2026-09-29 — UL-007 independent recovery composition accepted

RECOVERY-01–06 now pass for private AENMX007/ABI21: unchanged script through three
native dash parents, actual EPIPE/pump42 followed by healthy argv and pipeline,
closed descriptors, exact49-byte stdout/20-byte stderr and24 terminal/reclaims.
All128 capacity + five legacy command cases and119 Python/configured Zig/Rust
host checks pass; seven independent comparisons and36 rejection controls pass.
Evidence: [recovery consumer](../docs/evidence/recovery-consumer-2026-09-29/README.md).
Current matrix: [recovery acceptance](../experiments/dash-native/RECOVERY-ACCEPTANCE.md).
The replay export omitted the legacy driver/input bundle; an explicit21-file
historical supplement matches its manifest and the delivery's import digest.
No runtime changes or relaxed inputs. Next: failed-exec, scratch and serial
composition; separately finish SI-07 versioned bootstrap and rebuilt command
inputs. Full UL-007/M3/R1, shared SDK and independent reviews remain open.


## 2026-09-29 — UL-007 failed-exec session input ready

Prepared [SESSION-FAILED-EXEC](../experiments/dash-native/SESSION-FAILED-EXEC.md):
missing127 and denied126 followed by healthy argv/pipeline and descriptor/PID/
parent-stderr checks in the same shell, repeated across three native parents.
Original syntax/ShellCheck and seven explicitly relocated host references pass.
Evidence: [preparation](../docs/evidence/dash-failed-exec-session-plan-2026-09-29/README.md).
Initial host linker failure is retained; corrected build environment passes without
changing target inputs. Native EXEC-SESSION-01–06 remain NOT RUN. Current session
adapter's local non-helper EACCES rejection must become owner-backed lookup/denial;
no fake pathname result can satisfy acceptance. Expected21 copies/12 replacements/
15 admissions/24 terminal-reclaims need owner reconciliation within existing bounds.
Next: owner implementation with complete export/negative oracles, then independent
replay. Scratch/serial composition, SI-07, shared SDK and full M3/R1 remain open.


## 2026-09-29 — UL-007 failed-exec session independently accepted

EXEC-SESSION-01–06 pass for private AENMX007/ABI21. Three unchanged dash parents
recover from owner-backed missing127/denied126 and continue with healthy argv,
pipeline, descriptor/PID and parent-stderr checks. All137 capacity + five legacy
command cases,123 Python/configured Zig/Rust host checks, nine independent
comparisons and56 rejection controls pass. Exact60/25-byte streams,15 admissions
and24 terminal/reclaims; slot2 ends at15. All17 owners match final stack/image
bindings (maximum3768/4088). No consumer runtime retry or input relaxation.
Evidence: [failed-exec consumer](../docs/evidence/failed-exec-session-consumer-2026-09-29/README.md).
Current matrix: [failed-exec acceptance](../experiments/dash-native/FAILED-EXEC-ACCEPTANCE.md).
Original native and final delivered checker hashes are explicitly reconciled;
fresh legacy replay qualifies delivered sources without claiming old receipt
identity. Next: scratch and real serial compositions; independently SI-07 complete
bootstrap/transport and rebuilt runner/bytecount. UL-007/M3/R1, shared SDK and
independent reader reviews remain open.


## 2026-09-29 — UL-007 scratch session input ready

Prepared [SESSION-SCRATCH](../experiments/dash-native/SESSION-SCRATCH.md): truncate
stale data, preserve shared-offset alias lifetime, deny protected write, reopen
and readAB/EOF, then healthy argv/pipeline, closed descriptors, same PID and stderr.
Original syntax/ShellCheck and11 explicitly relocated host references pass, including
wrong file state, allowed/skipped denial, missing reader, wrong environment, FD leak,
wrong bytes and closed stderr. Evidence: [scratch preparation](../docs/evidence/dash-scratch-session-plan-2026-09-29/README.md).
Native SCRATCH-SESSION-01–06 remain NOT RUN. Expected three-parent21 copies/15 helper
replacements/18 admissions/24 reclaims require owner resource/lifetime reconciliation
and fresh linked code/stack review within current bounds. Next owner integration,
sealed complete delivery and independent replay. SI-07 complete bootstrap/transport,
real serial composition, shared SDK/reviews and full M3/R1 remain open.

## 2026-09-29 — UL-007 scratch session independently accepted

SCRATCH-SESSION-01–06 pass:149 capacity plus five legacy native cases;127 Python
and configured Rust/Zig checks. Twelve independent comparisons and100 rejection
controls pass.26 locally rebuilt owners match sealed raw/ELF hashes, max3896/4088
estimated stack. Exact52/19-byte streams across three parents;21 copies,15 helper
replacements,18 admissions,24 terminal/reclaims. Full owner-local data/denial
oracles reviewed with native semantic controls. Only the delivered host checker
changed after the producer native receipts; exact source reconciliation retained.
Evidence: [scratch consumer](../docs/evidence/scratch-session-consumer-2026-09-29/README.md).
Next real serial composition; SI-07 complete transport/rebuilt payloads, SDK,
independent reviews and full M3/R1 remain open. Original pinned inputs unchanged.

## 2026-09-29 — UL-007 real serial SESSION input ready

[Serial handoff](../experiments/dash-native/SESSION-SERIAL.md) preserves the accepted
SESSION commands as three prompt-driven lines. Eight relocated host stdin controls,
syntax and ShellCheck pass; native NOT RUN. Exact65/19-byte program streams and
90-byte combined UART per parent are pinned. Require fresh-prompt input gating,
state across prompts, phase child cleanup, owner UART authority/short transfers,
EAGAIN and explicit cancellation with confirmed reclaim.27 copies,21 replacements,
24 admissions and30 terminal/reclaims are planned across three parents; exact native
map/control codes and fresh resource review remain owner-delivery prerequisites.
Evidence: [serial preparation](../docs/evidence/dash-serial-session-plan-2026-09-29/README.md).
Next Aether implementation/delivery then independent SERIAL-SESSION-01–06 replay.
No native acceptance, general TTY/hangup, SI-07, SDK or full M3/R1 closure is claimed.

## 2026-09-29 — UL-007 real serial SESSION independently accepted

SERIAL-SESSION-01–06 pass for private008/ABI23: one fresh complete160-case capacity
run, five legacy and four envelope/ABI cases;132 Python/configured host checks.
Eleven independent comparisons and151 counterexamples pass.35 local owner raw/ELF
pairs match sealed audits; max3944/4088 estimated stack, serial max3832. Three
parents/nine prompted inputs retain x/PID and exact65/19-byte streams plus6 prompt
bytes,90 UART.27 copies,21 replacements,24 admissions,30 terminal/reclaims.
Source reconciliation preserves producer incomplete attempts and final host-only
checker correction. Consumer preflight prompt-end correction retained; native
suites passed first attempt. Evidence: [serial consumer](../docs/evidence/serial-session-consumer-2026-09-29/README.md).
Next UL-081 shared SDK boundary and reader reviews; SI-07 complete transport and
rebuilt payloads, general TTY/persistence/packages/sys-init/full M3/R1 remain open.

## 2026-09-29 — UL-081 assessed; native continuation blocked on runtime/review

Current accepted serial link reproduced byte-for-byte. Four omission/duplicate
experiments and30 provider mappings pass: missing facade/process and duplicate
facade reject; omitted memory adapter still links through musl, yielding a different
unqualified ELF. [SDK boundary](../docs/SESSION-SDK-BOUNDARY.md) requires exact component
admission and an owner-agreed, sealed application/runtime split before SSDK-01–06.
UL-081's assessment is done; no runtime implementation or review approval is implied.
Evidence: [boundary audit](../docs/evidence/session-sdk-boundary-2026-09-29/README.md).
Small driver duplication/owned helper retained, no active path removed; UL-063 broad
source audit stays open. First static sentinel check corrected with retained attempt.
Independent [reader packet](../docs/quality/SESSION-RUNTIME-REVIEW.md) is ready, review
pending. Further M3 integration waits for runtime-owner agreement/delivery and
independent review; SI-07 separately waits for complete transport/rebuilt payloads.

## UL-007 runtime ownership cleared — 2026-09-29

The maintainer assigned bounded libc/POSIX runtime implementation to userland.
Proceed with experiments/session-runtime: separate application startup/path policy,
retain qualified mechanism inputs, enforce explicit component closure, rebuild and
exercise native serial behavior. SSDK-01–06, independent review and broader
UL-007/063/M3 remain open. SI-07 remains a separate versioned-lifetime integration.

## UL-007 extraction/candidate checkpoint — 2026-09-29

Userland runtime ownership agreed and implemented in experiments/session-runtime.
Evidence: docs/evidence/session-runtime-extraction-2026-09-29/README.md.49 fresh
native executions and49 independent comparisons; seven component/eight malformed
bundle controls; sealed standalone008 candidate rebuilds identical tested ELFs.
Next actual independent technical/reader findings and SSDK-01–06 disposition.
Preserved007 compatibility recompiles do not advertise a007 SDK bundle. Full
UL-007/063/M3/R1 remain open; SI-07 versioned lifetime composition is separate.

## UL-007 build dependency selection fixed — 2026-09-29

Evidence: docs/evidence/session-runtime-build-imports-2026-09-29/README.md. The old
builder could reuse a cached validator and admit an omitted memory component.
The corrected builder loads exactly verified support files, preserves caller import
state, rejects that omission and reproduces the native-tested parent/helper bytes.
Five host cases pass; native sources/helper and prior evidence remain unchanged.
Independent review/SSDK disposition remains pending. Aether has cleared its SI-07
v2 protocol design review; next prepare full bootstrap/transport and runner/bytecount
closure after affected UL-063 source review, then matched owner/native qualification.

## SI-07 client checkpoint, 2026-10-03 (UL-058/UL-063)

[Opt-in client delivery](../docs/evidence/sustained-runtime-2026-10-03/README.md)
completes maintained bootstrap/transport and rebuilt runner/bytecount with scoped
source review and host/static evidence. Default legacy ELF bytes are preserved.
Acceptance remains incomplete: matching Aether runtime hooks, five real cycles,
65536pre-effect rejection, native cleanup/authorized halt and independent userland
consumption remain required. Independent review and broader UL-063 remain open.

## SI-07 matched checkpoint consumed — 2026-10-03

[Independent consumer](../docs/evidence/si07-consumer-2026-10-03/README.md) passes nine
fresh native replays, including five useful cycles1–5, seeded epoch boundaries,
pre-admission exhaustion, both parent mismatches and cohort divergence.242 semantic
trace corruptions reject; exact ISO/client/owner identities and scoped resource
models are bound. The missing-input/generation3 gate is closed. sys-init BG-067
owns consuming sustained policy and outstanding-work settlement; remaining native
child-profile/malformed/stale/foreign/partial/poisoned-close schedules, reader/SDK
and broader UL-058/063/M3/R1 acceptance remain open.

## Quiescent SI-07 continuation — 2026-10-03

[Independent loop consumer](../docs/evidence/si07-loop-consumer-2026-10-03/README.md)
passes seven native cases and179 host trace controls. Six actual cycles and halt
before/after work remove the fixed-five continuation gate. This is a scoped private
ABI22 checkpoint; remaining partial/unknown/cleanup schedules, useful-session
composition, independent reader/SDK and full SI-07/M3/R1 are separate requirements.

## SI-07 failure controls consumed — 2026-10-03 (UL-058/063)

[Four fresh userland native replays](../docs/evidence/si07-errors-consumer-2026-10-03/README.md)
pass: real fragmented replies complete; accepted write/reply-reader loss prevents
replay/completion/halt; actual close/reclaim errors retain Unknown ownership and
deny cleanup/stop/start replay.183host trace corruptions reject. Exact sealed
producer/base/client/owner/tool/ISO closure and scoped resource models are bound.
No maintained runtime or sibling changes. Bounded continuation is unblocked.
[Current disposition](../docs/SI07-DISPOSITION.md) separates established SUSTAIN
requirements from broader native schedules, useful-session/wait policy, SDK reader
review/disposition and full UL-007/058/063/M3/R1. No production recovery claimed.

## UL-007 minimum Python builder repaired — 2026-10-03

[Actual minimum/current interpreter evidence](../docs/evidence/session-runtime-python310-2026-10-03/README.md)
reproduces two Python3.10 hashing failures and repairs both maintained streaming
hash paths. Pinned3.10.21/3.14.7 each pass ten controls and rebuild exactly the
previously native-qualified parent/helper. New sealed candidate preserves all
other recipe/SDK/runtime/helper inputs; historical evidence is unchanged.
SSDK-01 scoped build evidence improves; independent technical/reader disposition,
SSDK-02–06, native enforcement schedules and full UL-007/063/M3/R1 remain open.
No sibling or native runtime changes and no new QEMU claim.
