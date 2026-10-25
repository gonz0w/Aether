# Public aether-run contract proposal (UL-059)

Status: userland proposal, 2026-09-06. Not a shipped command, approved shared
interface or runtime acceptance. Userland owns this CLI specification; affected
producer, package and service owners have not signed off. Shared requirements
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
or six with the optional leading --. The current producer's fixed one-string
parent startup must be replaced by an explicitly versioned owner contract that
can carry this shape; do not assume child bounds also define parent bounds.

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
| Aether command-I/O producer | Opt-in public-runner profile accepts requested parent startup instead of fixed ["client"]; validates mapped runner results instead of mandatory 29; preserves old probe mode and terminal markers |
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

UL-059 remains active pending affected-owner review. No sibling implementation or
message is authorized by this document alone. UL-069 reference-tool work is
retained but is not a prerequisite for this specification.
