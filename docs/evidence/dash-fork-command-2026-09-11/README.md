# Actual dash fork/exec/wait command — 2026-09-11

Pinned actual dash evaluates `(exec /next); exit $?` through its real main, parser,
foreground subshell, forkshell, exec builtin and wait3. Its child replaces itself
with the already-granted /next image. The replacement verifies argv/environment,
fresh TLS, PID/parent, restored zero mask and inherited stdio without FD10/CLOEXEC,
then reads a and exits 72. Dash collects the actual status and exits 72. Two fresh
generations require three backend closes each, backend17 and six reclaims.

AECAT003 provides fixture identity 1000 and a connection-scoped /work directory
using existing op4/op5 semantics. The owner restores AECAT001 for the replacement.
The original parent table has stdio plus an extra CLOEXEC stdin alias; exec drops
that alias without dropping any stdio holder or prematurely closing the backend.
The selected wrapper closes remaining parent descriptors only on known completed
application exits 72/73; uncertain staging exits do not start new cleanup traffic.
The replacement consumes the complete table/mask bootstrap before semantic
validation, and performs no application operations until every field is valid.

All 227 connections cases and five launch cases pass, together with host tests and
format/workflow/pin checks. The skip-main control falsely exits 72 before fork and
must reject parent72/owner1950. Retaining child CLOEXEC must reject child224/owner2130.
Corrupting the actual wait status must reject parent73/owner2130. All require zero
reclaims and their exact ordered context; generic panic or timeout cannot pass.

Attempt1 passed host/launch but its first dash boot rejected owner1901 before child
admission. The profile enabled signal actions without the existing signal-copy
opt-in, so freeze correctly refused the operation. Only build selection changed.
Attempt2 passed host/launch, the real dash positive and skip-main, but the leaked
CLOEXEC control produced child224/owner1950 rather than expected owner2130. The
replacement had rejected its table before reading the pending mask record. The
final receiver consumes the complete bootstrap before validation; the exact
original control remains required. Every attempt retains frozen inputs, commands,
timings, outputs and artifacts. No kernel relaxation was made.

The pre-code requirement and SE-01–SE-05 review are in NATIVE-SHELL-STARTUP.md.
Reuse real upstream objects and existing private musl adapters instead of another
fake shell caller. Explicit subshell syntax selects upstream fork without a fake
vfork alias. Startup metadata and dispatch remain in the one capability-scoped
owner; no new service, allocation framework or kernel syscall is introduced.
The owner retains the 16 KiB code bound, one-page stack, six channels and existing
worker memory quotas. Stable valid pointers, one caller context, synchronous
staging, a single fork and fixed /next authority remain limits.

The 32 dash object hashes and native ENV-guard main pin are checked at link time.
Only the pinned native main replaces the Linux-reference main. The remaining 31
objects are unchanged. Final linked disassembly and symbol inspection show wrapper
to actual main, forkshell to fork, execve to the private staging hook and wait3 via
wait4 to the retained wait adapter. The ordinary vfork path remains present and
unmodified. Source-authenticity/native-configuration and independent consumer
acceptance limits of the original object receipts still apply.

This is a bounded producer shell command, not a complete interactive shell, native
SDK publication or R1 acceptance. No persistent executable lookup, ordinary vfork,
redirection/pipelines, live SIGCHLD composition, arbitrary user pointer handling or
general recovery is claimed. No sibling repository, released pin, dependency,
kernel source or ABI changed. Next settle ordinary native command launch and the
matching SDK/dash handoff, then continue serial-shell and persistent-storage work.
No independent owner or reader approval is claimed.

run-sources binds frozen execution inputs; sources adds final documentation.
The source/artifact archives are read back against their indexes. compatibility
compares every prior 223 case: all worker and owner payload bytes are unchanged
outside developer entropy, and all kernel loadable bytes match. owner-sizes checks
version-specific bounds. qualification records counts and measured owner sizes;
final-checks records host, format, workflow, standards and whitespace results.
collect.py also verifies the previous sealed packet and four-file simplicity pin.
manifest.json seals all packet files. Reproduce with the SDK/tool paths and suite
commands recorded in timing records and NATIVE-CONNECTIONS.md. Only verified
superseded unpacked duplicates are eligible for cleanup; sealed archives remain.

Use fresh evidence/output destinations when replaying the recorded helper recipes;
never overwrite this sealed packet or its predecessors.

The positive dash owner measures8,904 bytes; the largest new control is8,920 bytes.
All six superseded unpacked build directories were verified against their preserved
archives and removed. The current connections/launch baseline and earlier init
baselines remain unpacked. cleanup.json records exact paths, bytes and archive hashes.
