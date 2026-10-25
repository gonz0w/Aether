# Public aether-run contract proposal (UL-059)

Status: userland proposal, 2026-09-06. Not a shipped command, approved shared
interface or runtime acceptance. Userland owns this CLI specification; the producer has supplied a scoped carrier/result witness, while full
producer, package and service acceptance remains open. Shared requirements
belong in Aether-standards through its contribution process. This proposal does
not allocate wire fields, native ABI numbers or change immutable consumer pins.

## Invocation and startup

```
aether-run --help
aether-run --version
aether-run [--] COMMAND [ARG ...]
```

Launch exactly one command in an explicitly delegated immutable namespace. There
is no PATH lookup, shell parsing, redirection, expansion, script evaluation or
prompt. A slash-containing command is invalid usage in this initial name-only
profile. A syntactically valid but unavailable name is a selection failure.

Recognize --help and --version only as sole arguments. A leading -- ends runner
option parsing. After COMMAND, every argument is child data, including --help,
--version, -- and strings beginning with a hyphen. Reject unknown leading options,
missing command or excess arguments before any launch request. The runner's own
argv[0] is not forwarded: child argv is exactly COMMAND followed by ARG values;
child argv[0] is therefore COMMAND. No extra --decimal or other command option is
injected. An empty child argument after COMMAND is representable; empty COMMAND
is invalid. No alternate argv[0] option is proposed in this first CLI.

The current command-I/O candidate permits 1–4 child strings, each at most 31 bytes
plus NUL. Bound by bytes, not displayed characters; never silently truncate.
Thus the runner receives at most five startup strings including its own argv[0],
or six with the optional leading --. The producer now supplies the opt-in AERUN001 carrier for this shape, while
retaining kernel argv=["client"]. Userland selected it for bounded evaluation in
[the integration review](RUNNER-INTEGRATION.md); logical CLI startup is distinct
from the native argv slots. Independent consumer execution now covers three successful startup shapes; see
the native checkpoint below. Public CLI/result acceptance remains pending.

For this first workload, the child environment is exactly ["LC_ALL=C"], declared
as a runner profile default. No ambient environment is forwarded, no NAME=VALUE
prefix grammar is accepted and no --env option is advertised. This is a proposed
CLI policy within the producer's LC_ALL=C allowlist, not a general environment
API. Arguments and environment never create executable or I/O authority.

Caller-supplied startup and bootstrap bindings must be complete and valid before
publication or command admission. Userland owns validation/serialization; the
producer independently validates/copies the entire existing launch frame. Local
usage failure emits no launch. Copied bytes must survive caller-buffer mutation.
Parent startup failure occurs before the public CLI and must be reported by the
owning launcher, not fabricated as a child result.

## I/O and authority

The caller explicitly delegates input and output. For the existing candidate,
parent binding 3/read maps to child 0/read, and parent 4/read-write to child
1/write; validate both before either is live. This is a workload profile, not
ambient authority for arbitrary descriptors. Names and package metadata are data.
No stderr grant is implied by a console, service name or POSIX UID.

A successful command invocation adds nothing to stdout: those bytes belong to
the child. Runner diagnostics go only to an explicitly provided stderr sink;
without it, terminal/result evidence remains authoritative. Do not divert errors
to child stdout or invent a grant. Runner --help/--version require a suitable
explicit output grant and real write/close success. The existing 64-byte file
profile is not sufficient evidence for a full help response; caller/output scope
must be reviewed separately before advertising native help support.

Output-file position is shared. The runner's post-command EOF does not verify
output bytes. Preserve the service-side verifier's independent backend readback,
exact byte/length and input-preservation checks in CR-01 evidence. No local seek
or position reset may bypass this boundary.

## Public result mapping proposal

Use the pinned Experience new-command exits for runner-owned outcomes. Earlier
125/126/127 ideas remain historical proposals, not an implemented exception.
They are not selected here without a future explicit compatibility decision.

