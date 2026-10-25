# Minimal Toybox Linux-reference candidate (UL-065)

Toybox 0.8.14 builds unmodified with Clang/LLD 21.1.8 and the retained musl 1.2.6
Linux SDK. The six selected applets (plus the `[` alias) pass 22 independent
runtime checks and 162 cases from four upstream suites. Two host-helper controls
also pass. This is an experimental package feasibility result for contributors;
it is not a native Aether utility set or POSIX certification.

## Inputs and build boundary

[source.lock.json](source.lock.json) pins the HTTPS release archive at SHA-256
`827e4cdfd69f5da973e00e2a59b30b3c9857fb7fae74c362fd0b4f96be7929b0` before
extraction. This is byte identity, not independently authenticated release trust.
[Upstream downloads](https://landley.net/toybox/downloads/) is the acquisition
source. UL-016 retains signature/origin, post-release fixes and release eligibility.

The [minimal configuration](miniconfig) requests cat, wc, printf, test, true,
false, dispatch/help and floating-point printf. Generated config additionally
contains TEST_GLUE, TOYBOX_LSM_NONE and hidden TOYBOX_FORK. The hidden fork symbol
remains enabled despite a miniconfig disable request; it describes a build-platform
facility, not an extra applet or a claim that the candidate never uses fork.
The actual dispatch inventory is exactly `[ cat false printf test true wc`.
No pending, login/init, network or setuid applets are selected. Test grammar/glue
and floating-point printf are deliberate scope, not an all-features default.

Target compilation has explicit musl headers, startup objects and libc.a, static
LLD linkage, stack protection and section garbage collection. There is no target
GCC runtime, added Linux header tree or optional target library in this artifact.
The build probes optional libraries but records an empty LIBRARIES result. Unused
shared-library code is removed at link time; compiling all lib/*.c does not mean
all those facilities are reachable. Upstream warning/optimization flags are retained.

Host generators kconfig and mkflags use pinned Clang against the explicit macOS
SDK. They generate configuration/option/help tables; this differs from dash's
signal-table generators that required target execution. Host tools include Bash,
GNU sed 4.10 and standard macOS utilities. GNU sed was explicitly provisioned and
[its executable pinned](host-tools.lock.json). Homebrew also updated its own runtime
and metadata during provisioning. That network phase is separate from the offline
build. The full host SDK/shared-library closure is not hermetically pinned.
No target generator execution, real-prefix install or package activation occurs.

## Reproduce

Prerequisites: Python 3.12+, the pinned local LLVM tools, GNU sed and unchanged
reference SDK identified in experiments/musl-reference. Runtime tests additionally
need the existing pinned Podman image and running VM; the scripts neither pull
images nor start a VM. From the repository root:

1. Place the separately acquired archive at the locked build/ path.
2. Run `python3 -B experiments/toybox-reference/build.py`.
3. Run `python3 -B experiments/toybox-reference/test.py BUILD_DIRECTORY`, replacing
   BUILD_DIRECTORY with the absolute directory printed by the build.
4. Run `python3 -B docs/quality/check.py` and inspect all evidence/limits.

A successful build prints its directory and a reference-build PASS. A failed
phase retains stdout/stderr and commands there; inspect those before retrying.
The final validated build is `build/toybox-reference-1safvmep`, with test output
at `build/toybox-cases-of82lf0l`. Different source, tools, SDK or test inputs require
fresh evidence. The test script rejects changed recorded inputs.

Each build phase has a 240-second deadline and owned process-group termination.
Each test uses a uniquely named, disposable container: UID 65534, no capabilities,
no network, read-only root and inputs, 16 MiB scratch, 512 MiB memory and 32 PIDs.
Independent cases have 45-second deadlines; each upstream suite has 180 seconds.
Cleanup explicitly removes only its named container and must succeed. The host
script may require local socket permission. No sibling state is changed.

## Results and test attribution

The final ELF is 157,984 bytes (unstripped), x86-64 ET_EXEC, with no interpreter,
dynamic segment, W+X load, executable stack or unresolved external symbol.
LLD retains musl's local hidden zero-valued _DYNAMIC marker, as in the earlier musl
reference; it is not an unresolved external runtime dependency. File size is not
peak memory, portability or native loader admission evidence.

| Layer | Actual result |
| --- | --- |
| Independent command execution | 22 cases: exact inventory, disabled sh rejection, true/false, test/bracket success/false/syntax, printf text/NUL/error, cat binary/empty/missing, wc bytes/lines/empty/missing, and cat/printf/wc full-output errors |
| Upstream cat | 9 pass, 0 fail, 0 skip |
| Upstream wc | 25 pass, 0 fail, 0 skip |
| Upstream printf | 47 pass, 0 fail, 0 skip |
| Upstream test | 81 pass, 0 fail, 0 skip |
| Host helper controls | Two pass: xxd -p hex formatting/line wrapping and rejection of other options |
| Harness control | Actual cat output fails the same output matcher when given a deliberately incorrect expected result |

The runner retains 28 container results: 22 independent cases, two helper controls
and four suite invocations. Upstream has no true.test or false.test in this release;
independent direct executions cover their statuses. Zero discovery, skips, failure
markers or nonzero suite exits reject the selected upstream run.

Candidate wrappers explicitly invoke qemu-x86_64 with the static ELF and applet
name. Bash builtins test, [, printf, true and false are disabled for upstream
suite execution so they cannot silently replace the candidate. Other tools, fixture
creation, Bash and Linux device/permission behavior belong to the pinned host image.
The cat suite's executable-file copying case copies its wrapper; the independent
binary case separately covers all byte values across multiple 4096-byte buffers.

The image lacks xxd. A host-only Python helper implements the exact xxd -p mode
used by upstream printf tests, including 30-byte lines, and is checked separately.
No xxd applet or Python interpreter is added to the target payload. Upstream test
files remain unchanged. UTF-8 wc cases execute, but they do not establish a full
locale or Unicode terminal profile. These are QEMU Linux calls, not native Aether
syscalls or target capability-denial witnesses.

## Failures retained and native follow-ons

The first build failed on macOS sed syntax and sandboxed /dev/stderr probe logging.
A second linked successfully but our initial check rejected the known local musl
_DYNAMIC marker. GNU sed, quiet library probing and external-symbol inspection
resolved those setup issues without upstream patches. An initial test run expected
the wrong printf diagnostic and lacked xxd; both attempts remain in retained records.
The final runner additionally binds upstream test bytes and shares its output
matcher with the negative control. Earlier passes are not substituted for this run.

Native adaptation needs more than read/write hooks. Shared startup handles umask
and locale; cat uses loopfiles and checked writes; wc uses fstat for its regular-file
byte-count shortcut plus character classification; test reaches file metadata,
access and isatty. Optional code and linked symbol presence require path-sensitive
review before deciding which operations a native build actually needs. Never turn
these into successful stubs. ELF size alone does not establish runtime memory fit.

UL-067 will map retained imports to exact native operations and decide whether a
standalone cat/wc build reduces startup requirements and authority ambiguity. Public
runner startup, command identity and grants remain UL-059/owner contracts. UL-063
still precedes UL-058 behavior changes. Source-trust/security audit (UL-016), host
sanitizers/fuzzing (UL-062), native execution and packaging remain open.

## Licenses and evidence

Toybox's archive LICENSE grants permissive use (0BSD-style wording). Preserve all
per-file notices and the complete source archive; do not relicense it under our
first-party BSD-2-Clause default. Retain musl COPYRIGHT as well. Source/build tools
and embedded-library update closure still require package-owner review.

[Retained evidence](../../docs/evidence/toybox-reference-2026-09-06/summary.json)
includes the candidate ELF, exact archive/config, build/test scripts, tool/SDK
identities, logs, results, earlier attempts and notice files. Source SHA-256 and
passing tests do not establish a security audit or permission to publish a supported
base. No upstream tool was rewritten for the Aether userland in this slice.

## UL-067 source audit checkpoint

The [native dependency audit](../../docs/research/TOYBOX-NATIVE-AUDIT.md) verifies
pinned startup/cat/wc/helper source and retained artifacts. Standalone dispatch
still reaches shared umask/locale/allocation setup; filename closes ignore errors,
and Toybox's flush/_exit path does not inherit bytecount's finish() cleanup.
Standalone cat/wc now pass 34 upstream and 10 independent Linux-reference cases,
plus two wrong-output oracle controls. Their static unstripped sizes are 79,888 and
85,848 bytes versus the retained multicall 157,984 bytes. Shared startup remains;
no native port is claimed. The audit records config-default surprises, symbol
comparison and the next partial-I/O/close/locale controls. Baseline evidence unchanged.

With the existing pinned SDK/archive/tools and running local Podman VM:

```sh
python3 -B experiments/toybox-reference/build.py --applet cat
python3 -B experiments/toybox-reference/test-standalone.py build/<printed-build-root>
```

Use `--applet wc` for the second candidate. Omitting `--applet` retains the multicall
configuration. Both tools require Python 3.12+; help/version exit 0 on stdout and
invalid usage exits 64 on stderr. Tests never start a VM or pull an image. Build
failures retain private logs; the actual generated config, not miniconfig alone,
is authoritative. Existing Linux-reference evidence is not target conformance.

## Direct I/O fault experiment

Run `python3 -B experiments/toybox-reference/check-io-faults.py` with the retained
standalone cat objects and pinned local tools/image. It verifies earlier evidence,
pins local object bytes, reproduces the original ELF, then relinks a separate
instrumented candidate. Seven cases cover exact copying, short I/O, EINTR, a
committed output prefix followed by EIO and ignored filename-close EIO. This is
Linux reference evidence; the locale and buffered-output follow-up is below. See the
[native audit](../../docs/research/TOYBOX-NATIVE-AUDIT.md) for observed limitations.

## Locale and buffered-output experiment

Run `python3 -B experiments/toybox-reference/check-locale-buffered.py` with the
same retained objects, tools and running pinned local image. Four instrumented
locale cases check exact call traces and input-time codeset; four uninstrumented
cat -e cases check small/large successful output and real /dev/full failures.
Both locale-allocation denials leave a non-UTF-8 codeset but do not stop cat.
Buffered ENOSPC returns status1. See the native audit for precise limits and the
next candidate-scope proposal; none of these results is native acceptance.

The [bounded native-cat proposal](../../docs/TOYBOX-NATIVE-CAT.md) defines the next
candidate scope and owner gaps. No Toybox native build or execution is claimed.

The [host finalizer](FINALIZER.md) tests shutdown callback ordering, error
preservation, re-entry and uncertain cleanup. It is not linked into Toybox/native
runtime; the next local task is the private stdio bridge proposal.

The [private vector candidate](VECTOR.md) supplies host-tested ordered gathering
and no-replay state for a future stdio bridge. It also records process-mask
semantics as an unimplemented proposal. Actual musl-loop integration comes next.

The [actual musl write-loop fixture](STDIO-LOOP.md) now exercises private-vector
progress/error handling against real FILE callback code in Linux reference.
Shared poison/finalizer composition remains the next local integration step.

The [shared host session](SESSION.md) now connects write uncertainty to finalization
without further transport after poison. Bounded process-mask state tests are next.

The [process-mask host candidate](MASK.md) now tests real state exchange, lifecycle
and context isolation. Native umask remains unsupported pending accepted integration.

The [combined Toybox fixture](COMPOSED.md) now exercises real startup, stdio and
shutdown with the host candidates in Linux reference. Native owner review comes next.
