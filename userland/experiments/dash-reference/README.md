# Dash Linux-reference candidate (UL-034)

Dash 0.5.13.5 builds with Clang/LLD 21.1.8 and the retained unmodified musl 1.2.6
Linux SDK. Twelve bounded reference outcomes pass. This is package feasibility
and consumer-requirements evidence, not an Aether port, a permanent shell
selection, a performance result or POSIX certification.

## Inputs and build

[source.lock.json](source.lock.json) pins the upstream release archive before
extraction. The upstream HTTP download matches the digest in the separately
retrieved HTTPS Homebrew formula. Upstream HTTPS was unavailable; the Debian
mirror index did not contain this version. These are byte-identity observations,
not independently authenticated source or release eligibility. UL-016 remains open.
The retained formula is a dated research snapshot, never a moving build input.

Target is x86_64-linux-musl; build host is macOS arm64. The script verifies every
SDK file against the existing large-TLS inventory and checks LLVM/make executable
hashes. It excludes host Clang configuration, host include paths and implicit
startup/library discovery. Link inputs are explicit target crt1/crti/libc/crtn;
this artifact needed no compiler-rt members or other target libraries. Generated
config selects SMALL (no libedit), LINENO, internal glob/fnmatch, and disables
tee and memfd_create usage. Job-control code remains compiled; disabling libedit
does not remove process/session dependencies.

All four upstream build generators are target ELF programs, executed with
QEMU in the pinned container. This avoids importing macOS signal numbers or
other host ABI properties through CC_FOR_BUILD. No upstream source patch is
applied. The release includes configure and generated arithmetic parser sources;
no autoconf, automake or yacc regeneration was needed.

The build uses private host directories and explicitly approved Podman access.
Generator containers have no network, read-only root, dropped capabilities and
bounded memory/PIDs; they can write their private build mount. Host build tools
and shared libraries are not a fully hermetic closure. No network fetch occurs
inside the build script. No real-prefix install, package activation, sibling edit
or VM lifecycle change occurs.

After separately acquiring the locked archive at its recorded path:

```sh
python3 experiments/dash-reference/build.py
python3 experiments/dash-reference/test.py build/dash-reference-zx5wokn_
python3 experiments/dash-reference/audit-imports.py build/dash-reference-zx5wokn_
```

Use the newly printed build directory for a new run. Outputs are deliberately
fresh; commands and evidence contain exact paths. This procedure has not been
validated as byte-reproducible across independent hosts.

## Results

Retained build: `build/dash-reference-zx5wokn_`.
Retained cases: `build/dash-cases-vziqj4gz`.
[Durable records](../../docs/evidence/dash-reference-2026-09-05/summary.json)
include source/tool/SDK identities, configuration, notices, object imports,
commands, scripts, stdout and guest syscall traces.

The unstripped ELF is 241,200 bytes; PT_LOAD memory sizes sum to 207,746 bytes
before page rounding, stack and heap. Inspection verifies x86-64 ET_EXEC, no
undefined external symbols, no dynamic/interpreter segments, no W+X LOAD and a
non-executable stack. These sizes are not peak memory measurements or native
loader admission evidence.

| Case | Expected result |
| --- | --- |
| argv | External helper sees quoted space, literal asterisk and environment |
| wait | Background helper's status 7 is retained by wait |
| pipeline | Three stages deliver exact bytes and terminate at EOF |
| substitution | External output is captured with trailing newline removed |
| redirection | Duplicated file descriptors share the write offset; readback is AB |
| fd-closure | No descriptors 3–63 are visible to external helper |
| fd-leak-control | Deliberately inherited FD 9 makes the same checker reject, shell exits 22 |
| early-reader | One-byte reader exits; writer observes EPIPE and exits 42; pipefail retains it |
| failed-exec | Missing path returns 127; existing non-executable returns 126 |
| denied-redirection | Read-only input mount rejects file creation with a diagnostic |
| signal-table | Linux signal 10 is USR1 and a self-directed USR1 trap runs |
| syntax-error | Invalid syntax exits 2 with a syntax diagnostic |

