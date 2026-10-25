# UP-02: first useful native command runner

2026-09-05. Aether implementation proposal for affected-owner review. The user
selected real userland integration as the next direction. This document makes
that workload and the Aether-side choices concrete; it does not record agreement
from userland, sys-init or pkg-mgr. Shared normative decisions and actual review
records remain in the canonical [PD proposal](../../Aether-standards/drafts/distribution-v0.2.0/PROCESS-FD.md).
No new native ABI, syscall number, release or consumer pin is allocated here.

## Current implementation boundary

A separate [command-I/O candidate](NATIVE-COMMAND-IO.md) now executes a real
byte-counting C command through musl read/write/close, two inherited standard-file
bindings and copied startup data. Nine native cases cover nonempty/empty input,
short writes, full output, rejection/retry and targeted corrupted results/effects.
The runner is a conformance probe; independent userland acceptance, general CLI
result mapping, remaining failure/recovery coverage and packaging are still open.
The proposal below remains the broader CR-01 target, not a completed milestone.

## Decision recommended by Aether

Build a spawn-only `aether-run` userland command runner first. It accepts an
explicit command name and argument vector, launches a fresh image, collects its
result and returns a mapped result to its caller. It has no shell grammar,
interactive prompt, PATH search, expansion, pipelines or command substitution.
Do not fork a temporary shell implementation or adapt dash around missing process
semantics merely to obtain a prompt.

For the eventual dash port, implement bounded eager-copy fork and transactional
exec before considering optimized vfork or copy-on-write. Keep the first fork
single-threaded and local to one kernel instance. Userland owns POSIX identities,
parent/child relationships, descriptor tables and libc entry points. Aether owns
address-space/register isolation, executable authority and the native commit
boundary. Service startup/stop policy stays with sys-init, and artifact transport
stays with pkg-mgr. These are Aether's proposed implementation boundaries, not
unilateral assignments of production services to another project.

## CR-01: executable workload

Userland supplies two actual native C programs: the runner and a small `bytecount`
command. The command uses the intended public libc read/write/close path, not
native trap calls or a replacement conformance helper pretending to be libc.
The runner selects `bytecount` inside its delegated immutable command namespace.
The file backend remains a separate user-space service.

The initial reproducible invocation is conceptually:

```text
command: bytecount
argv:    ["bytecount", "--decimal"]
env:     ["LC_ALL=C"]
stdin:   explicitly delegated read-only input file containing "abcdef"
stdout:  explicitly delegated write-only, initially empty output file
stderr:  absent; no implicit console grant
```

The command reads to EOF, writes exactly `6\n`, closes its descriptors and exits
0. The runner collects that actual exit result once and reports success. The
parent/service-side verifier reads the output through its separately owned
reference, verifies exact bytes and length, verifies input bytes unchanged, and
confirms final descriptor/backend/native cleanup. Run again with an empty input:
expected output `0\n`, exit 0. Both launches use the same command image with
request-supplied startup data; an image hard-coded to the first input does not pass.

The runner does not parse shell redirection. A trusted caller explicitly binds
input/output references before the request. Package names and paths in the
manifest are inert selection data; they never create grants. The first command
need not implement open/path traversal, cwd, account lookup, TTYs or directories.

The core workload now executes in the local candidate above. Its two-reference
protocol is explicitly a candidate for userland review; it does not supersede
existing consumer pins or establish the complete public command-runner stack.

## Concrete contract choices for the integration

