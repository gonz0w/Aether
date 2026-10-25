# Pipe descriptor execution boundary

## Requirement and review before implementation

The next combined dash execution/substitution path needs the existing 16-slot
descriptor preparation to account for three stream bindings plus a pipe reader
and writer. Preserve the three-binding entry point and its semantics. Prepare a
five-binding candidate without effects; at execution commit, only the authenticated
process's pipe holders may shrink. A surviving alias preserves its endpoint, and
another process's holders and queued bytes survive. Failed preparation/admission
must leave the original descriptors and pipe unchanged.

The pipe owner must validate the active pipe generation, ready caller identity,
exact previous holder set and absence of added rights before changing any holder.
The eventual native execution dispatcher must quiesce the caller's I/O, validate
the complete descriptor snapshot and replacement readiness, then apply this local
transition once with descriptor publication. This core method cannot establish
that distributed commit or authenticate a transport itself. A lost reply is not
permission to replay execution. No public ABI or SDK operation is introduced.

Forbidden outcomes: CLOEXEC releasing a surviving alias or peer's endpoint,
premature EOF, revival of an endpoint, stale-generation mutation, dropped bytes
on rejected admission, or claiming a host model is native pipe-through-exec.
The bound remains 16 descriptors, five bindings, one 256-byte pipe and two holders;
no allocation, new unsafe code, dependency, kernel authority or quota is added.
The owner remains Aether's private Rust connection dispatcher; independent
Aether-userland acceptance remains required before adopting the runtime interface.

Simplicity (SE-01–SE-05): retain one descriptor-filter algorithm, instantiated for
the existing three and required five bindings. Duplicating filtering would create
two CLOEXEC rules to maintain; a general descriptor/service framework is unnecessary.
Borrow only the established Unix rule that CLOEXEC removes descriptor aliases on
successful exec while surviving aliases retain the open endpoint. The extra local
pipe transition is necessary to preserve that rule across separate processes;
it removes no native adapter yet. The existing PIPE+EXEC guard remains until
native admission, replacement, signals and receipt delivery are composed.

Applicable rules: Foundations O-02–O-04, I-01/I-03–I-06, E-01/E-03–E-06;
local DEVELOPMENT and the pinned simplicity snapshot. No standard pin changes.
Touched Rust uses the Rust 1.98.0 toolchain (rustfmt 1.9.0), edition 2024; the existing Python host harness
keeps its scoped format. Update NATIVE-SHELL-STARTUP, DEVELOPMENT and STATE with
the exact coverage and next native integration step. No new entry point/profile.

Selected checks: alias/CLOEXEC preparation, malformed five-binding snapshots,
successful holder retention/release, EOF/EPIPE, stale identity/generation and
no-mutation rejection; no_std x86_64 compilation; semantic mutant rejection;
the required host suite and existing connections target regressions on frozen
sources. Preserve attempts, commands, timing and source identities here.

## Results

All 23 core tests pass, including 1,920 pipe alias/flag combinations, and five
semantic mutants fail in their named behavioral tests. The five-binding helper
and pipe commit compile without std for x86_64-unknown-none. The complete host
suite passes (100 Python tests plus the existing Zig checks and immutable pins).
Formatting and the separately pinned simplicity manifest/four files pass.

All 274 existing connections QEMU cases pass in 827.14 seconds. This is regression
coverage of the existing separate execution and pipe paths. No new native profile
calls `prepare_pipe` or `commit_exec` yet. The 89 copied-fork C ELFs are unchanged;
the largest owner remains 12,320 bytes within the 16 KiB limit. The descriptor
filter refactor changes 75 existing owner binaries, which is why the complete
connections regression was selected. The other 192 owner binaries are unchanged.
Separate launch/console-only suites were not repeated: their source paths do not
consume this descriptor preparation; serial dash cases are included in connections.

The harness's own pre-build source hashes match the archived source inventory and
final working files. `sources.json`/`sources.tar.gz` retain runtime/test sources;
`connections-results.json` and the checked artifact archive retain target commands,
inputs, images and serial logs. `qualification.json` records counts and limits.
Host command/timing receipts, compiler identity, no_std object, core-test binary,
mutant inputs and outputs, and the implementation diff are retained here.

Two setup issues are retained, not runtime failures: the supplemental inventory
initially assumed a nonexistent build.zig.zon; its corrected snapshot was taken
during the run, and verified against the harness's independent pre-build hashes.
The attempted cancellation was denied and the run continued unchanged; see
`inventory-attempt-1.txt`. The first mutant driver matched two generation guards
and stopped after two successful mutant rejections. Its corrected attempt targets
only the commit guard and rejects all five mutants. No runtime source changed
between these checks and final regression completion. No failed evidence was deleted.

Next wire the existing parked-child executable replacement into the pipe owner:
validate a complete five-binding snapshot, preserve admitted endpoint references,
publish the filtered table and signal mask, and commit holder changes before the
replacement can issue I/O. Prove an external writer and peer reader through EOF,
wait/ack and reclaim, plus denied admission that preserves descriptors. Then use
that path in serial dash. Interrupted/ambiguous replacement, installed SDK delivery,
independent consumer acceptance and filesystem/sys-init/package assembly remain open.

No kernel source, ABI, quota, SDK, sibling repository, upstream object, released pin
or boot marker changed. This packet does not establish native execution across a
live pipe, full shell support, independent owner sign-off or release readiness.