| Outcome | Proposed public exit | Evidence that must remain distinct |
| --- | --- | --- |
| Runner help/version fully delivered | 0 | Local action; no child admission |
| Invalid runner invocation | 64 | Usage rejection; no launch sent |
| Valid name absent, authority denied, unavailable capacity or required binding absent | 2 | Precondition failure; exact owner error, no admitted child |
| Local runtime/I/O failure before admission | 1 | Runner error; known no-child outcome |
| Observed normal child exit in 0–255 | Exactly child exit | Normal kind, full raw detail and consumed receipt |
| Observed child fault or stop | 1 | Original terminal kind/detail; never manufacture POSIX signal encoding |
| Normal detail outside 0–255 | 1 | Unrepresentable CLI outcome; full raw detail retained, no truncation |
| Delivery or collection outcome unknown | 1 | Unknown admission/result; retain recovery ownership, never infer no child |
| Malformed reply, exhausted observation budget, or required cleanup failure | 1 | Runner failure plus any already observed child result; not child success |

Normal child statuses 1, 2, 64, 125, 126 and 127 retain their values. A numeric
process exit alone cannot distinguish those from runner failures. A trusted caller
requiring that distinction needs owner-approved result evidence carrying phase,
known/unknown admission, receipt if known, native terminal kind/raw detail,
public exit, and independent cleanup/recovery state. This is an information
requirement, not a new serialized protocol or public --format option.

Runner success requires observed normal child exit 0 and required owned cleanup.
Cleanup failure does not erase the observed child result; it prevents public
success. A native fault detail such as 134 is not automatically signal 6 or a
normal exit 134. Cancellation/stop mapping is proposed as operational failure;
there is no installed POSIX signal or cancellation API in this profile.

Collection consumes once, separately from native reclaim. Parent file close must
not erase child results or revoke the child's retained bindings. On ambiguous
transport delivery, poison the connection according to its existing contract;
never replay spawn, writes or consuming collection. A finite observation budget
is not proof of child death. An owner must define retained-resource resolution
before claiming unattended recovery; CLI exit alone cannot close this gap.

## Owner handoff and acceptance

| Owner/work | Concrete proposal or required evidence |
| --- | --- |
| Userland UL-059 | Review this startup/result/I/O contract and examples; keep proposal distinct from implementation |
| Aether command-I/O producer | Opt-in carrier plus collected-result mapping delivered; independent consumer adoption and zero-admission/error/recovery acceptance remain open; preserve old probe mode and markers |
| Userland UL-063 then UL-058 | Audit existing runner/adapter boundaries before behavior changes; complete bootstrap atomicity, malformed/unknown delivery and abnormal-child controls |
| Aether/userland integration | Agree reply/error identity, representable status domain, bounded observation and explicit unknown-result recovery; publish matching versioned producer/consumer evidence |
| pkg-mgr UL-012 boundary | Reconstruct exact approved runner/command artifacts privately; verify bytes/modes/startup description without granting authority or claiming activation |
| sys-init boundary | Explicit admission/grants, service lifecycle and result observation; CLI exits do not define restart/stop policy or confer service authority |
| Aether-standards | Route any new cross-project requirement to canonical owner review/versioning; no local competing shared release |

Required tests before implementation acceptance (NOT RUN for the public CLI):

| ID | Acceptance witness |
| --- | --- |
| AR-01 | Sole help/version, missing/unknown runner options; exact stream/status and zero admissions |
| AR-02 | Leading -- and child --help/--/hyphen arguments preserved without shell interpretation |
| AR-03 | 1/4 child argv boundary, fifth rejection, 31/32-byte boundary, empty argument and empty-command distinction |
| AR-04 | Exact argv[0]/argv/env observed by independent child; no ambient environment or hidden arguments |
| AR-05 | Both bootstrap bindings publish atomically; rights/source/duplicate/missing rejection without effects |
| AR-06 | Unknown command and denied/capacity outcomes map 2 with exact no-admission proof |
| AR-07 | Normal child statuses 0/1/2/64/125/126/127/255 preserved; out-of-range detail retained and fails explicitly |
| AR-08 | Fault/stop remains distinguishable from the same numeric normal detail |
| AR-09 | Complete rejected frames followed by valid launch; partial-frame EOF/unknown reply poisons without replay |
| AR-10 | One-time result consumption, foreign receipt denial, parent-close/child survival, bounded observation and reclaim |
| AR-11 | Child 0 plus cleanup failure returns 1 with both facts retained; absent stderr never corrupts stdout |
| AR-12 | Same command produces exact 6-newline/0-newline with independent backend verification; wrong-output control rejects |
| AR-13 | Existing finite exit-29 producer/consumer suite remains intact alongside opt-in public profile |
| AR-14 | Matching pkg-mgr reconstruction and sys-init lifecycle/grant evidence; installation, selection and activation distinct |