| Area | Proposed first-runner behavior |
| --- | --- |
| Command lookup | Connection-scoped immutable name `bytecount` maps to an existing executable grant. No PATH, arbitrary path or supplied numeric grant. Unknown command is ENOENT before admission. |
| Arguments | 1–4 strings, each at most 31 bytes plus NUL; retain caller-supplied argv[0]. Broker copies all bytes before launch. No implicit argument injection. |
| Environment | 0–4 strings with the same bound. Explicit allowlist for this workload: only `LC_ALL=C`; no inherited ambient environment or loader configuration. Native strings remain data, not authority. |
| Inheritance | Exactly two distinct entries for this workload: parent source reference to child FD 0 with read rights; another to FD 1 with write rights. Reject duplicate destination, unsupported flags, wrong directions, missing reference and rights expansion before effects. |
| Startup delivery | Child libc facade obtains its descriptor bindings through its private broker connection before command I/O. No copied pointer, raw backend handle or parent-local FD table is trusted. |
| File owner | One user-space owner serializes shared positions, rights and final-close state. Input and output are distinct open-file records; each inherited alias shares its own source record. Actual storage remains in the file service. |
| Process capacity | Runner, one command and file backend: current three worker slots plus broker suffice. No kernel capacity increase for CR-01. |
| Channel capacity | One private pair per runner, command and backend: current six channels suffice. Multiple file references share a client connection; do not allocate a new channel per FD. |
| File/descriptor bounds | Two backend open records; child bindings at 0/1. Retain 64-byte volatile file bounds initially, with room for bounded output. This does not implement all indices 0–15 or dash's descriptor requirements. |
| Working memory | Retain current 128-page worker budget and startup bounds. Measure linked image, actual committed pages and peak command/libc allocations before requesting increases. |
| Admission failure | No child identity/receipt/table publication, no change to source positions or references, all temporary native resources released. Validation must not truncate the output file. |
| Child completion | Preserve observed normal exit detail; runner success only for command exit 0. Report fault/stop distinctly from normal exit, never fabricate success. Keep native cleanup separate from facade result consumption. |
| Unknown outcome | Failed delivery after successful admission or collection remains unknown, with owned resources retained for explicit resolution. Do not replay spawn, write or consuming collection automatically. |

The separate candidate specifies an opt-in operation and byte layout. Agree
consumer adoption explicitly before replacing any existing adapter or pin. Extend a separately identified user-space contract on
ABI 9; preserve old producer modes and their immutable receipts. Bound total frame
size, copy/validation, incremental receive state and malformed-prefix EOF behavior
in that contract. Runtime tests must use the exact same contract as the consumer.

Admission rollback must distinguish task generations from channel generations.
Current rejected native launches do not publish/spend a child generation, but
allocating and closing a temporary channel does spend its finite generation.
Do not decrement those generations to simulate unlimited rollback. Declare the
remaining retry budget and return exhaustion honestly; existing two-round tests
demonstrate only their specific bounded rejection/retry schedules.

For this admitted one-command tier, recommend runner exit 0 when the command
returns 0, propagation of other normal eight-bit command exits, 127 for unknown
command, 126 for known-but-denied/invalid executable, and 125 for a runner-side
admission/transport failure. These are proposed runner UX values, not POSIX wait
status or a new native error mapping. Retain the underlying signed error and
observed outcome in test evidence; no successful shell-port claim follows from
these familiar numbers.

## What is already usable, and what changes next

| Owner-facing step | Concrete output | Dependency |
| --- | --- | --- |
| Userland UL-051 | Independently consume pinned one-reference admission and terminal collection | Completed Aether producer; no new kernel work required |
| Aether + userland contract review | Agree copied argv/env and two-entry standard-file bootstrap for CR-01, plus real output and error mapping | This proposal and current libc/descriptor implementation |
| Aether producer follow-through | Extend the user-space broker's request validation, two-record alias handling and actual child outcomes; preserve rollback and old modes | Agreed user-space contract; existing native paired launch and startup copy suffice |
| Userland command execution | Implement runner/bytecount using public libc FD calls and independently verify actual startup, output and outcomes | Two-entry protocol and libc file-table integration |
| pkg-mgr consumption | Stage the exact accepted runner/command/backend/broker/kernel artifact set, reconstruct and boot it | Userland's matching native receipt; installation remains inert transport |
| sys-init integration | Decide how this runner is admitted/stopped as a service or child and consume its actual lifecycle | Separately agreed service policy; ABI-6 and ABI-9 are not implicitly composed |

Do not mark affected owners approved, or move their backlog items to done, from
Aether's implementation proposal. Keep shared PD review pending until those owners
supply their review. The implemented candidate uses existing native launch; no kernel fork primitive
is required for this spawn-only workload.