Each case runs as UID 65534 with network disabled, a read-only root/input mount,
16 MiB private scratch tmpfs, 512 MiB container memory and 32 PID ceiling. Every
script runs under the candidate dash through qemu-x86_64. External helper commands
explicitly exec the container's `/usr/bin/qemu-x86_64` with our static helper ELF;
this avoids relying on a host binfmt registration. It exercises shell exec/wait
and inheritance across that boundary, but does not prove direct x86-64 helper
exec on native Aether. Helper internals are not included in the parent shell's
-strace stream. Concurrent trace lines may interleave; observed call lists are
not exhaustive syscall inventories.

The FD scan is bounded to 3–63. Wait/pipeline traces show child status and ECHILD,
but this is not a global leak or race audit. TTY, interactive jobs, disconnect,
large here-documents, ENOEXEC script fallback, fork exhaustion, interrupted wait,
pathname authority and native allocation pressure remain untested here. The first
helper compile was rejected by Clang's deprecated linker-path warning; the build
now uses --ld-path. A first test container failed because its deliberately empty
PATH also hid the emulator; an absolute entrypoint fixed that. Neither setup
failure is counted as a semantic pass.

## Native dependency audit

See [the source-based audit](../../docs/research/DASH-0.5.13.5.md). UL-035 completed the
[libc/process and descriptor witness](../process-reference/README.md); UL-007 remains waiting on
native owner-assigned process/VFS support. Shared interface requirements must go
through Aether-standards; these local findings do not assign sibling APIs.

## Host import-auditor process boundary (UL-075)

The import auditor now verifies the pinned nm executable with an explicit check
that remains active under Python optimization. Each invocation uses the input build
as cwd, fixed PATH/LC_ALL and a private TMPDIR, a 30-second wait and a 1 MiB per-file
limit. It reuses the existing command-runner helper to own the child session and
non-detached descendants. Raw streams and process receipts remain under a fresh
`build/dash-imports-*`; successful receipts bind the report and helper hash.

The positional command and `libc-imports.json` keys/symbol subtraction are unchanged.
Success remains silent. A failed invocation raises an error and does not publish a
new report; a report from an earlier successful run may still exist, so require
successful completion and the matching receipt before consuming it. The trusted
private build tree is not a hostile-path sandbox. Detached processes, owner SIGKILL,
concurrent source mutation and a total multi-object deadline are outside this scope.

Run `python3 -B experiments/dash-reference/test-audit-imports.py` for six host
controls (four test methods), with a 30-second suite allowance. Evidence in
[UL-075](../../docs/evidence/dash-import-process-2026-09-06/README.md) records
Python 3.10.21/3.14.7 execution and exact comparison with 32 retained objects/99
imports. This is host inspection, not a fresh Linux or native dash execution.
Independent review of this change remains pending. The separate build.py/test.py
launchers still need process-boundary review, including remote container cleanup;
killing a local Podman client would not by itself prove guest cleanup.

## Test-helper compilation (UL-076)

The test runner now delegates only `helper-build` to host-build.py, an adapter over
the existing process helper. It retains the verified cc.py/LLVM/SDK inputs and
compiler flags, with explicit output-directory cwd, private TMPDIR, minimal PATH
and LC_ALL, a 45-second wait and 16 MiB per-file limit. Receipt completeness and
exit zero are required before guest cases start. Existing helper-build.stdout and
helper-build.trace remain separate raw streams; helper-build.process.json also
records local process cleanup. Successful case evidence adds adapter/helper hashes.

Run `python3 -B experiments/dash-reference/test-host-build.py` for six controls
(three test methods), allowing 30 seconds. The
[host evidence](../../docs/evidence/dash-host-build-2026-09-06/README.md) includes
actual pinned compilation matching the previous helper bytes. It does not rerun
the guest cases. Independent review of the adapter/integration remains pending.

UL-077 tracks the still-unmigrated remote boundary in build.py's generated target
launchers and test.py's Podman calls. A client timeout or --rm is not an observed
container cleanup result. Required work includes per-attempt container identity,
creation/start ambiguity, bounded cleanup through the same connection, positive
absence checks, and retained unresolved status if the service cannot answer.
Do not infer whole-build or whole-test cleanup from the local compiler receipts.

## Remote lifecycle prototype (UL-077)