Examples: `aether-run bytecount --decimal` proposes child
["bytecount", "--decimal"]. `aether-run bytecount --help` requests child help,
not runner help. `aether-run -- bytecount --decimal` has the same child startup.
These are contract examples, not commands currently available on Aether.

UL-059 remains active. The [producer refresh](RUNNER-INTEGRATION.md) selects a
bounded carrier/result input; full affected-owner acceptance remains open. No sibling implementation or
message is authorized by this document alone. UL-069 reference-tool work is
retained but is not a prerequisite for this specification.

Implementation prerequisite review: [UL-063 source audit](quality/COMMAND-RUNNER-REVIEW.md)
records completed scoped C formatting, subprocess/environment corrections and
Python restructuring, with independent reviews pending. Scoped host and native
[UL-058 boundary witnesses](../experiments/command-runner/BOUNDARY-PLAN.md)
are now recorded through NB-04; wider recovery and review remain open.
No public runtime acceptance follows from identical fixture ELFs or the audit.


## Pure parser checkpoint — 2026-09-06

[Host parser evidence](evidence/runner-parser-2026-09-06/summary.json) exercises
224-byte carrier validation, owned copies, sole help/version, leading `--`,
name-only commands and exact child arguments/environment. Rejection leaves output
unchanged. Callers must branch on the action before using the invocation; actions
are not delivered help, exit statuses or admission receipts. `AR_LAUNCH` means
syntactically valid selection, including an unknown command name; actual lookup
and authority checks remain separate.

The new component is not wired into native bootstrap or the finite runner. AR
public acceptance cases remain pending native integration. Next: consume the
carrier once within opt-in initialization and independently observe the child's
full argv/environment before adding public result mapping. Zero-admission output
and recovery still require affected-owner acceptance.


## Native startup checkpoint — 2026-09-06

[Native startup evidence](evidence/runner-startup-2026-09-06/summary.json) connects
the decoder and actual selector to opt-in single-attempt initialization. The
simple, leading-delimiter and four-child-string cases execute on Aether. A
separate child checks full argc/argv (including empty and 31-byte arguments) and
exact environment. Corrupting the fourth argument rejects at child80/parent53/
broker970. Positive cases preserve independent backend output verification and
six reclaims over two generations. Host controls cover every truncated prefix,
failed publication and cross-entry re-entry; native malformed carrier controls
remain a separate follow-on.

This supplies scoped startup/forwarding evidence for AR-01/02/04/05, not completion
of those public cases. The parent still follows the finite exit29 convention;
no public local action, result mapping or recovery is implemented. Next: pure
admission/collection decoding and explicit mapped-result integration against the
reviewed producer. Independent technical/reader and affected-owner acceptance
remain pending.


## Pure result checkpoint — 2026-09-06

[Result evidence](evidence/runner-results-2026-09-06/summary.json) exercises
admission, collection, pending and owner-error decoding under UBSan. It validates
exact size, generation/receipt, reserved bytes, bounded wire errno and terminal
kind before publishing. All normal statuses0–255 are preserved by terminal policy
only when cleanup is explicitly complete. Fault/stop, wide detail and incomplete
cleanup map to1 with raw facts unchanged. Four broken receipt/padding/kind/cleanup
variants reject at exact test oracles.

This is pure host evidence and native object generation. Decoder calls do not
perform or consume collection, prove peer authority, grant retry permission or
resolve unknown outcomes. Local/precondition exits remain separate. Next: wire
these helpers into the opt-in runner and qualify mapped_results natively while
preserving the finite parent29 suite and full raw result evidence.


## Native collected-result checkpoint — 2026-09-06