## Required native acceptance

| Workload | What must be observed |
| --- | --- |
| Nonempty and empty input | Exact `6\n`/`0\n`, libc EOF behavior, normal exit 0 and complete cleanup |
| Startup values and copying | Command observes requested argc/argv/environment; parent mutates its source buffer after admission without changing child values |
| Unknown/denied command | Correct distinct error, no child, no spent native admission generation, unchanged file positions/data and a subsequent valid launch |
| Invalid inheritance | Duplicate target, bad source, wrong rights and unsupported flags reject before allocation/publication; both existing references still work |
| Resource rejection | Full second-record/descriptor or channel reservation failure rolls back the whole request, followed by a valid retry |
| Output-full/short write | Real libc caller handles the declared result; no silent truncation or success after losing bytes |
| Command error/fault | Preserve actual normal nonzero exit or native fault kind, collect once, reject stale/duplicate receipt and reclaim everything |
| Parent/file lifetime | Closing the parent's alias preserves the child's file; closing files does not destroy collection ownership |
| Failed delivery | Distinguish known pre-admission rejection from unknown post-admission/post-write/post-collection delivery; no automatic replay |
| Packaged reconstruction | Same accepted bytes and outcomes after explicit package staging and image reconstruction |

These are future CR-01 acceptance requirements, not a count of tests already run.
Use independent userland assertions and targeted producer mutations. Never replace
bytecount with a hard-coded exit/output helper and call the command tier complete.

## Dash sequence after CR-01

1. **Define and implement local eager-copy fork.** Reserve a child domain, private
   memory and scoped file/endpoint bindings before publication. Copy heap, stack,
   TLS and user register state; return child identity to the parent and zero to
   the child. Test independent writes and shared open-file positions. No user-space
   namespace server can substitute for native private-memory enforcement.
2. **Define transactional exec.** Preflight and copy startup/image inputs into
   fresh resources while the old image remains runnable. Failure preserves the
   process, file table, offsets and identity. Commit replaces mappings/registers
   and applies agreed CLOEXEC changes together. POSIX process identity belongs to
   the facade and must survive any native image-generation transition. This needs
   an explicit native preparation/commit contract; current launch is insufficient.
3. **Resolve libc and shell signal paths before enabling them.** Musl's mask
   helpers and dash's signal setters can ignore raw failures. Audit and implement
   the required semantics or use a checked, owner-reviewed refusal/adaptation;
   returning ENOSYS underneath an unchecked caller is not adequate. Cover wait3,
   waitpid, child notifications and interrupted close/wait independently.
4. **Handle vfork deliberately.** Prefer a reviewed, tested fork-backed adaptation
   for the initial single-threaded port if the actual dash/musl build permits it.
   Otherwise leave that path unsupported until suspension/shared-memory semantics
   are implemented. Do not claim the Linux-reference vfork witness proves either.
5. **Add native shell script acceptance.** Integrate descriptor flags (including
   index 10), atomic CLOEXEC, pipe alias lifetime/backpressure, redirection and
   substitution. The shell-plus-three-stage pipeline requires more processes
   than CR-01; measure and specify that separately. Interactive TTY/jobs come later.

Eager copy is chosen for an auditable first correctness implementation. There is
no measured performance claim, no copy-on-write design commitment and no promise
that today's kernel exposes the required clone/exec transaction.

## Review inputs and evidence scope

The [dash gap audit](../userland/docs/NATIVE-DASH-GAPS.md),
[musl process/FD audit](../userland/docs/research/MUSL-PROCESS-FD.md),
[consumer process plan](../userland/docs/NATIVE-PROCESS-PLAN.md),
[existing startup copy contract](NATIVE-LAUNCH.md), and
[inherited-launch/collection contract](NATIVE-INHERITED-LAUNCH.md) are the inputs.
[Review inventory](evidence/command-runner-review-2026-09-05/README.md) pins inspected
bytes and records offline checks. That review inventory remains planning-only. Runtime results are retained
separately in the command-I/O candidate evidence; neither records owner approval,
a shared standard, release or updated consumer pin.