container-process.py is now used by test.py and the top-level build generator
stages (integration checkpoints below). Its Client takes an explicitly pinned executable and fixed URL/identity
paths. run_container creates a unique labelled container from an immutable image,
checks its returned ID/name/label, attaches to that ID, then removes only an inspected
owned container and checks absence of both name and ID. Calls retain local process
receipts and container.json records the lifecycle. No default-connection switching,
VM restart, image pull or broad container cleanup is performed.

The prototype uses non-root UID, no network, read-only root, dropped capabilities,
512 MiB memory and 32 PIDs. The original prototype had no mounts; test integration adds only the fixed
read-only input mount described below. Build generators use the separately validated writable-child mode below.
Management calls wait at most 20 seconds each; guest attach defaults to 45 seconds.
Local files are bounded at 16 MiB each. Deadlines are per call, not a hard total
wall-clock guarantee. Local process-owner and trusted-daemon limitations still apply.

`complete` means a completed client run and observed remote removal; the caller
must separately check guest exit semantics. Exit 125/126/127 is conservatively
rejected because client/runtime errors may be ambiguous. A nonzero guest exit such
as 7 is retained. An incomplete create response remains unresolved even if cleanup
observes absence: late creation has not been excluded. Service loss, wrong ownership
or missing cleanup evidence cannot pass. Labels/name matching assume a trusted
service and no competing resource mutation; they are not native authority.

Run `python3 -B experiments/dash-reference/test-container-process.py` for eleven
modeled protocol cases. [UL-077 evidence](../../docs/evidence/dash-container-2026-09-06/README.md)
also records three real controls using the existing VM. The timeout witness shows
a container still running after local client termination, then exact-ID forced
removal and independent absence checks. Service failure/late-create models are not
live daemon failure tests. The original prototype left launcher integration and full dash regression open;
the test integration below supplies that guest witness. Generated-tool cleanup and
independent technical review remain open.


## Guest lifecycle integration (UL-077)

The existing `python3 experiments/dash-reference/test.py BUILD` command snapshots
one existing default Podman SSH connection through a bounded owned local query.
It records and pins client bytes before use, freezes URL/identity for all cases,
and never starts a VM or changes the default. Missing or ambiguous configuration
fails before container creation. This records local tool identity, not trust in a
remote server or complete host-library provenance.

Each guest case now uses create/inspect/start/remove/absence handling. The input
mount remains read-only at /inputs, with the original 16 MiB /scratch tmpfs and
WITNESS/LC_ALL/PATH values. Sources must resolve to a private build descendant;
comma/newline delimiters reject before client calls. This is input validation,
not protection against concurrent filesystem mutation. The test-input mode never allows writable mounts; generator mode is separate
and described below.

Existing scripts, expected exits, stdout and trace paths are unchanged. Commands
now identify the actual attach argv and guest argv plus the lifecycle receipt.
Aggregate evidence adds the container adapter/client identities. A case cannot
pass its semantic oracle without a complete lifecycle receipt. Failure receipts
remain even if no aggregate evidence.json is produced.

[Integration evidence](../../docs/evidence/dash-container-integration-2026-09-06/README.md)
records twelve cases on Python 3.14.7 and twelve on 3.10.21. Scripts, exits, stdout,
dash and helper bytes match original evidence; traces are fresh and may contain
different PIDs/timing. All 24 containers pass independent name/ID absence queries.
This also exercises UL-076 host helper compilation within the complete runner.
Independent review, writable build generators and live service-loss/creation
ambiguity still remain open. No native shell or TTY support is implied.


## Controlled build generators (UL-077)

build.py now compiles the four target generators in a local make stage, runs each
container from the top-level Python owner, then finishes local make. No nested
remote cleanup owner runs beneath a make timeout. The generated compiler wrappers
use exec, and configure/make/inspection commands use the existing local process
helper with a 240-second per-call wait and 16 MiB file limit. Original compile/link
flags and the four target-ABI generators remain. Upstream source and recipes are
unchanged; the pinned Makefile.am supplies the checked 27-source mkinit argument list.

Each generator's compiled ELF is retained as NAME.elf. A NAME shell guard exits 97
if make unexpectedly tries to execute it; all four guards are exercised. Generator
input hashes are recorded before consumption and checked afterward. Generated output
and guard hashes must remain unchanged through the final make stage.