[Mapped evidence](evidence/runner-mapped-2026-09-06/summary.json) connects validated
admission and collection decoding to the opt-in runner. Nine normal statuses
0/1/2/64/125/126/127/134/255 are preserved; real fault134/kind2 becomes parent1.
All ten positives retain raw child terminal records, independent backend output
checks and six reclaims across two generations. Incorrect kind and forced-zero
mappings reject. A local close-error report preserves raw child0/kind1/receipt
through policy evaluation and yields parent1; the producer rejects that mismatch.
This does not qualify failed remote cleanup or recovery.

All47 combined native and nine default-pin cases pass; prior28 client ELF bytes
are unchanged. These are scoped AR-07/08/10/12/13 witnesses. Native stop and wide
normal detail remain outside this run; host policy tests are separate. The runner
still lacks accepted local help/usage/precondition outcomes and unknown-result
resolution. Next: a concrete affected-owner handoff for zero-admission lifecycle,
output grants/capacity and cleanup evidence, plus remaining mapped-path uncertainty
controls. No installed public CLI or package/sys-init acceptance is claimed.


## Proposed local-outcome acceptance — 2026-09-06

The [owner handoff](RUNNER-LOCAL-OUTCOMES.md) defines RL-01–12 for help/version,
usage, complete denied admission, delivery/cleanup failures and broken verifier
controls. Candidate text fixtures have measured byte/line bounds, not native
delivery acceptance. Existing64-byte output and absent stderr grant are insufficient;
the proposed separate512/256-byte roles need owner review and explicit transport.
Completed-child gates remain intact. No sibling change or acceptance is implied.


## Mapped control-flow host checkpoint — 2026-09-06

[Uncertainty controls](evidence/runner-uncertainty-2026-09-06/summary.json) run the
actual mapped runner and decoders against scripted exchange/I/O. Twenty-five
scenarios and four semantic mutations verify exact request frames, no calls after
lost/malformed replies, explicit-pending-only retry, the100,000-poll boundary,
cleanup failure and raw-result preservation. No production change was required.

These are host complete-exchange controls, not native fragment delivery or resource
recovery witnesses. The current path aborts1 on uncertain or rejected exchange;
it does not implement public precondition diagnostics. Next: native mapped-path
lost/malformed reply controls with exact parent/child/owner rejection evidence.
The RL local-outcome extension remains pending affected-owner review.


## Native mapped uncertainty checkpoint — 2026-09-06

[Six native witnesses](evidence/runner-native-uncertainty-2026-09-06/summary.json)
exercise the real adapter/runner after locally losing the final received fragment
or corrupting a complete real admission/collection reply. The runner returns1;
wrappers prove one injection and no later guarded effects before witness101/102.
A retry mutation is caught at109 before reaching the adapter. Collection cases
retain actual child0; admission cases do not assume child termination timing.
All deliberately reject at broker970/reclaimed0, without claiming recovery.

The full 53 combined cases and nine legacy cases pass; prior42 client ELF bytes
match. These add scoped AR-09/10 evidence; native malformed startup, pending-budget,
local RL outcomes and unknown-resource resolution remain open. Next local work:
native startup-carrier rejection and publication controls. The owner proposal for
help/usage and other local outcomes is still pending review, not implicitly adopted.

## Native startup rejection checkpoint — 2026-09-06

[Nine native controls](evidence/runner-native-startup-2026-09-06/summary.json)
reject corrupted real carrier magic/count/reserved/slot padding, invalid second
binding rights, and receive prefixes0/223/255. Witness111 checks unpublished
arguments/references, real musl EBADF on FD0–4 and no auxiliary lookup/channel
activity on retries. A private early-argument-publication adapter mutation triggers
witness112 before the following receive. No child is launched. Exact parent-only
terminal records and owner970/990 with reclaimed0 establish deliberate rejection,
not cleanup or recovery. Original complete records are validated before mutation;
partial receives are local fault injection, not a remotely truncated producer.

