# UL-066 tr/stty source and build plan

2026-09-06. Evaluate released GNU coreutils 9.11 and BusyBox 1.38.0 (upstream labels it unstable) inputs,
without treating a release label as security acceptance. Pin downloaded bytes
before extracting; retain upstream archives, notices and source/configuration
inspection. Existing source authentication/security review remains UL-016.

Scope: compare exact tr/stty build options, dependency closure and upstream tests;
prepare minimal static Linux-musl builds using verified Clang/SDK inputs. Host
configuration tools are distinct from target objects and Linux-emulated binaries.
Do not install, change sibling repositories or use the user's terminal. Use only
owned disposable PTYs for later terminal testing. Source review is not runtime
acceptance. No package recipes or shared standards are introduced.

Apply E-01–08, PX/TX, CD/CP, TD/TE and DP. Record source/tool/SDK hashes, flags,
commands, configuration guesses and failed attempts. Every build phase is bounded
by 240 seconds and owns its process group; all generated files stay under build/.
Use Python 3.12+ standard library and existing pinned host tools. Preserve upstream
style/licenses. Independent source/reader review remains pending UL-061–063.

Expected follow-on runtime checks: C-locale whitespace deletion used by pkg-mgr,
translation/squeeze, NUL/high bytes, malformed arrays, read/write errors; stty
no-terminal failure, disposable-PTY inspection, echo/canonical changes and exact
termios restoration, malformed mode preserving state. GNU -g does not save window
size; do not claim total terminal/session restoration. Native permission and
session-generation boundaries remain UL-008.

Run python3 -B docs/quality/check.py and affected harness checks before reporting.
Do not mark UL-066 complete until the remaining comparison/review is recorded.

First GNU build showed that direct executable targets omit Automake's
BUILT_SOURCES prerequisites. Explicitly build that upstream variable's targets
before tr/stty; retain the failed attempt. The local make fragment only orders
existing generated inputs and does not patch upstream code or build all utilities.

GNU first runtime slice uses 17 independent fixtures: twelve tr byte/error cases,
no-terminal failure, PTY save, echo disable, exact termios restore and invalid mode
with unchanged termios. Every command has 15 seconds within a 180-second owned
container (512 MiB/32 PIDs); the PTY is opened and closed inside that container.
These do not replace upstream suites, raw/canonical/session/permission tests or
full provider comparison. No /dev/tty from the user's session is consumed.

UL-068 provides a verified case-sensitive x86 UAPI export as an additional
-isystem directory after musl. The first consuming build reached link but used
unqualified host ar/ranlib. Explicitly select the already pinned LLVM archive
and index tools for target libraries, retain that attempt, and rebuild freshly.

The LLVM-archive build links both programs but fails the strict no-undefined
inspection on four optional weak gnulib thread probes (pthread_mutex_lock,
pthread_mutex_unlock, pthread_mutexattr_gettype, thrd_exit). Select the supported
--disable-threads configure profile for these single-thread tr/stty executables
and rebuild, preserving the rejected binaries/symbol table. No weak-symbol waiver
or stub is introduced. This choice does not support multithreaded coreutils users.

BusyBox slice: build 1.38.0 with only TR/STTY, character/equivalence classes and
static linking enabled from allnoconfig. Verify the effective applet inventory;
disable setuid machinery and installation. Use pinned LLVM target tools and
Clang for native host configuration helpers, with the existing separate UAPI
view. Compare the same seventeen fixtures without changing GNU expectations:
unsupported constructs count as differences, not silently accepted passes.
Retain complete configs, helper/build logs and all failures. Re-run GNU after
any common-runner edit; no upstream patches without a separately recorded reason.

The first BusyBox build revealed that allnoconfig selects a sh alias and that
-r partial links need no CRT objects. Explicit SH_IS_NONE and a target-only
partial-link wrapper correct the build; require exactly two applets. Build only
busybox_unstripped, so no additional strip tool is consumed. Upstream tr.tests
runs unchanged with its testing.sh, verified against the archive, and exactly
five PASS/no FAIL/no SKIPPED markers are required. Host /bin/echo is a test helper,
not a BusyBox applet; preserve this upstream stdout-oriented oracle's limitations.

GNU upstream slice: run the archive-verified tests/tr/tr.pl and tests/Coreutils.pm
unchanged with the pinned-image Perl interpreter and an explicit QEMU tr wrapper.
Require a nonempty exact inventory of both .r/.p test markers and upstream exit 0;
retain raw stdout/stderr and archive-pinned fixture definitions (DEBUG=0). Check a deliberately failing
wrapper as an oracle control in a separate owned container. No runtime rebuild,
header mount or user terminal is needed. Each container has a 180-second deadline,
512 MiB/32 PIDs and 64 MiB scratch tmpfs, with owned removal in 15 seconds.
Shell-generated wrapper is quoted, checked with /bin/sh -n in the pinned image.
Remaining shell tr suite and stty scripts are separate: stty bad-speed uses
LD_PRELOAD incompatible with static ELF, pairs is expensive, invalid needs
getlimits and controlling PTY, main requires strace, row-col needs private PTY.
Never count not-run scripts or prerequisite skips as passes. CP/CD, TD/TE and
E-01–08 apply; existing source authentication and independent review stay open.

First GNU upstream attempt stopped with missing File::Compare before any tests.
Pin local macOS Perl 5.34 pure-Perl File::Compare 1.1006 and Text::ParseWords 3.30
plus Perl license texts before supplying them in the private test include path.
These are test helpers only, not target dependencies; retain their bytes and
origin. Exercise the full suite and deliberate exit-99 control with the actual
image Perl. No package installation or runtime image modification is required.

The second attempt exposed the upstream Makefile requirement to preload CuSkip
before Coreutils. Retain the compile failure and copy CuSkip.pm from the pinned
archive; use the upstream module order without patching either module.