Containers mount the private build tree read-only and only obj/src writable, with
cwd there. Their lifecycle records sit outside the writable subtree. A live control
writes the allowed child but cannot create a file in its parent. This does not
sandbox host compilation or defend against malicious pinned generators/concurrent
mutation; the provenance and ownership assumptions remain explicit.

[Generator evidence](../../docs/evidence/dash-generator-2026-09-06/README.md) records
the initial Python 3.14.7 build and final identity-checked Python 3.10.21 build, four
guards, four generator lifecycles per build, import audit and twelve fresh guest
cases. Dash matches the original ELF bytes; generated files match after replacing
only build-directory paths in comments. All 21 containers across the two builds,
mount control and guest run pass independent name/ID absence checks. The retained
legacy host-sandbox metadata is explicitly corrected by the final source; no host
sandbox claim is made. Independent review and live creation/service-loss ambiguity
remain open; native shell acceptance is separate.

## Live connection-loss fixture (UL-077)

`test-container-transport.py` uses the test-only `transport-relay.py` to cut its own
loopback connection after confirmed creation. The unchanged adapter must leave the
attempt unresolved; separate recovery through the original connection checks ownership,
removes the container and verifies absence. No shared VM stop is part of this test.
Do not run the fixture against an unreviewed connection or infer that recovery makes
the interrupted run successful.

[Transport evidence](../../docs/evidence/dash-transport-loss-2026-09-06/README.md)
records a passing Python 3.14.7 run. Python 3.10.21 qualification is incomplete because
the original VM endpoint became unavailable before creation; subsequent status reports
the VM stopped. No restart was attempted. Recovery reporting for that setup-failure
path still needs improvement. A lost/in-flight create response and independent review
remain open. This is a test fixture, not a new production proxy or recovery CLI.

Follow-up in this change: recovery reporting now skips remote calls when no create
request was sent and retains recovery errors instead of masking the original failure.
Three offline controls pass on Python 3.10.21/3.14.7 for no-create, unreachable and
absent cases. The successful earlier live execution is retained as test-executed.py
in the transport evidence packet; final fixture live qualification remains pending
until the existing VM is available. No runtime adapter behavior changed.

## Relay directional EOF correction (UL-077)

The relay fixture now preserves TCP half-close semantics: EOF in one direction
allows the other direction to continue, with queued bytes drained before shutdown.
`python3 -B experiments/dash-reference/test-transport-relay.py` exercises request EOF
followed by a large response and response EOF followed by a late request. Both
controls failed before the fix and pass on Python 3.10.21/3.14.7 afterward; see
[EOF evidence](../../docs/evidence/dash-relay-eof-2026-09-06/README.md).

These are loopback fixture controls only. The updated relay still needs live Podman
outage qualification once the existing VM is available, plus independent review.
No production container/build adapter behavior changed.

## Revised live fixture qualification — 2026-09-07

With user-authorized startup of the existing VM, the current EOF/recovery fixture
passes live post-create connection-loss controls on Python 3.14.7 and 3.10.21.
Each preserves its unresolved original outcome and verifies owned recovery/absence.
[Qualification evidence](../../docs/evidence/dash-transport-qualified-2026-09-07/README.md)
retains the initial setup failures and successful retries. In this execution environment,
startup, endpoint check and live tests succeeded when kept in one command session;
a separate-session startup did not leave a reachable VM. No persistent-VM guarantee
is inferred. True in-flight create-response ambiguity and independent review remain
open; revised-relay minimum-version live qualification is no longer pending.

## In-flight create-response fault (UL-077)

`test-container-transport.py --create-response` delays opaque reply bytes through the
owned relay while observe-create.py witnesses actual creation over the original
connection. The relay cuts before the create client receives its ID. The adapter
must leave creation unconfirmed and the run unresolved; separate recovery verifies
and removes the witnessed container. The observer's local process group is owned
and reaped by the fixture. No guest start or shared-service outage is induced.

Both this mode and the original default outage mode pass on Python 3.10.21/3.14.7;
the default success marker is preserved. See
[response-loss evidence](../../docs/evidence/dash-create-response-2026-09-07/README.md).
The planned local lifecycle qualification is now ready for
[independent review](../../docs/quality/DASH-REVIEW.md). Broader migration and native
acceptance remain separate; this one live schedule does not prove every creation race.