All62 combined native cases and nine original-pin cases pass; all48 prior client
ELFs remain identical. Host startup270+2 mutations, mapped25+4, parser1293+2,
result28159+4 and21 command regressions pass. Source review corrected intermediate
pointer arithmetic in the new test witness; the superseded attempt and corrected
rerun are retained. Production code and producer/SDK pins are unchanged.
Native pending-budget controls, independent reviews and owner acceptance of local
help/error/output and unknown-resource recovery remain open. UL-059 stays active.

## Native collection-budget checkpoint — 2026-09-06

[Four native controls](evidence/runner-native-budget-2026-09-06/summary.json)
exercise the unchanged 100,000-attempt runner bound. After obtaining an actual
child0/kind1 collected result, a private wrapper supplies local canonical pending
replies and counts synthetic yields without scheduling. Completion on the final
allowed attempt returns0, uses real EOF/closes and passes two generations with six
reclaims. Exhaustion returns1 with no further transport/output cleanup/policy
calls, verified by witness114. Private off-by-one mutants produce witness115 before
attempt100,001 reaches transport, or witness116 after only99,999 attempts. Negative
cases require exact child0/parent witness/owner970 with reclaimed0 and no success.

All 66 combined native cases, nine legacy cases and affected host regressions pass;
all 57 prior client ELFs remain identical. The first attempt passed. This is Aether
execution of runner control flow with injected replies/yield observation, not
100,000 remote pending exchanges, stuck-child scheduling, a time deadline or
unknown-resource recovery. Production behavior and all producer/SDK pins remain
unchanged. Current relevant owner contract/broker/backend hashes still match the
consumed producer; local help/error output needs the proposed owner extension.

Next local work: plan host local-outcome delivery and cleanup controls against the
proposed output fixtures. Native local outcomes, unknown-resource recovery and
independent reviews remain open. UL-059 stays active; UL-069 remains deferred.

## Host local-output delivery checkpoint — 2026-09-06

[Host-only delivery candidate](evidence/runner-local-delivery-2026-09-06/summary.json)
passes 6,130 UBSan scenarios and four semantic mutations against the six pinned
proposal text fixtures. Positive short writes retain only the unwritten suffix;
known write failure still closes each owned logical sink once, while unknown or
malformed results stop all calls on the shared connection. The state preserves
original action/admission error, confirmed byte progress and individual close facts.
Exit0/2/64 requires complete delivery and both successful close reports; other
outcomes return1 without replay. Logical sink labels grant no native authority.

Parser/result/mapped and21 command host regressions pass. Both the initial algorithm
run and final contributor CLI adoption run are retained. Native behavior is unchanged
and not rerun here; native RL-01–12, remote resource recovery and independent reviews
remain open. This helper is not wired into runner.c or a package. See the
[local candidate guide](../experiments/command-runner/LOCAL-OUTPUT.md).
Next: host parser/admission-to-fixture delivery integration. Native use still needs
the proposed owner sink-role/lifecycle extension. UL-059 active; UL-069 deferred.

## Host local frontend checkpoint — 2026-09-06

[Host frontend evidence](evidence/runner-local-frontend-2026-09-06/summary.json)
connects the actual carrier/parser, admission decoder and local-output helper.
Help/version/usage select pinned generated fixture bytes without an admission
callback. Launch selection forwards the complete owned invocation once; only
validated complete ENOENT/EACCES/EBUSY replies select unavailable/denied/capacity.
Accepted admission returns a distinct receipt-bearing action, without local output
or collection. Unknown/malformed replies, unsupported errors and invalid startup
produce no invented diagnostic, replay or cleanup. Original parser/admission facts
remain separate from local delivery failure.

The 280 UBSan scenarios cover28 configurations, two generations and five delivery
modes (inert for nonlocal outcomes). Three mutations detect admission on help,
collapsed denial classification and repairing malformed reply padding. Existing
6130 delivery/four-mutant, parser/result/mapped and21 command host regressions pass.
The initial mutation-anchor setup failure and corrected passing rerun are retained.
No native production path changed or ran here; native RL-01–12 and independent
reviews remain open. Next: consolidate the affected-owner handoff with current
consumer evidence. Native local outcomes still need the proposed sink/lifecycle
extension and a new explicitly pinned producer bundle. UL-059 stays active.
